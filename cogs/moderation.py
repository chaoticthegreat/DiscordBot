import discord
from datetime import datetime, timedelta
from discord.ext import commands
from database import load_json, write_json
from discord.utils import get
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Moderation(commands.Cog):
    def __init__(self, client):
        self.scheduler = AsyncIOScheduler()
        self.client = client
        self.polls = []

    @commands.command(name="createpoll", aliases=["mkpoll"], brief="Create a public poll",
                      help="Create a poll with up to 10 options and a time limit.")
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def create_poll(self, ctx, hours: int, question: str, *options):
        numbersdict = {"1️⃣":1, "2⃣":2, "3⃣":3, "4⃣":4, "5⃣":5,
                   "6⃣":6, "7⃣":7, "8⃣":8, "9⃣":9, "🔟":10}
        numbers = list(numbersdict)
        if len(options) > 10:
            await ctx.send("Only 10 options are allowed")

        else:
            embed = discord.Embed(title="Poll",
                                  description=question,
                                  colour=discord.Colour.orange(),
                                  timestamp=datetime.utcnow())

            fields = [("Options", "\n".join([f"{numbers[idx]} {option}" for idx, option in enumerate(options)]), False),
                      ("Instructions", "React to cast a vote!", False)]

            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            message = await ctx.send(embed=embed)

            for emoji in numbers[:len(options)]:
                await message.add_reaction(emoji)

            self.polls.append((message.channel.id, message.id))

            self.scheduler.add_job(self.complete_poll, "date", run_date=datetime.now() + timedelta(hours=hours),
                                   args=[message.channel.id, message.id, question, options, numbersdict])
            self.scheduler.start()

    async def complete_poll(self, channel_id, message_id, question, options, numbersdict):
        message = await self.client.get_channel(channel_id).fetch_message(message_id)
        x=message.reactions.copy()
        most_voted = max(x, key=lambda r: r.count)
        embed = discord.Embed(
            title="Poll",
            description=question,
            colour=discord.Colour.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="The results are in!", value="Our winner is "+options[int(numbersdict[most_voted.emoji])], inline=False)
        try:
            del x[x.index(most_voted)]
            second_voted = max(x, key=lambda r: r.count)
            del x[x.index(second_voted)]
            third_voted = max(x, key=lambda r: r.count)
            embed.add_field(name=f"Option {most_voted.emoji}: {options[int(numbersdict[most_voted.emoji])-1]}", value=f"```{str(most_voted.count-1)}```", inline=False)
            embed.add_field(name=f"Option {second_voted.emoji}: {options[int(numbersdict[second_voted.emoji])-1]}", value=f"```{str(second_voted.count-1)}```", inline=False)
            embed.add_field(name=f"Option {third_voted.emoji}: {options[int(numbersdict[third_voted.emoji])-1]}", value=f"```{str(third_voted.count-1)}```", inline=False)
        except:
            embed.add_field(name=f"Option {most_voted.emoji}", value=str(most_voted.count))
        # await message.channel.send(f"The results are in and {options[int(numbersdict[most_voted.emoji])]}(option {most_voted.emoji}) was the most popular with {most_voted.count - 1:,} votes!")
        await message.channel.send(embed=embed)
        self.polls.remove((message.channel.id, message.id))

    @commands.command(brief="Clear messages", help="Clears up to 100 messages at a time")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = "default"):
        amount = amount if amount != "default" else load_json()[str(ctx.guild.id)]["clear"]
        with ctx.channel.typing():
            await ctx.message.delete()
            await ctx.channel.purge(limit=amount)
        data=load_json()
        b = data[str(ctx.guild.id)]["log_channel"]
        if b != "":
            embed = discord.Embed(
                title="Deleted Message",
                colour=discord.Colour.orange()
            )
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name=f">>> {ctx.author} cleared {amount} message(s)", value=f"\u200b", inline=True)
            channel = self.client.get_channel(int(b))
            await channel.send(embed=embed)

    @commands.command(brief="Announce something",
                      help="Announce something to the whole server. The @everyone can be toggled of with \"change-annmention\". The channel the announcement is sent to can be changed by \"change-annchannel\"")
    @commands.has_permissions(mention_everyone=True, manage_messages=True)
    async def announce(self, ctx, *, title):
        _type = load_json()[str(ctx.guild.id)]["announce_mention"]
        channel = load_json()[str(ctx.guild.id)]["announce_channel"]
        embed = discord.Embed(
            title=title,
            colour=discord.Colour.orange(),
        )
        mention = True
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        if _type:
            mention = True
        elif not _type:
            mention = False
        mention = "||@everyone||" if mention else ""
        try:
            channel = get(ctx.guild.channels, id = int(channel))
            await channel.send(mention, embed=embed)
        except AttributeError:
            await ctx.guild.create_text_channel(channel)
            channel = get(ctx.guild.channels, name=channel)
            await channel.send(mention, embed=embed)

def setup(client):
    client.add_cog(Moderation(client))
