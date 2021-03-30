from discord.ext import commands
from .cog_helpers import LogGetter
import discord
from asyncio import TimeoutError
from asyncio import sleep

class LivelogHelper(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.helper = LogGetter()
        self.livelogs = {}

    @commands.group(name="livelog", aliases=["ll"])
    async def livelog(self, ctx): pass

    @livelog.command(name="set")
    async def set_livelog(self, ctx, *, link):
        try:
            link = (link.split("/"))
            #split will remove all / and sometimes the link will end in / use the 2nd to last list item as the id if thats the case
            if not link[-1]: report_id = link[-2]
            else: report_id = link[-1]

            rankings = await self.helper.get_reports_page(report_id)
            num_rankings = len(rankings)
            self.livelogs.update({ctx.author.id: {"rankings": rankings, "num_rankings": num_rankings, "report_id": report_id}})
        except TypeError:
            await ctx.send("I can't find that log. Make sure you set your livelog to public.")
        else:
            await ctx.send("Livelog set successfully.")

            try:
                if (num_rankings > 0):
                    msg = await ctx.send(f"I found {num_rankings} kill(s) in the report. Would you like me to display them? Y(es) / N(o)")

                    if await self.get_user_input(ctx):
                        await self.display_all_reports(ctx, rankings)

                    else: await msg.edit(content="Ok. I won't display the logs.")

            except TimeoutError: await msg.edit(content="You didn't respond in time. I won't display the logs.")

    @set_livelog.error
    async def livelog_error(self, ctx, error):
        if isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
            await ctx.send("I need a link to the livelog to track it.")

    @livelog.command(name="update")
    async def update_livelog(self, ctx):
        try:
            new_rankings = await self.helper.get_reports_page(self.livelogs[ctx.author.id]["report_id"])
            old_num_rankings = self.livelogs[ctx.author.id]["num_rankings"]
            new_num_rankings = len(new_rankings)
            new_kills = new_num_rankings - old_num_rankings

            if new_kills <= 0:
                await ctx.send("I didn't find any new kills.")
            else:
                await ctx.send(f"I found {new_kills} new kill(s).\nDisplaying new kills now.")
                self.livelogs[ctx.author.id]["rankings"] = new_rankings
                self.livelogs[ctx.author.id]["num_rankings"] = new_num_rankings

                for i in (new_kills - 1, new_num_rankings):
                    await sleep(0.5)
                    await ctx.send(f"New kill {i - new_kills + 2}:")
                    await sleep(1.2)
                    await self.display_logs(ctx, new_rankings[i])

        except TypeError: #happens because fflogs sends back null
            await ctx.send("Don't delete the log or make it private, please. You'll have to set the livelog again now.")
            del self.livelogs[ctx.author.id]
        except KeyError:
            await ctx.send("I'm not tracking a livelog for you right now. You can set one for me to track with #livelog set")

    @livelog.command(name="end")
    async def end_livelog_tracking(self, ctx):
        try:
            del self.livelogs[ctx.author.id]
            await ctx.send("I am no longer tracking a livelog for you.")
        except KeyError:
            await ctx.send("I'm not tracking a livelog for you right now. You can set one for me to track with #livelog set")

    @livelog.command(name="view")
    async def view_all_reports(self, ctx):
        try:
            test = self.livelogs[ctx.author.id]
            reports = self.livelogs[ctx.author.id]["rankings"]
            await self.display_all_reports(ctx, reports)
        except KeyError:
            await ctx.send("I'm not tracking a livelog for you right now. You can set one for me to track with #livelog set")

    async def display_all_reports(self, ctx, reports):
        for index, report in enumerate(reports):
            await sleep(0.5)
            await ctx.send(f"Kill {index + 1}:")
            await sleep(1.2)
            await self.display_logs(ctx, report)

    async def get_user_input(self, ctx):
        m = await self.bot.wait_for("message",
                                    check=lambda m: m.author == ctx.author and m.content.lower() in ("y", "n", "yes", "no"),
                                    timeout=20.0)
        m = m.content.lower()
        if m in ("y", "yes"): return True
        else: return False

    #assuming standard comp ie 2t2h4d
    async def display_logs(self, ctx, logs):
        url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBWGf-z9n4zCvF9OR8ZLUrVEQyLRU3ifMTmR_iWtGDaF5DzOXeXQCZZVbRb92maEXVebA&usqp=CAU"
        fight_name = logs['encounter']['name']
        speed_parse = logs['speed']['rankPercent']

        color = await self.get_color(speed_parse)
        title = f"**__{fight_name}__**"

        embed = discord.Embed(title=title, color=color)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed = await self.get_tank_logs(logs['roles']['tanks'], embed)
        embed = await self.get_healer_logs(logs['roles']['healers'], embed)
        embed = await self.get_dps_logs(logs['roles']['dps'], embed)
        embed.add_field(name="__Overall__", value=f"Speed: {speed_parse}", inline=False)
        embed.set_thumbnail(url=url)

        await ctx.send(embed=embed)

    async def get_tank_logs(self, logs, embed):
        tank1_name = logs['characters'][0]['name']
        tank1_dps = round(logs['characters'][0]['amount'], 2)
        tank1_parse = logs['characters'][0]['rankPercent']
        tank2_name = logs['characters'][1]['name']
        tank2_dps = round(logs['characters'][1]['amount'], 2)
        tank2_parse = logs['characters'][1]['rankPercent']
        combined_tank_dps = round(logs['characters'][2]['amount'], 2)
        combined_tank_parse = logs['characters'][2]['rankPercent']

        embed.add_field(name="\n**__Tanks__**", value="\u200b", inline=False)
        embed.add_field(name=f"__{tank1_name}__", value=f"DPS: {tank1_dps:,}\nParse: {tank1_parse}", inline=True)
        embed.add_field(name=f"__{tank2_name}__", value=f"DPS: {tank2_dps:,}\nParse: {tank2_parse}", inline=True)
        embed.add_field(name=f"__Combined__", value =f"DPS: {combined_tank_dps:,}\nParse: {combined_tank_parse}\n", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        return embed

    async def get_healer_logs(self, logs, embed):
        healer1_name = logs['characters'][0]['name']
        healer1_dps = round(logs['characters'][0]['amount'], 2)
        healer1_parse = logs['characters'][0]['rankPercent']
        healer2_name = logs['characters'][1]['name']
        healer2_dps = round(logs['characters'][1]['amount'], 2)
        healer2_parse = logs['characters'][1]['rankPercent']
        combined_healer_dps = round(logs['characters'][2]['amount'], 2)
        combined_healer_parse = logs['characters'][2]['rankPercent']

        embed.add_field(name="\n**__Healers__**", value="\u200b", inline=False)
        embed.add_field(name=f"__{healer1_name}__", value=f"DPS: {healer1_dps:,}\nParse: {healer1_parse}", inline=True)
        embed.add_field(name=f"__{healer2_name}__", value=f"DPS: {healer2_dps:,}\nParse: {healer2_parse}", inline=True)
        embed.add_field(name=f"__Combined__", value=f"DPS: {combined_healer_dps:,}\nParse: {combined_healer_parse}\n", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        return embed

    async def get_dps_logs(self, logs, embed):
        dps1_name = logs['characters'][0]['name']
        dps1_dps = round(logs['characters'][0]['amount'], 2)
        dps1_parse = logs['characters'][0]['rankPercent']
        dps2_name = logs['characters'][1]['name']
        dps2_dps = round(logs['characters'][1]['amount'], 2)
        dps2_parse = logs['characters'][1]['rankPercent']
        dps3_name = logs['characters'][2]['name']
        dps3_dps = round(logs['characters'][2]['amount'], 2)
        dps3_parse = logs['characters'][2]['rankPercent']
        dps4_name = logs['characters'][3]['name']
        dps4_dps = round(logs['characters'][3]['amount'], 2)
        dps4_parse = logs['characters'][3]['rankPercent']

        embed.add_field(name="\n**__DPS__**", value="\u200b", inline=False)
        embed.add_field(name=f"__{dps1_name}__", value=f"DPS: {dps1_dps:,}\nParse: {dps1_parse}", inline=True)
        embed.add_field(name=f"__{dps2_name}__", value=f"DPS: {dps2_dps:,}\nParse: {dps2_parse}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name=f"__{dps3_name}__", value=f"DPS: {dps3_dps:,}\nParse: {dps3_parse}", inline=True)
        embed.add_field(name=f"__{dps4_name}__", value=f"DPS: {dps4_dps:,}\nParse: {dps4_parse}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        return embed

    async def get_color(self, rank):
        gold = discord.Color.from_rgb(229, 204, 128)
        pink = discord.Color.from_rgb(226, 104, 168)
        orange = discord.Color.from_rgb(255, 128, 0)
        purple = discord.Color.from_rgb(163, 53, 238)
        blue = discord.Color.from_rgb(0, 112, 255)
        green = discord.Color.from_rgb(30, 255, 0)
        gray = discord.Color.from_rgb(102, 102, 102)

        if rank > 0:
            if rank > 24.99:
                if rank > 49.99:
                    if rank > 74.99:
                        if rank > 94.99:
                            if rank > 98.99:
                                if rank > 99.99:
                                    color = gold
                                else:
                                    color = pink
                            else:
                                color = orange
                        else:
                            color = purple
                    else:
                        color = blue
                else:
                    color = green
            else:
                color = gray

        return color

def setup(bot):
    bot.add_cog(LivelogHelper(bot))