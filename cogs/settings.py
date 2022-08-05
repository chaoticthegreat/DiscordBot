import discord
from discord.ext import commands
from database import load_json, write_json


class Settings(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(brief="Can change data for guild", help="Can change core data for the server/guild. Settings such "
                                                            "as default amount to clear or which channel "
                                                            "announcements are sent.")
    async def set(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Add what you want to change as a argument!")

    @set.command()
    @commands.has_permissions(administrator=True)
    async def prefix(self, ctx, prefix:str):
        prefix = prefix.replace("_", " ")
        prefixes = load_json()
        previousprefix = prefixes[str(ctx.guild.id)]["prefix"]
        prefixes[str(ctx.guild.id)]["prefix"] = prefix

        write_json(prefixes)

        await ctx.send(f"Prefix \"{previousprefix}\" changed to \"{prefix}\"")
        data=load_json()
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Bot prefix changed",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> Prefix \"{previousprefix}\" changed to \"{prefix}\"", value=f"\u200b",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)

    @set.command(brief="Changes default amount to clear.", help="Changes the amount messages to clear when using "
                                                                   "the clear command")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        data = load_json()
        before = data[str(ctx.guild.id)]["clear"]
        data[str(ctx.guild.id)]["clear"] = amount
        write_json(data)
        await ctx.send(
            f"Default amount being cleared \"{before}\" has been changed to \"{data[str(ctx.guild.id)]['clear']}\"")
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Default clear amount changed",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> Clear amount \"{before}\" changed to \"{data[str(ctx.guild.id)]['clear']}\"", value=f"\u200b",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)

    @set.command(brief="Changes if announcements mention @everyone", help="Can toggle on/off if announcements "
                                                                             "change @everyone and notify them")
    @commands.has_permissions(mention_everyone=True, manage_messages=True)
    async def announcemention(self, ctx, toggle: bool):
        data = load_json()
        before = data[str(ctx.guild.id)]["announce_mention"]
        data[str(ctx.guild.id)]["announce_mention"] = toggle
        write_json(data)
        await ctx.send(
            f"Announcement mention \"{before}\" has been changed to \"{data[str(ctx.guild.id)]['announce_mention']}\"")
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Announcement Mention",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> Announcement \"{before}\" changed to \"{data[str(ctx.guild.id)]['announce_mention']}\"",
                            value=f"\u200b",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)

    @set.command(brief="Changes the announcement channel", help="Changes where announcement messages are sent")
    @commands.has_permissions(mention_everyone=True, manage_messages=True)
    async def announcechannel(self, ctx, channel:discord.TextChannel):
        data = load_json()
        before = data[str(ctx.guild.id)]["announce_channel"]
        data[str(ctx.guild.id)]["announce_channel"] = int(channel.id)
        write_json(data)
        await ctx.send(
            f"Announcement Channel \"{self.client.get_channel(int(before))}\" has been changed to \"{self.client.get_channel(int(data[str(ctx.guild.id)]['announce_channel']))}\"")
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Announcement Channel change",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> Announcement channel \"{self.client.get_channel(int(before))}\" changed to \"{self.client.get_channel(int(data[str(ctx.guild.id)]['announce_channel']))}\"",
                            value=f"\u200b",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)
    @set.command(aliases=["ban-word"], brief="Marks a word as profanity", help="Bans a word in the server! "
                                                                                  "Auto-deletes the word and warns "
                                                                                  "the user that uses the banned "
                                                                                  "word.")
    @commands.has_permissions(manage_messages=True)
    async def ban_word(self, ctx, *bad_words):
        await ctx.message.delete()
        data = load_json()
        before = data[str(ctx.guild.id)]["profanity"]
        for key in bad_words:
            data[str(ctx.guild.id)]["profanity"].append(key)
        write_json(data)
        await ctx.send("Bad Word Banned!")
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Default clear amount changed",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> Prefix \"{before}\" changed to \"{data[str(ctx.guild.id)]['clear']}\"",
                            value=f"\u200b",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)
            b = data[str(ctx.guild.id)]["log_channel"]
            if b != "":
                embed = discord.Embed(
                    title="Banned profanity",
                    colour=discord.Colour.orange()
                )
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.add_field(name=f"Banned words",
                                value=f">>> {bad_words}",
                                inline=True)
                channel = self.client.get_channel(int(b))
                await channel.send(embed=embed)
    @set.command(aliases=["unban-word"], brief="Unbans word in the server.", help="Unbans a word in the server! "
                                                                                     "The word will no longer be "
                                                                                     "auto-deleted.")
    @commands.has_permissions(manage_messages=True)
    async def unban_word(self, ctx, *bad_words):
        data = load_json()
        before = data[str(ctx.guild.id)]["profanity"]
        for key in bad_words:
            data[str(ctx.guild.id)]["profanity"].remove(key)
        write_json(data)
        await ctx.send("Words unbanned!")
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Unbanned profanity",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f"Unbanned words",
                            value=f">>> {bad_words}",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)
    @set.command()
    @commands.has_permissions(administrator=True)
    async def log_channel(self, ctx, channel:discord.TextChannel):
        data=load_json()
        before = data[str(ctx.guild.id)]["log_channel"]
        data[str(ctx.guild.id)]["log_channel"] = str(channel.id)
        write_json(data)
        await ctx.send(
            f"Logging channel \"{before}\" has been changed to \"{data[str(ctx.guild.id)]['log_channel']}\"")
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Logging Channel changed",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> Logging Channel \"{before}\" changed to \"{data[str(ctx.guild.id)]['log_channel']}\"",
                            value=f"\u200b",
                            inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)
    @set.command()
    @commands.has_permissions(administrator = True)
    async def automod(self,ctx,toggle:bool):
        data=load_json()
        before=data[str(ctx.guild.id)]["automod"]
        data[str(ctx.guild.id)]["automod"] = toggle
        write_json(data)
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Automod toggled",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(
                name=f">>> Automod \"{before}\" changed to \"{data[str(ctx.guild.id)]['automod']}\"",
                value=f"\u200b",
                inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)
def setup(client):
    client.add_cog(Settings(client))
