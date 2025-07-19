#!/bin/bash
# Script de monitoreo para Social Content Automation en Amazon Linux
# Ejecutar: ./monitoring_script_amazon_linux.sh

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR="/home/ec2-user/social-content-automation"
LOG_DIR="/var/log/social-content-automation"
LOG_FILE="$LOG_DIR/telegram_content.log"

echo -e "${BLUE}🔍 Monitoreo del Sistema - Social Content Automation (Amazon Linux)${NC}"
echo "=================================================="
echo ""

# Función para imprimir estado
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "OK" ]; then
        echo -e "${GREEN}✅ $message${NC}"
    elif [ "$status" = "WARNING" ]; then
        echo -e "${YELLOW}⚠️  $message${NC}"
    else
        echo -e "${RED}❌ $message${NC}"
    fi
}

# 1. Verificar que el directorio del proyecto existe
echo -e "${BLUE}📁 Verificando estructura del proyecto...${NC}"
if [ -d "$PROJECT_DIR" ]; then
    print_status "OK" "Directorio del proyecto existe: $PROJECT_DIR"
else
    print_status "ERROR" "Directorio del proyecto no existe: $PROJECT_DIR"
    exit 1
fi

# 2. Verificar archivo .env
echo ""
echo -e "${BLUE}⚙️  Verificando configuración...${NC}"
if [ -f "$PROJECT_DIR/.env" ]; then
    print_status "OK" "Archivo .env encontrado"
    
    # Verificar si tiene credenciales reales (no placeholder)
    if grep -q "your_openai_api_key_here" "$PROJECT_DIR/.env"; then
        print_status "WARNING" "Archivo .env tiene valores placeholder - configurar credenciales reales"
    else
        print_status "OK" "Archivo .env parece tener credenciales configuradas"
    fi
else
    print_status "ERROR" "Archivo .env no encontrado"
fi

# 3. Verificar dependencias
echo ""
echo -e "${BLUE}🐍 Verificando Python y dependencias...${NC}"
if command -v python3 &> /dev/null; then
    print_status "OK" "Python3 instalado: $(python3 --version)"
else
    print_status "ERROR" "Python3 no encontrado"
fi

if command -v pipenv &> /dev/null; then
    print_status "OK" "Pipenv instalado: $(pipenv --version)"
else
    print_status "ERROR" "Pipenv no encontrado"
fi

# 4. Verificar entorno virtual
echo ""
echo -e "${BLUE}🔧 Verificando entorno virtual...${NC}"
cd "$PROJECT_DIR"
if [ -f "Pipfile.lock" ]; then
    print_status "OK" "Pipfile.lock encontrado"
    
    # Verificar si el entorno virtual existe
    if pipenv --venv &> /dev/null; then
        print_status "OK" "Entorno virtual activo"
    else
        print_status "WARNING" "Entorno virtual no encontrado - ejecutar: pipenv install"
    fi
else
    print_status "ERROR" "Pipfile.lock no encontrado"
fi

# 5. Verificar cron jobs (cronie en Amazon Linux)
echo ""
echo -e "${BLUE}⏰ Verificando cron jobs...${NC}"
if command -v crontab &> /dev/null; then
    CRON_JOBS=$(crontab -l 2>/dev/null | grep -c "social-content-automation" || echo "0")
    if [ "$CRON_JOBS" -gt 0 ]; then
        print_status "OK" "Cron jobs configurados: $CRON_JOBS job(s)"
        echo "Jobs activos:"
        crontab -l 2>/dev/null | grep "social-content-automation" || echo "  Ninguno encontrado"
    else
        print_status "WARNING" "No se encontraron cron jobs para social-content-automation"
    fi
else
    print_status "ERROR" "Cron no disponible"
fi

# 6. Verificar estado del servicio cronie
echo ""
echo -e "${BLUE}🔄 Verificando servicio cronie...${NC}"
if sudo systemctl is-active --quiet crond; then
    print_status "OK" "Servicio cronie ejecutándose"
else
    print_status "WARNING" "Servicio cronie no ejecutándose"
    echo "  Para iniciar: sudo systemctl start crond"
fi

