# 📚 Documentación - Bot de Asistencia RP Soft

## 🎯 Documentación Principal

### 📖 Para Entender el Bot
- **[DOCUMENTACION_TECNICA.md](./DOCUMENTACION_TECNICA.md)** 
  - Arquitectura completa del sistema
  - Explicación de cada módulo (bot.py, database.py, google_sheets.py, utils.py)
  - Esquema de base de datos
  - Integración con Google Sheets
  - Todos los comandos del bot
  - Guía de modificaciones comunes

### 🚀 Para Desplegar
- **[REQUISITOS_SERVIDOR.md](./REQUISITOS_SERVIDOR.md)** ⭐ **LEER PRIMERO**
  - Lista única de requisitos del servidor VPS
  - Instalar Docker, Git, Firewall, etc.
  - **Hacer UNA SOLA VEZ para todos los proyectos**
  
- **[DEPLOYMENT_HETZNER.md](./DEPLOYMENT_HETZNER.md)**
  - Guía paso a paso para desplegar el bot
  - Comandos de mantenimiento
  - Troubleshooting específico

### 🔄 Para Migrar/Configurar
- **[MIGRACION_MYSQL.md](./MIGRACION_MYSQL.md)**
  - Migrar de TiDB Cloud a MySQL local
  - Dos opciones: Docker o instalación directa
  - Backups automáticos

- **[CREAR_SERVICE_ACCOUNT.md](./CREAR_SERVICE_ACCOUNT.md)**
  - Crear Service Account de Google propio de la empresa
  - Independizarse de cuentas personales
  - Proceso de transición

### 🎓 Para Capacitar
- **[PLAN_CAPACITACION.md](./PLAN_CAPACITACION.md)**
  - Plan completo para enseñar deployment
  - Metodología "Yo hago → Nosotros hacemos → Tú haces"
  - Scripts para cada sesión
  - Tips para enseñar efectivamente

---

## 🚀 Inicio Rápido

### Si eres nuevo:
```
1. Lee DOCUMENTACION_TECNICA.md (30 min)
2. Entiende cómo funciona el bot
3. Si vas a modificar código, revisa los módulos
```

### Si vas a desplegar:
```
1. Lee REQUISITOS_SERVIDOR.md (instalar una vez)
2. Sigue DEPLOYMENT_HETZNER.md paso a paso
3. Verifica que funciona
```

### Si vas a capacitar:
```
1. Lee PLAN_CAPACITACION.md
2. Prepara las guías de cada proyecto
3. Agenda 3 sesiones de capacitación
```

---

## 📋 Archivos de Referencia (No leer primero)

Estos archivos son complementarios o legacy:

- `deploy_vps.md` - Versión anterior de deployment
- `guia_configuracion.md` - Configuración legacy
- `overview.md` - Overview antiguo
- `testing.md` - Guía de testing
- `PLAN_MIGRACION.md` - Plan de migración antiguo
- `PLANTILLA_DEPLOYMENT.md` - Plantilla para otros proyectos (copiar al Desktop)

---

## 🎯 Flujo de Trabajo Recomendado

### Para un Practicante Nuevo:
```
1. DOCUMENTACION_TECNICA.md → Entender el sistema
2. Hacer cambios pequeños
3. Probar localmente
4. Hacer deployment siguiendo DEPLOYMENT_HETZNER.md
```

### Para Deployment de Producción:
```
1. REQUISITOS_SERVIDOR.md → Preparar servidor (una vez)
2. CREAR_SERVICE_ACCOUNT.md → Service Account propio
3. MIGRACION_MYSQL.md → Base de datos local
4. DEPLOYMENT_HETZNER.md → Desplegar bot
5. Verificar funcionamiento
```

### Para Salir de la Empresa:
```
1. CREAR_SERVICE_ACCOUNT.md → Nuevo Service Account
2. PLAN_CAPACITACION.md → Capacitar reemplazo
3. Transferir accesos
4. Documentar todo
5. Verificar independencia
```

---

## 📞 Soporte

**Orden de consulta:**
1. Buscar en DOCUMENTACION_TECNICA.md
2. Revisar troubleshooting de la guía específica
3. Ver logs: `docker-compose logs -f`
4. Contactar al equipo de desarrollo

---

**Última actualización:** 2026-02-10  
**Mantenido por:** Equipo RP Soft
