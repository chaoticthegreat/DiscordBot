import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup


class Web(commands.Cog):

    def __init__(self, client):
        self.client = client

    def mak_req(self, language, error):
        resp = requests.get("https://api.stackexchange.com/" +
                            f"/2.3/search?order=desc&sort=activity&tagged={language}&intitle={error}&site=stackoverflow")
        print(resp.json())
        return resp.json()

    def get_urls(self, json_dict):
        url_list = []
        count = 0

        for i in json_dict['items']:
            # print(i)
            url_list.append(i)
        newlist = sorted(url_list, key=lambda k: k['view_count'], reverse=True)
        url_list.clear()
        url_list.append(newlist[0]["link"])
        url_list.append(newlist[1]["link"])
        url_list.append(newlist[2]["link"])
        return url_list

    @commands.group(brief="Search algorithm category picker", help="Searches in web api's for answers.")
    async def search(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Pick a algorithm to search in!")

    @search.command(brief="Searches StackOverflow", help="Searches StackOverflow for answers. Tip: Keeps answer short and concise!")
    async def stack(self, ctx, language, *, query):
        urls = self.get_urls(self.mak_req(language, query))
        for key in urls:
            await ctx.send(f"{key}")
        if len(urls) == 0:
            await ctx.send("No results were found trying making your input concise")


def setup(client):
    client.add_cog(Web(client))