# 7. Verificar supervisor
echo ""
echo -e "${BLUE}👀 Verificando supervisor...${NC}"
if command -v supervisorctl &> /dev/null; then
    print_status "OK" "Supervisor instalado"
    
    # Verificar estado del servicio
    if sudo supervisorctl status social-content-automation &> /dev/null; then
        SERVICE_STATUS=$(sudo supervisorctl status social-content-automation | awk '{print $2}')
        if [ "$SERVICE_STATUS" = "RUNNING" ]; then
            print_status "OK" "Servicio supervisor ejecutándose"
        else
            print_status "WARNING" "Servicio supervisor no ejecutándose (estado: $SERVICE_STATUS)"
        fi
    else
        print_status "WARNING" "Servicio supervisor no configurado"
    fi
else
    print_status "WARNING" "Supervisor no instalado"
fi

# 8. Verificar logs
echo ""
echo -e "${BLUE}📝 Verificando logs...${NC}"
if [ -d "$LOG_DIR" ]; then
    print_status "OK" "Directorio de logs existe: $LOG_DIR"
    
    if [ -f "$LOG_FILE" ]; then
        print_status "OK" "Archivo de log principal existe"
        
        # Mostrar últimas líneas del log
        echo ""
        echo -e "${YELLOW}📋 Últimas 10 líneas del log:${NC}"
        tail -n 10 "$LOG_FILE" 2>/dev/null || echo "  No se puede leer el archivo de log"
        
        # Verificar tamaño del log
        LOG_SIZE=$(du -h "$LOG_FILE" 2>/dev/null | cut -f1 || echo "0")
        echo -e "${YELLOW}📊 Tamaño del log: $LOG_SIZE${NC}"
    else
        print_status "WARNING" "Archivo de log principal no existe"
    fi
else
    print_status "ERROR" "Directorio de logs no existe: $LOG_DIR"
fi

# 9. Verificar espacio en disco
echo ""
echo -e "${BLUE}💾 Verificando espacio en disco...${NC}"
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_status "OK" "Espacio en disco: ${DISK_USAGE}% usado"
else
    print_status "WARNING" "Espacio en disco alto: ${DISK_USAGE}% usado"
fi

# 10. Verificar memoria
echo ""
echo -e "${BLUE}🧠 Verificando memoria...${NC}"
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
if (( $(echo "$MEMORY_USAGE < 80" | bc -l) )); then
    print_status "OK" "Uso de memoria: ${MEMORY_USAGE}%"
else
    print_status "WARNING" "Uso de memoria alto: ${MEMORY_USAGE}%"
fi

# 11. Verificar conectividad de red
echo ""
echo -e "${BLUE}🌐 Verificando conectividad...${NC}"
if ping -c 1 8.8.8.8 &> /dev/null; then
    print_status "OK" "Conectividad a internet disponible"
else
    print_status "ERROR" "Sin conectividad a internet"
fi

# 12. Prueba rápida del script
echo ""
echo -e "${BLUE}🧪 Prueba rápida del script...${NC}"
if [ -f "$PROJECT_DIR/run_telegram_content.sh" ]; then
    print_status "OK" "Script de ejecución existe"
    
    # Verificar permisos
    if [ -x "$PROJECT_DIR/run_telegram_content.sh" ]; then
        print_status "OK" "Script tiene permisos de ejecución"
    else
        print_status "WARNING" "Script no tiene permisos de ejecución"
    fi
else
    print_status "ERROR" "Script de ejecución no encontrado"
fi

# 13. Verificar versión de Amazon Linux
echo ""
echo -e "${BLUE}🐧 Verificando sistema operativo...${NC}"
if [ -f /etc/os-release ]; then
    OS_VERSION=$(grep "PRETTY_NAME" /etc/os-release | cut -d'"' -f2)
    print_status "OK" "Sistema: $OS_VERSION"
else
    print_status "WARNING" "No se pudo determinar la versión del sistema"
fi

echo ""
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}📊 Resumen del monitoreo completado${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo -e "${YELLOW}💡 Comandos útiles:${NC}"
echo "  - Ver logs en tiempo real: tail -f $LOG_FILE"
echo "  - Ver cron jobs: crontab -l"
echo "  - Editar cron: crontab -e"
echo "  - Estado cronie: sudo systemctl status crond"
echo "  - Estado supervisor: sudo supervisorctl status"
echo "  - Reiniciar servicio: sudo supervisorctl restart social-content-automation"
echo "  - Probar conexión: cd $PROJECT_DIR && pipenv run python run_me_telegram_content.py --test-connection"
echo ""
echo -e "${GREEN}✅ Monitoreo completado${NC}" 