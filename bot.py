import discord
from discord.ext import commands
import yt_dlp
import dotenv
import json

import os
import discord.opus

if not discord.opus.is_loaded():
    discord.opus.load_opus('/opt/homebrew/lib/libopus.dylib')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user.name}')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Musisz być na kanale głosowym")

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()


@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        await ctx.invoke(bot.get_command("join"))

    # pobierz audio do pliku tymczasowego
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.%(ext)s',
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        title = info.get('title')

    source = discord.FFmpegPCMAudio(file_path)
    ctx.voice_client.play(source, after=lambda e: os.remove(file_path))
    await ctx.send(f"▶️ Odtwarzam: {title}")
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.stop()
        await ctx.send("Bot rozłączony")


@bot.command()
async def create(ctx, name: str, *links):
    if not links:
        ctx.send('Podaj przynajmniej jeden link')
        return
    try:
        with open("playlists.json", "r") as f:
            playlists = json.load(f)
    except FileNotFoundError:
        playlists = {}

    playlists[name] = list(links)
    with open("playlists.json", "w") as f:
        json.dump(playlists, f, indent=2)

    await ctx.send(f"Playlista {name} utworzona. Zapisano {len(links)} utworów.")

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)

