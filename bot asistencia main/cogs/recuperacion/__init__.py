"""Módulo de Recuperación - Comandos para gestión de recuperaciones"""

from .commands import Recuperacion

async def setup(bot):
    await bot.add_cog(Recuperacion(bot))


