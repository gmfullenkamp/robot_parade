import time

from javascript import require, once


class MinecraftBot:
    max_inventory_slots = 36
    block_pos_error = 0.9

    def __init__(self, host: str, port: int, command: str, username: str = "Robot", master_username: str = "GermF"):
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

        once(self.bot, "login")
        if "come" in command:
            self.come()
        elif "mine" in command:
            self.mine(command)
        elif "show_inventory" in command:
            self.show_inventory()
        elif "hunt" in command:
            self.hunt(command)
        elif "equip" in command:
            self.equip(command)
        else:
            raise ValueError(f"command '{command}' doesn't contain an implemented command.")

    def mine(self, message: str) -> None:
        _, number, block = message.split(" ")  # TODO: chat a message issue if not properly formatted
        # TODO: Use inventory as a way to detect when num blocks mined
        for _ in range(int(number)):
            try:
                # TODO: Fix failure to mine certain blocks (unreachable blocks)
                block_pos = self.bot.findBlocks({"point": self.bot.entity.position,
                                                 "matching": self.minecraft_data.blocksByName[block]["id"],
                                                 "maxDistance": 32,
                                                 "count": 1})[0]
                self.bot.pathfinder.setGoal(self.pathfinder.goals.GoalNear(block_pos.x, block_pos.y, block_pos.z, 0))
                while True:
                    if block_pos.x - self.block_pos_error <= self.bot.entity.position.x \
                            <= block_pos.x + self.block_pos_error \
                            and block_pos.y - self.block_pos_error <= self.bot.entity.position.y \
                            <= block_pos.y + self.block_pos_error \
                            and block_pos.z - self.block_pos_error <= self.bot.entity.position.z \
                            <= block_pos.z + self.block_pos_error:
                        time.sleep(1)
                        break
                # TODO: Fix js bridge exception on 26th call?
            except:
                pass

    def come(self) -> None:
        player = self.bot.players[self.master_username]
        target = player.entity
        if not target:
            return
        pos = target.position
        self.bot.pathfinder.setMovements(self.movements)
        blocks_from_player = 1
        self.bot.pathfinder.setGoal(self.pathfinder.goals.GoalNear(pos.x, pos.y, pos.z, blocks_from_player))
        while True:
            if pos.x - blocks_from_player - self.block_pos_error <= self.bot.entity.position.x \
                    <= pos.x + blocks_from_player + self.block_pos_error \
                    and pos.y - blocks_from_player - self.block_pos_error <= self.bot.entity.position.y \
                    <= pos.y + blocks_from_player + self.block_pos_error \
                    and pos.z - blocks_from_player - self.block_pos_error <= self.bot.entity.position.z \
                    <= pos.z + blocks_from_player + self.block_pos_error:
                time.sleep(1)
                break

    def show_inventory(self) -> None:
        condensed_inventory = {}
        for item in self.bot.inventory.items():
            if item.name in condensed_inventory.keys():
                condensed_inventory[item.name] += item.count
            else:
                condensed_inventory.update({item.name: item.count})
        for key in condensed_inventory.keys():
            print(f"{key}: {condensed_inventory[key]}")

    def hunt(self, message: str) -> None:
        # TODO: Implement a hunt command
        _, number, mob = message.split(" ")  # TODO: chat a message issue if not properly formatted
        raise ValueError(f"Command '{message}' not implemented.")

    def equip(self, message: str) -> None:
        # TODO: Implement equip command
        _, item = message.split(" ")  # TODO: chat a message issue if not properly formatted
        raise ValueError(f"Command '{message}' not implemented.")
