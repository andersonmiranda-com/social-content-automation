# 🚀 Guía de Despliegue en EC2 - Social Content Automation

Esta guía te ayudará a desplegar tu proyecto de automatización de contenido social en un servidor EC2 de AWS y configurarlo para ejecutarse automáticamente con cron.

## 📋 Prerrequisitos

- Una instancia EC2 de Ubuntu (recomendado: t3.medium o superior)
- Acceso SSH a tu instancia EC2
- Tu archivo `.pem` de AWS configurado
- Todas las credenciales de API necesarias

## 🔧 Paso 1: Preparar tu instancia EC2

### 1.1 Conectar a tu instancia EC2

```bash
# Reemplaza con tu IP pública y archivo .pem
ssh -i "tu-archivo.pem" ubuntu@tu-ip-publica-ec2
```

### 1.2 Actualizar el sistema

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

## 📦 Paso 2: Transferir tu código

### Opción A: Usando SCP (desde tu máquina local)

```bash
# Desde tu máquina local, en el directorio del proyecto
scp -i "tu-archivo.pem" -r . ubuntu@tu-ip-publica-ec2:/home/ubuntu/social-content-automation/
```

### Opción B: Usando Git (si tienes un repositorio)

```bash
# En tu instancia EC2
cd /home/ubuntu
git clone https://github.com/tu-usuario/social-content-automation.git
```

## 🚀 Paso 3: Ejecutar el script de despliegue

### 3.1 Dar permisos de ejecución

```bash
cd /home/ubuntu/social-content-automation
chmod +x deploy_ec2.sh
```

### 3.2 Ejecutar el script de despliegue

```bash
./deploy_ec2.sh
```

Este script automáticamente:
- Instala todas las dependencias del sistema
- Configura Python y pipenv
- Instala las dependencias del proyecto
- Crea el archivo `.env` con plantillas
- Configura cron jobs
- Configura supervisor para monitoreo

## ⚙️ Paso 4: Configurar credenciales

### 4.1 Editar el archivo .env

```bash
nano .env
```

Reemplaza todas las variables con tus credenciales reales:

```bash
# Configuración de OpenAI
OPENAI_API_KEY=sk-tu-api-key-real

# Configuración de Telegram
TELEGRAM_BOT_TOKEN=tu-bot-token-real
TELEGRAM_CHAT_ID=tu-chat-id-real

# Configuración de Cloudinary
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-api-key
CLOUDINARY_API_SECRET=tu-api-secret

# ... otras credenciales según necesites
```

## 🧪 Paso 5: Probar la configuración

### 5.1 Probar la conexión de Telegram

```bash
cd /home/ubuntu/social-content-automation
pipenv run python run_me_telegram_content.py --test-connection
```

### 5.2 Ejecutar una prueba en modo dry-run

```bash
pipenv run python run_me_telegram_content.py --dry-run
```

### 5.3 Verificar que el script de ejecución funciona

```bash
./run_telegram_content.sh
```

## ⏰ Paso 6: Configurar cron (si no se configuró automáticamente)

### 6.1 Instalar el cron job

```bash
(crontab -l 2>/dev/null; cat crontab_ec2.txt) | crontab -
```

### 6.2 Verificar que se instaló correctamente

```bash
crontab -l
```

### 6.3 Editar manualmente si es necesario

```bash
crontab -e
```

## 📊 Paso 7: Monitoreo y logs

### 7.1 Ver logs en tiempo real

```bash
tail -f /var/log/social-content-automation/telegram_content.log
```

### 7.2 Ver logs de supervisor

```bash
tail -f /var/log/social-content-automation/supervisor_*.log
```

### 7.3 Verificar estado de supervisor

```bash
sudo supervisorctl status
```

## 🔧 Comandos útiles

### Gestión de cron
```bash
# Ver jobs activos
crontab -l

# Editar jobs
crontab -e

# Eliminar todos los jobs
crontab -r
```

### Gestión de supervisor
```bash
# Ver estado
sudo supervisorctl status

# Reiniciar servicio
sudo supervisorctl restart social-content-automation

# Ver logs
sudo supervisorctl tail social-content-automation
```

### Gestión de logs
```bash
# Ver logs de la aplicación
tail -f /var/log/social-content-automation/telegram_content.log

# Ver logs de errores
tail -f /var/log/social-content-automation/supervisor_err.log

# Limpiar logs antiguos
sudo logrotate -f /etc/logrotate.conf
```

## 🚨 Solución de problemas

### Problema: El script no se ejecuta
```bash
# Verificar permisos
ls -la run_telegram_content.sh

# Verificar que existe
which python3
which pipenv

# Verificar variables de entorno
echo $PATH
```

### Problema: Errores de dependencias
```bash
# Reinstalar dependencias
cd /home/ubuntu/social-content-automation
pipenv install --deploy
```

### Problema: Errores de permisos
```bash
# Corregir permisos
sudo chown -R ubuntu:ubuntu /home/ubuntu/social-content-automation
chmod +x run_telegram_content.sh
```

### Problema: Cron no ejecuta
```bash
# Verificar que cron está corriendo
sudo systemctl status cron

# Verificar logs de cron
sudo tail -f /var/log/syslog | grep CRON
```

## 📅 Programación de cron

### Ejemplos de programación:

```bash
# Todos los días a las 9:00 AM
0 9 * * * /home/ubuntu/social-content-automation/run_telegram_content.sh

# Lunes, miércoles y viernes a las 10:00 AM
0 10 * * 1,3,5 /home/ubuntu/social-content-automation/run_telegram_content.sh

# Cada 6 horas
0 */6 * * * /home/ubuntu/social-content-automation/run_telegram_content.sh

# Solo en días laborables a las 8:00 AM
0 8 * * 1-5 /home/ubuntu/social-content-automation/run_telegram_content.sh
```

## 🔒 Seguridad

### Configurar firewall
```bash
# Permitir solo SSH
sudo ufw allow ssh
sudo ufw enable
```

### Actualizar regularmente
```bash
# Crear script de actualización
sudo crontab -e
# Agregar: 0 2 * * 0 sudo apt-get update && sudo apt-get upgrade -y
```

## 📈 Monitoreo avanzado

### Instalar herramientas de monitoreo
```bash
sudo apt-get install -y htop iotop nethogs
```

### Configurar alertas por email (opcional)
```bash
sudo apt-get install -y mailutils
# Configurar postfix para enviar emails de alerta
```

---

## ✅ Checklist de verificación

- [ ] Instancia EC2 configurada y accesible
- [ ] Código transferido al servidor
- [ ] Script de despliegue ejecutado exitosamente
- [ ] Archivo .env configurado con credenciales reales
- [ ] Prueba de conexión exitosa
- [ ] Prueba dry-run exitosa
- [ ] Cron job configurado y funcionando
- [ ] Logs configurados y accesibles
- [ ] Supervisor configurado (opcional)
- [ ] Firewall configurado
- [ ] Sistema de respaldo configurado (recomendado)

¡Tu automatización de contenido social está lista para ejecutarse en EC2! 🎉 