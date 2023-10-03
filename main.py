import asyncio

import discord
import os
import openai
import time

discord_token = os.getenv('discord_token')
openai.api_key = os.getenv('openai_key')
bot = discord.Bot(intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

connections = {}


@bot.command()
async def record(ctx):  # If you're using commands.Bot, this will also work.
    voice = ctx.author.voice
    if not voice:
        await ctx.respond("You aren't in a voice channel!")

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        discord.sinks.WaveSink(),  # The sink type to use.
        once_done,  # What to do once done.
        ctx.channel  # The channel to disconnect from.
    )
    await ctx.respond(f"Started recording at {time.strftime('%I:%M %p',time.localtime())}")


async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()  # Disconnect from the voice channel.
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    for file in files:
        with open(file.filename, 'wb') as f:
            f.write(file.fp.read())
        audio_file = open(file.filename, 'rb')
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        audio_file.close()
        await channel.send(f"<@{file.filename.replace('.wav','')}>: {transcript['text']}")
        os.remove(file.filename)


@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        await ctx.respond(f"Stopped recording at {time.strftime('%I:%M %p',time.localtime())}")
    else:
        await ctx.respond("I am currently not recording here.")  # Respond with this if we aren't recording.




bot.run(discord_token)
