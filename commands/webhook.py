import discord

from datetime import datetime, timedelta
import random
import requests
import json
import re


def get_name_and_avatar_from_discord(server, uid):
    avatar_url = ""
    member = server.get_member(uid)
    name = "-"
    if member is not None:
        if member.nick is not None:
            name = str(member.nick)
        else:
            name = str(member)
        avatar_url = member.display_avatar.url
    return name, avatar_url


def post_webhook(name, avatar_url, content, url=""):
    request = {"username": "", "avatar_url": "", "content": ""}
    headers = {"content-type": "application/json"}
    if len(url) < 1:
        print("url required.")
        return
    if len(name) < 2:
        name += "."
    request["username"] = name
    request["avatar_url"] = avatar_url
    request["content"] = content
    response = requests.post(url, data=json.dumps(request), headers=headers)
    print(response)


class Handler:
    def __init__(self, _db):
        self.db = _db
        self.webhook_name = ""
        self.webhook_avatar_url = ""

    def get_plugin_info(self):
        info = {
            "name": "webhook",
            "commands": {
                "ja": ["*", "!設定", "!登録", "!解除"],
                "en": [],
            },
            "available_channels": "all",
            "version": "0.0.1",
        }
        return info

    async def on_message(self, client, message, command, locale):
        if client.user == message.author:
            return False

        channel = message.channel

        m = message.author.mention + "\n"

        settings = self.db.tables["webhook_setting"].select_by_server_id(
            message.guild.id
        )
        if settings:
            for setting in settings:
                inspection_channels = setting["channels"].split(",")
                if str(message.channel.id) in inspection_channels:
                    image_url = ""
                    if message.attachments:
                        image_url = message.attachments[0].url
                    has_image = ""
                    if len(image_url) > 0:
                        has_image = "【添付ファイルあり〼】"

                    name, avatar_url = get_name_and_avatar_from_discord(
                        message.guild, message.author.id
                    )
                    post_webhook(
                        name,
                        avatar_url,
                        f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}\n"
                        + message.content
                        + has_image,
                        setting["webhook_url"],
                    )

        commands = command.split(" ")
        if command.startswith("!設定リスト"):
            if settings:
                await channel.send("このサーバーの設定リストにゃ。\n" + str(settings))
            else:
                await channel.send("このサーバーはまだ設定がないにゃ。")
            return True
        elif command.startswith("!設定"):
            if len(commands) > 2:
                self.db.tables["webhook_setting"].logical_delete(
                    str(message.guild.id), commands[1]
                )
                self.db.tables["webhook_setting"].insert(
                    str(message.guild.id), "", commands[1], commands[2]
                )
                await channel.send("設定したにゃ。")
            else:
                await channel.send("「！設定　カテゴリ名　webhookurl」で指定するんだにゃ。")
            return True
        elif command.startswith("!登録"):
            if len(commands) > 1:
                setting = self.db.tables["webhook_setting"].select_by_category_name(
                    str(message.guild.id), commands[1]
                )
                if setting:
                    channels = setting["channels"].split(",")
                    channels.append(str(message.channel.id))
                    self.db.tables["webhook_setting"].update_channels(
                        str(message.guild.id), commands[1], ",".join(channels)
                    )
                    await channel.send("登録したにゃ。")
                else:
                    await channel.send("まだそのカテゴリの設定がないわん。！設定コマンドで設定するんだにゃ。")
            else:
                await channel.send("「！登録 カテゴリ名」でこのチャンネルを登録するんだにゃ。")
            return True
        elif command.startswith("!解除"):
            if len(commands) > 1:
                setting = self.db.tables["webhook_setting"].select_by_category_name(
                    str(message.guild.id), commands[1]
                )
                if setting:
                    channels = setting["channels"].split(",")
                    channels.remove(message.channel.id)
                    self.db.tables["webhook_setting"].update_channels(
                        str(message.guild.id), commands[1], ",".join(channels)
                    )
                    await channel.send("解除したにゃ。")
                else:
                    await channel.send("まだそのカテゴリの設定がないにゃ。")
            else:
                await channel.send("「！解除 カテゴリ名」でこのチャンネルを解除するんだにゃ。")
            return True
