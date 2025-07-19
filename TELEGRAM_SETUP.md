# Telegram Setup Guide

Para usar el Pipeline 2 (RAG Content + Telegram), necesitas configurar las variables de entorno de Telegram.

## 1. Crear un Bot de Telegram

1. Ve a [@BotFather](https://t.me/botfather) en Telegram
2. Envía `/newbot`
3. Sigue las instrucciones para crear tu bot
4. Guarda el **Bot Token** que te proporciona

## 2. Obtener el Chat ID

### Opción A: Para un canal público
1. Agrega tu bot como administrador del canal
2. El Chat ID será algo como `@nombre_del_canal`

### Opción B: Para un chat privado
1. Envía un mensaje a tu bot
2. Ve a: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
3. Busca el `chat_id` en la respuesta

## 3. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Telegram Configuration
TELEGRAM_BOT_TOKEN=tu_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# OpenAI Configuration (requerido para RAG)
OPENAI_API_KEY=tu_openai_api_key_aqui
```

## 4. Probar la Configuración

```bash
# Probar conexión de Telegram
python run_rag_content.py --test-connection

# Ejecutar pipeline completo
python run_rag_content.py
```

## 5. Configuración Adicional

Puedes personalizar la configuración editando `configs/telegram.yaml`:

- Hashtags por defecto
- Formato de mensajes
- Configuración de medios 