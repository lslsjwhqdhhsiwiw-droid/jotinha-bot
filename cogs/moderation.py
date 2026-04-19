import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio
import json
import os
import re
from collections import defaultdict


# ── Configurações de auto-mod ──────────────────────────────────────────────────
SPAM_THRESHOLD = 5          # mensagens em SPAM_WINDOW segundos = spam
SPAM_WINDOW = 5             # janela de tempo em segundos
CAPS_THRESHOLD = 0.70       # 70% de maiúsculas = caps excessivo
CAPS_MIN_LEN = 10           # mínimo de caracteres para checar caps
RAID_THRESHOLD = 8          # joins em RAID_WINDOW segundos = raid
RAID_WINDOW = 10            # janela de tempo em segundos
WARN_LIMIT = 3              # warns antes do kick automático

PALAVRAS_PROIBIDAS = [
    # Adicione palavras conforme necessário
    "n1gger", "nigger", "faggot",
]

LINK_SUSPEITO_PATTERN = re.compile(
    r"(discord\.gg/|discordapp\.com/invite/|bit\.ly/|tinyurl\.com/|t\.co/)",
    re.IGNORECASE,
)

WARNS_FILE = "mod_warns.json"


class Moderacao(commands.Cog):
    """⚔️ Sistema de Segurança e Gestão de Comunidade"""

    def __init__(self, bot):
        self.bot = bot
        # {guild_id: {user_id: [{"reason": str, "mod": str, "ts": str}]}}
        self.warns: dict = self._load_warns()
        # Rastreamento de spam: {guild_id: {user_id: [timestamp, ...]}}
        self.spam_tracker: dict = defaultdict(lambda: defaultdict(list))
        # Rastreamento de raid: {guild_id: [join_timestamp, ...]}
        self.raid_tracker: dict = defaultdict(list)
        # Canais de log por guild: {guild_id: channel_id}
        self.log_channels: dict = {}

    # ── Persistência de warns ──────────────────────────────────────────────────

    def _load_warns(self) -> dict:
        try:
            if os.path.exists(WARNS_FILE):
                with open(WARNS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[Moderação] Erro ao carregar warns: {e}")
        return {}

    def _save_warns(self):
        try:
            with open(WARNS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.warns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Moderação] Erro ao salvar warns: {e}")

    def _get_warns(self, guild_id: int, user_id: int) -> list:
        return self.warns.get(str(guild_id), {}).get(str(user_id), [])

    def _add_warn(self, guild_id: int, user_id: int, reason: str, mod_id: int):
        gid, uid = str(guild_id), str(user_id)
        self.warns.setdefault(gid, {}).setdefault(uid, [])
        self.warns[gid][uid].append({
            "reason": reason,
            "mod": str(mod_id),
            "ts": datetime.now().isoformat(),
        })
        self._save_warns()
        return len(self.warns[gid][uid])

    def _remove_last_warn(self, guild_id: int, user_id: int) -> bool:
        gid, uid = str(guild_id), str(user_id)
        warns = self.warns.get(gid, {}).get(uid, [])
        if not warns:
            return False
        warns.pop()
        self.warns[gid][uid] = warns
        self._save_warns()
        return True

    def _clear_warns(self, guild_id: int, user_id: int):
        gid, uid = str(guild_id), str(user_id)
        if gid in self.warns and uid in self.warns[gid]:
            self.warns[gid][uid] = []
            self._save_warns()

    # ── Canal de auditoria ─────────────────────────────────────────────────────

    async def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel | None:
        """Retorna o canal de log configurado ou tenta encontrar um automaticamente."""
        channel_id = self.log_channels.get(guild.id)
        if channel_id:
            ch = guild.get_channel(channel_id)
            if ch:
                return ch
        # Fallback: procura por nomes comuns
        for name in ("mod-log", "mod-logs", "logs", "auditoria", "moderação", "moderacao"):
            ch = discord.utils.get(guild.text_channels, name=name)
            if ch and ch.permissions_for(guild.me).send_messages:
                return ch
        return None

    async def _audit_log(self, guild: discord.Guild, embed: discord.Embed):
        """Envia embed no canal de auditoria, se disponível."""
        ch = await self._get_log_channel(guild)
        if ch:
            try:
                await ch.send(embed=embed)
            except Exception:
                pass

    # ── Embed de log padrão ────────────────────────────────────────────────────

    async def _embed_log(self, ctx, title, target, moderator, color, reason):
        embed = discord.Embed(title=title, color=color, timestamp=datetime.now())
        embed.add_field(name="👤 Alvo", value=target.mention, inline=True)
        embed.add_field(name="👮 Responsável", value=moderator.mention, inline=True)
        embed.add_field(name="📝 Motivo", value=reason or "Não especificado", inline=False)
        embed.set_footer(text=f"ID do Usuário: {target.id}")
        await ctx.send(embed=embed)
        await self._audit_log(ctx.guild, embed)

    # ── Auto-mod: on_message ───────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        if message.author.guild_permissions.manage_messages:
            return  # Moderadores ficam isentos

        guild_id = message.guild.id
        user_id = message.author.id
        content = message.content

        # 1. Filtro de palavras proibidas
        content_lower = content.lower()
        for palavra in PALAVRAS_PROIBIDAS:
            if palavra in content_lower:
                try:
                    await message.delete()
                except Exception:
                    pass
                await message.channel.send(
                    f"🚫 {message.author.mention}, essa palavra não é permitida aqui.",
                    delete_after=8,
                )
                await self._auto_warn(message, "Uso de palavra proibida")
                return

        # 2. Filtro de links suspeitos
        if LINK_SUSPEITO_PATTERN.search(content):
            try:
                await message.delete()
            except Exception:
                pass
            await message.channel.send(
                f"🔗 {message.author.mention}, links de convite não são permitidos sem autorização.",
                delete_after=8,
            )
            await self._auto_warn(message, "Link suspeito/convite não autorizado")
            return

        # 3. Detecção de caps excessivo
        if len(content) >= CAPS_MIN_LEN:
            letters = [c for c in content if c.isalpha()]
            if letters and (sum(1 for c in letters if c.isupper()) / len(letters)) >= CAPS_THRESHOLD:
                try:
                    await message.delete()
                except Exception:
                    pass
                await message.channel.send(
                    f"🔠 {message.author.mention}, por favor evite escrever tudo em MAIÚSCULAS.",
                    delete_after=8,
                )
                return

        # 4. Detecção de spam
        now = datetime.now().timestamp()
        tracker = self.spam_tracker[guild_id][user_id]
        tracker.append(now)
        # Remove timestamps fora da janela
        self.spam_tracker[guild_id][user_id] = [t for t in tracker if now - t <= SPAM_WINDOW]
        if len(self.spam_tracker[guild_id][user_id]) >= SPAM_THRESHOLD:
            self.spam_tracker[guild_id][user_id] = []
            try:
                await message.channel.purge(
                    limit=SPAM_THRESHOLD + 2,
                    check=lambda m: m.author == message.author,
                )
            except Exception:
                pass
            await message.channel.send(
                f"⚠️ {message.author.mention}, spam detectado! Suas mensagens foram removidas.",
                delete_after=10,
            )
            await self._auto_warn(message, "Spam detectado pelo auto-mod")

    async def _auto_warn(self, message: discord.Message, reason: str):
        """Aplica warn automático e kick se atingir o limite."""
        guild_id = message.guild.id
        user_id = message.author.id
        count = self._add_warn(guild_id, user_id, f"[AUTO-MOD] {reason}", self.bot.user.id)

        embed = discord.Embed(
            title="⚠️ Advertência Automática",
            description=f"{message.author.mention} recebeu um warn automático.",
            color=discord.Color.yellow(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="Motivo", value=reason, inline=False)
        embed.add_field(name="Total de Warns", value=f"{count}/{WARN_LIMIT}", inline=True)
        await self._audit_log(message.guild, embed)

        if count >= WARN_LIMIT:
            try:
                await message.author.kick(reason=f"Limite de {WARN_LIMIT} warns atingido (auto-mod)")
                self._clear_warns(guild_id, user_id)
                kick_embed = discord.Embed(
                    title="👢 Kick Automático",
                    description=f"{message.author.mention} foi expulso por atingir {WARN_LIMIT} warns.",
                    color=discord.Color.red(),
                    timestamp=datetime.now(),
                )
                await self._audit_log(message.guild, kick_embed)
                await message.channel.send(
                    f"👢 {message.author.mention} foi expulso automaticamente após {WARN_LIMIT} advertências.",
                    delete_after=15,
                )
            except Exception:
                pass

    # ── Detecção de raid ───────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_id = member.guild.id
        now = datetime.now().timestamp()
        self.raid_tracker[guild_id].append(now)
        # Limpa entradas antigas
        self.raid_tracker[guild_id] = [t for t in self.raid_tracker[guild_id] if now - t <= RAID_WINDOW]

        if len(self.raid_tracker[guild_id]) >= RAID_THRESHOLD:
            self.raid_tracker[guild_id] = []
            embed = discord.Embed(
                title="🚨 ALERTA DE RAID DETECTADO",
                description=(
                    f"**{RAID_THRESHOLD}+ membros** entraram nos últimos **{RAID_WINDOW}s**!\n"
                    "Considere ativar o modo de verificação elevado com `!lock` ou via painel do Discord."
                ),
                color=discord.Color.red(),
                timestamp=datetime.now(),
            )
            embed.set_footer(text="Auto-Mod · Proteção Anti-Raid")
            await self._audit_log(member.guild, embed)
            # Tenta alertar em qualquer canal de texto disponível
            ch = await self._get_log_channel(member.guild)
            if not ch:
                for c in member.guild.text_channels:
                    if c.permissions_for(member.guild.me).send_messages:
                        ch = c
                        break
            if ch:
                await ch.send(embed=embed)

    # ── Comandos de moderação ──────────────────────────────────────────────────

    @commands.command(name='setlog', help='Define o canal de logs de moderação. Uso: !setlog #canal')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        self.log_channels[ctx.guild.id] = channel.id
        await ctx.send(f"✅ Canal de auditoria definido como {channel.mention}.")

    @commands.command(name='kick', aliases=['expulsar'], help='Remove um membro da guilda.')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            await self._embed_log(ctx, "👢 Membro Expulso", member, ctx.author, discord.Color.orange(), reason)
        except Exception as e:
            await ctx.send(f"❌ Erro ao processar expulsão: {e}")

    @commands.command(name='ban', aliases=['banir'], help='Bane permanentemente um usuário.')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            await self._embed_log(ctx, "🔨 Banimento Aplicado", member, ctx.author, discord.Color.red(), reason)
        except Exception as e:
            await ctx.send(f"❌ Erro ao processar banimento: {e}")

    @commands.command(name='clear', aliases=['limpar', 'purge'], help='Limpa o histórico de mensagens.')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        if amount < 1 or amount > 100:
            return await ctx.send("⚠️ Informe uma quantidade entre 1 e 100.")
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🧹 **Protocolo de Limpeza:** `{len(deleted)-1}` mensagens incineradas.")
        await asyncio.sleep(5)
        await msg.delete()

    @commands.command(name='lock', aliases=['trancar'], help='Bloqueia o envio de mensagens.')
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        embed = discord.Embed(
            description="🔒 **Protocolo de Segurança Ativado:** Canal trancado para interações.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)
        await self._audit_log(ctx.guild, discord.Embed(
            title="🔒 Canal Trancado",
            description=f"{ctx.channel.mention} trancado por {ctx.author.mention}",
            color=discord.Color.red(),
            timestamp=datetime.now(),
        ))

    @commands.command(name='unlock', aliases=['destrancar'], help='Libera o envio de mensagens.')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(
            description="🔓 **Segurança Restabelecida:** Canal liberado para interações.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)

    @commands.command(name='slowmode', aliases=['lento'], help='Define o tempo de espera entre mensagens.')
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🕒 **Modo Lento:** Intervalo de `{seconds}s` aplicado com sucesso.")

    @commands.command(name='mute', aliases=['silenciar'], help='Remove a permissão de fala de um membro.')
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, minutes: int = 10, *, reason=None):
        try:
            duration = timedelta(minutes=minutes)
            await member.timeout(duration, reason=reason)
            await self._embed_log(
                ctx, "🔇 Silenciamento Temporário", member, ctx.author,
                discord.Color.dark_grey(), f"{reason} (Duração: {minutes}m)",
            )
        except Exception as e:
            await ctx.send(f"❌ Não foi possível aplicar o timeout: {e}")

    @commands.command(name='warn', help='Adverte um usuário. Uso: !warn @user [motivo]')
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Não especificado"):
        if member.bot:
            return await ctx.send("❌ Não é possível advertir um bot.")

        count = self._add_warn(ctx.guild.id, member.id, reason, ctx.author.id)

        embed = discord.Embed(
            title="⚠️ Advertência Aplicada",
            description=f"{member.mention} recebeu uma advertência.",
            color=discord.Color.yellow(),
            timestamp=datetime.now(),
        )
        embed.add_field(name="📝 Motivo", value=reason, inline=False)
        embed.add_field(name="👮 Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="📊 Total", value=f"**{count}/{WARN_LIMIT}**", inline=True)

        if count >= WARN_LIMIT:
            embed.add_field(
                name="🚨 Limite Atingido!",
                value=f"Usuário será expulso automaticamente.",
                inline=False,
            )

        await ctx.send(embed=embed)
        await self._audit_log(ctx.guild, embed)

        # Kick automático ao atingir o limite
        if count >= WARN_LIMIT:
            try:
                await member.kick(reason=f"Limite de {WARN_LIMIT} warns atingido")
                self._clear_warns(ctx.guild.id, member.id)
                await ctx.send(f"👢 **{member.display_name}** foi expulso após atingir {WARN_LIMIT} advertências.")
            except discord.Forbidden:
                await ctx.send("⚠️ Não tenho permissão para expulsar este usuário.")

    @commands.command(name='unwarn', help='Remove a última advertência de um usuário. Uso: !unwarn @user')
    @commands.has_permissions(kick_members=True)
    async def unwarn(self, ctx, member: discord.Member):
        removed = self._remove_last_warn(ctx.guild.id, member.id)
        if removed:
            remaining = len(self._get_warns(ctx.guild.id, member.id))
            embed = discord.Embed(
                title="✅ Advertência Removida",
                description=f"A última advertência de {member.mention} foi removida.",
                color=discord.Color.green(),
                timestamp=datetime.now(),
            )
            embed.add_field(name="📊 Warns Restantes", value=f"{remaining}/{WARN_LIMIT}", inline=True)
            embed.add_field(name="👮 Moderador", value=ctx.author.mention, inline=True)
            await ctx.send(embed=embed)
            await self._audit_log(ctx.guild, embed)
        else:
            await ctx.send(f"ℹ️ {member.mention} não possui advertências para remover.")

    @commands.command(name='warns', help='Mostra as advertências de um usuário. Uso: !warns @user')
    @commands.has_permissions(kick_members=True)
    async def warns(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        warn_list = self._get_warns(ctx.guild.id, member.id)

        embed = discord.Embed(
            title=f"⚠️ Advertências — {member.display_name}",
            color=discord.Color.yellow(),
            timestamp=datetime.now(),
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Total", value=f"**{len(warn_list)}/{WARN_LIMIT}**", inline=True)

        if warn_list:
            lines = []
            for i, w in enumerate(warn_list[-10:], 1):
                ts = w.get("ts", "")[:10]
                lines.append(f"**{i}.** {w['reason']} *(em {ts})*")
            embed.add_field(name="📋 Histórico", value="\n".join(lines), inline=False)
        else:
            embed.add_field(name="✅ Usuário Limpo", value="Nenhuma advertência registrada.", inline=False)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderacao(bot))

