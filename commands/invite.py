import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime, timedelta
from utils.logger import log_action
from typing import Literal

INVITE_FILE = "invites.json"
LOG_CHANNEL_ID = 1468183917562433618

def load_invites():
    try:
        with open(INVITE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            data = json.loads(content)
        if isinstance(data, list):
            data = {}
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_invites(data):
    with open(INVITE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class InviteManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_invites_cache = {}  # Cache de invites por guild

    def make_embed(self, title: str, description: str, color: int):
        return discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )

    # ─────────────── CRIA CONVITE ───────────────
    @app_commands.command(
        name="convite",
        description="Cria um convite para o servidor"
    )
    @app_commands.describe(
        expiracao="Tempo de expiração do invite",
        usos="Quantidade máxima de usos"
    )
    @app_commands.choices(
        expiracao=[
            app_commands.Choice(name="30 minutos", value="30 minutos"),
            app_commands.Choice(name="1 hora", value="1 hora"),
            app_commands.Choice(name="6 horas", value="6 horas"),
            app_commands.Choice(name="12 horas", value="12 horas"),
            app_commands.Choice(name="1 dia", value="1 dia"),
        ],
        usos=[
            app_commands.Choice(name="1", value=1),
            app_commands.Choice(name="5", value=5),
            app_commands.Choice(name="10", value=10),
            app_commands.Choice(name="25", value=25),
            app_commands.Choice(name="50", value=50),
            app_commands.Choice(name="100", value=100),
        ]
    )
    async def create_invite(
        self,
        interaction: discord.Interaction,
        expiracao: Literal["30 minutos", "1 hora", "6 horas", "12 horas", "1 dia"],
        usos: Literal[1, 5, 10, 25, 50, 100]
    ):
        expire_map = {
            "30 minutos": 30*60,
            "1 hora": 60*60,
            "6 horas": 6*60*60,
            "12 horas": 12*60*60,
            "1 dia": 24*60*60
        }

        invite = await interaction.channel.create_invite(
            max_age=expire_map[expiracao],
            max_uses=usos,
            reason=f"Convite criado por {interaction.user}"
        )

        data = load_invites()
        data[invite.code] = {
            "expires_at": str(datetime.utcnow() + timedelta(seconds=expire_map[expiracao])),
            "max_uses": usos
        }
        save_invites(data)

        # Atualiza cache de invites
        await self.update_invite_cache(interaction.guild)

        # ───────── VIEW COM BOTÕES ─────────
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Copiar invite", style=discord.ButtonStyle.link, url=str(invite)))

        async def remove_callback(i: discord.Interaction):
            try:
                await invite.delete()
                data = load_invites()
                if invite.code in data:
                    del data[invite.code]
                    save_invites(data)

                await i.response.send_message(embed=self.make_embed(
                    "✅ Invite removido",
                    f"Invite `{invite.code}` removido por {i.user.mention}",
                    0xE74C3C
                ), ephemeral=True)

                await log_action(
                    self.bot,
                    action="Invite",
                    embed=self.make_embed(
                        "❌ Invite removido",
                        f"👤 Autor: {i.user.mention}\n🔗 Invite: {invite.code}",
                        0xE74C3C
                    )
                )
            except Exception:
                await i.response.send_message("❌ Não foi possível remover o invite", ephemeral=True)

        remove_btn = discord.ui.Button(label="Remover invite", style=discord.ButtonStyle.danger)
        remove_btn.callback = remove_callback
        view.add_item(remove_btn)

        await interaction.response.send_message(
            embed=self.make_embed(
                "✅ Invite criado",
                f"🔗 Invite: {invite}\n⏱ Expira: {expiracao}\n👥 Máx usos: {usos}",
                0x2ECC71
            ),
            view=view,
            ephemeral=True
        )

        await log_action(
            self.bot,
            action="Invite",
            embed=self.make_embed(
                "📢 Invite criado",
                f"👤 Autor: {interaction.user.mention}\n🔗 Invite: {invite.code}\n⏱ Expira: {expiracao}\n👥 Máx usos: {usos}",
                0x2ECC71
            )
        )

    # ─────────────── LISTAR CONVITES ───────────────
    @app_commands.command(name="convite_listar", description="Lista todos os convites criados")
    async def list_invites(self, interaction: discord.Interaction):
        data = load_invites()
        if not data:
            await interaction.response.send_message(embed=self.make_embed(
                "📋 Convites",
                "Nenhum convite salvo.",
                0x3498DB
            ), ephemeral=True)
            return

        embed = discord.Embed(title="📋 Convites salvos", color=0x3498DB, timestamp=datetime.utcnow())
        for code, info in data.items():
            embed.add_field(
                name=f"Invite: {code}",
                value=f"Expira em: {info['expires_at']}\nMáx usos: {info['max_uses']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

        await log_action(
            self.bot,
            action="Invite",
            embed=self.make_embed(
                "📋 Convites listados",
                f"👤 Autor: {interaction.user.mention}\nTotal convites: {len(data)}",
                0x3498DB
            )
        )

    # ─────────────── CACHE DE INVITES ───────────────
    async def update_invite_cache(self, guild: discord.Guild):
        try:
            invites = await guild.invites()
            self.guild_invites_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        except Exception:
            self.guild_invites_cache[guild.id] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.update_invite_cache(guild)

async def setup(bot):
    cog = InviteManager(bot)
    await bot.add_cog(cog)
    await bot.tree.sync()
