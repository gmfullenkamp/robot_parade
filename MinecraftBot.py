import time

from javascript import require, once


class MinecraftBot:
    block_pos_error = 0.9

    def __init__(self, host: str, port: int, username: str, command: str = ""):
        """Initializes the bot and the different required packages."""
        self.username = username
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

        once(self.bot, "login")
        if "mine" in command:
            self.mine(command)
        else:
            print(f"Command '{command}' doesn't contain an implemented command. {username} will do nothing.")

    def mine(self, message: str) -> None:
        _, x, y, z = message.split("_")  # TODO: chat a message issue if not properly formatted
        x, y, z = int(x), int(y), int(z)
        while True:
            self.bot.pathfinder.setGoal(self.pathfinder.goals.GoalNear(x, y, z, 0))
            time.sleep(1)
            if x - self.block_pos_error <= self.bot.entity.position.x <= x + self.block_pos_error \
                    and y - self.block_pos_error <= self.bot.entity.position.y <= y + self.block_pos_error \
                    and z - self.block_pos_error <= self.bot.entity.position.z <= z + self.block_pos_error:
                time.sleep(1)
                break
