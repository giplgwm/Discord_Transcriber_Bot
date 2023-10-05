import asyncio
import discord
import os
import openai
import time
from dotenv import load_dotenv

load_dotenv()
discord_token = os.getenv('discord_token')
openai.api_key = os.getenv('openai_key')
bot = discord.Bot(intents=discord.Intents.all())
transcribing = False
connections = {}


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


async def files_to_text(files, channel):
    for file in files:
        with open(file.filename, 'wb') as f:
            f.write(file.fp.read())
        with open(file.filename, 'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        await channel.send(f"<@{file.filename.replace('.wav','')}>: {transcript['text']}")


@bot.command()
async def record(ctx):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice
    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(discord.sinks.WaveSink(), once_done, ctx.channel)
    await ctx.respond(f"Started recording at {time.strftime('%I:%M %p',time.localtime())}")


async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    # await sink.vc.disconnect()  # Disconnect from the voice channel.
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    await files_to_text(files, channel)
    for file in files:
        os.remove(file.filename)


@bot.command()
async def stop(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        if transcribing:
            del connections[ctx.guild.id]
            await ctx.respond(f"Stopped recording at {time.strftime('%I:%M %p',time.localtime())}")
            return
        vc = connections[ctx.guild.id]
        try:
            vc.stop_recording()  # Stop recording, and call the callback (once_done).
        except discord.sinks.errors.RecordingException:
            pass 
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        await vc.disconnect()
        await ctx.respond(f"Stopped recording at {time.strftime('%I:%M %p',time.localtime())}")
    else:
        await ctx.respond("I am currently not recording here.")  # Respond with this if we aren't recording.


@bot.command()
async def transcribe(ctx):
    transcribing = True
    voice = ctx.author.voice
    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    await ctx.respond(f"Transcription begins at: {time.strftime('%I:%M %p',time.localtime())}")

    while vc.guild.id in connections:
        vc.start_recording(discord.sinks.WaveSink(), once_done, ctx.channel)
        if vc.guild.id in connections:
            await asyncio.sleep(15)
        else: break
        if vc.guild.id in connections:
            try:
                vc.stop_recording()  # Stop recording, and call the callback (once_done).
            except discord.sinks.errors.RecordingException:
                pass
        else: break
        if vc.guild.id in connections: #Checking again becauseit may have been changed and we dont need to sleep if it has
            await asyncio.sleep(2)
        else: break
    await vc.disconnect()
    transcribing = False


bot.run(discord_token)
