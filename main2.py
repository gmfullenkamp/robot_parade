import os
import time
from multiprocessing import Process

HOST = "192.168.0.15"
PORT = 50355
NUM_BOTS = 7  # Can only have a 7 bot max on lan worlds (8 player max)
COMMAND = "mine-100000-grass_block"


def main():
    for i in range(NUM_BOTS):
        bot_username = f"robot_{i}"
        proc = Process(target=os.system, args=[f"python create_bot.py --host {HOST} --port {PORT} "
                                               f"--username {bot_username} --command {COMMAND}"])
        proc.start()
        time.sleep(1)


if __name__ == "__main__":
    main()
