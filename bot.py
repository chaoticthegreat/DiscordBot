import os
from database import load_json, write_json
import discord
from discord.ext import commands


def get_prefix(client, message):
    prefixes = load_json()
    return prefixes[str(message.guild.id)]["prefix"]


client = commands.Bot(command_prefix=get_prefix)
client.remove_command("help")


@client.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.name == "general":
            await channel.send("Hey there, I'm Chaotic")
            await channel.send("To setup logging use $change logging")
    prefixes = load_json()
    dictionary = {}
    prefixes[str(guild.id)] = {"prefix": "$", "clear": 10, "messages": dictionary, "announce_mention": True,
                               "announce_channel": "announcements", "profanity": [], "log_channel": "", "automod": True}
    write_json(prefixes)


# Deleting Data when bot is kicked/banned
@client.event
async def on_guild_remove(guild):
    prefixes = load_json()
    prefixes.pop(str(guild.id))
    write_json(prefixes)
@client.event
async def on_ready():
    print("Bot is online!")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f"cogs.{filename[:-3]}")

client.run("ODI0MTAxNjgzNjA4OTQ0Njgw.YFqegA.erHBjFgfgC5hwEQFPFt-m0ld-Bc")
