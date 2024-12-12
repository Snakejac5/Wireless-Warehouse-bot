import contextlib
import io
import logging
import sys
import time
from contextlib import redirect_stdout
from io import StringIO
from typing import Final, Union, Optional
import os
from discord import (Intents, Client, Message, Poll, PollAnswer, Member, User, HTTPException, PollLayoutType, Status, Game,
                     BaseActivity, ActivityType, CustomActivity, Activity, Interaction, Attachment, File, DMChannel, Button, Spotify)
import discord
import discord.ext
import discord.ext.commands
import json
import importlib

import responses
import views

env__read = open(".private/.env").read()
TOKEN: Final[str] = env__read[env__read.index("DISCORD_TOKEN=") + 14:env__read.index("DISCORD_TOKEN=") + 14 + env__read[env__read.index("DISCORD_TOKEN=") + 14:].index("\n")]

op_list = [int(n) for n in open("op_list.txt").read().strip().split("\n")]
print(op_list)

reload_file = True


# STEP 1: BOT SETUP
# intents: Intents = Intents.default()
# intents.message_content = True  # NOQA
# client: Client = Client(intents=intents)

# yn_to_keys = {
#     "Quantum bridge (wireless anywhere)?": "quantum bridge",
#     "Access to infinite steak?": "steak",
#     "Access to infinite iron?": "iron",
#     "Access to infinite cobblestone?": "cobblestone",
#     "Access to infinite create bits?": "create bits",
#     "Access to infinite ae2 bits?": "ae2 bits",
#     "Access to infinite liquids?": "liquids",
# }


def check_username(value: str) -> str:
    if not " " in value.strip():
        return value
    return ""


def check_bool(value: str):
    v = value.lower()
    if v == "y" or v == "yes":
        return True
    if v == "n" or v == "no":
        return False
    raise ValueError



class WirelessWarehouseBot(discord.ext.commands.Bot):
    def __init__(self) -> None:
        super().__init__(intents=Intents.all(), presence=Status.idle, command_prefix="-", self_bot=False)
        # self.intents.message_content = True  # NOQA
        self.data: dict = json.load(open("data.json"))
        self.eggs: dict = json.load(open("eggs.json"))
        self.notifications: dict = json.load(open("notification.json"))
        self.waiting = {}
        self.views = {}
        self.respond = True
    
    def startup(self):
        self.run(TOKEN)
    
    async def reload(self, data=False):
        global op_list
        op_list = [int(n) for n in open("op_list.txt").read().strip().split("\n")]
        if data:
            self.data: dict = json.load(open("data.json"))
    
    def get_data(self, user: str or User or Member) -> dict:
        user = str(user)
        if not self.data.get(user):
            self.data[user] = {
                "minecraft username": "",
                "storage space": "",
                "quantum bridge": False,
                "magnet card": False,
                "terminal": "Physical\u00a0Terminal",
                "steak": False,
                "iron": False,
                "cobblestone": False,
                "create bits": False,
                "ae2 bits": False,
                "liquids": False,
                "status": "Incomplete"
            }
        return self.data[user]
    
    async def on_ready(self) -> None:
        print(f'{self.user} is now running!')
        # await self.change_presence(activity=CustomActivity(name="-help for instructions"))
        await self.update_status()
    
    async def close(self, user: User or Member or None = None, reload=False) -> None:
        global reload_file
        reload_file = reload
        if user:
            print(f"Stopped by {str(user)}")
        else:
            print("Stopped")
        await super().close()
    
    async def on_message(self, message: Message) -> None:
        # await super().on_message(message)
        importlib.reload(responses)
        importlib.reload(views)
        username: str = str(message.author)
        user_message: str = message.content
        channel: str = str(message.channel)
        
        print(f'[{channel}] {username}: "{user_message}"')
        if message.author.id in op_list and not message.channel.guild:
            if message.content.lower().strip() == "-hold":
                if self.respond:
                    await message.author.send("-# stopping response functionality")
                    self.respond = not self.respond
                    return
            if message.content.lower().strip() == "-release":
                if not self.respond:
                    await message.author.send("-# starting response functionality")
                    self.respond = not self.respond
                    return
            if not self.respond:
                return
            elif message.content.lower().split(" ")[0] == "-exec":
                with redirect_stdout(io.StringIO()) as f:
                    exec(message.content.split(" ", 1)[1])
                s = f.getvalue()
                if "\n" in s:
                    with open("out.txt", "w") as f:
                        f.write(s)
                    await message.author.send(" ", file=File("out.txt"))
                
                else:
                    await message.author.send(str(s or "||\u200b||"))
                return
            
        if message.author.id == self.user.id:
            if not message.content and message.poll is None and message.components is None:
                await message.delete()
            elif message.components and type(message.channel) is DMChannel and (message.content == "" or "\0" in message.content):
                # message.channel: DMChannel
                if self.views.get(message.channel.id):
                    self.views[message.channel.id].append(message)
                else:
                    self.views[message.channel.id] = [message]
            return
        
        if not self.respond and message.content[0] == "-":
            await message.channel.send("-# Bot is under maintenance right now, and is not recieving messages at this time.\n"
                                       "-# If you need to use this bot right now, contact Snakejac to open this bot again.", delete_after=120, reference=message)

        elif message.content.lower()[0] == "-":
            try:
                if command := getattr(responses, message.content.lower().split(" ")[0][1:] + "_"):
                    async with message.channel.typing():
                        response = await command(self, message, self.data, self.get_data, message.author.id in op_list, *message.content.lower().split(" ")[1:])
                    if response is False:
                        raise PermissionError("You are not OP, or you are in a public channel")
            except PermissionError as e:
                async with message.channel.typing():
                    await message.author.send(f"**{str(e)}**", delete_after=5, reference=message)
                    await responses.help_(self, message, self.data, self.get_data, message.author.id in op_list)
                return
            except AttributeError as e:
                print(e)
                async with message.channel.typing():
                    await message.author.send(f"**Not a recognized command**: `{message.content.lower().strip().split(" ")[0]}`", delete_after=5, reference=message)
                    await responses.help_(self, message, self.data, self.get_data, message.author.id in op_list)
                return
        else:  # message.content.lower() == "-help":
            async with message.channel.typing():
                await responses.help_(self, message, self.data, self.get_data, message.author.id in op_list)
            return
    
    async def update_status(self):
        await self.change_presence(activity=Activity(name=f"{", ".join([str(self.get_channel(name).recipient.display_name) for name in self.views])}", details="Details", type=ActivityType.listening))  # NOQA

    async def send_order(self, user: Message.author):
        owner = await self.fetch_user(770839473322721312)
        self.data[str(user)]["status"] = "Ordered"
        if user != owner:
            await owner.send(views.beautify(user, self.data))
        await self.save()
        await user.send("-# Order submitted")  # , file=File("submitted_final.gif"))
    
    async def save(self):
        with open("data.json", "w") as file:
            json.dump(self.data, file, indent="\t")  # NOQA
        with open("notification.json", "w") as file:
            json.dump(self.notifications, file, indent="\t")  # NOQA

# if __name__ == '__main__':
#     bot = MyBot()
#     bot.run(TOKEN)