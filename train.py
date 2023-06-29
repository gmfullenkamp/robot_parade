"""
Author: Grant Fullenkamp
Email: gmfullenkamp@gmail.com
Creation Date: 06-29-2023
Description: Run training of the Minecraft bot on the user's world.
"""
from argparse import ArgumentParser


def get_arguments():
    """Parses the CLI."""
    parser = ArgumentParser(description="Run training of the Minecraft bot on the user's world.",
                            allow_abbrev=True)
    parser.add_argument("-h", "--host", type=str, required=True,
                        help="The ip address to the host machine or server. (i.e. 123.45.67.89)")
    parser.add_argument("-p", "--port", type=int, required=True,
                        help="The port on the host ip address. (i.e. 45678)")
    parser.add_argument("-n", "--name", type=str, default="Bot",
                        help="The name of the Minecraft bot being created.")
    return parser.parse_args()


def main() -> None:
    """The main function for training a Minecraft bot on the user's world."""
    args = get_arguments()
    print(f"Host: {args.host}, Port: {args.port}, Name: {args.name}")


if __name__ == "__main__":
    main()
