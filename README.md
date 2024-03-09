# Discord Voice Transcription Bot

This is a Discord bot that transcribes the audio from a discord Voice Channel in real-time using OpenAI's API.

## Environment Variables

The following environment variables need to be set:

- `discord_token`: The Discord bot token.
- `openai_key`: The OpenAI API key.

## Libraries Used

The following libraries are used:

- `discord`: A Python wrapper for the Discord API.
- `openai`: A Python wrapper for the OpenAI API.
- `dotenv`: A Python library for loading environment variables from a `.env` file.

## Commands

The bot has the following commands:

- `/record`: Starts recording audio from the user's voice channel.
- `/stop`: Stops recording audio and transcribing it.
- `/transcribe`: Starts transcribing audio from the user's voice channel continuously.
