import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from utils.logger import log_action  # ← ADIÇÃO (já existente no projeto)

class Sync(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="sync",
        description="Sincroniza os comandos Slash e Apps sem reiniciar o bot"
    )
    async def sync(self, interaction: discord.Interaction):
        # ────────────── PERMISSÃO ──────────────
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Permissão negada",
                    description="Apenas administradores podem usar este comando.",
                    color=0xE74C3C,
                    timestamp=datetime.utcnow()
                ),
                ephemeral=True
            )
            return

        try:
            synced = await self.bot.tree.sync()

            # ────────────── RESPOSTA AO USUÁRIO ──────────────
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="✅ Sincronização concluída",
                    description=f"**{len(synced)} comandos** foram sincronizados com sucesso.",
                    color=0x2ECC71,
                    timestamp=datetime.utcnow()
                ),
                ephemeral=True
            )

            # ────────────── LOG AUTOMÁTICO (ADIÇÃO) ──────────────
            await log_action(
                self.bot,
                action="DEFAULT",
                embed=discord.Embed(
                    title="🔄 Sync executado",
                    description=(
                        f"🛡️ **Autor:** {interaction.user.mention}\n"
                        f"📦 **Comandos sincronizados:** {len(synced)}\n"
                        f"🏷️ **Guild:** {interaction.guild.name} (`{interaction.guild.id}`)"
                    ),
                    color=0x3498DB,
                    timestamp=datetime.utcnow()
                )
            )

        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Erro ao sincronizar",
                    description=f"```{e}```",
                    color=0xE74C3C,
                    timestamp=datetime.utcnow()
                ),
                ephemeral=True
            )

            # ────────────── LOG DE ERRO (ADIÇÃO) ──────────────
            await log_action(
                self.bot,
                action="DEFAULT",
                embed=discord.Embed(
                    title="❌ Erro no /sync",
                    description=(
                        f"🛡️ **Autor:** {interaction.user.mention}\n"
                        f"🏷️ **Guild:** {interaction.guild.name} (`{interaction.guild.id}`)\n\n"
                        f"🧨 **Erro:**\n```{e}```"
                    ),
                    color=0xE74C3C,
                    timestamp=datetime.utcnow()
                )
            )

async def setup(bot):
    await bot.add_cog(Sync(bot))
