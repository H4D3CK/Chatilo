import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime
from utils.raw_api import send_raw_v2
from utils.logger import log_action

class Raw(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ────────────── EMBED HELPER ──────────────
    def make_embed(self, title: str, description: str, color: int):
        return discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )

    # ────────────── JSON VALIDATOR (API v10 + COMPONENTS V2) ──────────────
    def validate_payload(self, payload: dict):
        if not isinstance(payload, dict):
            raise ValueError("O payload precisa ser um objeto JSON")

        if not any(k in payload for k in ("content", "embeds", "components")):
            raise ValueError(
                "Payload inválido: é necessário `content`, `embeds` ou `components`"
            )

        if "components" not in payload:
            return  # payload só de texto/embed é válido

        if not isinstance(payload["components"], list):
            raise ValueError("`components` precisa ser uma lista")

        def validate_component(comp, path="components"):
            if "type" not in comp:
                raise ValueError(f"{path} sem campo `type`")

            ctype = comp["type"]

            # ───── CONTAINER (Layout / Components V2) ─────
            if ctype == 17:
                if "components" not in comp or not isinstance(comp["components"], list):
                    raise ValueError(f"{path}: container precisa de `components`")

                for i, child in enumerate(comp["components"]):
                    validate_component(child, f"{path}.components[{i}]")

            # ───── ACTION ROW ─────
            elif ctype == 1:
                if "components" not in comp:
                    raise ValueError(f"{path}: action row sem `components`")

                for i, child in enumerate(comp["components"]):
                    validate_component(child, f"{path}.components[{i}]")

            # ───── BUTTON ─────
            elif ctype == 2:
                if "style" not in comp:
                    raise ValueError(f"{path}: botão sem `style`")

                if comp.get("style") == 5:
                    if "url" not in comp:
                        raise ValueError(f"{path}: botão link precisa de `url`")
                else:
                    if "custom_id" not in comp:
                        raise ValueError(f"{path}: botão precisa de `custom_id`")

            # ───── TEXT ─────
            elif ctype == 10:
                if "content" not in comp:
                    raise ValueError(f"{path}: texto sem `content`")

            # ───── MEDIA ─────
            elif ctype == 12:
                if "items" not in comp:
                    raise ValueError(f"{path}: media sem `items`")

            # ───── DIVIDER ─────
            elif ctype == 14:
                pass  # divider não exige validação extra

            else:
                raise ValueError(f"{path}: tipo não suportado ({ctype})")

        for i, component in enumerate(payload["components"]):
            validate_component(component, f"components[{i}]")

    # ────────────── SLASH COMMAND ──────────────
    @app_commands.command(name="enviar_raw_v2", description="Envia Components V2 RAW")
    async def enviar_raw_v2(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        arquivo: str
    ):
        try:
            with open(f"messages/{arquivo}.json", "r", encoding="utf-8") as f:
                payload = json.load(f)

            # ────────────── VALIDAÇÃO ──────────────
            self.validate_payload(payload)

            send_raw_v2(canal.id, payload)

            await interaction.response.send_message(
                embed=self.make_embed(
                    "✅ RAW enviado",
                    f"Arquivo `{arquivo}.json` enviado em {canal.mention}.",
                    0x2ECC71
                ),
                ephemeral=True
            )

            # ────────────── LOG SUCESSO ──────────────
            await log_action(
                self.bot,
                action="RAW",
                embed=discord.Embed(
                    title="📦 RAW enviado",
                    description=(
                        f"📄 Arquivo: `{arquivo}.json`\n"
                        f"📢 Canal: {canal.mention}\n"
                        f"🛡️ Autor: {interaction.user.mention}"
                    ),
                    color=0x2ECC71,
                    timestamp=datetime.utcnow()
                )
            )

        except Exception as e:
            await interaction.response.send_message(
                embed=self.make_embed(
                    "❌ Erro ao enviar RAW",
                    str(e),
                    0xE74C3C
                ),
                ephemeral=True
            )

            # ────────────── LOG ERRO ──────────────
            await log_action(
                self.bot,
                action="RAW",
                embed=discord.Embed(
                    title="❌ Erro ao enviar RAW",
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
    await bot.add_cog(Raw(bot))
