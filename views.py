import inspect
import json
from typing import Callable

import discord.ui
from discord import Message, Member, User, Interaction
from discord._types import ClientT
from discord.ui import Button, Modal, TextInput, ChannelSelect

WHITE = "\u001b[1;37m"
CYAN = "\u001b[1;36m"
BLUE = "\u001b[1;34m"
YELLOW = "\u001b[1;33m"
GREEN = "\u001b[1;32m"
RED = "\u001b[1;31m"
GRAY = "\u001b[30m"
BOLD = "\u001b[1m"
RESET = "\u001b[0m"

keys_to_beauty = {
    "minecraft username": "Minecraft username",
    "storage space": "Storage",
    "quantum bridge": "Quantum bridge",
    "magnet card": "Magnet card",
    "terminal": "Terminal\u00a0type",
    "steak": "Access to infinite steak",
    "iron": "Access to infinite iron",
    "cobblestone": "Access to infinite cobblestone",
    "create bits": "Access to infinite create bits",
    "ae2 bits": "Access to infinite ae2 bits",
    "liquids": "Access to infinite liquids",
    "status": "Status",
}


def beautify(user, data, one=False, *whitelist):
    lens = [len(data[str(user)]["minecraft username"]),
            len(data[str(user)]["storage space"]), len(data[str(user)]["status"])]
    if whitelist:
        return "\n".join([f"```ansi"] +
                         [f"\0{f"{get_color(t)}{keys_to_beauty[t[0]] + ":": <35}{RESET} {get_color(t)}{str(t[1]):<{max(lens)}} {RESET}"}"
                          for t in data[str(user)].items() if t[0] in whitelist] + ["\n```"])
    
    return "\n".join([f"### `{str(user)}`'s order:\n```ansi" if not one else "Your order:\n```ansi"] +
                     [f"{f"{get_color(t)}{keys_to_beauty[t[0]] + ":": <31}\u00a0{RESET}{get_color(t)}{("Yes" if t[1] else "No") if type(t[1]) is bool else (str(t[1])):<{max(lens)}} {RESET}"}"
                      for t in data[str(user)].items()] + ["\n```"])


def get_color(t):
    return CYAN if not type(t[1]) is bool else (BLUE if t[1] else GRAY)


class InfoPrompt(Modal):
    def __init__(self, interaction: Interaction, data: dict, view):
        super().__init__(title="Minecraft Username")
        self.view = view
        self.interaction = interaction
        self.data = data
        minecraft_username_ = data["minecraft username"]
        amount = data["storage space"]
        self.username = TextInput(label="Minecraft username?", placeholder="eg. Snakejac", default=minecraft_username_)
        self.amount = TextInput(label="How much do you want to store?", placeholder="20 stacks or 2 vaults", default=amount)
        self.add_item(self.username)
        self.add_item(self.amount)
    
    async def on_submit(self, interaction: Interaction[ClientT], /) -> None:
        await super().on_submit(interaction)
        self.data["minecraft username"] = self.username.value
        self.data["storage space"] = self.amount.value.title().replace(" ", "\u00a0")
        self.view.update()
        await self.interaction.message.edit(content=self.view.content, view=self.view)
        await interaction.response.defer()  # NOQA


class InfoInput(discord.ui.View):
    messages = {}
    
    def __init__(self, questions: list[str], examples: list[str], defaults: list[str], label: str, data: dict, user_data: dict, user: User or Member):
        super().__init__()
        self.data = data
        self.questions = questions
        self.examples = examples
        self.defaults = defaults
        self.input_button.style = discord.ButtonStyle.blurple
        self.input_button.label = label
        self.user_data = user_data
        self.user = user
        self.content = ""
        self.update()
    
    def update(self):
        self.content = (f"Minecraft Username: `{self.user_data["minecraft username"] or " "}`\n"
                        f"Storage: `{self.user_data["storage space"] or " "}`")
        self.content = beautify(self.user, self.data, False, "minecraft username", "storage space")
    
    @discord.ui.button()
    async def input_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(InfoPrompt(interaction, self.user_data, self))  # NOQA
        self.update()
        await interaction.message.edit(content=self.content, view=self)


class TFQuestion(discord.ui.View):
    questions = {}
    
    def __init__(self, question: str, data: dict, key: str, user: User or Member):
        super().__init__()
        self.question = question
        self.user_data: dict = data
        self.key: str = key
        self.q_button.label = question
        self.q_button.style = discord.ButtonStyle.green if self.user_data[self.key] else discord.ButtonStyle.gray
        if user in self.questions:
            self.questions[user].append(self.q_button)
        else:
            self.questions[user] = [self.q_button]
    
    @discord.ui.button()
    async def q_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if button.style == discord.ButtonStyle.green:
            button.style = discord.ButtonStyle.gray
            self.user_data[self.key] = False
        else:
            button.style = discord.ButtonStyle.green
            self.user_data[self.key] = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()  # NOQA


def check_username(value: str) -> str:
    if not " " in value.strip():
        return value
    return ""


