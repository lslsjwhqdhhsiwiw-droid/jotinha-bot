import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import json
import os
from typing import Optional

class AdminAvancado(commands.Cog):
    """Cog com comandos avançados de administração"""
    
    def __init__(self, bot):
        self.bot = bot
        self.auto_mod_enabled = True
        self.spam_detection = {}
        self.banned_words = [
            # Lista básica de palavras proibidas (pode ser expandida)
            'spam', 'hack', 'cheat', 'bot', 'raid'
        ]
        self.user_warnings = {}  # Sistema de warns melhorado
        self.moderation_logs = {}  # Logs de moderação
        self.server_configs = {}  # Configurações por servidor
        self.load_configs()
        self.load_warnings()
    
    def load_configs(self):
        """Carrega configurações dos servidores"""
        try:
            if os.path.exists('admin_configs.json'):
                with open('admin_configs.json', 'r', encoding='utf-8') as f:
                    self.server_configs = json.load(f)
        except:
            self.server_configs = {}
    
    def save_configs(self):
        """Salva configurações dos servidores"""
        try:
            with open('admin_configs.json', 'w', encoding='utf-8') as f:
                json.dump(self.server_configs, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configs admin: {e}")
    
    def get_server_config(self, guild_id):
        """Obtém configuração de um servidor"""
        guild_id = str(guild_id)
        if guild_id not in self.server_configs:
            self.server_configs[guild_id] = {
                "auto_mod": True,
                "warn_threshold": 3,
                "mute_duration": 10,
                "log_channel": None,
                "staff_roles": [],
                "protected_roles": []
            }
            self.save_configs()
        return self.server_configs[guild_id]
    
    def load_warnings(self):
        """Carrega warns do arquivo JSON"""
        try:
            if os.path.exists('user_warnings.json'):
                with open('user_warnings.json', 'r', encoding='utf-8') as f:
                    self.user_warnings = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar warns: {e}")
            self.user_warnings = {}
        
    @commands.command(name='nuke', help='Apaga TODAS as mensagens do canal (CUIDADO!)')
    @commands.has_permissions(administrator=True)
    async def nuke_channel(self, ctx):
        """Comando para limpar completamente um canal"""
        # Confirmação de segurança
        embed = discord.Embed(
            title="⚠️ CONFIRMAÇÃO NECESSÁRIA",
            description=f"Você tem CERTEZA que quer apagar TODAS as mensagens do canal {ctx.channel.mention}?\n\n**Esta ação é IRREVERSÍVEL!**",
            color=discord.Color.red()
        )
        embed.add_field(
            name="Para confirmar:",
            value="Digite `CONFIRMAR NUKE` em 30 segundos",
            inline=False
        )
        
        warning_msg = await ctx.send(embed=embed)
        
        def check(message):
            return (message.author == ctx.author and 
                   message.channel == ctx.channel and 
                   message.content == "CONFIRMAR NUKE")
        
        try:
            await self.bot.wait_for('message', check=check, timeout=30.0)
            
            # Executa o nuke
            channel_name = ctx.channel.name
            channel_position = ctx.channel.position
            channel_category = ctx.channel.category
            
            # Clona o canal (método mais eficiente para limpar tudo)
            new_channel = await ctx.channel.clone(reason=f"Canal limpo por {ctx.author}")
            await new_channel.edit(position=channel_position)
            await ctx.channel.delete(reason=f"Nuke executado por {ctx.author}")
            
            # Envia confirmação no novo canal
            embed = discord.Embed(
                title="💥 Canal Nukado",
                description=f"Canal `{channel_name}` foi completamente limpo por {ctx.author.mention}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await new_channel.send(embed=embed)
            
        except asyncio.TimeoutError:
            await warning_msg.edit(content="⏰ Tempo esgotado. Nuke cancelado.")

    @commands.command(name='slowmode_adv', help='Define modo lento no canal. Uso: !slowmode_adv [segundos]')
    @commands.has_permissions(manage_channels=True)
    async def slowmode_adv(self, ctx, segundos: int = 0):
        """Define slowmode em um canal (Versão Avançada)"""
        if segundos < 0 or segundos > 21600:  # Max 6 horas
            await ctx.send("❌ O slowmode deve ser entre 0 e 21600 segundos (6 horas).")
            return
            
        await ctx.channel.edit(slowmode_delay=segundos)
        
        if segundos == 0:
            await ctx.send("✅ Slowmode desativado!")
        else:
            await ctx.send(f"✅ Slowmode definido para {segundos} segundos!")

    @commands.command(name='lock_adv', help='Bloqueia o canal para @everyone (Avançado)')
    @commands.has_permissions(manage_channels=True)
    async def lock_channel_adv(self, ctx):
        """Bloqueia um canal (Versão Avançada)"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(
            title="🔒 Canal Bloqueado (ADV)",
            description=f"Canal {ctx.channel.mention} foi bloqueado por {ctx.author.mention}",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(name='unlock_adv', help='Desbloqueia o canal (Avançado)')
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel_adv(self, ctx):
        """Desbloqueia um canal (Versão Avançada)"""
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
        
        embed = discord.Embed(
            title="🔓 Canal Desbloqueado (ADV)",
            description=f"Canal {ctx.channel.mention} foi desbloqueado por {ctx.author.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='massban', help='Bane múltiplos usuários. Uso: !massban @user1 @user2 @user3...')
    @commands.has_permissions(ban_members=True)
    async def mass_ban(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        """Bane múltiplos membros de uma vez"""
        if not members:
            await ctx.send("❌ Mencione pelo menos um membro para banir.")
            return
            
        if reason is None:
            reason = f"Ban em massa por {ctx.author}"
            
        banned_count = 0
        failed_bans = []
        
        loading_msg = await ctx.send(f"🔨 Banindo {len(members)} membros...")
        
        for member in members:
            try:
                await member.ban(reason=reason)
                banned_count += 1
                await asyncio.sleep(0.5)  # Evita rate limiting
            except discord.Forbidden:
                failed_bans.append(f"{member} (sem permissão)")
            except discord.HTTPException:
                failed_bans.append(f"{member} (erro HTTP)")
        
        embed = discord.Embed(
            title="🔨 Resultado do Ban em Massa",
            color=discord.Color.red()
        )
        embed.add_field(
            name="✅ Banidos com Sucesso",
            value=f"{banned_count} membros",
            inline=True
        )
        
        if failed_bans:
            embed.add_field(
                name="❌ Falhas",
                value="\n".join(failed_bans[:10]),  # Mostra até 10 falhas
                inline=False
            )
            
        embed.add_field(
            name="👮 Moderador",
            value=ctx.author.mention,
            inline=True
        )
        
        await loading_msg.edit(content="", embed=embed)

    @commands.command(name='masskick', help='Expulsa múltiplos usuários. Uso: !masskick @user1 @user2...')
    @commands.has_permissions(kick_members=True)
    async def mass_kick(self, ctx, members: commands.Greedy[discord.Member], *, reason=None):
        """Expulsa múltiplos membros de uma vez"""
        if not members:
            await ctx.send("❌ Mencione pelo menos um membro para expulsar.")
            return
            
        if reason is None:
            reason = f"Kick em massa por {ctx.author}"
            
        kicked_count = 0
        failed_kicks = []
        
        loading_msg = await ctx.send(f"👢 Expulsando {len(members)} membros...")
        
        for member in members:
            try:
                await member.kick(reason=reason)
                kicked_count += 1
                await asyncio.sleep(0.5)
            except discord.Forbidden:
                failed_kicks.append(f"{member} (sem permissão)")
            except discord.HTTPException:
                failed_kicks.append(f"{member} (erro HTTP)")
        
        embed = discord.Embed(
            title="👢 Resultado do Kick em Massa",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="✅ Expulsos com Sucesso",
            value=f"{kicked_count} membros",
            inline=True
        )
        
        if failed_kicks:
            embed.add_field(
                name="❌ Falhas",
                value="\n".join(failed_kicks[:10]),
                inline=False
            )
            
        await loading_msg.edit(content="", embed=embed)

    @commands.command(name='banlist', help='Mostra a lista de usuários banidos')
    @commands.has_permissions(ban_members=True)
    async def ban_list(self, ctx):
        """Mostra lista de usuários banidos"""
        banned_users = [entry async for entry in ctx.guild.bans()]
        
        if not banned_users:
            await ctx.send("✅ Nenhum usuário banido neste servidor.")
            return
            
        embed = discord.Embed(
            title="🔨 Lista de Banidos",
            description=f"Total: {len(banned_users)} usuários banidos",
            color=discord.Color.red()
        )
        
        # Mostra os primeiros 20 banidos
        ban_list = []
        for i, ban_entry in enumerate(banned_users[:20]):
            user = ban_entry.user
            reason = ban_entry.reason or "Sem motivo especificado"
            ban_list.append(f"{i+1}. {user} - {reason[:50]}...")
            
        embed.add_field(
            name="📋 Usuários Banidos",
            value="\n".join(ban_list) if ban_list else "Nenhum",
            inline=False
        )
        
        if len(banned_users) > 20:
            embed.set_footer(text=f"Mostrando 20 de {len(banned_users)} banidos")
            
        await ctx.send(embed=embed)

    @commands.command(name='serverinfo', help='Mostra informações detalhadas do servidor')
    async def server_info(self, ctx):
        """Mostra informações completas do servidor"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 Informações do Servidor",
            description=guild.name,
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            
        embed.add_field(
            name="👑 Dono",
            value=guild.owner.mention if guild.owner else "Desconhecido",
            inline=True
        )
        
        embed.add_field(
            name="📅 Criado em",
            value=guild.created_at.strftime("%d/%m/%Y"),
            inline=True
        )
        
        embed.add_field(
            name="🆔 ID",
            value=guild.id,
            inline=True
        )
        
        embed.add_field(
            name="👥 Membros",
            value=f"Total: {guild.member_count}\n🟢 Online: {sum(1 for m in guild.members if m.status != discord.Status.offline)}",
            inline=True
        )
        
        embed.add_field(
            name="💬 Canais",
            value=f"Texto: {len(guild.text_channels)}\nVoz: {len(guild.voice_channels)}",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Cargos",
            value=len(guild.roles),
            inline=True
        )
        
        embed.add_field(
            name="😄 Emojis",
            value=f"{len(guild.emojis)}/50",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Boost",
            value=f"Nível: {guild.premium_tier}\nBoosts: {guild.premium_subscription_count}",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Verificação",
            value=str(guild.verification_level).title(),
            inline=True
        )
        
        await ctx.send(embed=embed)

    @commands.command(name='purge_user', help='Remove todas as mensagens de um usuário no canal. Uso: !purge_user @user [limite]')
    @commands.has_permissions(manage_messages=True)
    async def purge_user(self, ctx, member: discord.Member, limit: int = 100):
        """Remove todas as mensagens de um usuário específico"""
        if limit > 1000:
            await ctx.send("❌ Limite máximo de 1000 mensagens.")
            return
            
        def is_user(message):
            return message.author == member
            
        loading_msg = await ctx.send(f"🧹 Removendo mensagens de {member.mention}...")
        
        try:
            deleted = await ctx.channel.purge(limit=limit, check=is_user)
            
            embed = discord.Embed(
                title="🧹 Limpeza de Usuário",
                description=f"Removidas {len(deleted)} mensagens de {member.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
            
            await loading_msg.edit(content="", embed=embed)
            
            # Remove a mensagem após 5 segundos
            await asyncio.sleep(5)
            await loading_msg.delete()
            
        except discord.HTTPException as e:
            await loading_msg.edit(content=f"❌ Erro ao limpar mensagens: {str(e)}")

    @commands.command(name='warn', help='Aplica warn a um usuário. Uso: !warn @user [motivo]')
    @commands.has_permissions(kick_members=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason=None):
        """Sistema de warns melhorado"""
        if reason is None:
            reason = "Nenhum motivo especificado"
            
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        # Inicializa warns do usuário se não existir
        if guild_id not in self.user_warnings:
            self.user_warnings[guild_id] = {}
        if user_id not in self.user_warnings[guild_id]:
            self.user_warnings[guild_id][user_id] = []
            
        # Adiciona o warn
        warn_data = {
            "reason": reason,
            "moderator": str(ctx.author.id),
            "timestamp": datetime.now().isoformat(),
            "warn_id": len(self.user_warnings[guild_id][user_id]) + 1
        }
        
        self.user_warnings[guild_id][user_id].append(warn_data)
        warn_count = len(self.user_warnings[guild_id][user_id])
        
        # Salva warns
        try:
            with open('user_warnings.json', 'w', encoding='utf-8') as f:
                json.dump(self.user_warnings, f, indent=2, ensure_ascii=False)
        except:
            pass
            
        embed = discord.Embed(
            title="⚠️ Warn Aplicado",
            description=f"{member.mention} recebeu um warn!",
            color=discord.Color.yellow()
        )
        embed.add_field(name="Motivo", value=reason, inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Total de Warns", value=f"{warn_count}/3", inline=True)
        
        # Verifica se deve aplicar punição automática
        config = self.get_server_config(ctx.guild.id)
        if warn_count >= config.get("warn_threshold", 3):
            embed.add_field(
                name="🚨 Limite Atingido", 
                value="Usuário será mutado automaticamente!", 
                inline=False
            )
            
            # Aplica mute automático (se possível)
            try:
                muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
                if muted_role:
                    await member.add_roles(muted_role, reason="Muitos warns")
                    embed.add_field(name="Punição", value="Usuário mutado", inline=True)
            except:
                pass
                
        await ctx.send(embed=embed)

    @commands.command(name='warns', help='Mostra warns de um usuário. Uso: !warns @user')
    @commands.has_permissions(kick_members=True)
    async def show_warns(self, ctx, member: Optional[discord.Member] = None):
        """Mostra warns de um usuário"""
        if member is None:
            member = ctx.author
            
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        # Carrega warns
        try:
            if os.path.exists('user_warnings.json'):
                with open('user_warnings.json', 'r', encoding='utf-8') as f:
                    self.user_warnings = json.load(f)
        except:
            self.user_warnings = {}
        
        warns = self.user_warnings.get(guild_id, {}).get(user_id, [])
        
        embed = discord.Embed(
            title=f"⚠️ Warns de {member.display_name}",
            description=f"Total: {len(warns)} warns",
            color=discord.Color.yellow()
        )
        
        if warns:
            warn_list = []
            for i, warn in enumerate(warns[-10:], 1):  # Últimos 10 warns
                moderator = ctx.guild.get_member(int(warn["moderator"]))
                mod_name = moderator.display_name if moderator else "Desconhecido"
                warn_list.append(f"**{i}.** {warn['reason']}\n*Por: {mod_name}*")
                
            embed.add_field(
                name="📋 Histórico de Warns",
                value="\n\n".join(warn_list),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Usuário Limpo",
                value="Este usuário não possui warns!",
                inline=False
            )
            
        await ctx.send(embed=embed)

    @commands.command(name='clearwarns', help='Remove todos os warns de um usuário. Uso: !clearwarns @user')
    @commands.has_permissions(administrator=True)
    async def clear_warns(self, ctx, member: discord.Member):
        """Remove todos os warns de um usuário"""
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
        
        # Carrega e limpa warns
        try:
            if os.path.exists('user_warnings.json'):
                with open('user_warnings.json', 'r', encoding='utf-8') as f:
                    self.user_warnings = json.load(f)
        except:
            self.user_warnings = {}
            
        if guild_id in self.user_warnings and user_id in self.user_warnings[guild_id]:
            del self.user_warnings[guild_id][user_id]
            
            # Salva mudanças
            try:
                with open('user_warnings.json', 'w', encoding='utf-8') as f:
                    json.dump(self.user_warnings, f, indent=2, ensure_ascii=False)
            except:
                pass
                
            embed = discord.Embed(
                title="✅ Warns Limpos",
                description=f"Todos os warns de {member.mention} foram removidos!",
                color=discord.Color.green()
            )
            embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        else:
            embed = discord.Embed(
                title="ℹ️ Nenhum Warn",
                description=f"{member.mention} não possui warns para remover.",
                color=discord.Color.blue()
            )
            
        await ctx.send(embed=embed)

    @commands.command(name='config_admin', help='Configura settings administrativos. Uso: !config_admin [setting] [valor]')
    @commands.has_permissions(administrator=True)
    async def config_admin(self, ctx, setting=None, *, value=None):
        """Configurações administrativas do servidor"""
        config = self.get_server_config(ctx.guild.id)
        
        if setting is None:
            # Mostra configurações atuais
            embed = discord.Embed(
                title="⚙️ Configurações Administrativas",
                description="Configure como o bot administra este servidor",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🤖 Auto Moderação",
                value="Ativa" if config["auto_mod"] else "Inativa",
                inline=True
            )
            embed.add_field(
                name="⚠️ Limite de Warns",
                value=f"{config['warn_threshold']} warns",
                inline=True
            )
            embed.add_field(
                name="🔇 Duração do Mute",
                value=f"{config['mute_duration']} minutos",
                inline=True
            )
            
            log_channel = ctx.guild.get_channel(config["log_channel"]) if config["log_channel"] else None
            embed.add_field(
                name="📝 Canal de Logs",
                value=log_channel.mention if log_channel else "Não configurado",
                inline=True
            )
            
            embed.add_field(
                name="📚 Como Usar",
                value="`!config_admin warn_threshold 5`\n`!config_admin auto_mod true`\n`!config_admin log_channel #logs`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            return
            
        # Aplica configuração
        if setting == "auto_mod":
            if value is None:
                await ctx.send("❌ Valor não pode ser vazio!")
                return
            config["auto_mod"] = value.lower() in ["true", "on", "ativo", "sim"]
            self.save_configs()
            await ctx.send(f"✅ Auto moderação: {'Ativa' if config['auto_mod'] else 'Inativa'}")
            
        elif setting == "warn_threshold":
            if value is None:
                await ctx.send("❌ Valor não pode ser vazio!")
                return
            try:
                config["warn_threshold"] = int(value)
                self.save_configs()
                await ctx.send(f"✅ Limite de warns definido para: {value}")
            except ValueError:
                await ctx.send("❌ Valor deve ser um número!")
                
        elif setting == "mute_duration":
            if value is None:
                await ctx.send("❌ Valor não pode ser vazio!")
                return
            try:
                config["mute_duration"] = int(value)
                self.save_configs()
                await ctx.send(f"✅ Duração do mute definida para: {value} minutos")
            except ValueError:
                await ctx.send("❌ Valor deve ser um número!")
                
        elif setting == "log_channel":
            if value is None:
                await ctx.send("❌ Valor não pode ser vazio!")
                return
            channel = None
            if value.startswith("<#") and value.endswith(">"):
                try:
                    channel_id = int(value[2:-1])
                    channel = ctx.guild.get_channel(channel_id)
                except:
                    pass
            
            if channel:
                config["log_channel"] = channel.id
                self.save_configs()
                await ctx.send(f"✅ Canal de logs definido: {channel.mention}")
            else:
                await ctx.send("❌ Canal inválido! Mencione um canal válido.")
        else:
            await ctx.send("❌ Configuração inválida! Use: `auto_mod`, `warn_threshold`, `mute_duration`, `log_channel`")

    # Tratamento de erros
    @nuke_channel.error
    @mass_ban.error
    @mass_kick.error
    async def admin_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissões de administrador para este comando.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argumento inválido. Verifique o uso do comando.")
        else:
            await ctx.send(f"❌ Erro: {str(error)}")

async def setup(bot):
    await bot.add_cog(AdminAvancado(bot))