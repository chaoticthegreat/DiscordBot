import discord
from discord.utils import get
from discord.ext import commands
from database import load_json, write_json
from discord.ext.menus import MenuPages, ListPageSource
from googleapiclient import discovery
import json

class HelpMenu(ListPageSource):
    def __init__(self, ctx, data, client):
        self.ctx = ctx
        self.client=client
        super().__init__(data, per_page=10)

    async def write_page(self, menu, offset, fields=[]):
        len_data = len(self.entries)

        embed = discord.Embed(title="XP Leaderboard",
                      colour=self.ctx.author.colour)
        embed.set_thumbnail(url=self.ctx.guild.icon_url)
        embed.set_footer(text=f"{offset:,} - {min(len_data, offset + self.per_page - 1):,} of {len_data:,} members.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, menu, entries):
        offset = (menu.current_page * self.per_page) + 1
        fields = []
        # int(list(entry.values())[2])
        # user = await self.ctx.message.guild.query_members(user_ids=[entry.values[2]])
        table = ("\n".join(
            f"{idx + offset}. {self.client.get_user(801507608384634881).display_name()} (XP: {list(entry['experience'])} | Level: {list(entry['level'])})"
            for idx, entry in enumerate(entries)))

        fields.append(("Ranks", table))

        return await self.write_page(menu, offset, fields)


class Experience(commands.Cog):

    def __init__(self, client):
        self.client = client

    # For Level Up System
    # Check if user exists or not for level up system
    async def update_data(self, users, user):
        if str(user.id) not in users and user.id != 824101683608944680:
            users[str(user.id)] = {}
            users[str(user.id)]["experience"] = 0
            users[str(user.id)]["level"] = 1
            return users, True
        return users, False

    # For level up System
    # Add 5 experience per message
    async def add_experience(self, users, user, exp):
        try:
            users[str(user.id)]["experience"] += exp
        except:
            pass
        return users

    # For Level Up Systemj
    # Levels up if experience is right
    async def level_up(self, users, user, channel):
        try:
            experience = users[str(user.id)]["experience"]
            lvl_start = users[str(user.id)]["level"]
            lvl_end = int(experience ** (1 / 4))
            levelup = False
            if lvl_start < lvl_end:
                embed = discord.Embed(
                    colour=discord.Colour.orange(),
                    title="Level Up!"
                )
                embed.add_field(name="Congratulations", value=f"{user} leveled up to {lvl_end}")
                embed.set_footer(text="Make some CHAOS for me!")
                await channel.send(embed=embed)
                users[str(user.id)]["level"] = lvl_end
                levelup = True
        except:
            levelup = False
        return users, levelup, users[str(user.id)]["level"]

    # For Level Up system
    # Calls all functions and add roles for level systems
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == 824101683608944680:
            return
        data = load_json()
        if data[str(message.guild.id)]["automod"] == True:
            API_KEY = 'AIzaSyCI7HHgDL1yfOXeCKIJSdlMlMRUKum2Xrs'

            client = discovery.build(
                "commentanalyzer",
                "v1alpha1",
                developerKey=API_KEY,
                discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                static_discovery=False,
            )
            embed = discord.Embed(
                title="Toxicity Detected! Message Deleted",
                colour = discord.Colour.orange()
            )
            embed.set_author(name=message.author.name,  icon_url=message.author.avatar_url)
            embed.add_field(name=f">>> {message.content}", value=f"\u200b", inline=True)
            b = data[str(message.guild.id)]["log_channel"]
            analyze_request = {
                'comment': {'text': message.content},
                "languages": ["en"],
                'requestedAttributes': {'TOXICITY': {}}
            }

            response = client.comments().analyze(body=analyze_request).execute()
            # print(response)
            x=round(json.loads(json.dumps(response, indent=2))["attributeScores"]["TOXICITY"]["summaryScore"]["value"]*100)
            # print(x)
            if x>=95:
                await message.delete()
                await message.author.send("This is a friendly server!, please be nice!")
                if b!="":
                    channel = self.client.get_channel(int(b))
                    await channel.send(embed=embed)
                return
        data[str(message.guild.id)]["messages"], new = await self.update_data(data[str(message.guild.id)]["messages"],
                                                                              message.author)
        if new:
            data[str(message.guild.id)][str(message.author.id)] = {
                "experience": 0,
                "level": 1
            }
            write_json(data)
            if get(message.guild.roles, name=f"Chaos Level 1"):
                await message.author.add_roles(get(message.guild.roles, name=f"Chaos Level 1"))
                return
            role = await message.guild.create_role(name=f"Chaos Level 1", colour=discord.Colour.random(),
                                                   mentionable=True)
            await message.author.add_roles(role)
            return
        data[str(message.guild.id)]["messages"] = await self.add_experience(data[str(message.guild.id)]["messages"],
                                                                            message.author, 5)
        data[str(message.guild.id)]["messages"], level, what_level = await self.level_up(
            data[str(message.guild.id)]["messages"], message.author, message.channel)
        if level:
            if what_level - 1 != 0:
                if not message.channel:
                    return
                print(what_level)
                role = get(message.guild.roles, name=f"Chaos Level {what_level - 1}")
                print(message.author)
                print(what_level)
                print(role)
                await message.author.remove_roles(role)
            if get(message.guild.roles, name=f"Chaos Level {what_level}"):
                await message.author.add_roles(get(message.guild.roles, name=f"Chaos Level {what_level}"))
            else:
                role = await message.guild.create_role(name=f"Chaos Level {what_level}", colour=discord.Colour.random(),
                                                       mentionable=True)
                await message.author.add_roles(role)
        words = data[str(message.guild.id)]["profanity"]
        for word in words:
            if word in message.content:
                await message.delete()
                await message.channel.send("You can't use that word")
        write_json(data)
    @commands.command()
    async def leaderboard(self, ctx):
        def sortFunction(value):
            return value["experience"]
        x=load_json()[str(ctx.guild.id)]["messages"]
        y=x.values()
        sortedStudents = sorted(y, key=sortFunction)
        sortedStudents.reverse()
        id_ = load_json()[str(ctx.guild.id)]["messages"]
        for item in id_.keys():
            for thing in sortedStudents:

                if id_[item] == thing:
                    print("Success")
                    break
            print(sortedStudents)
            sortedStudents[sortedStudents.index(thing)]["id"] = item
            print(sortedStudents[sortedStudents.index(thing)]["id"])
        menu = MenuPages(source=HelpMenu(ctx, sortedStudents, self.client),
                         clear_reactions_after=True,
                         timeout=60.0)
        await menu.start(ctx)
def setup(client):
    client.add_cog(Experience(client))
