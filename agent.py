import discord
import os
from dotenv import load_dotenv

import db as d

import importlib
from importlib import machinery

import re
import glob

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_IDS = os.environ.get("ADMIN_IDS").split(",")
DEBUG = os.environ.get("DEBUG", False)


class Agent:
    def __init__(self, client):
        self.client = client
        self.load_config()
        self.load_plugin()

    def load_config(self):
        self.db = d.Manager("agent.db")
        self.token = BOT_TOKEN
        self.admin_ids = ADMIN_IDS
        self.debug = DEBUG

    def load_plugin(self):
        self.plugin_handlers = []
        plugins = [
            filepath.replace(".py", "")
            for filepath in glob.glob("commands/**/*.py", recursive=True)
        ]
        for plugin in plugins:
            loader = machinery.SourceFileLoader(plugin, plugin + ".py")
            module = loader.load_module()
            plugin_instance = module.Handler(self.db)
            self.plugin_handlers.append(plugin_instance)
            print("load plugin", plugin_instance.get_plugin_info())

    def run(self):
        self.client.run(self.token)

    def trim_white_space(self, text):
        # 全角スペースを半角スペースにする
        text = text.replace("\u3000", " ")
        # # 全角？を半角?にする
        # text = text.replace("？","?")
        # 全角！を半角?にする
        text = text.replace("！", "!")
        # 全角：を半角:にする
        text = text.replace("：", ":")
        # 2連続以上のスペース、スペースを1個にする
        text = re.sub("[ ]{2,}", " ", text)
        # # 改行をスペースに変換
        # text = text.replace("\n"," ")
        return text

    async def on_ready(self):
        print("Logged in as", self.client.user.name, self.client.user.id)

    async def on_message(self, message):
        try:
            if self.debug:
                print(
                    "message:",
                    message.guild.id,
                    message.author.id,
                    message.author.name,
                    message.content,
                )
            content = self.trim_white_space(message.content)
            if not isinstance(message.channel, discord.abc.PrivateChannel):
                processed = False
                for handler in self.plugin_handlers:
                    info = handler.get_plugin_info()
                    for locale, commands in info["commands"].items():
                        for command in commands:
                            if content.startswith(command) or command == "*":
                                processed = await handler.on_message(
                                    client, message, content, locale
                                )
                                if processed is True:
                                    break
                    if processed is True:
                        break
        except:
            import traceback

            trace = traceback.format_exc()
            print(trace)
            if self.debug:
                await message.channel.send(trace)

    async def on_member_join(self, member):
        pass

    async def on_member_remove(self, member):
        pass

    async def on_reaction_add(self, reaction, user):
        pass

    async def on_reaction_remove(self, reaction, user):
        pass

    async def on_message_edit(self, before, after):
        pass

    async def on_message_delete(self, message):
        pass


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    await agent.on_ready()


@client.event
async def on_message(message):
    await agent.on_message(message)


@client.event
async def on_member_join(member):
    await agent.on_member_join(member)


@client.event
async def on_member_remove(member):
    await agent.on_member_remove(member)


@client.event
async def on_reaction_add(reaction, user):
    await agent.on_reaction_add(reaction, user)


@client.event
async def on_reaction_remove(reaction, user):
    await agent.on_reaction_remove(reaction, user)


@client.event
async def on_message_edit(before, after):
    await agent.on_message_edit(before, after)


@client.event
async def on_message_delete(message):
    await agent.on_message_delete(message)


agent = Agent(client)

agent.run()
