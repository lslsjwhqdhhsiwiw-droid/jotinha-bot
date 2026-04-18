import discord
from discord.ext import commands
import json
import os

class ChannelConfig(commands.Cog):
    """Sistema de configuração de canais específicos para o bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "channel_config.json"
        self.channel_config = self.load_config()
    
    def load_config(self):
        """Carrega configuração de canais"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_config(self):
        """Salva configuração de canais"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.channel_config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar config de canais: {e}")
    
    def get_guild_config(self, guild_id):
        """Obtém configuração de um servidor"""
        guild_id = str(guild_id)
        if guild_id not in self.channel_config:
            self.channel_config[guild_id] = {
                "bot_channel": None,
                "general_channel": None,
                "music_channel": None,
                "news_channel": None,
                "ai_channel": None,
                "events_channel": None,
                "economy_channel": None,
                "auto_messages": True,
                "preferred_language": "pt-br"
            }
            self.save_config()
        return self.channel_config[guild_id]
    
    def set_channel_config(self, guild_id, channel_type, channel_id):
        """Define canal específico para um tipo"""
        config = self.get_guild_config(guild_id)
        config[f"{channel_type}_channel"] = channel_id
        self.save_config()
    
    def get_preferred_channel(self, guild, message_type):
        """Retorna canal preferido para um tipo de mensagem"""
        config = self.get_guild_config(guild.id)
        
        # Mapeia tipos de mensagem para configurações
        channel_mapping = {
            "bot": "bot_channel",
            "general": "general_channel", 
            "music": "music_channel",
            "news": "news_channel",
            "ai": "ai_channel",
            "events": "events_channel",
            "economy": "economy_channel"
        }
        
        channel_config_key = channel_mapping.get(message_type)
        if channel_config_key:
            channel_id = config.get(channel_config_key)
            if channel_id:
                channel = guild.get_channel(channel_id)
                if channel and channel.permissions_for(guild.me).send_messages:
                    return channel
        
        # Fallback para canais padrão
        fallback_names = {
            "bot": ["bots", "bot-commands", "commands", "bot"],
            "general": ["geral", "chat-geral", "general", "chat"],
            "music": ["musica", "music", "audio", "som"],
            "news": ["noticias", "news", "informacoes", "brasil"],
            "ai": ["ia", "ai", "inteligencia", "bot-ia"],
            "events": ["eventos", "events", "jogos", "diversao"],
            "economy": ["economia", "economy", "moedas", "coins"]
        }
        
        names = fallback_names.get(message_type, ["geral", "chat"])
        
        # Procura pelos nomes padrão
        for name in names:
            channel = discord.utils.get(guild.channels, name=name)
            if channel and channel.permissions_for(guild.me).send_messages:
                return channel
        
        # Último recurso: primeiro canal disponível
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return channel
        
        return None
    
    @commands.command(name='config_canais', help='Configurar canais específicos do bot')
    @commands.has_permissions(administrator=True)
    async def configure_channels(self, ctx):
        """Interface principal de configuração"""
        embed = discord.Embed(
            title="⚙️ Configuração de Canais - JOTINHA ADM",
            description="Configure onde o bot deve enviar cada tipo de mensagem!",
            color=discord.Color.blue()
        )
        
        config = self.get_guild_config(ctx.guild.id)
        
        # Mostra configuração atual
        channel_types = [
            ("🤖 Bot/Comandos", "bot_channel", "Respostas de comandos gerais"),
            ("💬 Chat Geral", "general_channel", "Mensagens automáticas gerais"),
            ("🎵 Música", "music_channel", "Comandos e notificações de música"),
            ("📰 Notícias", "news_channel", "Notícias automáticas do Brasil"),
            ("🧠 IA", "ai_channel", "Conversas e análises da IA"),
            ("🎪 Eventos", "events_channel", "Jogos e eventos automáticos"),
            ("💰 Economia", "economy_channel", "Sistema de moedas e ranking")
        ]
        
        current_config = ""
        for emoji_name, config_key, description in channel_types:
            channel_id = config.get(config_key)
            if channel_id:
                channel = ctx.guild.get_channel(channel_id)
                channel_text = channel.mention if channel else "❌ Canal não encontrado"
            else:
                channel_text = "⚠️ Não configurado"
            
            current_config += f"{emoji_name}: {channel_text}\n"
        
        embed.add_field(
            name="📋 Configuração Atual:",
            value=current_config,
            inline=False
        )
        
        embed.add_field(
            name="🛠️ Comandos de Configuração:",
            value=(
                "`!set_canal bot #canal` - Canal para comandos\n"
                "`!set_canal geral #canal` - Chat geral\n" 
                "`!set_canal musica #canal` - Canal de música\n"
                "`!set_canal noticias #canal` - Canal de notícias\n"
                "`!set_canal ia #canal` - Canal da IA\n"
                "`!set_canal eventos #canal` - Canal de eventos\n"
                "`!set_canal economia #canal` - Canal de economia"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Outros Comandos:",
            value="`!reset_canais` - Reset configurações\n`!test_canais` - Testar configuração",
            inline=False
        )
        
        embed.set_footer(text="⚡ Configuração inteligente com fallbacks automáticos")
        await ctx.send(embed=embed)
    
    @commands.command(name='set_canal', help='Define canal específico')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx, tipo: str, canal: discord.TextChannel):
        """Define canal para um tipo específico"""
        valid_types = {
            "bot": "bot_channel",
            "geral": "general_channel",
            "musica": "music_channel", 
            "noticias": "news_channel",
            "ia": "ai_channel",
            "eventos": "events_channel",
            "economia": "economy_channel"
        }
        
        tipo = tipo.lower()
        if tipo not in valid_types:
            await ctx.send(f"❌ Tipo inválido! Use: {', '.join(valid_types.keys())}")
            return
        
        self.set_channel_config(ctx.guild.id, tipo, canal.id)
        
        embed = discord.Embed(
            title="✅ Canal Configurado!",
            description=f"Canal para **{tipo}** definido como {canal.mention}",
            color=discord.Color.green()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='test_canais', help='Testa configuração de canais')
    @commands.has_permissions(administrator=True)
    async def test_channels(self, ctx):
        """Testa envio em todos os canais configurados"""
        config = self.get_guild_config(ctx.guild.id)
        
        test_messages = {
            "bot": "🤖 Teste do canal de bot/comandos!",
            "general": "💬 Teste do chat geral!",
            "music": "🎵 Teste do canal de música!",
            "news": "📰 Teste do canal de notícias!",
            "ai": "🧠 Teste do canal da IA!",
            "events": "🎪 Teste do canal de eventos!",
            "economy": "💰 Teste do canal de economia!"
        }
        
        results = []
        
        for channel_type, message in test_messages.items():
            channel = self.get_preferred_channel(ctx.guild, channel_type)
            if channel:
                try:
                    await channel.send(f"🔧 {message}")
                    results.append(f"✅ {channel_type}: {channel.mention}")
                except:
                    results.append(f"❌ {channel_type}: Erro ao enviar")
            else:
                results.append(f"⚠️ {channel_type}: Canal não encontrado")
        
        embed = discord.Embed(
            title="🧪 Teste de Canais Concluído",
            description="\n".join(results),
            color=discord.Color.purple()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='reset_canais', help='Reseta configuração de canais')
    @commands.has_permissions(administrator=True)
    async def reset_channels(self, ctx):
        """Reseta toda configuração de canais"""
        guild_id = str(ctx.guild.id)
        if guild_id in self.channel_config:
            del self.channel_config[guild_id]
            self.save_config()
        
        embed = discord.Embed(
            title="🔄 Configuração Resetada",
            description="Todas as configurações de canal foram removidas. O bot usará canais padrão.",
            color=discord.Color.orange()
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='canal_auto_config', help='Configuração automática inteligente de canais')
    @commands.has_permissions(administrator=True)
    async def auto_configure(self, ctx):
        """Configuração automática baseada nos nomes dos canais"""
        guild = ctx.guild
        config = self.get_guild_config(guild.id)
        
        # Mapas de detecção automática
        auto_mappings = {
            "bot_channel": ["bots", "bot", "commands", "comandos"],
            "general_channel": ["geral", "general", "chat", "principal"],
            "music_channel": ["musica", "music", "audio", "som"],
            "news_channel": ["noticias", "news", "brasil", "informacoes"],
            "ai_channel": ["ia", "ai", "inteligencia", "bot-ia"],
            "events_channel": ["eventos", "events", "jogos", "diversao"],
            "economy_channel": ["economia", "economy", "moedas", "coins"]
        }
        
        configured = []
        
        for config_key, possible_names in auto_mappings.items():
            for name in possible_names:
                channel = discord.utils.get(guild.channels, name=name)
                if channel and channel.permissions_for(guild.me).send_messages:
                    config[config_key] = channel.id
                    configured.append(f"✅ {config_key.replace('_channel', '')}: {channel.mention}")
                    break
        
        self.save_config()
        
        embed = discord.Embed(
            title="🤖 Configuração Automática Concluída",
            description="Detectei e configurei os seguintes canais:",
            color=discord.Color.gold()
        )
        
        if configured:
            embed.add_field(
                name="📍 Canais Configurados:",
                value="\n".join(configured),
                inline=False
            )
        else:
            embed.add_field(
                name="⚠️ Nenhum Canal Detectado",
                value="Não encontrei canais com nomes padrão. Use `!set_canal` para configurar manualmente.",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChannelConfig(bot))