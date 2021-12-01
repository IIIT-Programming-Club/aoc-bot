import time
import json
import urllib.request

from discord.ext import commands

from builder import make_pages
import utils.paginator as paginator
import config

TOKEN = config.DISCORD_TOKEN
URL = config.AOC_URL
COOKIE = config.AOC_COOKIE
CHANNEL_NAME = config.CHANNEL
PREFIX = config.PREFIX
POLL_MINS = config.POLL_MINS
WAIT_TIME = config.WAIT_TIME

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
                member["name"]
                if member["name"] != None
                else "anon #" + member["id"],
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


@bot.command(name="leaderboard", help="Get the current leaderboard")
async def leaderboard(ctx):

    if not allow_message(ctx):
        return

    print("Leaderboard requested")

    players = get_players()
    pages = make_pages(players, "Leaderboard")
    paginator.paginate(
        bot,
        ctx.channel,
        pages,
        wait_time=WAIT_TIME * 60,
        set_pagenum_footers=True,
    )


@bot.event
async def on_ready():
    print("Ready!")


if __name__ == "__main__":
    bot.run(TOKEN)
