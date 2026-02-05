import os
import discord
from datetime import datetime
from urllib.parse import urlparse

# ────────────── LOAD ENV ──────────────
LOG_WEBHOOK_URL = os.getenv("LOG_WEBHOOK_URL")
LOG_WEBHOOK_MUTE = os.getenv("LOG_WEBHOOK_MUTE")
LOG_WEBHOOK_KICK = os.getenv("LOG_WEBHOOK_KICK")
LOG_WEBHOOK_BAN = os.getenv("LOG_WEBHOOK_BAN")
LOG_WEBHOOK_UNMUTE = os.getenv("LOG_WEBHOOK_UNMUTE")
LOG_WEBHOOK_DEFAULT = os.getenv("LOG_WEBHOOK_DEFAULT")

# ────────────── LOG CHANNEL ──────────────
LOG_CHANNEL_ID = 1468183917562433618

# ────────────── THREADS FIXAS ──────────────
THREAD_NAMES = {
    "Mute": "🔇 logs-mute",
    "Mute (Apps)": "🔇 logs-mute",
    "Unmute": "🔊 logs-unmute",
    "Kick": "👢 logs-kick",
    "Ban": "🔨 logs-ban",
    "DEFAULT": "📋 logs-geral"
}

WEBHOOKS = {
    "Mute": LOG_WEBHOOK_MUTE or LOG_WEBHOOK_URL,
    "Mute (Apps)": LOG_WEBHOOK_MUTE or LOG_WEBHOOK_URL,
    "Unmute": LOG_WEBHOOK_UNMUTE or LOG_WEBHOOK_URL,
    "Kick": LOG_WEBHOOK_KICK or LOG_WEBHOOK_URL,
    "Ban": LOG_WEBHOOK_BAN or LOG_WEBHOOK_URL,
    "DEFAULT": LOG_WEBHOOK_DEFAULT or LOG_WEBHOOK_URL
}

# ────────────── VALIDATION ──────────────
def is_valid_webhook(url: str | None) -> bool:
    if not url:
        return False
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ("http", "https")
            and "discord.com" in parsed.netloc
            and "/api/webhooks/" in parsed.path
        )
    except Exception:
        return False

# ────────────── THREAD MANAGER ──────────────
async def get_or_create_thread(bot, action: str):
    try:
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel is None:
            channel = await bot.fetch_channel(LOG_CHANNEL_ID)

        if not isinstance(channel, discord.TextChannel):
            return None

        thread_name = THREAD_NAMES.get(action, THREAD_NAMES["DEFAULT"])

        # procura thread existente
        for thread in channel.threads:
            if thread.name == thread_name:
                return thread

        # cria se não existir
        return await channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.public_thread,
            auto_archive_duration=10080  # 7 dias
        )

    except Exception:
        return None

# ────────────── MAIN LOGGER ──────────────
async def log_action(bot, *, action: str = "DEFAULT", embed: discord.Embed):
    # ────────────── 1️⃣ LOG VIA CANAL (THREAD FIXA) ──────────────
    try:
        thread = await get_or_create_thread(bot, action)
        if thread:
            await thread.send(embed=embed)
    except Exception:
        pass  # nunca quebra comando

    # ────────────── 2️⃣ LOG VIA WEBHOOK ──────────────
    try:
        webhook_url = WEBHOOKS.get(action)

        if not is_valid_webhook(webhook_url):
            webhook_url = WEBHOOKS.get("DEFAULT")

        if not is_valid_webhook(webhook_url):
            return

        webhook = discord.Webhook.from_url(
            webhook_url,
            client=bot.http._HTTPClient__session
        )

        await webhook.send(
            embed=embed,
            username="Mod Logs"
        )

    except Exception:
        pass  # webhook nunca pode derrubar comando
