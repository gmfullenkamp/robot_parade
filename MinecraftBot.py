import time
from tqdm import tqdm

from javascript import require, On, off


class MinecraftBot:
    def __init__(self, host: str, port: int, username: str = "Robot", master_username: str = "GermF"):
        """Initializes the bot and the different required packages."""
        self.username = username
        self.master_username = master_username
        mineflayer = require("mineflayer")
        self.bot = mineflayer.createBot({"host": host,
                                         "port": port,
                                         "username": self.username,
                                         "hideErrors": False})

        # Load the pathfinder and minecraft bot data
        self.pathfinder = require("mineflayer-pathfinder")
        self.bot.loadPlugin(self.pathfinder.pathfinder)
        self.minecraft_data = require("minecraft-data")(self.bot.version)
        self.movements = self.pathfinder.Movements(self.bot, self.minecraft_data)

        @On(self.bot, "chat")
        def handle_msg(this, sender, message, *args):
            """Handles the chat messages."""
            if sender and (sender != self.username) and (sender == self.master_username):
                self.bot.chat(f"Command '{message}' received master {self.master_username}")
                if "come" in message:
                    self.come()
                elif "mine" in message:
                    self.mine(message)
                elif "inventory" in message:
                    self.inventory()
                elif "leave" in message:
                    off(self.bot, "chat", handle_msg)
                elif "hunt" in message:
                    self.hunt(message)
                else:
                    self.bot.chat(f"Command '{message}' not available. I'm sorry master {self.master_username}")

    def mine(self, message: str) -> None:
        _, number, block = message.split(" ")  # TODO: chat a message issue if not properly formatted
        # TODO: Use inventory as a way to detect when num blocks mined
        for _ in tqdm(range(int(number)), desc="Mining"):
            try:
                # TODO: Fix failure to mine certain blocks
                block_pos = self.bot.findBlocks({"point": self.bot.entity.position,
                                                 "matching": self.minecraft_data.blocksByName[block]["id"],
                                                 "maxDistance": 32,
                                                 "count": 1})[0]
                # print(block_pos.x, block_pos.y, block_pos.z)
                self.bot.pathfinder.setGoal(self.pathfinder.goals.GoalNear(block_pos.x, block_pos.y, block_pos.z, 0))
                time.sleep(4)  # TODO: Instead of sleep, detect when bot made it to the goal
                # TODO: Fix js bridge exception on 26th call?
            except:
                pass

    def come(self) -> None:
        player = self.bot.players[self.master_username]
        target = player.entity
        if not target:
            self.bot.chat(f"I don't see you master {self.master_username}")
            return
        pos = target.position
        self.bot.pathfinder.setMovements(self.movements)
        self.bot.pathfinder.setGoal(self.pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, 1))

    def inventory(self) -> dict:
        condensed_inventory = {}
        for item in self.bot.inventory.items():
            if item.name in condensed_inventory.keys():
                condensed_inventory[item.name] += item.count
            else:
                condensed_inventory.update({item.name: item.count})
        for key in condensed_inventory.keys():
            self.bot.chat(f"{key}: {condensed_inventory[key]}")
        return condensed_inventory

    def hunt(self, message: str) -> None:
        # TODO: Implement a hunt command
        _, number, mob = message.split(" ")  # TODO: chat a message issue if not properly formatted
        self.bot.chat(f"Command '{message}' not implemented. I'm sorry master {self.master_username}")
