from discord.ext import commands


class Miscellaneous(commands.Cog):

    @commands.command(name="invite", aliases=["inv"])
    async def invite(self, ctx):
        invite_url = "https://discord.com/oauth2/authorize?client_id=822655619403874324&permissions=116736&scope=bot"
        await ctx.send(invite_url)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))

