#!/bin/bash
# Script de despliegue para EC2 Amazon Linux - Social Content Automation
# Ejecutar como: bash deploy_ec2_amazon_linux.sh

set -e  # Salir si hay algún error

echo "🚀 Iniciando despliegue en EC2 Amazon Linux..."

# Variables
PROJECT_NAME="social-content-automation"
PROJECT_DIR="/home/ec2-user/$PROJECT_NAME"
LOG_DIR="/var/log/$PROJECT_NAME"

# Actualizar sistema
echo "📦 Actualizando sistema..."
sudo yum update -y

# Instalar dependencias del sistema
echo "🔧 Instalando dependencias del sistema..."
sudo yum install -y \
    python3 \
    python3-pip \
    git \
    curl \
    wget \
    unzip \
    gcc \
    python3-devel \
    openssl-devel \
    libffi-devel \
    cronie \
    supervisor

# Habilitar y iniciar cronie
echo "⏰ Configurando cronie..."
sudo systemctl enable crond
sudo systemctl start crond

# Crear directorio del proyecto
echo "📁 Creando directorio del proyecto..."
sudo mkdir -p $PROJECT_DIR
sudo chown ec2-user:ec2-user $PROJECT_DIR

# Crear directorio de logs
echo "📝 Creando directorio de logs..."
sudo mkdir -p $LOG_DIR
sudo chown ec2-user:ec2-user $LOG_DIR

# Clonar repositorio (asumiendo que ya tienes el código)
echo "📥 Copiando código del proyecto..."
# Si tienes el código local, puedes usar scp o rsync
# scp -r . ec2-user@your-ec2-ip:$PROJECT_DIR/

# Instalar pipenv globalmente
echo "🐍 Instalando pipenv..."
pip3 install --user pipenv

# Agregar pipenv al PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Navegar al directorio del proyecto
cd $PROJECT_DIR

# Instalar dependencias del proyecto
echo "📚 Instalando dependencias del proyecto..."
pipenv install --deploy

# Crear archivo .env desde ejemplo
echo "⚙️ Configurando variables de entorno..."
if [ ! -f .env ]; then
    echo "Creando archivo .env..."
    cat > .env << EOF
# Configuración de OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Configuración de Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Configuración de Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret

# Configuración de Google Sheets (opcional)
GOOGLE_SHEETS_CREDENTIALS_FILE=path_to_credentials.json

# Configuración de Canva (opcional)
CANVA_ACCESS_TOKEN=your_canva_access_token

# Configuración de LinkedIn (opcional)
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token

# Configuración de Instagram (opcional)
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# Configuración de logs
LOG_LEVEL=INFO
LOG_FILE=$LOG_DIR/app.log
EOF
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales"
fi

# Crear script de ejecución
echo "📜 Creando script de ejecución..."
cat > run_telegram_content.sh << EOF
#!/bin/bash
# Script para ejecutar el pipeline de contenido de Telegram
# Ejecutar desde cron

cd $PROJECT_DIR
export PATH="\$HOME/.local/bin:\$PATH"

# Activar entorno virtual y ejecutar
pipenv run python run_me_telegram_content.py >> $LOG_DIR/telegram_content.log 2>&1

# Verificar si la ejecución fue exitosa
if [ \$? -eq 0 ]; then
    echo "\$(date): ✅ Ejecución exitosa" >> $LOG_DIR/telegram_content.log
else
    echo "\$(date): ❌ Error en la ejecución" >> $LOG_DIR/telegram_content.log
fi
EOF

chmod +x run_telegram_content.sh

# Configurar cron job
echo "⏰ Configurando cron job..."
CRON_JOB="0 9 * * * $PROJECT_DIR/run_telegram_content.sh"

# Agregar al crontab del usuario ec2-user
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# Crear configuración de supervisor (opcional, para monitoreo)
echo "👀 Configurando supervisor..."
sudo tee /etc/supervisord.d/social-content.ini > /dev/null << EOF
[program:social-content-automation]
command=$PROJECT_DIR/run_telegram_content.sh
directory=$PROJECT_DIR
user=ec2-user
autostart=true
autorestart=true
stderr_logfile=$LOG_DIR/supervisor_err.log
stdout_logfile=$LOG_DIR/supervisor_out.log
EOF

# Reiniciar supervisor
sudo systemctl enable supervisord
sudo systemctl start supervisord
sudo supervisorctl reread
sudo supervisorctl update

echo "✅ Despliegue completado!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Edita el archivo .env con tus credenciales reales"
echo "2. Prueba la conexión: pipenv run python run_me_telegram_content.py --test-connection"
echo "3. Ejecuta una prueba: pipenv run python run_me_telegram_content.py --dry-run"
echo "4. Verifica el cron job: crontab -l"
echo "5. Monitorea los logs: tail -f $LOG_DIR/telegram_content.log"
echo ""
echo "🔧 Comandos útiles:"
echo "- Ver logs: tail -f $LOG_DIR/telegram_content.log"
echo "- Ver cron jobs: crontab -l"
echo "- Editar cron: crontab -e"
echo "- Reiniciar supervisor: sudo supervisorctl restart social-content-automation"
echo "- Estado del sistema: sudo systemctl status crond" 