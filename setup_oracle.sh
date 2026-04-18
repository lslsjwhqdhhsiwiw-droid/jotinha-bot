#!/bin/bash
# Script de setup automático para Oracle Cloud

echo "═══════════════════════════════════════════════════════════"
echo "🚀 SETUP AUTOMÁTICO - BOT JOTINHA NO ORACLE CLOUD"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Atualiza o sistema
echo "📦 [1/6] Atualizando sistema..."
sudo apt update -qq && sudo apt upgrade -y -qq

# Instala Python e dependências
echo "🐍 [2/6] Instalando Python e ferramentas..."
sudo apt install -y python3 python3-pip python3-venv git ffmpeg tmux -qq

# Instala Node.js e PM2
echo "📱 [3/6] Instalando PM2 para gerenciamento..."
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null 2>&1
sudo apt install -y nodejs -qq
sudo npm install -g pm2 -q

# Cria ambiente virtual
echo "🔧 [4/6] Criando ambiente virtual Python..."
python3 -m venv venv
source venv/bin/activate

# Instala dependências do bot
echo "⚙️ [5/6] Instalando dependências do bot..."
pip install -q --upgrade pip
pip install -q discord.py[voice] yt-dlp python-dotenv flask beautifulsoup4 requests trafilatura wavelink aiohttp psutil pytz pynacl openai

# Configura firewall interno
echo "🔒 [6/6] Configurando firewall..."
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT
sudo iptables -I INPUT -p tcp --dport 3000 -j ACCEPT

# Salva regras do firewall
sudo apt install -y iptables-persistent -qq
sudo netfilter-persistent save

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ SETUP COMPLETO!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "📝 PRÓXIMOS PASSOS:"
echo ""
echo "1. Configure seu token do Discord:"
echo "   nano .env"
echo ""
echo "2. Inicie o bot com PM2:"
echo "   pm2 start start_bot.sh --name jotinha-bot"
echo ""
echo "3. Configure autostart:"
echo "   pm2 startup"
echo "   pm2 save"
echo ""
echo "4. Ver logs:"
echo "   pm2 logs jotinha-bot"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎉 BOT PRONTO PARA RODAR 24/7!"
echo "═══════════════════════════════════════════════════════════"
