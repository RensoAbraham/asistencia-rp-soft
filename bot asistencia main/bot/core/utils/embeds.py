"""Utilidades para crear embeds de Discord"""

from typing import Optional
from discord import Embed, Color

from bot.config.constants import MSG_CONTACTO_ADMIN


def create_success_embed(
    title: str,
    description: str,
    footer: Optional[str] = None
) -> Embed:
    """Crea un embed de éxito (verde)"""
    embed = Embed(
        title=f"✅ {title}",
        description=description,
        color=Color.green()
    )
    embed.set_footer(text=footer or MSG_CONTACTO_ADMIN)
    return embed


def create_error_embed(
    title: str,
    description: str,
    footer: Optional[str] = None
) -> Embed:
    """Crea un embed de error (rojo)"""
    embed = Embed(
        title=f"❌ {title}",
        description=description,
        color=Color.red()
    )
    embed.set_footer(text=footer or MSG_CONTACTO_ADMIN)
    return embed


def create_warning_embed(
    title: str,
    description: str,
    footer: Optional[str] = None
) -> Embed:
    """Crea un embed de advertencia (naranja)"""
    embed = Embed(
        title=f"⚠️ {title}",
        description=description,
        color=Color.orange()
    )
    embed.set_footer(text=footer or MSG_CONTACTO_ADMIN)
    return embed


def create_info_embed(
    title: str,
    description: str,
    color: Color = Color.blue(),
    footer: Optional[str] = None
) -> Embed:
    """Crea un embed informativo"""
    embed = Embed(
        title=title,
        description=description,
        color=color
    )
    embed.set_footer(text=footer or MSG_CONTACTO_ADMIN)
    return embed


