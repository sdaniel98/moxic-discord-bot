import sys

sys.path.append("cogs/cog_helpers")
from .cog_helpers import DatabaseManager, LogGetter
from discord.ext import commands
import discord
import traceback
import urllib.request
from PIL import Image
from io import BytesIO
import math
from sqlite3 import IntegrityError
from random import Random

# times are stored in time from epoch in ms
release_dates = {"ucob": 1508832000000, "uwu": 1528192800000, "tea": 1573547400000, "current_tier": 1607389200000}
MS_IN_A_WEEK = 604800000


class LogShamer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.helper = LogGetter()
        self.db = DatabaseManager()

    @commands.group(name="logs", aliases=["l"], invoke_without_command=True)
    async def get_logs(self, ctx, *, user: discord.Member):
        try:
            await self.display_logs(ctx, user.id)
        except TypeError:
            await ctx.send(f"I don't know who that is. Tell them to use {self.bot.command_prefix}iam")

    @get_logs.command(name="ultimate", aliases=["Ultimate", "Ult", "ult"])
    async def get_ultimate_logs(self, ctx, *, user: discord.Member):
        try:
            await self.display_ultimate_logs(ctx, user.id)
        except TypeError:
            await ctx.send(f"I don't know who that is. Tell them to use {self.bot.command_prefix}iam")

    @get_logs.error
    @get_ultimate_logs.error
    async def logs_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You have to @ someone to get their logs.")

    @commands.command(name="iam")
    async def setup_profile(self, ctx, *, character):
        try:
            # expecting command to be formatted like <first_name last_name server>
            print(character)
            tmp = character.split(" ")
            name = tmp[0] + " " + tmp[1]
            server = tmp[2]
            discord_id = ctx.author.id

            msg = await ctx.send("This will take a few seconds...")
            await self.add_to_db(discord_id, name, server)
        except TypeError:
            await msg.edit(content=f"I couldn't find {name} on {server}")
        except IntegrityError:
            await msg.edit(
                content="Uh oh either you're already in the database or that character is already associated with someone else.")
        except Exception as e:
            await msg.edit(
                content="Couldn't be added. I'll update this to catch specific exceptions later. Enter in shit right next time you fucking monkey.")
            print(f"Error adding a user {e} {type(e)}")
        else:
            await msg.edit(content="User successfully added.")

    @commands.group(name="mylogs", aliases=["ml"], invoke_without_command=True)
    async def get_caller_logs(self, ctx):
        try:
            await self.display_logs(ctx, ctx.author.id)
        except TypeError:
            traceback.print_exc()
            await ctx.send("I don't know who you are. Use #iam to add your character")

    @get_caller_logs.command(name="ultimate", aliases=["Ultimate", "Ult", "ult"])
    async def get_caller_ultimate_logs(self, ctx):
        try:
            await self.display_ultimate_logs(ctx, ctx.author.id)
        except TypeError:
            traceback.print_exc()
            await ctx.send("I don't know who you are. Use #iam to add your character")

    @commands.command(name="add", hidden=True)
    @commands.is_owner()
    async def add_user(self, ctx, *, character):
        try:
            print(character)
            tmp = character.split(" ")
            print(tmp)
            discord_id = int(tmp[0][3:-1])
            name = tmp[1] + " " + tmp[2]
            server = tmp[3]

            msg = await ctx.send("This will take a few seconds...")
            await self.add_to_db(discord_id, name, server)
        except TypeError:
            await msg.edit(content=f"I couldn't find {name} on {server}")
        except Exception as e:
            print(e + " " + type(Exception))
        else:
            await msg.edit(content="User successfully added")

    async def add_to_db(self, discord_id, name, server):
        name = name.lower()
        server = server.lower()

        fflogs_id = await self.helper.get_fflogs_id(name, server)
        lodestone_id = await self.helper.get_lodestone_id(name, server)
        lodestone_data = await self.helper.get_lodestone_data(lodestone_id)

        await self.db.add_user(discord_id, fflogs_id, lodestone_id, lodestone_data)

    @commands.group(name="update")
    async def update(self, ctx):
        pass

    @update.command(name="lodestone")
    async def update_lodestone_cache(self, ctx):
        discord_id = ctx.author.id
        url = "https://media.tenor.com/images/f7b50a770d9db130a0dd297141153e9a/tenor.gif"
        try:
            lodestone_id = await self.db.get_lodestone_id(discord_id)
            msg = await ctx.send("This will take a few seconds...")
            loading_msg = await ctx.send(url)
            lodestone_data = await self.helper.get_lodestone_data(lodestone_id)
            await self.db.update_lodestone_cache(discord_id, lodestone_data)

        except Exception as e:
            print(e)
            await loading_msg.delete()
            await msg.edit(content="I couldn't update your lodestone data")

        else:
            await loading_msg.delete()
            await msg.edit(content="Lodestone data successfully updated")

    @update.command(name="logs")
    async def update_fflogs_cache(self, ctx):
        discord_id = ctx.author.id
        url = "https://media.tenor.com/images/f7b50a770d9db130a0dd297141153e9a/tenor.gif"

        await ctx.send("This command doesn't do anything right now.")

    async def shit_on(self, ctx, logs):
        median_avg = round(logs['data']['characterData']['character']['zoneRankings']['medianPerformanceAverage'], 2)
        best_avg = round(logs['data']['characterData']['character']['zoneRankings']['bestPerformanceAverage'], 2)

        if median_avg < 95.0:
            await ctx.send(f"Median avg: {median_avg}\nYou're fucking shit")
        elif median_avg > 95.0:
            await ctx.send(f"Median avg: {median_avg}\nnice.")
        if best_avg < 95.0:
            await ctx.send(f"Best avg: {best_avg}\nYou're fucking shit")
        elif best_avg > 95.0:
            await ctx.send(f"Best avg: {best_avg}\nnice.")

    @commands.command(name="clown")
    async def clownify(self, ctx, *, user: discord.Member):
        try:
            lodestone_data = await self.db.get_lodestone_cache(user.id)
            character_portrait_url = lodestone_data["Character"]["Avatar"]

            await ctx.send(file=await self.overlay_clown_image(character_portrait_url))
        except TypeError:
            await ctx.send("I don't know who that is. Tell them to use #iam")
        except Exception as e:
            await ctx.send(f"Idk what you did here's the exception message: {e}")
        else:
            await ctx.send(f"<@{user.id}> this is your gray ass")

    @clownify.error
    async def clownify_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("You have to @ someone to clown them.")

    async def overlay_clown_image(self, url):
        buffer = BytesIO()
        img = Image.open(urllib.request.urlopen(url))
        clown_img = Image.open("./pictures/clown.png")

        img.paste(clown_img, (-1, -22), mask=clown_img)
        img.save(buffer, format='PNG')
        buffer.seek(0)
        discord_readable_img = discord.File(buffer, filename="clown.png")

        return discord_readable_img

    async def display_ultimate_logs(self, ctx, discord_id):
        rng = Random()
        color_num = rng.randint(1, 100)
        color = await self.get_color(color_num)

        fflogs_id = await self.db.get_fflogs_id(discord_id)
        lodestone_data = await self.db.get_lodestone_cache(discord_id)

        output = "**__The Unending Coil of Bahamut__**\n"
        output += await self.get_ucob_logs(fflogs_id)
        output += "\n**__The Weapon's Refrain__**\n"
        output += await self.get_uwu_logs(fflogs_id)
        output += "\n**__The Epic of Alexander__**\n"
        output += await self.get_tea_logs(fflogs_id)

        embed = discord.Embed(description=output, color=color)
        embed.set_thumbnail(url=lodestone_data["Character"]["Avatar"])
        embed.set_author(name=lodestone_data["Character"]["Name"], icon_url=lodestone_data["Character"]["Avatar"])

        await ctx.send(embed=embed)

    async def get_ucob_logs(self, fflogs_id):
        output = "\n__Stormblood__\n"

        logs_sb = await self.helper.get_logs_by_encounter(encounter="ucob_sb", id=fflogs_id)
        sb_kills = logs_sb['data']['characterData']['character']['encounterRankings']['totalKills']
        sb_best = await self.get_best_rank(logs_sb['data']['characterData']['character']['encounterRankings']['ranks'])
        sb_median = logs_sb['data']['characterData']['character']['encounterRankings']['medianPerformance']
        if not sb_median:
            sb_median = "-"
        else:
            sb_median = round(sb_median, 2)

        output += f"Best: {sb_best}\n"
        output += f"Median: {sb_median}\n"
        output += f"Kills: {sb_kills}\n"
        output += "\n__Shadowbringers__\n"

        logs_shb = await self.helper.get_logs_by_encounter(encounter="ucob_shb", id=fflogs_id)
        shb_kills = logs_shb['data']['characterData']['character']['encounterRankings']['totalKills']
        shb_best = await self.get_best_rank(
            logs_shb['data']['characterData']['character']['encounterRankings']['ranks'])
        shb_median = logs_shb['data']['characterData']['character']['encounterRankings']['medianPerformance']
        if not shb_median:
            shb_median = "-"
        else:
            shb_median = round(shb_median, 2)

        output += f"Best: {shb_best}\n"
        output += f"Median: {shb_median}\n"
        output += f"Kills: {shb_kills}\n"

        return output

    async def get_uwu_logs(self, fflogs_id):
        output = "\n__Stormblood__\n"

        logs_sb = await self.helper.get_logs_by_encounter(encounter="uwu_sb", id=fflogs_id)
        sb_kills = logs_sb['data']['characterData']['character']['encounterRankings']['totalKills']
        sb_best = await self.get_best_rank(logs_sb['data']['characterData']['character']['encounterRankings']['ranks'])
        sb_median = logs_sb['data']['characterData']['character']['encounterRankings']['medianPerformance']
        if not sb_median:
            sb_median = "-"
        else:
            sb_median = round(sb_median, 2)

        output += f"Best: {sb_best}\n"
        output += f"Median: {sb_median}\n"
        output += f"Kills: {sb_kills}\n"
        output += "\n__Shadowbringers__\n"

        logs_shb = await self.helper.get_logs_by_encounter(encounter="uwu_shb", id=fflogs_id)
        shb_kills = logs_shb['data']['characterData']['character']['encounterRankings']['totalKills']
        shb_best = await self.get_best_rank(
            logs_shb['data']['characterData']['character']['encounterRankings']['ranks'])
        shb_median = logs_shb['data']['characterData']['character']['encounterRankings']['medianPerformance']
        if not shb_median:
            shb_median = "-"
        else:
            shb_median = round(shb_median, 2)

        output += f"Best: {shb_best}\n"
        output += f"Median: {shb_median}\n"
        output += f"Kills: {shb_kills}\n"

        return output

    async def get_tea_logs(self, fflogs_id):
        output = "\n__Shadowbringers__\n"

        logs_shb = await self.helper.get_logs_by_encounter(encounter="tea", id=fflogs_id)
        shb_kills = logs_shb['data']['characterData']['character']['encounterRankings']['totalKills']
        shb_best = await self.get_best_rank(
            logs_shb['data']['characterData']['character']['encounterRankings']['ranks'])
        shb_median = logs_shb['data']['characterData']['character']['encounterRankings']['medianPerformance']
        if not shb_median:
            shb_median = "-"
        else:
            shb_median = round(shb_median, 2)

        output += f"Best: {shb_best}\n"
        output += f"Median: {shb_median}\n"
        output += f"Kills: {shb_kills}\n"

        return output

    async def get_best_rank(self, logs):
        best = 0
        if not logs: return "-"
        for fight in logs:
            rank = fight['rankPercent']
            if rank > best:
                best = rank
        return round(best, 2)

    async def display_logs(self, ctx, discord_id):

        fflogs_id = await self.db.get_fflogs_id(discord_id)
        lodestone_data = await self.db.get_lodestone_cache(discord_id)
        logs = await self.helper.get_main_page_logs(id=fflogs_id)

        median_avg = round(logs['data']['characterData']['character']['zoneRankings']['medianPerformanceAverage'], 2)
        best_avg = round(logs['data']['characterData']['character']['zoneRankings']['bestPerformanceAverage'], 2)
        all_stars_percentile = round(
            logs['data']['characterData']['character']['zoneRankings']['allStars'][0]['rankPercent'], 2)
        encounters = logs['data']['characterData']['character']['zoneRankings']['rankings']

        # formats the logs into a nice string for discord output
        output = "\n\n"
        formatted_data = list()
        prev_week_cleared = None
        # doing it in reverse so that i can find if a fight later in the tier has an older log than earlier fights
        # and setting the earlier fights to be cleared on that week
        for encounter in reversed(encounters):
            name = encounter['encounter']['name']
            best = encounter['rankPercent']
            median = encounter['medianPercent']
            week_cleared = await self.get_week_cleared_on(discord_id, encounter['encounter']['id'],
                                                          release_dates['current_tier'])

            if prev_week_cleared is None: prev_week_cleared = week_cleared
            if week_cleared > prev_week_cleared:
                week_cleared = prev_week_cleared
            else:
                prev_week_cleared = week_cleared

            if best:
                best = round(best, 2)
                median = round(median, 2)
            else:
                best = "-"
                median = "-"

            tmp = f"**__{name}__**\n"
            tmp += f"Best: {best}\n"
            tmp += f"Median: {median}\n"
            tmp += f"Cleared on week {week_cleared}\n\n"

            formatted_data.append(tmp)

        # adding the data in reverse so the fights are in the correct order since previous loop was done in reverse
        for i in reversed(formatted_data):
            output += i

        color = await self.get_color(all_stars_percentile)

        embed = discord.Embed(title=f'Best avg:   {best_avg}\nMedian avg:   {median_avg}',
                              description=output, color=color)
        embed.set_thumbnail(url=lodestone_data["Character"]["Avatar"])
        embed.set_author(name=lodestone_data["Character"]["Name"], icon_url=lodestone_data["Character"]["Avatar"])

        await ctx.send(embed=embed)

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

    async def get_week_cleared_on(self, discord_id, encounter_id, fight_release_date):
        first_e12_kill = await self.get_first_kill_time(discord_id, encounter_id)
        if first_e12_kill:
            week_number = math.ceil((first_e12_kill - fight_release_date) / MS_IN_A_WEEK)
        if not first_e12_kill:
            week_number = "-"

        return week_number

    async def get_first_kill_time(self, discord_id, fight_id):
        fflogs_id = await self.db.get_fflogs_id(discord_id)
        logs = await self.helper.get_logs_by_encounter(encounter_id=fight_id, id=fflogs_id)
        posted_fights = logs['data']['characterData']['character']['encounterRankings']['ranks']

        if posted_fights:  # checks if there are logs
            first_log_time = None
            for fight in posted_fights:
                t = fight['report']['startTime']
                if first_log_time is None:
                    first_log_time = t
                elif t < first_log_time:
                    first_log_time = t
        else:
            first_log_time = 0

        return first_log_time

    def cog_unload(self):
        print("Closing connections")
        try:
            self.db.close()
            self.helper.close_connections()
        except Exception as e:
            print(f"Error closing connections: {e}")
        else:
            print(f"Connection closed successfully")


def setup(bot):
    bot.add_cog(LogShamer(bot))
