import discord
import subprocess
import shlex
import asyncio
import re
import datetime

TOKEN = os.getenv("TOKEN")
COMMAND_PREFIX = '!'

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

MAX_OUTPUT_LENGTH = 1800  # Limit for Discord messages

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

def is_safe_command(command_str):
    # Reject dangerous shell characters
    return not re.search(r'[|&;><$`\\]', command_str)

@client.event
async def on_ready():
    log(f"✅ Bot is online as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(f'{COMMAND_PREFIX}nmap'):
        user = f"{message.author.name}#{message.author.discriminator}"
        raw_command = message.content[len(f'{COMMAND_PREFIX}nmap '):].strip()
        log(f"📥 Received Nmap command from {user}: {raw_command}")

        if not raw_command:
            await message.channel.send("❗ Please provide a valid Nmap command.")
            log("⚠️ Empty command received.")
            return

        if not is_safe_command(raw_command):
            await message.channel.send("🛑 Command contains disallowed characters like `|`, `&`, `;`, etc.")
            log(f"🚫 Rejected unsafe command from {user}: {raw_command}")
            return

        loading_msg = await message.channel.send("🛰️ Launching scan with Nmap... stand by~ 🐸💻")

        try:
            command_args = shlex.split(raw_command)
            full_command = ['./nmap.AppImage'] + command_args
            log(f"🚀 Running command: {' '.join(full_command)}")

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
                log("⚠️ No output from Nmap.")

            if len(output) > MAX_OUTPUT_LENGTH:
                output = output[:MAX_OUTPUT_LENGTH] + "\n\n📉 Output truncated..."

            formatted_output = f"```ansi\n[0;32m{output}\n```"  # Green text for Discord

            await loading_msg.edit(content="✅ Nmap scan complete!\n" + formatted_output)
            log(f"📤 Scan result sent to Discord channel by {user}")

        except Exception as e:
            error_msg = f"❌ Error while running scan: `{e}`"
            await loading_msg.edit(content=error_msg)
            log(f"🔥 Exception while scanning: {e}")
