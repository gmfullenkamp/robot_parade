import time
from tqdm import tqdm
from javascript import require, On, off

HOST = "192.168.0.15"
PORT = 52921
BOT_USERNAME = "Robot"  # Same name == keep previous inventory

mineflayer = require("mineflayer")

bot = mineflayer.createBot({"host": HOST,
                            "port": PORT,
                            "username": BOT_USERNAME,
                            "hideErrors": False})

# Load the pathfinder and minecraft bot data
pathfinder = require("mineflayer-pathfinder")
bot.loadPlugin(pathfinder.pathfinder)
minecraft_data = require("minecraft-data")(bot.version)
movements = pathfinder.Movements(bot, minecraft_data)
bot.removeAllListeners("chat")


@On(bot, "chat")
def handle_msg(this, sender, message, *args):
    if sender and (sender != BOT_USERNAME):
        bot.chat("Hi, you said " + message)
        if "come" in message:
            player = bot.players[sender]
            target = player.entity
            if not target:
                bot.chat("I don't see you!")
                return
            pos = target.position
            bot.pathfinder.setMovements(movements)
            bot.pathfinder.setGoal(pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))
        if "mine" in message:
            _, number, block = message.split(" ")
            for _ in tqdm(range(int(number)), desc="Mining"):
                try:
                    block_pos = bot.findBlock({"point": bot.entity.position,
                                               "matching": minecraft_data.blocksByName[block]["id"],
                                               "maxDistance": 32,
                                               "count": 1})["position"]
                    bot.pathfinder.setGoal(pathfinder.goals.GoalNear(block_pos.x, block_pos.y, block_pos.z, 0))
                    time.sleep(10)
                except:
                    pass
            bot.chat(f"Finished mining {number} {block}")
        if "inventory" in message:
            print(bot.inventory.items())
        if "leave" in message:
            off(bot, "chat", handle_msg)
