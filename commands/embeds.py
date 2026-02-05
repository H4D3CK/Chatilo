import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime
from utils.logger import log_action  # ← ADIÇÃO

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ────────────── EMBED HELPER (JÁ EXISTENTE) ──────────────
    def make_embed(self, title: str, description: str, color: int):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        return embed

    # ────────────── JSON VALIDATOR (ADIÇÃO) ──────────────
    def validate_embed_json(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError("O JSON precisa ser um objeto")

        if "embeds" not in data:
            raise ValueError("Campo obrigatório ausente: `embeds`")

        if not isinstance(data["embeds"], list):
            raise ValueError("`embeds` precisa ser uma lista")

        if not data["embeds"]:
            raise ValueError("A lista `embeds` está vazia")

        for i, embed in enumerate(data["embeds"], start=1):
            if not isinstance(embed, dict):
                raise ValueError(f"Embed #{i} inválido")

            if "title" not in embed and "description" not in embed:
                raise ValueError(f"Embed #{i} precisa de `title` ou `description`")

            if "fields" in embed and not isinstance(embed["fields"], list):
                raise ValueError(f"`fields` do embed #{i} precisa ser uma lista")

    def load_embeds(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ────────────── VALIDAÇÃO (ADIÇÃO) ──────────────
        self.validate_embed_json(data)

        embeds = []
        for e in data.get("embeds", []):
            embed = discord.Embed(
                title=e.get("title"),
                description=e.get("description"),
                color=e.get("color", 0x2F3136)
            )

            for field in e.get("fields", []):
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", False)
                )

            if "footer" in e:
                embed.set_footer(text=e["footer"].get("text"))

            embeds.append(embed)

        if not embeds:
            raise ValueError("Nenhum embed válido")

        return embeds

    # ────────────── SLASH COMMAND ──────────────
    @app_commands.command(name="enviar_embed", description="Envia embed do Discohook")
    async def enviar_embed(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        arquivo: str
    ):
        try:
            embeds = self.load_embeds(f"embeds/{arquivo}.json")
            await canal.send(embeds=embeds)

            await interaction.response.send_message(
                embed=self.make_embed(
                    "✅ Embed enviado",
                    f"Os embeds do arquivo `{arquivo}.json` foram enviados em {canal.mention}.",
                    0x2ECC71
                ),
                ephemeral=True
            )

            # ────────────── LOG SUCESSO (ADIÇÃO) ──────────────
            await log_action(
                self.bot,
                action="EMBED",
                embed=discord.Embed(
                    title="📨 Embed enviado",
                    description=(
                        f"📄 Arquivo: `{arquivo}.json`\n"
                        f"📢 Canal: {canal.mention}\n"
                        f"🛡️ Autor: {interaction.user.mention}\n"
                        f"🧩 Quantidade: {len(embeds)} embeds"
                    ),
                    color=0x2ECC71,
                    timestamp=datetime.utcnow()
                )
            )

        except Exception as e:
            await interaction.response.send_message(
                embed=self.make_embed(
                    "❌ Erro ao enviar embed",
                    str(e),
                    0xE74C3C
                ),
                ephemeral=True
            )

            # ────────────── LOG ERRO (ADIÇÃO) ──────────────
            await log_action(
                self.bot,
                action="EMBED",
                embed=discord.Embed(
                    title="❌ Erro ao enviar embed",
                    description=(
                        f"📄 Arquivo: `{arquivo}.json`\n"
                        f"📢 Canal: {canal.mention}\n"
                        f"🛡️ Autor: {interaction.user.mention}\n\n"
                        f"🧨 Erro:\n```{e}```"
                    ),
                    color=0xE74C3C,
                    timestamp=datetime.utcnow()
                )
            )

async def setup(bot):
    await bot.add_cog(Embeds(bot))