class Submit(discord.ui.View):
    def __init__(self, client, label: str, data: dict, user_data: dict, user):
        super().__init__()
        self.label = label
        self.client = client
        self.user = user
        self.data: dict = data
        self.user_data: dict = user_data
        self.submit.label = label
        self.submit.style = discord.ButtonStyle.blurple
    
    @discord.ui.button()
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with interaction.message.channel.typing():
            if not check_username(self.user_data["minecraft username"]):
                await interaction.response.defer()  # NOQA
                mess = await self.user.send("**Please enter a valid Minecraft username**", delete_after=3)
                # await mess.delete(delay=3)
                return
            elif not self.user_data["storage space"]:
                await interaction.response.defer()  # NOQA
                mess = await self.user.send("**Please enter a valid amount of storage**", delete_after=3)
                #                 await mess.delete(delay=3)
                return
            await interaction.response.defer()  # NOQA
            # for message in TFQuestion.questions[self.user]:
            #     await message.delete()
            await interaction.message.delete()
            for message in self.client.views[interaction.channel.id]:
                message: Message
                try:
                    await message.delete()
                except discord.errors.NotFound:
                    pass
                # if message.content:
                #     await message.edit(view=None)
                # else:
            # await interaction.message.edit(view=None)
            self.user_data["status"] = "Ordered"
            await self.client.save()
            o = json.load(open("data.json"))
            client = str(interaction.user)
            # await interaction.user.send("\n\n".join([f"{"\n".join([f"Your order: "] +  # NOQA
            #                                                       [f"> `{order[0]:>18}: {str(order[1]):<{max(len(o[client]["minecraft username"]), len(o[client]["storage space"]))}}`" for order in o[client].items()])}"]))  # NOQA
            # if interaction.user.is_on_mobile():
            #     await interaction.user.send("-# You are on a mobile device, which does not support colors. ")
            await interaction.user.send(beautify(interaction.user, self.data, True))
            await self.client.send_order(self.user)
            del self.client.views[interaction.channel.id]
            await self.client.update_status()


class UserFunctions(discord.ui.View):
    def __init__(self, client, data: dict, user_data: dict, user, notify: Callable):
        super().__init__()
        self.client = client
        self.user = user
        self.data: dict = data
        self.user_data: dict = user_data
        self.notify_func = notify
        if client.notifications.get(str(user)):
            self.notify.disabled = not client.notifications[str(user)]["notifications"]
        else:
            self.notify.disabled = True
    
    @discord.ui.button(label="Finished", style=discord.ButtonStyle.green)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_data["status"] = "Finished"
        await self.client.save()
        await interaction.message.edit(content=beautify(self.user, self.data))
        await interaction.response.defer()  # NOQA
    
    @discord.ui.button(label="In Progress", style=discord.ButtonStyle.blurple)
    async def progress(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_data["status"] = "In\u00a0Progress"
        await self.client.save()
        await interaction.message.edit(content=beautify(self.user, self.data))
        await interaction.response.defer()  # NOQA
    
    @discord.ui.button(label="Ordered", style=discord.ButtonStyle.gray)
    async def order(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_data["status"] = "Ordered"
        await self.client.save()
        await interaction.message.edit(content=beautify(self.user, self.data))
        await interaction.response.defer()  # NOQA
    
    @discord.ui.button(label="Incomplete", style=discord.ButtonStyle.red)
    async def incomplete(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_data["status"] = "Incomplete"
        await self.client.save()
        await interaction.message.edit(content=beautify(self.user, self.data))
        await interaction.response.defer()  # NOQA
    
    @discord.ui.button(label="Invalid", style=discord.ButtonStyle.red)
    async def invalid(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.user_data["status"] = "Invalid"
        await self.client.save()
        await interaction.message.edit(content=beautify(self.user, self.data))
        await interaction.response.defer()  # NOQA
    
    @discord.ui.button(label="Notify", style=discord.ButtonStyle.blurple, row=1)
    async def notify(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.client.save()
        if await self.notify_func(self.client, str(self.user)) is None:
            await interaction.user.send("Operation completed")
        else:
            await interaction.user.send("Operation failed; user was not notified")
        
        await interaction.message.edit(content=beautify(self.user, self.data))
        await interaction.response.defer()  # NOQA


class Confirm(discord.ui.View):
    def __init__(self, label: str, func, *args):
        super().__init__()
        self.func = func
        self.args = args
        self.custom_button.label = label
    
    @discord.ui.button(style=discord.ButtonStyle.red)
    async def custom_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if inspect.iscoroutinefunction(self.func):
            await self.func(*self.args)
        else:
            self.func(*self.args)
        await interaction.response.defer()  # NOQA
        await interaction.message.delete()
        
        
class MultiSelect(discord.ui.View):
    def __init__(self, user_data, key, placeholder, *options):
        super().__init__()
        self.user_data = user_data
        self.key = key
        for option, description in options:
            self.menu.add_option(label=option, description=description)
        self.menu.placeholder = placeholder
    
    @discord.ui.select(cls=discord.ui.Select)
    async def menu(self, interaction: discord.Interaction, select: ChannelSelect):
        self.user_data[self.key] = select.values[0]
        await interaction.response.defer()  # NOQA
