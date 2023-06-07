from multiprocessing import Process

from MinecraftBot import MinecraftBot

HOST = "192.168.0.15"
PORT = 51568
COMMAND = "mine 100000 grass_block"
BOT_USERNAME = "robot"  # Same name == keep previous inventory


def main():
    MinecraftBot(host=HOST, port=PORT, username=BOT_USERNAME, command=COMMAND)


if __name__ == "__main__":
    main()
