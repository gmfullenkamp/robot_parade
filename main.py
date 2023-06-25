from multiprocessing import Process
from multiprocessing import Queue
import time
import os

from MinecraftBot import MinecraftBot

HOST = "192.168.0.15"
PORT = 50056
PRODUCER_BOT = "Producer"
PLAYER = "GermF"
BLOCK_RANGE = 5
BLOCK_ID = "grass_block"


def producer(queue):
    # Initialize the producer robot
    producer_bot = MinecraftBot(host=HOST, port=PORT, username=PRODUCER_BOT)
    time.sleep(1)
    player_location = producer_bot.bot.players[PLAYER].entity.position
    count = (BLOCK_RANGE * 2) ** 3
    block_locations = producer_bot.bot.findBlocks({"point": player_location,
                                                   "matching": producer_bot.minecraft_data.blocksByName[BLOCK_ID]["id"],
                                                   "maxDistance": BLOCK_RANGE,
                                                   "count": count})
    for block in block_locations:
        command = f"mine_{block.x}_{block.y}_{block.z}"
        queue.put(command)
    # all done
    queue.put(None)
    return producer_bot


def consumer(queue, producer_bot):
    while True:
        total_players = 0
        for i, _ in enumerate(producer_bot.bot.players):
            total_players = i + 1
        if total_players < 8:
            command = queue.get()
            if command is None:
                break
            else:
                proc = Process(target=os.system, args=[f"python create_bot.py --host {HOST} --port {PORT} "
                                                       f"--username {command} --command {command}"])
                proc.start()
                time.sleep(1)
        else:
            time.sleep(2)


# entry point
if __name__ == "__main__":
    # create the shared queue
    queue = Queue()
    producer_bot = producer(queue)
    consumer(queue, producer_bot)
    print("Done!")