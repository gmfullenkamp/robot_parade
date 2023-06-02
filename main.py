from multiprocessing import Process

from MinecraftBot import MinecraftBot

HOST = "192.168.0.15"
PORT = 50319
BOT_USERNAME = "Robot"  # Same name == keep previous inventory


def main():
    MinecraftBot(host=HOST, port=PORT, username=BOT_USERNAME)
    # proc_bot_one = Process(target=MinecraftBot, args={"host": HOST,
    #                                                   "port": PORT,
    #                                                   "username": BOT_USERNAME})
    # proc_bot_one.start()


if __name__ == "__main__":
    main()
