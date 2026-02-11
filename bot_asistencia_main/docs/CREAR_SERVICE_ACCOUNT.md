# 🔐 Guía: Crear Service Account de Google para el Bot de Asistencia

## 📋 ¿Por qué necesitamos esto?

El bot usa Google Sheets API para sincronizar datos. Necesitamos crear un **Service Account** propio de la empresa para:
- ✅ Tener control total sobre el acceso
- ✅ No depender de cuentas personales
- ✅ Evitar problemas cuando alguien se retira
- ✅ Mantener la seguridad de los datos

---

## 🎯 Paso 1: Crear Proyecto en Google Cloud

### 1.1 Ir a Google Cloud Console

Abrir: https://console.cloud.google.com/

**Iniciar sesión con la cuenta de Gmail de la empresa** (no personal)

### 1.2 Crear Nuevo Proyecto

1. Click en el selector de proyectos (arriba a la izquierda)
2. Click en **"Nuevo Proyecto"**
3. Configurar:
   - **Nombre del proyecto:** `Bot-Asistencia-RP-Soft`
   - **Organización:** (dejar en blanco si no tienes)
   - **Ubicación:** (dejar en blanco)
4. Click en **"Crear"**
5. Esperar 30 segundos
6. Seleccionar el proyecto recién creado

---

## 🔌 Paso 2: Habilitar APIs Necesarias

### 2.1 Habilitar Google Sheets API

1. En el menú lateral, ir a: **APIs y servicios** → **Biblioteca**
2. Buscar: `Google Sheets API`
3. Click en **Google Sheets API**
4. Click en **"Habilitar"**
5. Esperar a que se active

### 2.2 Habilitar Google Drive API

1. Click en **"Biblioteca"** nuevamente
2. Buscar: `Google Drive API`
3. Click en **Google Drive API**
4. Click en **"Habilitar"**
5. Esperar a que se active

---

## 👤 Paso 3: Crear Service Account

### 3.1 Ir a Credenciales

1. En el menú lateral: **APIs y servicios** → **Credenciales**
2. Click en **"+ Crear credenciales"** (arriba)
3. Seleccionar: **"Cuenta de servicio"**

### 3.2 Configurar Service Account

**Paso 1 de 3: Detalles de la cuenta de servicio**
- **Nombre de la cuenta de servicio:** `bot-asistencia-rp-soft`
- **ID de la cuenta de servicio:** (se genera automáticamente)
- **Descripción:** `Service Account para el bot de asistencia de Discord`
- Click en **"Crear y continuar"**

**Paso 2 de 3: Otorgar acceso**
- **Seleccionar una función:** Dejar en blanco o seleccionar "Editor"
- Click en **"Continuar"**

**Paso 3 de 3: Otorgar acceso a usuarios**
- Dejar en blanco
- Click en **"Listo"**

---

## 🔑 Paso 4: Generar Clave JSON

### 4.1 Crear Clave

1. En la lista de cuentas de servicio, encontrar la que acabas de crear
2. Click en el **email** de la cuenta (algo como `bot-asistencia-rp-soft@proyecto.iam.gserviceaccount.com`)
3. Ir a la pestaña **"Claves"**
4. Click en **"Agregar clave"** → **"Crear clave nueva"**
5. Seleccionar tipo: **JSON**
6. Click en **"Crear"**

### 4.2 Guardar el Archivo

- Se descargará automáticamente un archivo `.json`
- **⚠️ IMPORTANTE:** Este archivo contiene credenciales sensibles
- Renombrar el archivo a: `credentials.json`
- **NO compartir este archivo públicamente**
- **NO subirlo a GitHub**

---

## 📊 Paso 5: Compartir Google Sheet con el Service Account

### 5.1 Copiar Email del Service Account

Del archivo `credentials.json` que descargaste, buscar la línea:
```json
"client_email": "bot-asistencia-rp-soft@proyecto-123456.iam.gserviceaccount.com"
```

Copiar ese email completo.

### 5.2 Compartir la Hoja de Cálculo

1. Abrir tu Google Sheet: `Practicantes_RP_Soft`
2. Click en **"Compartir"** (arriba a la derecha)
3. Pegar el email del Service Account
4. Permisos: **"Editor"**
5. **Desmarcar** "Notificar a las personas"
6. Click en **"Compartir"**

---

## 🚀 Paso 6: Actualizar el Bot

### 6.1 Reemplazar credentials.json

**En tu PC local:**
```powershell
# Ir al directorio del bot
cd "C:\Users\Renso Abraham\Desktop\Rp Soft\Sala 4 6to\Bots discord\bot_asistencia_main"

# Hacer backup del anterior
mv credentials.json credentials.json.backup

# Copiar el nuevo archivo descargado
# (Arrastrarlo a la carpeta o copiarlo manualmente)
```

