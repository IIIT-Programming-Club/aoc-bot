import time
import json
import urllib.request
import config

from discord.ext import commands

TOKEN = config.DISCORD_TOKEN
URL = config.AOC_URL
COOKIE = config.AOC_COOKIE
CHANNEL_NAME = config.CHANNEL
PREFIX = config.PREFIX
POLL_MINS = config.POLL_MINS

players_cache = ()
bot = commands.Bot(command_prefix=PREFIX)


def allow_message(ctx):
    if CHANNEL_NAME not in ctx.channel.name:
        return False
    return True


def get_players():
    global players_cache
    now = time.time()

    # If the cache is more than POLL_MINS old, refresh the cache, else use the cache
    if not players_cache or (now - players_cache[0]) > (60 * POLL_MINS):
        print("Cache expired. Getting new leaderboard.")

        req = urllib.request.Request(URL)
        req.add_header("Cookie", "session=" + COOKIE)
        page = urllib.request.urlopen(req).read()

        data = json.loads(page)

        players = [
            (
                member["name"],
                member["local_score"],
                member["stars"],
                int(member["last_star_ts"]),
                member["completion_day_level"],
                member["id"],
            )
            for member in data["members"].values()
        ]

        # Sort the table primarily by score, secondly by stars and finally by timestamp
        players.sort(key=lambda tup: (tup[1], tup[2], -tup[3]), reverse=True)
        players_cache = (now, players)
    else:
        print("Using Cached Leaderboard.")

    return players_cache[1]


async def output_leaderboard(context, leaderboard_lst):
    await context.send(leaderboard_lst[:1])


@bot.command(name="leaderboard", help="Get the current leaderboard")
async def leaderboard(context):

    if not allow_message(context):
        return

    print("Leaderboard requested")
    players = get_players()
    await output_leaderboard(context, players)


@bot.event
async def on_ready():
    print("Ready!")


if __name__ == "__main__":
    bot.run(TOKEN)
