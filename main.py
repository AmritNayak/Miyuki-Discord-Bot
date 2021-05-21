import os
import json
import requests
import random
import discord
from discord.ext import commands
from DiscordMessages import *
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)


def get_day_quote():
    response = requests.get("https://zenquotes.io/api/today")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    author = json_data[0]['a']
    return quote, author


def get_random_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q']
    author = json_data[0]['a']
    return quote, author


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" The Stars"))
    print(f"Logged in as {bot.user.name}\n"
          f"ID: {bot.user.id}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Sorry, Invalid Command Used!",
                              description=f"Please use ( {PREFIX}help ) for available Bot Commands.",
                              color=discord.Color.red())
        await ctx.send(embed=embed)
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(title="Member NOT Found!",
                              description=f"Please check spelling of the user!",
                              color=discord.Color.red())
        await ctx.send(embed=embed)


@bot.event
async def on_guild_join(guild):
    system_channel = guild.system_channel
    if system_channel.permissions_for(guild.me).send_messages:
        await system_channel.send("Warm Greetings...\n\n"
                                  "I am Motivate Bot\n"
                                  "I send inspiring quotes and heartwarming messages\n"
                                  "use this command '^help' for bot instructions\n"
                                  "(under development, more features coming soon...)\n"
                                  "Thank you for having me on your server!\n\n"
                                  "  - Developed by Amrit Nayak")


@bot.event
async def on_member_join(member: discord.Member):
    channel = member.guild.system_channel
    if channel.permissions_for(member.guild.me).send_messages:
        await channel.send(f"Hey, it's great to have you with us! {member.mention} ❤")


@bot.event
async def on_message(message):
    msg = message.content.lower()
    if message.author == bot.user:
        return
    if any(sad_word in msg for sad_word in SAD_TRIGGER) and msg[0] != PREFIX:
        await message.channel.send(random.choice(ENCOURAGING_MSG))
    if any(greet_word in msg for greet_word in GREET_TRIGGER) and msg[0] != PREFIX:
        await message.channel.send(f"{random.choice(GREET_MSG)} {message.author.mention}")

    await bot.process_commands(message)


@bot.command(name="quote", help=" - Quote of The Day!")
async def quote_of_the_day(ctx):
    quote, author = get_day_quote()
    embed = discord.Embed(title="Quote of The Day!",
                          color=discord.Color.gold())
    embed.add_field(name=f'"{quote}"', value=f"- {author}")
    await ctx.send(embed=embed)


@bot.command(name="inspire", help=" - Random Motivational Quote")
async def quote_random(ctx):
    quote, author = get_random_quote()
    embed = discord.Embed(title=f'"{quote}"',
                          description=f"- {author}",
                          color=discord.Color.random())
    await ctx.send(embed=embed)


@bot.command(name="smile", help=" - Sends messages that will make you smile :)")
async def smile_msg(ctx, member: discord.Member = None):
    msg = random.choice(SMILE_MSG)
    if member is None:
        member = ctx.message.author
    await ctx.send(f"{member.mention}\n{msg}")


@bot.command(name="hearten", help=" - Sends Encouraging messages to cheer you up!")
async def motivate_msg(ctx, member: discord.Member = None):
    msg = random.choice(ENCOURAGING_MSG)
    if member is None:
        member = ctx.message.author
    await ctx.send(f"Hey {member.mention}... Cheer up!\n{msg}")


@bot.command(name="info", help=" - Shows Member Info")
async def user_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.guild.get_member(843839492904189952)

    embed = discord.Embed(title="Member Info",
                          description=member.mention,
                          color=discord.Color.random())

    embed.set_thumbnail(url=member.avatar_url)

    fields = [("Name", member.display_name, True),
              ("ID", member.id, True),
              ("Bot", "Yes" if member.bot else "No", True),
              ("Top Role", member.top_role.mention, True),
              ("Status", str(member.status).title(), True),
              ("Activity", f"{str(member.activity.type).split('.')[-1].title() if member.activity else 'No Activity'}"
                           f" {member.activity.name if member.activity else ''}", True),
              ("Created at", member.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
              ("Joined at", member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
              ("Boosted", "Yes" if bool(member.premium_since) else "No", True)]

    for (name, value, inline) in fields:
        embed.add_field(name=name, value=value, inline=inline)

    await ctx.send(embed=embed)


@bot.command(name="server", help=" - Shows Server Info")
async def server_info(ctx):
    embed = discord.Embed(title="Server information",
                          colour=ctx.guild.owner.colour)

    embed.set_thumbnail(url=ctx.guild.icon_url)

    fields = [("Name", ctx.guild.name, True),
              ("ID", ctx.guild.id, True),
              ("\u200b", "\u200b", True),
              ("Owner", ctx.guild.owner, True),
              ("Region", str(ctx.guild.region).title(), True),
              ("Created at", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
              ("Members", len(ctx.guild.members), True),
              ("Humans", len([human for human in ctx.guild.members if not human.bot]), True),
              ("Bots", len([human for human in ctx.guild.members if human.bot]), True),
              ("Text channels", len(ctx.guild.text_channels), True),
              ("Voice channels", len(ctx.guild.voice_channels), True),
              ("\u200b", "\u200b", True),
              ("Categories", len(ctx.guild.categories), True),
              ("Roles", len(ctx.guild.roles), True),
              ("\u200b", "\u200b", True)]

    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)

    embed.set_footer(text="Motivate Bot Developed by - Amrit Nayak")

    await ctx.send(embed=embed)


@bot.command(name="toss", help=" - Toss a coin and sort out the BET!")
async def coin_toss(ctx):
    coin = ["Heads", "Tails"]
    await ctx.send(f"Tossing Coin...\nIt's {random.choice(coin)}!")


@bot.command(name="clear")
async def clear_msg(ctx, amount=5):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"Vanished {amount} messages :)")


bot.run(TOKEN)