**En el VPS:**
```bash
# Conectar al VPS
ssh root@tu_ip_vps

# Ir al directorio del bot
cd ~/bot_asistencia

# Hacer backup del anterior
mv credentials.json credentials.json.backup

# Subir el nuevo desde tu PC
# Desde PowerShell en tu PC:
scp credentials.json root@tu_ip_vps:~/bot_asistencia/
```

### 6.2 Reiniciar el Bot

```bash
# En el VPS
cd ~/bot_asistencia

# Reiniciar
docker-compose restart

# Ver logs para verificar
docker-compose logs -f

# Deberías ver:
# "✅ Leídos X practicantes de Google Sheets"
# "📊 Reportes actualizados"
```

---

## ✅ Verificación

### Probar Sincronización

1. Esperar 10 minutos (intervalo de sincronización automática)
2. O forzar sincronización en Discord: `/admin sincronizar`
3. Verificar en Google Sheets que aparecen las hojas:
   - `Reporte Detallado`
   - `Resumen General`
   - `Reporte Anti-Farming`

### Ver Logs

```bash
# En el VPS
docker-compose logs google_sheets

# Buscar líneas como:
# "✅ Leídos 29 practicantes de Google Sheets"
# "📊 Reportes actualizados: 'Reporte Detallado' (119 filas)"
```

---

## 🔒 Seguridad y Buenas Prácticas

### ✅ Hacer

- ✅ Usar una cuenta de Gmail de la empresa (no personal)
- ✅ Guardar `credentials.json` en un lugar seguro
- ✅ Hacer backup del archivo
- ✅ Documentar el email del Service Account
- ✅ Revisar periódicamente los permisos en Google Cloud

### ❌ NO Hacer

- ❌ Compartir el archivo `credentials.json` públicamente
- ❌ Subirlo a GitHub o repositorios públicos
- ❌ Usar tu cuenta personal de Google
- ❌ Dar más permisos de los necesarios
- ❌ Compartir el Service Account con servicios externos

---

## 🆘 Troubleshooting

### Error: "SpreadsheetNotFound"

**Causa:** El Service Account no tiene acceso a la hoja.

**Solución:**
1. Verificar que compartiste la hoja con el email correcto
2. Verificar que el nombre en `.env` coincide: `GOOGLE_SHEET_NAME=Practicantes_RP_Soft`
3. Verificar que el Service Account tiene permisos de "Editor"

### Error: "Insufficient Permission"

**Causa:** APIs no habilitadas o permisos incorrectos.

**Solución:**
1. Verificar que Google Sheets API está habilitada
2. Verificar que Google Drive API está habilitada
3. Volver a compartir la hoja con permisos de "Editor"

### Error: "Invalid credentials"

**Causa:** Archivo `credentials.json` corrupto o incorrecto.

**Solución:**
1. Descargar nuevamente la clave desde Google Cloud Console
2. Verificar que el archivo es JSON válido
3. Reemplazar el archivo en el bot
4. Reiniciar: `docker-compose restart`

---

## 📝 Información para Documentar

**Guardar esta información en un lugar seguro:**

```
Proyecto Google Cloud: Bot-Asistencia-RP-Soft
Service Account Email: bot-asistencia-rp-soft@proyecto-123456.iam.gserviceaccount.com
Cuenta de Google usada: email@rpsoft.com
Fecha de creación: 2026-02-10
Google Sheet vinculado: Practicantes_RP_Soft
```

---

## 🔄 Proceso de Transición (Para el practicante que se retira)

### Antes de retirarte:

1. ✅ Crear nuevo Service Account (esta guía)
2. ✅ Compartir Google Sheet con el nuevo Service Account
3. ✅ Actualizar `credentials.json` en el bot
4. ✅ Verificar que funciona correctamente
5. ✅ Documentar todo el proceso
6. ✅ Capacitar al siguiente encargado

### Después de verificar que funciona:

1. ✅ Eliminar tu Service Account antiguo
2. ✅ Revocar acceso de tu cuenta personal a Google Cloud
3. ✅ Eliminar el proyecto de tu Google Cloud (si lo creaste tú)

---

## 📞 Contacto y Soporte

Si tienes problemas durante el proceso:
1. Revisar esta guía paso a paso
2. Verificar los logs del bot: `docker-compose logs -f`
3. Consultar la documentación técnica en `docs/DOCUMENTACION_TECNICA.md`

---

**Última actualización:** 2026-02-10
**Autor:** Equipo RP Soft
**Propósito:** Independizar el bot de cuentas personales
