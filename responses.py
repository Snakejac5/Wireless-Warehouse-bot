from typing import Callable

import discord
from discord import File
import discord.ext
import discord.ext.commands

from views import *

multi_select = {
    "terminal": (
        "-# Terminal type\0",
        ("Physical\u00a0Terminal", "(At Warehouse)"),
        ("Physical\u00a0Crafting\u00a0Terminal", "(At Warehouse)"),
        ("Wireless\u00a0Terminal", "(Item)"),
        ("Wireless\u00a0Crafting\u00a0Terminal", "(Item)"),
    )
}

select_placement = {
    2: "terminal"
}

yn_to_keys = {
    "Quantum bridge (Wireless anywhere)": "quantum bridge",
    "Magnet card (Item magnet)": "magnet card",
    "Access to infinite steak": "steak",
    "Access to infinite iron": "iron",
    "Access to infinite cobblestone": "cobblestone",
    "Access to infinite create bits": "create bits",
    "Access to infinite ae2 bits": "ae2 bits",
    "Access to infinite liquids": "liquids",
}

headers = {
    0: "-# General options\0",
    2: "-# Farm access\0",
}


async def message_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if not is_op:
        return False
    user = await client.fetch_user(int(message.content.lower().split(" ", 1)[1]))
    op = message.author.display_name
    await user.send(f"-# {op} has initiated this message\n"
                    f"Type `-start` to start an order")


async def stop_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if not is_op:
        return False
    await message.author.send("-# Stopping bot")
    await client.close(message.author, False)


async def reload_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if not is_op:
        return False
    await message.author.send("-# Reloading bot")
    await client.close(message.author, True)


async def eggs_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if client.eggs.get(str(message.author)):
        await message.author.send(f"You've found {len(client.eggs[str(message.author)])} easter eggs\n" +
                                  f"{"\n".join([f"- `{egg}`" for egg in client.eggs[str(message.author)]])}")
    else:
        await message.author.send(f"You've found 0 easter eggs")


async def sandwich_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    await message.author.send("**POOF!** You're a sandwich.", delete_after=10)
    if client.eggs.get(str(message.author)):
        if "sandwich" not in client.eggs[str(message.author)]:
            await message.author.send(f"Congratulations! You found an easter egg!\n"
                                      f"{len(client.eggs[str(message.author)])} eggs found")
        client.eggs[str(message.author)].append("sandwich")
        client.eggs[str(message.author)] = list(set(client.eggs[str(message.author)]))
    else:
        client.eggs[str(message.author)] = ["sandwich"]
    json.dump(client.eggs, open("eggs.json", "w"))  # NOQA


async def no_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    await message.author.send("no u", delete_after=10)
    if client.eggs.get(str(message.author)):
        if "no u" not in client.eggs[str(message.author)]:
            await message.author.send(f"Congratulations! You found an easter egg!\n"
                                      f"{len(client.eggs[str(message.author)])} eggs found")
        client.eggs[str(message.author)].append("no u")
        client.eggs[str(message.author)] = list(set(client.eggs[str(message.author)]))
    else:
        client.eggs[str(message.author)] = ["no u"]
    json.dump(client.eggs, open("eggs.json", "w"))  # NOQA


# async def menu_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
#     pass


# async def test_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
#     await message.author.send(f"""
# ```ansi
# {"\n".join([f"\u001b[{i}mHi" for i in range(30, 38)])}
# ```
# """)


async def getfiles_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if not is_op:
        return False
    await message.author.send(files=(File("main.py"), File("views.py"), File("responses.py"), File("notification.json"), File("eggs.json"), File("data.json")))



async def edit_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    await start_(client, message, data, user_data_call, is_op, *args)


async def start_(client, message: Message, data: dict, user_data_call: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    user_data = user_data_call(message.author)
    info_input = InfoInput(
        ["Minecraft Username: ", "How much do you want to store: ", ],
        ["eg. Snakejac", "eg. 1 vault", ], [user_data["minecraft username"], user_data["storage space"], ],
        "Input information", data, user_data, message.author)
    await message.author.send(content=info_input.content, view=info_input)
    await client.update_status()
    for i, (question, key) in enumerate(yn_to_keys.items()):
        if i in select_placement:
            selection = multi_select[select_placement[i]]
            await message.author.send(
                selection[0],
                view=MultiSelect(user_data, select_placement[i], user_data[select_placement[i]],
                                 *[option for option in selection if type(option) is tuple])
            )
        if i in headers:
            await message.author.send(headers[i], view=TFQuestion(question, user_data, key, message.author))
        else:
            await message.author.send(view=TFQuestion(question, user_data, key, message.author))
    if not client.notifications.get(str(message.author)):
        client.notifications[str(message.author)] = {
            "id": message.author.id,
            "notifications": True,
            "last": "ordered"
        }
    client.notifications[str(message.author)]["last"] = "ordered"
    await message.author.send("-# Notifications\0", view=TFQuestion("Notify me with status updates to my order", client.notifications[str(message.author)], "notifications", message.author))
    await message.author.send("||​||\0", view=Submit(client, "Submit", data, user_data, message.author))


async def view_(client, message: Message, data: dict, user_data: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    await message.author.send(beautify(message.author, data, True))


async def viewall_(client, message: Message, data: dict, user_data: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if not is_op:
        return False
    for user in data:
        await message.author.send(beautify(user, data))


async def mark_(client, message: Message, data: dict, user_data: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if not is_op:
        return False
    for author in data:
        await message.author.send(content=beautify(author, data), view=UserFunctions(client, data, data[author], author, notify))


async def help_(client, message: Message, data: dict, user_data: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if is_op and not message.channel.guild:
        await message.channel.send("`-start` to start an order\n"
                                   "`-edit` to edit your order\n"
                                   "`-view` to view your order\n"
                                   "`-delete` to delete your order\n"
                                   "`-eggs` to view the easter eggs you've discovered\n"
                                   "[OP]`-stop` to take this bot offline\n"
                                   "[OP]`-exec [code]` to execute the input as python code\n"
                                   "[OP]`-viewall` to view all orders\n"
                                   "[OP]`-mark` to edit statuses of orders\n"
                                   "[OP]`-message [uid]` to message the user (via uid)")
    else:
        await message.channel.send("`-start` to start an order\n"
                                   "`-edit` to edit your order\n"
                                   "`-view` to view your order\n"
                                   "`-delete` to delete your order\n"
                                   "`-eggs` to view the easter eggs you've discovered")


async def delete_(client, message: Message, data: dict, user_data: Callable[[str or User or Member], dict], is_op: bool = False, *args):
    if data.get(str(message.author)):
        await message.author.send("**Delete data?** This cannot be undone", view=Confirm("Delete", delete, client, message, data), delete_after=30)
    else:
        await message.author.send("-# You don't seem to have any data to delete...")


async def notify(client, user):
    if client.notifications.get(user) and client.notifications[user]["notifications"] and client.notifications[user]["last"] != client.get_data(user)["status"]:
        u = await client.fetch_user(client.notifications[user]["id"])
        await u.send(f"-# Your order status has been updated to `{client.get_data(user)["status"]}`")
        client.notifications[user]["last"] = client.get_data(user)["status"]
        await client.save()
    else:
        return False


async def delete(client, message: Message, data: dict):
    try:
        print(data, client.data, sep="\n")
        del data[str(message.author)]
        await client.save()
        await message.author.send("-# Data deleted")
        print(data, client.data, sep="\n")
    except KeyError:
        await message.author.send("-# You don't seem to have any data to delete...")
