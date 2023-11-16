import os
from enum import Enum
from time import time
from json import dumps, loads
from secrets import token_urlsafe

import interactions as ipy
from pynng import Pair1
from dotenv import load_dotenv
from interactions import (
    Button,
    ButtonStyle,
    OptionType,
    SlashContext,
    slash_command,
    slash_option,
)

BACKGROUND = 0x2B2D31


class Emoji:
    UPVOTE = "<:thumbup:1108127453840416908>"
    DOWNVOTE = "<:thumbdown:1108127481472487614>"
    WARNING = "<:alerttrianglefilled:1108126642158710845>"
    OPENAI = "<:openai:1108127724620480642>"
    LOADING = "<a:discordloading:1131012007957635123>"


CRYSTAL_LOGO = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGNsYXNzPSJpY29uIGljb24tdGFibGVyIGljb24tdGFibGVyLWRpYW1vbmQiIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZT0iY3VycmVudENvbG9yIiBmaWxsPSJub25lIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiPjxwYXRoIHN0cm9rZT0ibm9uZSIgZD0iTTAgMGgyNHYyNEgweiIgZmlsbD0ibm9uZSI+PC9wYXRoPjxwYXRoIGQ9Ik02IDVoMTJsMyA1bC04LjUgOS41YS43IC43IDAgMCAxIC0xIDBsLTguNSAtOS41bDMgLTUiPjwvcGF0aD48cGF0aCBkPSJNMTAgMTJsLTIgLTIuMmwuNiAtMSI+PC9wYXRoPjwvc3ZnPg=="

load_dotenv()

bot = ipy.Client(token=os.getenv("BOT_TOKEN"))

@slash_command(name="ping")
@slash_option(
    name="echo",
    description="The message to echo",
    opt_type=OptionType.STRING,
    required=False,
)
async def ping(ctx: SlashContext, echo: str = "Pong!"):
    sent_time = ctx.id.created_at
    current_time = ipy.models.Timestamp.now()
    if echo == "Pong!":
        await ctx.send(
            f"Pong! ({(current_time - sent_time).total_seconds() * 1000:.0f}ms)"
        )
        return
    await ctx.send(echo)


@slash_command(name="answer", description="AI answer generation for Star Citizen")
@slash_option(
    name="question",
    description="The question to answer",
    opt_type=OptionType.STRING,
    required=True,
)
async def answer(ctx: SlashContext, question: str):

    qid = token_urlsafe(16)

    msg = await ctx.send(embeds=[ipy.Embed(title="Working on it...", color=BACKGROUND)])

    log = []

    answer = None

    with Pair1(dial="tcp://localhost:23215", polyamorous=True) as s:
        await s.asend(dumps({"query": question, "id": qid, "timestamp": time()}).encode())
        while True:
            data = loads((await s.arecv_msg()).bytes)
            match data:
                case {"update": update}:
                    EMOJI = {"Searching": ":mag:", "Generating Response": ":pencil:"}
                    log.append((EMOJI.get(update, ":book:"), update))
                case {"error": err}:
                    send_error(ctx, err)
                case {"result": result}:
                    answer = result
                    break

            await ctx.edit(
                message=msg,
                embeds=[ipy.Embed(
                    title="Working on it...",
                    color=BACKGROUND,
                    description="\n".join(
                        [
                            f"{emoji} {text}"
                            if i + 1 != len(log)
                            else f"{Emoji.LOADING} {text}"
                            for (i, (emoji, text)) in enumerate(log)
                        ]
                    ),
                )],
            )

    embed = ipy.Embed(
        author=ipy.EmbedAuthor(
            name=question,
            # icon_url=CRYSTAL_LOGO,  # crystal icon
        ),
        description=answer,
        color=BACKGROUND,
    )

    await ctx.edit(message=msg, embeds=[embed], components=get_answer_actions(qid))


async def send_error(ctx: SlashContext, error_desc: str):
    embed = ipy.Embed(
        title=f"{Emoji.WARNING} {error_desc}",
        color=BACKGROUND,
    )
    await ctx.send(embed=embed)


def get_answer_actions(db_id):
    upvote = Button(
        label="‍",  # because discord doesn't like empty labels
        style=ButtonStyle.GREEN,
        emoji=Emoji.UPVOTE,
        custom_id=f"uv_{db_id}",
    )
    downvote = Button(
        label="‍",  # this is a zero width space
        style=ButtonStyle.RED,
        emoji=Emoji.DOWNVOTE,
        custom_id=f"dv_{db_id}",
    )
    return [upvote, downvote]


def update_btns(btns: list[ipy.ActionRow], disabled_btn):
    new_btns = btns[0].components
    for btn in new_btns:
        if btn.custom_id:
            btn.disabled = btn.custom_id[:2] == disabled_btn
    return new_btns


@bot.listen()
async def on_component(event: ipy.api.events.Component):
    ctx: ipy.ComponentContext = event.ctx
    with Pair1(dial="tcp://localhost:23214", polyamorous=True) as s:
        match ctx.custom_id.split("_", 1):
            case ["uv", db_id]:
                print(f"Upvoting {db_id}")
                s.send(dumps({"logs": {"rating": 1}, "id": db_id}).encode())
                await ctx.edit_origin(
                    components=[update_btns(ctx.message.components, "uv")]
                )
            case ["dv", db_id]:
                print(f"Downvoting {db_id}")
                s.send(dumps({"logs": {"rating": -1}, "id": db_id}).encode())
                await ctx.edit_origin(
                    components=[update_btns(ctx.message.components, "dv")]
                )


@bot.listen()
async def on_ready():
    print(f"Ready! Logged in as {bot.user.username} ({bot.user.id})")


print("Starting bot...")
bot.start()
