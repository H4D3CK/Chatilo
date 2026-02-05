import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = 797637779332661258

class Waffle(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)

        for ext in (
    		"commands.embeds",
    		"commands.raw",
    		"commands.moderation",
    		"commands.sync",
            "commands.invite",
		):
            await self.load_extension(ext)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("✅ Slash & Apps sincronizados")

bot = Waffle()

@bot.event
async def on_ready():
    print(f"🧇 {bot.user} online")

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="wafflebot-nine.vercel.app"
        )
    )

    # ────────────── ADIÇÃO OBRIGATÓRIA (THREADS DE LOG) ──────────────
    from utils.logger import get_or_create_thread, THREAD_NAMES

    for action in THREAD_NAMES.keys():
        await get_or_create_thread(bot, action)

    print("📋 Threads de log pré-criadas com sucesso")

bot.run(TOKEN)
