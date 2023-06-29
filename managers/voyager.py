"""
Author: Grant Fullenkamp
Email: gmfullenkamp@gmail.com
Creation Date: 06-29-2023
Description: The Minecraft LLM trainer.
Reference: https://github.com/MineDojo/Voyager/blob/main/voyager/voyager.py
"""
import os

from agents import ActionAgent, CriticAgent, CurriculumAgent, SkillManager
from envs import MinecraftEnv, MinecraftEventRecorder


class Voyager:
    def __init__(self, log_dir: str, host: str, port: int, resume: bool = False, env_wait_ticks: int = 20,
                 env_request_timeout: int = 600, max_iterations: int = 160, reset_placed_if_failed: bool = False,
                 action_agent_task_max_retries: int = 4, action_agent_settings: dict = None,
                 curriculum_agent_settings: dict = None, critic_agent_settings: dict = None,
                 skill_manager_settings: dict = None):
        """
        The Minecraft LLM trainer.
        Action agent is the iterative prompting mechanism.
        Curriculum agent is the automatic curriculum.
        Critic agent is the self-verification.
        Skill manager is the skill library.
        :param log_dir: The output directory that holds the checkpoints and skills.
        :param host: Minecraft host ip address.
        :param port: Minecraft in-game port.
        :param resume: Boolean for whether to resume learning or start new.
        :param env_wait_ticks: How many ticks at the end of each step will wait, if you found some chat log missing,
        you should increase this value.
        :param env_request_timeout: How many seconds to wait for each step, if the code execution exceeds this time,
        Python side will terminate the connection and need to be resumed.
        :param max_iterations: The number of maximum iterations to go through the voyager chain training process.
        :param reset_placed_if_failed: Whether to reset placed blocks if failed, useful for building task.
        :param action_agent_task_max_retries:  How many times to retry if failed.
        :param action_agent_settings: A dictionary of the ActionAgent kwargs.
        :param curriculum_agent_settings: A dictionary of the CurriculumAgent kwargs.
        :param critic_agent_settings: A dictionary of the CriticAgent kwargs.
        :param skill_manager_settings: A dictionary of the SkillManager kwargs.
        """
        # Set up the output paths
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        ckpt_dir = os.path.join(log_dir, "checkpoints")
        if not os.path.exists(ckpt_dir):
            os.mkdir(ckpt_dir)
        skills_dir = os.path.join(log_dir, "skill_library")
        if not os.path.exists(skills_dir):
            os.mkdir(skills_dir)

        self.env_wait_ticks = env_wait_ticks
        self.reset_placed_if_failed = reset_placed_if_failed
        self.max_iterations = max_iterations
        self.action_agent_max_retries = action_agent_task_max_retries
        self.resume = resume
        self.recorder = MinecraftEventRecorder(ckpt_dir=ckpt_dir, resume=resume)

        # Set up the default agent settings
        if action_agent_settings is None:
            action_agent_settings = {}
        if curriculum_agent_settings is None:
            curriculum_agent_settings = {}
        if critic_agent_settings is None:
            critic_agent_settings = {}
        if skill_manager_settings is None:
            skill_manager_settings = {}

        # Init the environment
        self.env = MinecraftEnv(host=host, port=port, request_timeout=env_request_timeout)

        # Init the agents
        self.action_agent = ActionAgent(ckpt_dir=ckpt_dir, resume=resume, **action_agent_settings)
        self.curriculum_agent = CurriculumAgent(ckpt_dir=ckpt_dir, resume=resume, **curriculum_agent_settings)
        self.critic_agent = CriticAgent(**critic_agent_settings)
        self.skill_manager = SkillManager(skills_dir=skills_dir, resume=resume, **skill_manager_settings)

        # Init attributes
        self.action_agent_rollout_num_iter = -1
        self.task = None
        self.context = ""
        self.messages = None
        self.conversations = []
        self.last_events = None

    def reset(self, task, context="", reset_env=True):
        """Resets the action agent, task, context, and environment."""
        self.action_agent_rollout_num_iter = 0
        self.task = task
        self.context = context
        if reset_env:
            self.env.reset(mode="soft", wait_ticks=self.env_wait_ticks)
        difficulty = ("easy" if len(self.curriculum_agent.completed_tasks) > 20 else "peaceful")
        # Step to peek an observation
        events = self.env.step("bot.chat(`/time set ${getNextTime()}`);\n" + f"bot.chat('/difficulty {difficulty}')")
        skills = self.skill_manager.retrieve_skills(query=self.context)
        print(f"\033[33mRender Action Agent system message with {len(skills)} skills\033[0m")
        system_message = self.action_agent.render_system_message(skills=skills)
        human_message = self.action_agent.render_human_message(events=events, code="", task=self.task, context=context,
                                                               critique="")
        self.messages = [system_message, human_message]
        print(f"\033[32m****Action Agent human message****\n{human_message.content}\033[0m")
        assert len(self.messages) == 2
        self.conversations = []
        return self.messages

    def close(self):
        """Closes the environment."""
        self.env.close()
