import argparse

from MinecraftBot import MinecraftBot

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="The ip address of the host computer.", type=str)
parser.add_argument("--port", help="The port address of the minecraft server.", type=int)
parser.add_argument("--username", help="The username of the bot.", type=str)
parser.add_argument("--command", help="The command for the bot to follow.", type=str)
args = parser.parse_args()
print(f"Creating bot '{args.username}'...")
MinecraftBot(host=args.host, port=args.port, username=args.username, command=args.command)
