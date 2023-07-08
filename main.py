import argparse

from voyager import Voyager


def get_main_args():
    """Parses the CLI for main.py."""
    parser = argparse.ArgumentParser(description="Perform lifelong training of a Minecraft agent.", allow_abbrev=True)
    parser.add_argument("-m", "--mc-port", type=int, required=True, help="The LAN port for your minecraft world.")
    parser.add_argument("-k", "--openai-api-key", type=str, required=True, help="Your OpenAI API key.")
    parser.add_argument("-t", "--task", type=str, default=None, help="The desired task for the Minecraft agent.")
    parser.add_argument("-s", "--skill-library-dir", type=str, default="./skill_library/all_trials",
                        help="The path to the skill library.")
    return parser.parse_args()


def main():
    args = get_main_args()

    voyager = Voyager(mc_port=args.mc_port,
                      openai_api_key=args.openai_api_key,
                      skill_library_dir=args.skill_library_dir)

    if args.task is None:
        # start lifelong learning
        voyager.learn()
    else:
        # start task oriented learning
        sub_goals = voyager.decompose_task(task=args.task)
        voyager.inference(sub_goals=sub_goals)


if __name__ == "__main__":
    main()
