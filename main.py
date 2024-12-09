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


# class InfoPrompt(Modal):
#     def __init__(self, interaction: Interaction, data: dict, view):
#         super().__init__(title="Minecraft Username")
#         self.view = view
#         self.interaction = interaction
#         self.data = data
#         minecraft_username_ = data[str(interaction.user)]["minecraft username"]
#         amount = data[str(interaction.user)]["storage space"]
#         self.username = TextInput(label="Minecraft username?", placeholder="eg. Snakejac", default=minecraft_username_)
#         self.amount = TextInput(label="How much do you want to store?", placeholder="20 stacks or 2 vaults", default=amount)
#         self.add_item(self.username)
#         self.add_item(self.amount)
#
#     async def on_submit(self, interaction: Interaction[ClientT], /) -> None:
#         await super().on_submit(interaction)
#         self.data[str(interaction.user)]["minecraft username"] = self.username.value
#         self.data[str(interaction.user)]["storage space"] = self.amount.value
#         self.view.update()
#         await self.interaction.message.edit(content=self.view.content, view=self.view)
#         await interaction.response.defer()  # NOQA
#
#
# class FirstView(discord.ui.View):
#     def __init__(self, data: dict, user: User, client):
#         super().__init__(timeout=None)
#         self.data = data
#         self.user = user
#         self.client = client
#         if str(user) not in self.data.keys():
#             self.user_data = {
#                 "minecraft username": "",
#                 "storage space": "",
#                 "quantum bridge": False,
#                 "steak": False,
#                 "iron": False,
#                 "cobblestone": False,
#                 "create bits": False,
#                 "ae2 bits": False,
#                 "liquids": False,
#                 "status": "Incomplete"
#             }
#             self.data[str(user)] = self.user_data
#         else:
#             self.user_data = self.data[str(user)]
#         self.content = ""
#         self.update()
#         self.quantum_bridge.style = discord.ButtonStyle.green if self.user_data["quantum bridge"] else discord.ButtonStyle.gray
#
#     def update(self):
#         self.content = (f"Minecraft Username: `{self.data[str(self.user)]["minecraft username"] or " "}`\n"
#                         f"Storage: `{self.data[str(self.user)]["storage space"] or " "}`")
#
#     @discord.ui.button(label="Input information", custom_id="info", style=discord.ButtonStyle.blurple)
#     async def info(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await interaction.response.send_modal(InfoPrompt(interaction, self.data, self))  # NOQA
#         self.update()
#         await interaction.message.edit(content=self.content, view=self)
#
#     @discord.ui.button(label="Quantum bridge (wireless anywhere)?", custom_id="quantum bridge", row=1)
#     async def quantum_bridge(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["quantum bridge"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["quantum bridge"] = True
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#
# class SecondView(discord.ui.View):
#     def __init__(self, data: dict, user: User, client):
#         super().__init__(timeout=None)
#         self.data = data
#         self.user = user
#         self.client = client
#         self.user_data = self.data[str(user)]
#         self.steak.style = discord.ButtonStyle.green if self.user_data["steak"] else discord.ButtonStyle.gray
#         self.iron.style = discord.ButtonStyle.green if self.user_data["iron"] else discord.ButtonStyle.gray
#         self.cobblestone.style = discord.ButtonStyle.green if self.user_data["cobblestone"] else discord.ButtonStyle.gray
#         self.create_bits.style = discord.ButtonStyle.green if self.user_data["create bits"] else discord.ButtonStyle.gray
#         self.ae2_bits.style = discord.ButtonStyle.green if self.user_data["ae2 bits"] else discord.ButtonStyle.gray
#
#     @discord.ui.button(label="Access to infinite steak?", custom_id="steak")
#     async def steak(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["steak"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["steak"] = True
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#     @discord.ui.button(label="Access to infinite iron?", custom_id="iron", row=1)
#     async def iron(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["iron"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["iron"] = True
#
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#     @discord.ui.button(label="Access to infinite cobblestone?", custom_id="cobblestone", row=2)
#     async def cobblestone(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["cobblestone"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["cobblestone"] = True
#
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#     @discord.ui.button(label="Access to infinite create bits?", custom_id="create bits", row=3)
#     async def create_bits(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["create bits"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["create bits"] = True
#
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#     @discord.ui.button(label="Access to infinite ae2 bits?", custom_id="ae2 bits", row=4)
#     async def ae2_bits(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["ae2 bits"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["ae2 bits"] = True
#
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#
# class ThirdView(discord.ui.View):
#     def __init__(self, data: dict, user: User, client, views: tuple):
#         super().__init__(timeout=None)
#         self.messages = []
#         self.views = (*views, self)
#         self.data = data
#         self.user = user
#         self.client = client
#         self.user_data = self.data[str(user)]
#         self.liquids.style = discord.ButtonStyle.green if self.user_data["liquids"] else discord.ButtonStyle.gray
#
#     @discord.ui.button(label="Access to infinite liquids?", custom_id="liquids")
#     async def liquids(self, interaction: discord.Interaction, button: discord.ui.Button):
#         if button.style == discord.ButtonStyle.green:
#             button.style = discord.ButtonStyle.gray
#             self.user_data["liquids"] = False
#         else:
#             button.style = discord.ButtonStyle.green
#             self.user_data["liquids"] = True
#         await interaction.message.edit(view=self)
#         await interaction.response.defer()  # NOQA
#
#     @discord.ui.button(label="Submit", custom_id="submit", style=discord.ButtonStyle.blurple, row=1)
#     async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
#         async with interaction.message.channel.typing():
#             if not check_username(self.user_data["minecraft username"]):
#                 await interaction.response.defer()  # NOQA
#                 mess = await self.user.send("**Please enter a valid Minecraft username**", delete_after=3)
#                 await mess.delete(delay=3)
#                 return
#             elif not self.user_data["storage space"]:
#                 await interaction.response.defer()  # NOQA
#                 mess = await self.user.send("**Please enter a valid amount of storage**", delete_after=3)
#                 await mess.delete(delay=3)
#                 return
#             for view in self.views:
#                 view: discord.ui.View
#                 for button in view.children:
#                     button: Button
#                     button.disabled = True
#             await interaction.response.defer()  # NOQA
#             for message in self.client.views[interaction.channel.id]:
#                 message: Message
#                 try:
#                     await message.delete()
#                 except discord.errors.NotFound:
#                     pass
#                 # if message.content:
#                 #     await message.edit(view=None)
#                 # else:
#             # await interaction.message.edit(view=None)
#             await self.client.save()
#             o = json.load(open("data.json"))
#             client = str(interaction.user)
#             await interaction.user.send("\n\n".join([f"{"\n".join([f"Your order: "] +   # NOQA
#                 [f"> `{order[0]:>18}: {str(order[1]):<{max(len(o[client]["minecraft username"]), len(o[client]["storage space"]))}}`" for order in o[client].items()])}"]))  # NOQA
#             await self.client.send_order(self.user)
#

