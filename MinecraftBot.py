import time

from javascript import require, On, off


class MinecraftBot:
    max_inventory_slots = 36
    block_pos_error = 0.9

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
                    self.come(verbose=True)
                elif "mine" in message:
                    self.mine(message, verbose=True)
                elif "show_inventory" in message:
                    self.show_inventory()
                elif "fill_inventory" in message:
                    self.fill_inventory(message)
                elif "leave" in message:
                    off(self.bot, "chat", handle_msg)
                elif "hunt" in message:
                    self.hunt(message)
                elif "equip" in message:
                    self.equip(message)
                else:
                    self.bot.chat(f"Command '{message}' not available. I'm sorry master {self.master_username}")

    def mine(self, message: str, verbose: bool) -> None:
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
        if verbose:
            self.bot.chat(f"Finished mining {number} {block} master {self.master_username}")

    def come(self, verbose: bool) -> None:
        player = self.bot.players[self.master_username]
        target = player.entity
        if not target:
            self.bot.chat(f"I don't see you master {self.master_username}")
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
                if verbose:
                    self.bot.chat(f"I am here master {self.master_username}")
                break

    def show_inventory(self) -> None:
        condensed_inventory = {}
        for item in self.bot.inventory.items():
            if item.name in condensed_inventory.keys():
                condensed_inventory[item.name] += item.count
            else:
                condensed_inventory.update({item.name: item.count})
        for key in condensed_inventory.keys():
            self.bot.chat(f"{key}: {condensed_inventory[key]}")

    def fill_inventory(self, message) -> None:
        _, block = message.split(" ")  # TODO: chat a message issue if not properly formatted
        slots_filled = 0
        for _ in self.bot.inventory.items():
            slots_filled += 1
        while slots_filled < self.max_inventory_slots:
            self.come(verbose=False)
            self.mine(f"mine {10} {block}", verbose=False)
            slots_filled = 0
            for _ in self.bot.inventory.items():
                slots_filled += 1
        self.bot.chat(f"Finished mining {block}, inventory full master {self.master_username}")

    def hunt(self, message: str) -> None:
        # TODO: Implement a hunt command
        _, number, mob = message.split(" ")  # TODO: chat a message issue if not properly formatted
        self.bot.chat(f"Command '{message}' not implemented. I'm sorry master {self.master_username}")

    def equip(self, message: str) -> None:
        # TODO: Implement equip command
        _, item = message.split(" ")  # TODO: chat a message issue if not properly formatted
        self.bot.chat(f"Command '{message}' not implemented. I'm sorry master {self.master_username}")
