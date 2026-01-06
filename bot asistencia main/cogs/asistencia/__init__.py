"""Módulo de Asistencia - Comandos para gestión de asistencia"""

from .commands import Asistencia

async def setup(bot):
    await bot.add_cog(Asistencia(bot))


