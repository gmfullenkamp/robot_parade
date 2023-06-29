"""
Author: Grant Fullenkamp
Email: gmfullenkamp@gmail.com
Creation Date: 06-29-2023
Description: The Minecraft LLM trainer.
Reference: https://github.com/MineDojo/Voyager/blob/main/voyager/voyager.py
"""
import copy
import os
import time

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
        self.action_agent_task_max_retries = action_agent_task_max_retries
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

    def step(self):
        """"""
        if self.action_agent_rollout_num_iter < 0:
            raise ValueError("Agent must be reset before stepping.")
        ai_message = self.action_agent.llm(self.messages)
        print(f"\033[34m****Action Agent ai message****\n{ai_message.content}\033[0m")
        self.conversations.append((self.messages[0].content, self.messages[1].content, ai_message.content))
        parsed_result = self.action_agent.process_ai_message(message=ai_message)
        success = False
        if isinstance(parsed_result, dict):
            code = parsed_result["program_code"] + "\n" + parsed_result["exec_code"]
            events = self.env.step(code, programs=self.skill_manager.programs)
            self.recorder.record(events, self.task)
            self.action_agent.update_chest_memory(events[-1][1]["nearbyChests"])
            success, critique = self.critic_agent.check_task_success(
                events=events, task=self.task, max_retries=5,
                chest_observation=self.action_agent.render_chest_observation(), context=self.context)
            if self.reset_placed_if_failed and not success:
                # Revert all the placing events in the last step
                blocks = []
                positions = []
                for event_type, event in events:
                    if event_type == "onSave" and event["onSave"].endswith("_placed"):
                        block = event["onSave"].split("_placed")[0]
                        position = event["status"]["position"]
                        blocks.append(block)
                        positions.append(position)
                new_events = self.env.step(f"await givePlacedItemBack(bot, {json_dumps(blocks)}, "
                                           f"{json_dumps(positions)})", programs=self.skill_manager.programs)
                events[-1][1]["inventory"] = new_events[-1][1]["inventory"]
                events[-1][1]["voxels"] = new_events[-1][1]["voxels"]
            new_skills = self.skill_manager.retrieve_skills(query=(self.context + "\n\n"
                                                                   + self.action_agent.summarize_chatlog(events)))
            system_message = self.action_agent.render_system_message(skills=new_skills)
            human_message = self.action_agent.render_human_message(events=events, code=parsed_result["program_code"],
                                                                   task=self.task, context=self.context,
                                                                   critique=critique)
            self.last_events = copy.deepcopy(events)
            self.messages = [system_message, human_message]
        else:
            assert isinstance(parsed_result, str)
            self.recorder.record([], self.task)
            print(f"\033[34m{parsed_result} Trying again!\033")
        assert len(self.messages) == 2
        self.action_agent_rollout_num_iter += 1
        done = (self.action_agent_rollout_num_iter >= self.action_agent_task_max_retries or success)
        info = {"task": self.task, "success": success, "conversations": self.conversations}
        if success:
            assert ("program_code" in parsed_result and "program_name" in parsed_result), \
                "program and program_name must be returned when success"
            info["program_code"] = parsed_result["program_code"]
            info["program_name"] = parsed_result["program_name"]
        else:
            print(f"\033[32m****Action Agent human message****\n{self.messages[-1].content}\033[0m")
        return self.messages, 0, done, info

    def rollout(self, *, task, context, reset_env=True):
        """The main train function that goes through each step."""
        self.reset(task=task, context=context, reset_env=reset_env)
        while True:
            messages, reward, done, info = self.step()
            if done:
                break
        return messages, reward, done, info

    def learn(self, reset_env=True):
        if self.resume:
            # Keep the inventory
            self.env.reset(mode="soft", wait_ticks=self.env_wait_ticks)
        else:
            # Clear the inventory
            self.env.reset(mode="hard", wait_ticks=self.env_wait_ticks)
            self.resume = True
        self.last_events = self.env.step("")

        while True:
            if self.recorder.iteration > self.max_iterations:
                print("Iteration limit reached")
                break
            task, context = self.curriculum_agent.propose_next_task(
                events=self.last_events, max_retries=5,
                chest_observation=self.action_agent.render_chest_observation())
            print(f"\033[35mStarting task {task} for at most {self.action_agent_task_max_retries} times\033[0m")
            try:
                messages, reward, done, info = self.rollout(task=task, context=context, reset_env=reset_env)
            except Exception as e:
                time.sleep(3)  # Wait for mineflayer to exit
                info = {"task": task, "success": False}
                # reset bot status here
                self.last_events = self.env.reset(mode="hard", wait_ticks=self.env_wait_ticks,
                                                  inventory=self.last_events[-1][1]["inventory"],
                                                  equipment=self.last_events[-1][1]["equipment"],
                                                  position=self.last_events[-1][1]["status"]["position"])
                # Use red color background to print the error
                print("Your last round rollout terminated due to error:")
                print(f"\033[41m{e}\033[0m")

            if info["success"]:
                self.skill_manager.add_new_skill(info)

            self.curriculum_agent.update_exploration_progress(info)
            print(f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m")
            print(f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m")

        return {"completed_tasks": self.curriculum_agent.completed_tasks,
                "failed_tasks": self.curriculum_agent.failed_tasks,
                "skills": self.skill_manager.skills}

    def decompose_task(self, task):
        if not self.last_events:
            self.last_events = self.env.reset(mode="hard", wait_ticks=self.env_wait_ticks)
        return self.curriculum_agent.decompose_task(task, self.last_events)

    def inference(self, task=None, sub_goals=None, reset_mode="hard", reset_env=True):
        if sub_goals is None:
            sub_goals = []
        if not task and not sub_goals:
            raise ValueError("Either task or sub_goals must be provided")
        if not sub_goals:
            sub_goals = self.decompose_task(task)
        self.env.reset(mode=reset_mode, wait_ticks=self.env_wait_ticks)
        self.curriculum_agent.completed_tasks = []
        self.curriculum_agent.failed_tasks = []
        self.last_events = self.env.step("")
        while self.curriculum_agent.progress < len(sub_goals):
            next_task = sub_goals[self.curriculum_agent.progress]
            context = self.curriculum_agent.get_task_context(next_task)
            print(f"\033[35mStarting task {next_task} for at most {self.action_agent_task_max_retries} times\033[0m")
            messages, reward, done, info = self.rollout(task=next_task, context=context, reset_env=reset_env)
            self.curriculum_agent.update_exploration_progress(info)
            print(f"\033[35mCompleted tasks: {', '.join(self.curriculum_agent.completed_tasks)}\033[0m")
            print(f"\033[35mFailed tasks: {', '.join(self.curriculum_agent.failed_tasks)}\033[0m")
