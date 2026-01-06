"""Módulo de Faltas - Comandos para gestión de faltas"""

from .commands import Faltas

async def setup(bot):
    await bot.add_cog(Faltas(bot))


