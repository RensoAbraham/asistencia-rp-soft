"""Utilidades para verificación de permisos"""

from typing import List, Optional
import discord
import logging

from bot.config import Settings, get_settings
from bot.core.exceptions import PermissionError

logger = logging.getLogger(__name__)


async def check_channel_permission(interaction: discord.Interaction) -> bool:
    """
    Verifica si el canal está permitido para el comando
    
    Args:
        interaction: Interacción de Discord
        
    Returns:
        True si el canal está permitido
        
    Raises:
        PermissionError: Si el canal no está permitido
    """
    settings = get_settings()
    guild_id = interaction.guild.id
    channel_id = interaction.channel.id
    
    canales_permitidos = settings.get_canales_permitidos(guild_id)
    
    if channel_id not in canales_permitidos:
        logger.warning(
            f'Canal no permitido para el usuario {interaction.user.display_name} '
            f'en servidor {guild_id}, canal {channel_id}'
        )
        raise PermissionError("Este comando no está habilitado en este canal.")
    
    return True


async def check_role_permission(
    interaction: discord.Interaction,
    allowed_roles: Optional[List[int]] = None,
    use_followup: bool = False
) -> bool:
    """
    Verifica si el usuario tiene alguno de los roles permitidos
    
    Args:
        interaction: Interacción de Discord
        allowed_roles: Lista de IDs de roles permitidos. Si es None o vacía, todos tienen permiso
        use_followup: Si usar followup en lugar de response
        
    Returns:
        True si tiene permisos
        
    Raises:
        PermissionError: Si no tiene permisos
    """
    if not allowed_roles:
        return True
    
    user_roles = [role.id for role in interaction.user.roles]
    has_permission = any(role_id in user_roles for role_id in allowed_roles)
    
    if not has_permission:
        logger.warning(
            f'Usuario {interaction.user.display_name} no tiene los roles necesarios'
        )
        raise PermissionError("No tienes los permisos necesarios para usar este comando.")
    
    return True