# def beautify(user, data, one=False):
#     return "\n".join([f"> `{str(user)}'s order:`" if not one else "`Your order:`"] +
#                      [f"> `{f"{t[0]:>18}: {str(t[1]):<{max(len(data[str(user)]["minecraft username"]),
#                                                            len(data[str(user)]["storage space"]))}}"}`"
#                       for t in data[str(user)].items()])


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
        
        @self.command()
        async def order(ctx):
            message = ctx
            await getattr(responses, "start_")(self, message, self.data, self.get_data, message.author.id in op_list)
        
        @self.command()
        async def view(ctx):
            message = ctx
            await getattr(responses, "view_")(self, message, self.data, self.get_data, message.author.id in op_list)
            
    
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
                    await message.author.send(str(s or "_"))
                return
            # elif message.content.lower() == "-viewall":
            #     o = json.load(open("data.json"))
            #     await message.author.send("\n\n".join([f"> {client}'s order:\n{"\n".join(
            #         [f"> `{order[0]:>18}: {str(order[1]):<{max(len(o[client]["minecraft username"]), len(o[client]["storage space"]))}}`" for order in o[client].items()])}"
            #                                            for client in o.keys()]))
            #     return
            # elif message.content.lower().split(" ")[0] == "-mark":
            #     for author in self.data:
            #         await message.author.send(content=f"`{author:<20}`:`{self.data[author]["status"]:<20}`", view=views.UserFunctions(self, self.data[author], author))
            #     return
            # elif message.content.lower().split(" ")[0] == "-complete":
            #     if message.content.lower().split(" ", 1)[1] in self.data.keys():
            #         self.data[message.content.lower().split(" ")[1]]["status"] = "complete"
            #         await message.author.send("\n".join([f"`{message.content.split(" ", 1)[1]}'s order:`"] +
            #                                             [f"`{f"{t[0]:>18}: {str(t[1]):<{max(len(self.data[message.content.split(" ", 1)[1]]["minecraft username"]),
            #                                                                                 len(self.data[message.content.split(" ", 1)[1]]["storage space"]))}}"}`"
            #                                              for t in self.data[message.content.split(" ", 1)[1]].items()]))
            #         await self.save()
            #     return
            # elif message.content.lower().split(" ")[0] == "-deny":
            #     if message.content.lower().split(" ", 1)[1] in self.data.keys():
            #         self.data[message.content.lower().split(" ")[1]]["status"] = "denied"
            #         await message.author.send("\n".join([f"`{message.content.split(" ", 1)[1]}'s order:`"] +
            #                                             [f"`{f"{t[0]:>18}: {str(t[1]):<{max(len(self.data[message.content.split(" ", 1)[1]]["minecraft username"]),
            #                                                                                 len(self.data[message.content.split(" ", 1)[1]]["storage space"]))}}"}`"
            #                                              for t in self.data[message.content.split(" ", 1)[1]].items()]))
            #         await self.save()
            #     return
            # elif message.content.lower().split(" ")[0] == "-cancel":
            #     if message.content.lower().split(" ", 1)[1] in self.data.keys():
            #         self.data[message.content.lower().split(" ")[1]]["status"] = "canceled"
            #         await message.author.send("\n".join([f"`{message.content.split(" ", 1)[1]}'s order:`"] +
            #                                             [f"`{f"{t[0]:>18}: {t[1]:<{max(len(self.data[message.content.split(" ", 1)[1]]["minecraft username"]),
            #                                                                            len(self.data[message.content.split(" ", 1)[1]]["storage space"]))}}"}`"
            #                                              for t in self.data[message.content.split(" ", 1)[1]].items()]))
            #         await self.save()
            #     return
            # elif message.content.lower().split(" ")[0] == "-message":
            #     user = await self.fetch_user(int(message.content.lower().split(" ", 1)[1]))
            #     op = message.author.display_name
            #     await user.send(f"{op} has initiated this message")
            #     await user.send("Type `-start` to start an order")
            #     return
        if message.author.id == self.user.id:
            if not message.content and message.poll is None and message.components is None:
                await message.delete()
            elif message.components and type(message.channel) is DMChannel and (message.content == "" or message.content.endswith("\0") or "\0" in message.content):
                # message.channel: DMChannel
                if self.views.get(message.channel.id):
                    self.views[message.channel.id].append(message)
                else:
                    self.views[message.channel.id] = [message]
            return
        
        if not self.respond and message.content[0] == "-":
            await message.channel.send("-# Bot is under maintenance right now, and is not recieving messages at this time.\n"
                                       "-# If you need to use this bot right now, contact Snakejac to open this bot again.", delete_after=120, reference=message)
        
        # if message.content.lower() == "-view":
        #     # o = json.load(open("data.json"))
        #     client = str(message.author)
        #     if client in self.data:
        #         await message.author.send("\n\n".join([f"> {client}'s order:\n{"\n".join(
        #             [f"> `{order[0]:>18}: {str(order[1]):<{max(len(self.data[client]["minecraft username"]), len(self.data[client]["storage space"]))}}`" for order in self.data[client].items()])}"]))
        #     return
        # elif message.content.lower() == "-start" or message.content.lower() == "-edit":
        #     async with message.channel.typing():
        #         await responses.start_(self, message, self.data, self.get_data, message.author.id in op_list)
        #         # view1 = FirstView(self.data, message.author, self)
        #         # view2 = SecondView(self.data, message.author, self)
        #         # view3 = ThirdView(self.data, message.author, self, (view1, view2))
        #         # await message.author.send(view1.content, view=view1)
        #         # await message.author.send(" ", view=view2)
        #         # await message.author.send(" ", view=view3)
        #         # return
        # elif message.content.lower() == "-delete":
        #     async with message.channel.typing():
        #         await responses.delete_(self, message, self.data, self.get_data, message.author.id in op_list)
        #         await self.save()
        #     return
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
    
    # STEP 3: MESSAGE FUNCTIONALITY
    # async def send_message(self, message: Message, user_message: str, user: Message.author) -> None:
    #     if not user_message:
    #         print('(Message was empty because intents were not enabled probably)')
    #         return
    #     user_message = user_message.strip()
    #     if user_message.lower() == "-help":
    #         if message.author.id in op_list.txt and not message.channel.guild:
    #             await message.channel.send("`-start` to start an order\n"
    #                                        "`-edit` to edit your order\n"
    #                                        "`-view` to view your order\n"
    #                                        "[OP]`-stop` to take this bot offline\n"
    #                                        "[OP]`-exec [code]` to execute the input as python code\n"
    #                                        "[OP]`-viewall` to view all orders\n"
    #                                        "[OP]`-message [uid]` to message the user (via uid)")
    #         else:
    #             await message.channel.send("`-start` to start an order\n"
    #                                        "`-edit` to edit your order\n"
    #                                        "`-view` to view your order")
    #     elif user_message.lower() == "-start" or (user_message.lower() == "-edit" and self.data.get(str(user))):
    #         await user.send("Minecraft username?")
    #         if user not in self.waiting:
    #             self.waiting[user] = 1
    #         if str(user) not in self.data.keys():
    #             self.data[str(user)] = {}
    #     elif message.channel.guild is None and user in self.waiting.keys():
    #         if self.waiting[user] == 1:
    #             self.waiting[user] = 2
    #             self.data[str(user)]["minecraft username"] = check_username(user_message)
    #             await user.send("How many items do you want to store? Vaults store 1620 stacks each. \n Example answers: `20 stacks` or `2 vaults`")
    #         elif self.waiting[user] == 2:
    #             self.waiting[user] = 3
    #             self.data[str(user)]["storage space"] = user_message.lower()
    #             poll = Poll("Options:", datetime.timedelta(hours=1), multiple=True)
    #             poll.add_answer(text="Quantum bridge [wireless anywhere)?")
    #             poll.add_answer(text="Access to infinite steak?")
    #             poll.add_answer(text="Access to infinite iron?")
    #             poll.add_answer(text="Access to infinite cobblestone?")
    #             poll.add_answer(text="Access to infinite create bits?")
    #             poll.add_answer(text="Access to infinite ae2 bits?")
    #             poll.add_answer(text="Access to infinite liquids?")
    #             for k in yn_to_keys.values():
    #                 self.data[str(user)][k] = False
    #             await message.author.send(poll=poll)
    #         else:
    #             pass
    #     else:
    #         if message.channel.guild is None:
    #             await message.author.send("> Sorry, but I don't understand. Try these: \n```fix\n-help``````fix\n-start``````fix\n-edit```")
    
    # @discord.app_commands.command(name="test")
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