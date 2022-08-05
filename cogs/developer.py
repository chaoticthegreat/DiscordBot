import discord, asyncio, os
from discord.ext import commands
from database import load_json, write_json


class Developer(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Data Handling

    @commands.command(brief = "Reloads a cog", help = "Can reloads multiple cogs to their latest update. Status update is shown.")
    async def reload(self, ctx, *args):
        reloadedextension = []
        fail = {}
        for extension in args:
            try:
                self.client.unload_extension(f"cogs.{extension}")
                self.client.load_extension(f"cogs.{extension}")
                reloadedextension.append(extension)
            except Exception as why:
                fail[extension] = why
        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title="Extension reload"
        )
        for extension in reloadedextension:
            embed.add_field(name=f"Reloaded Extension ```{extension}``` status", value="Pass :white_check_mark:",
                            inline=False)
        for failure in fail.keys():
            embed.add_field(name=f"Reloaded Extension ```{failure}``` status",
                            value=f"Fail :x:\n```{fail[failure]}```", inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief = "Returns latency", help = "Returns the clients latency rounded in to milliseconds")
    async def ping(self, ctx):
        await ctx.send(f"Pong! Latency: {round(self.client.latency * 1000)}ms")

    @commands.command(hidden=True)
    async def admin(self, ctx):

        try:

            if ctx.author.id == 801507608384634881:
                while True:
                    command = False
                    x = input("Next Message: ")
                    if x == "quit":
                        return
                    if x.startswith("clear"):
                        await ctx.channel.purge(limit=int(x.split()[1]))
                        await ctx.send(f"Cleared {int(x.split()[1]) + 1} messages")
                        command = True
                    embed = discord.Embed(
                        title="Discord Self Bot",
                        colour=discord.Colour.orange()
                    )
                    embed.add_field(name="Developer: ", value=x)
                    if not command:
                        await ctx.send(embed=embed)
                    command = False
            else:
                embed = discord.Embed(
                    title="Error",
                    colour=discord.Colour.orange()
                )
                embed.add_field(name="Unauthorized Access", value="This is a developer only command!")
                await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            await ctx.send("TIMEOUT")
    @commands.command(brief="Reload all cogs and check core data", help = "Reloads all cogs to the latest version and checks core data for recent updates")
    async def reboot(self, ctx):
        args = [x.replace(".py", "") for x in os.listdir("/Users/ryanabraham/PycharmProjects/DiscordBot#2/cogs")]
        reloadedextension = []
        fail = {}
        for extension in args:
            if extension=="__pycache__":
                continue
            try:
                try:
                    self.client.unload_extension(f"cogs.{extension}")
                except:
                    pass
                self.client.load_extension(f"cogs.{extension}")
                reloadedextension.append(extension)
            except Exception as why:
                fail[extension] = why
        embed = discord.Embed(
            colour=discord.Colour.orange(),
            title="Reboot",
            description="Reboot all extensions and make sure core server data exists"
        )
        for extension in reloadedextension:
            embed.add_field(name=f"Reloaded Extension ```{extension}``` status", value="Pass :white_check_mark:",
                            inline=False)
        for failure in fail.keys():
            embed.add_field(name=f"Reloaded Extension ```{failure}``` status",
                            value=f"Fail :x:\n```{fail[failure]}```", inline=False)
        data = load_json()
        core_data = {"clear": 10, "messages": {}, "prefix": "$", "announce_mention": True, "announce_channel": "announcements", "profanity": [], "log_channel":"","automod":True}
        missing_key = 0
        valid_key = 0
        for key in core_data.keys():
            if key not in data[str(ctx.guild.id)].keys() or type(data[str(ctx.guild.id)][key]) != type(core_data[key]):
                data[str(ctx.guild.id)][key] = core_data[key]
                missing_key += 1
                continue
            valid_key += 1
        write_json(data)
        embed.add_field(name="Valid Keys in Core Data", value=f"```{valid_key} key(s)```")
        embed.add_field(name="Missing/Corrupted Keys in Core Data", value=f"```{missing_key} key(s)```")
        embed.set_footer(text="Reboot Complete!")
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    async def shutdown(self, ctx):
        if ctx.message.author.id == 801507608384634881:  # replace OWNERID with your user id
            print("Shutdown")
            try:
                await self.client.logout()
            except:
                print("EnvironmentError")
                self.client.clear()
        else:
            await ctx.send("You do not own this bot!")


def setup(client):
    client.add_cog(Developer(client))
