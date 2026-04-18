#!/bin/bash
# Script para iniciar o bot JOTINHA

echo "🚀 Iniciando JOTINHA Bot..."

# Ativa o ambiente virtual (se existir)
if [ -d "venv" ]; then
    echo "✅ Ativando ambiente virtual..."
    source venv/bin/activate
fi

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "❌ ERRO: Arquivo .env não encontrado!"
    echo "Crie um arquivo .env com:"
    echo "DISCORD_TOKEN=seu_token_aqui"
    echo "OPENAI_API_KEY=sua_chave_aqui"
    exit 1
fi

# Verifica se as dependências estão instaladas
echo "📦 Verificando dependências..."
pip install -q -r requirements.txt

# Inicia o bot
echo "🎮 Iniciando bot..."
python3 bot.py
