import os
import json
import configparser
from telethon import TelegramClient
from telethon import events
import arabic_reshaper
from bidi.algorithm import get_display
from os import system, name


def clear():
    # for windows
    if name == "nt":
        _ = system("cls")

    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system("clear")


def print_bidi(text):
    reshaped_text = arabic_reshaper.reshape(repr(text))
    bidi_text = get_display(reshaped_text)
    print(bidi_text)


def get_config(config_filename: str):
    """Create a config object from config file.

    Args:
        config_filename (str): The config filename.

    Returns:
        ConfigParser: a new ConfigParser object.
    """
    if not os.path.exists(config_filename):
        raise FileNotFoundError(f"Not found: {config_filename}")
    config = configparser.ConfigParser()
    config.read(config_filename)
    return config


def create_client(config: configparser.ConfigParser):
    """Create a Telegram client object from given config.

    Args:
        config (configparser.ConfigParser): Parsed config object.

    Returns:
        TelegramClient: The Telegram client object.
    """
    client = TelegramClient(
        session=config["Access"]["session"],
        api_id=config["Access"]["id"],
        api_hash=config["Access"]["hash"],
        timeout=int(config["Client"]["timeout"]),
        device_model=config["Client"]["device_model"],
        lang_code=config["Client"]["lang_code"],
    )
    client.start()
    return client


def read_chats():
    with open("./chats.json", "r") as file:
        chats = json.load(file)

    return chats


def write_chat(from_chat, to_chat):
    with open("chats.json", "w") as file:
        file.write(json.dumps({"from": from_chat, "to": to_chat}, indent=4))


async def get_channel_list():
    dialogs = []
    i = 1
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            dialogs.append({"index": i, "name": dialog.name, "id": dialog.entity.id})
            i += 1
    return dialogs


async def get_channel_id(channel_name="test channel"):
    async for dialog in client.iter_dialogs():
        if dialog.name == channel_name and (dialog.is_group or dialog.is_channel):
            return dialog.entity.id


async def main():
    chats_config = read_chats()
    if not chats_config["from"] and not chats_config["to"]:
        dialogs = await get_channel_list()
        print_bidi("Enter index of the chat you want to forward from :")
        for dialog in dialogs:
            print(dialog["index"], end="-")
            print_bidi(dialog["name"])
        forward_from = int(input(">>>"))
        clear()
        print_bidi("Enter index of the chat you want to forward to :")
        for dialog in dialogs:
            print(dialog["index"], end="-")
            print_bidi(dialog["name"])
        forward_to = int(input(">>>"))
        clear()

        write_chat(
            from_chat=[item["id"] for item in dialogs if item["index"] == forward_from][
                0
            ],
            to_chat=[item["id"] for item in dialogs if item["index"] == forward_to][0],
        )
        chats_config = read_chats()

    print_bidi(
        f"forwarding from: {[item['name'] for item in dialogs if item['index'] == forward_from][0]}"
    )
    print_bidi(
        f"forwarding to: {[item['name'] for item in dialogs if item['index'] == forward_to][0]}"
    )

    forward_from_id = chats_config["from"]
    forward_to_id = chats_config["to"]

    if forward_from_id:
        print_bidi(f"Listening for new messages in: (ID: {forward_from_id})")

        @client.on(events.NewMessage(chats=forward_from_id))
        async def handler(event):
            print_bidi(f"New message in (ID: {forward_from_id}), forwarding ...")
            # await event.forward_to(forward_to_id)
            await client.send_message(forward_to_id,event.message.text)
            print_bidi(f"Forwarded to (ID: {forward_to_id})")

        await client.run_until_disconnected()
    else:
        print_bidi("Channel not found!")


config = get_config("config.ini")
client = create_client(config)
client.loop.run_until_complete(main())
