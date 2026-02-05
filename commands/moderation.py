import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta, datetime
from utils.logger import log_action

COLOR_MUTE = 0xF1C40F
COLOR_KICK = 0xE67E22
COLOR_BAN = 0xC0392B
COLOR_UNMUTE = 0x2ECC71
COLOR_ERROR = 0xE74C3C

def footer_info(user: discord.Member):
    return f"ID: {user.id} • {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}"

def make_embed(title, description, color, user=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if user:
        embed.set_footer(text=footer_info(user))
    return embed

async def send_dm_embed(user, embed):
    try:
        await user.send(embed=embed)
    except discord.Forbidden:
        pass

async def log_embed(bot, action, title, description, color):
    embed = discord.Embed(
        title=f"📋 {title}",
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    await log_action(bot, action=action, embed=embed)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ────────────── MUTE ──────────────
    @app_commands.command(name="mute")
    async def mute(self, interaction: discord.Interaction, membro: discord.Member, minutos: int):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(
                embed=make_embed("❌ Erro", "Sem permissão.", COLOR_ERROR, interaction.user),
                ephemeral=True
            )
            return

        await send_dm_embed(
            membro,
            make_embed(
                "🔇 Você foi mutado",
                f"Servidor: **{interaction.guild.name}**\n"
                f"Duração: **{minutos} minutos**\n"
                f"Moderador: {interaction.user.mention}",
                COLOR_MUTE,
                membro
            )
        )

        await membro.timeout(timedelta(minutes=minutos))

        await interaction.response.send_message(
            embed=make_embed(
                "🔇 Mute aplicado",
                f"{membro.mention} mutado por **{minutos} minutos**.",
                COLOR_MUTE,
                membro
            ),
            ephemeral=True
        )

        await log_embed(
            self.bot,
            "Mute",
            "Mute aplicado",
            f"👤 Alvo: {membro.mention}\n🛡️ Autor: {interaction.user.mention}\n⏱️ Duração: {minutos} minutos",
            COLOR_MUTE
        )

    # ────────────── UNMUTE (CORRIGIDO) ──────────────
    @app_commands.command(name="unmute")
    async def unmute(self, interaction: discord.Interaction, membro: discord.Member):
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message(
                embed=make_embed("❌ Erro", "Sem permissão.", COLOR_ERROR, interaction.user),
                ephemeral=True
            )
            return

        # ✅ DM ANTES de remover o timeout
        await send_dm_embed(
            membro,
            make_embed(
                "🔊 Mute removido",
                f"Servidor: **{interaction.guild.name}**\n"
                f"Moderador: {interaction.user.mention}",
                COLOR_UNMUTE,
                membro
            )
        )

        await membro.timeout(None)

        await interaction.response.send_message(
            embed=make_embed(
                "🔊 Unmute",
                f"{membro.mention} desmutado.",
                COLOR_UNMUTE,
                membro
            ),
            ephemeral=True
        )

        await log_embed(
            self.bot,
            "Unmute",
            "Mute removido",
            f"👤 Alvo: {membro.mention}\n🛡️ Autor: {interaction.user.mention}",
            COLOR_UNMUTE
        )

    # ────────────── KICK ──────────────
    @app_commands.command(name="kick")
    async def kick(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
        await send_dm_embed(
            membro,
            make_embed(
                "👢 Você foi expulso",
                f"Servidor: **{interaction.guild.name}**\nMotivo: {motivo}",
                COLOR_KICK,
                membro
            )
        )

        await membro.kick(reason=motivo)

        await interaction.response.send_message(
            embed=make_embed("👢 Kick", f"{membro} expulso.", COLOR_KICK, membro),
            ephemeral=True
        )

        await log_embed(
            self.bot,
            "Kick",
            "Usuário expulso",
            f"👤 Alvo: {membro}\n🛡️ Autor: {interaction.user.mention}\n📄 Motivo: {motivo}",
            COLOR_KICK
        )

    # ────────────── BAN ──────────────
    @app_commands.command(name="ban")
    async def ban(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Sem motivo"):
        await send_dm_embed(
            membro,
            make_embed(
                "🔨 Você foi banido",
                f"Servidor: **{interaction.guild.name}**\nMotivo: {motivo}",
                COLOR_BAN,
                membro
            )
        )

        await membro.ban(reason=motivo)

        await interaction.response.send_message(
            embed=make_embed("🔨 Ban", f"{membro} banido.", COLOR_BAN, membro),
            ephemeral=True
        )

        await log_embed(
            self.bot,
            "Ban",
            "Usuário banido",
            f"👤 Alvo: {membro}\n🛡️ Autor: {interaction.user.mention}\n📄 Motivo: {motivo}",
            COLOR_BAN
        )

# ────────────── CONTEXT MENU ──────────────
@app_commands.context_menu(name="Timeout 10 minutos")
async def ctx_timeout(interaction: discord.Interaction, membro: discord.Member):
    await send_dm_embed(
        membro,
        make_embed(
            "🔇 Você foi mutado",
            "Duração: **10 minutos**",
            COLOR_MUTE,
            membro
        )
    )

    await membro.timeout(timedelta(minutes=10))

    await interaction.response.send_message(
        embed=make_embed("🔇 Mute", "Mute aplicado por 10 minutos.", COLOR_MUTE, membro),
        ephemeral=True
    )

    await log_embed(
        interaction.client,
        "Mute (Apps)",
        "Mute via Apps",
        f"👤 Alvo: {membro.mention}\n🛡️ Autor: {interaction.user.mention}\n⏱️ Duração: 10 minutos",
        COLOR_MUTE
    )

async def setup(bot):
    await bot.add_cog(Moderation(bot))
    bot.tree.add_command(ctx_timeout)
