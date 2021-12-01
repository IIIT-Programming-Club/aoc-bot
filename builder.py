from utils import paginator
from utils import table
import discord

LEADERBOARD_COLOR = 0x28A745
PLAYERS_PER_PAGE = 15
NAME_MAX_SIZE = 20
TABLE_STYLE = "{:>}  {:<}  {:>}  {:>}"


def get_colored_embed(**kwargs):
    return discord.Embed(**kwargs, color=LEADERBOARD_COLOR)


def make_embed(chunk, curr):
    style = table.Style(TABLE_STYLE)
    t = table.Table(style)
    t += table.Header("#", "Name", "Score", "Stars")
    t += table.Line()

    i = 0
    for name, score, stars, _, _, _ in chunk:
        normalized_name = name
        if len(name) > NAME_MAX_SIZE:
            normalized_name = name[: NAME_MAX_SIZE - 1] + "…"

        t += table.Data(curr + i, normalized_name, score, stars)
        i += 1

    table_str = "```\n" + str(t) + "\n```"
    embed = get_colored_embed(description=table_str)
    return embed


def make_pages(players, title):
    pages = []

    chunks = paginator.chunkify(players, PLAYERS_PER_PAGE)
    curr = 0
    for chunk in chunks:
        embed = make_embed(chunk, curr)
        curr += len(chunk)
        pages.append((title, embed))
    return pages
