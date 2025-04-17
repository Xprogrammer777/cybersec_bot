import discord
import subprocess
import shlex
import asyncio
import re

TOKEN = TOKEN
COMMAND_PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

MAX_OUTPUT_LENGTH = 1800

def is_safe_command(command_str):
    return not re.search(r'[|&;><$`\\]', command_str)

@client.event
async def on_ready():
    print(f"🌐 CyberBot is online as {client.user}!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(f'{COMMAND_PREFIX}nmap'):
        raw_command = message.content[len(f'{COMMAND_PREFIX}nmap '):].strip()

        if not raw_command:
            await message.channel.send("❗ Please provide a valid Nmap command.")
            return

        if not is_safe_command(raw_command):
            await message.channel.send("🛑 Command contains disallowed characters like `|`, `&`, `;`, etc.")
            return

        loading_msg = await message.channel.send("🛰️ Launching...")

        try:
            command_args = shlex.split(raw_command)
            full_command = ['./nmap.AppImage'] + command_args

            # Run the command
            process = await asyncio.create_subprocess_exec(
                *full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            output = stdout.decode() or stderr.decode()
            output = output.strip()

            if not output:
                output = "⚠️ No output received."

            if len(output) > MAX_OUTPUT_LENGTH:
                output = output[:MAX_OUTPUT_LENGTH] + "\n\n📉 Output truncated..."

            formatted_output = f"```ansi\n[0;32m{output}\n```"  # Discord green via ANSI

            await loading_msg.edit(content="✅ Nmap scan complete\n" + formatted_output)

        except Exception as e:
            await loading_msg.edit(content=f"❌ Error while running scan: `{e}`")

