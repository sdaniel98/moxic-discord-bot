from discord.ext import commands


class Developer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="dev", hidden=True)
    @commands.is_owner()
    async def developer_commands(self, ctx):
        pass

    @developer_commands.command(name="reload", aliases=["rl"])
    async def reload_cog(self, ctx, *, cog_to_reload):
        try:
            self.bot.reload_extension("cogs." + cog_to_reload)
        except Exception as e:
            await ctx.send(f"ERROR: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"SUCCESS: {cog_to_reload} successfully reloaded")

    @developer_commands.command(name="disable")
    async def disable_cog(self, ctx, *, cog_to_disable):
        try:
            self.bot.unload_extension("cogs." + cog_to_disable)
        except Exception as e:
            await ctx.send(f"ERROR: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"SUCCESS: {cog_to_disable} successfully disabled")

    @developer_commands.command(name="enable")
    async def enable_cog(self, ctx, *, cog_to_enable):
        try:
            self.bot.load_extension("cogs." + cog_to_enable)
        except Exception as e:
            await ctx.send(f"ERROR: {type(e).__name__} - {e}")
        else:
            await ctx.send(f"SUCCESS: {cog_to_enable} successfully enabled")

    @developer_commands.command(name="repeat")
    async def repeat(self, ctx, *, msg):
        print(msg)
        await ctx.send(msg)


def setup(bot):
    bot.add_cog(Developer(bot))
