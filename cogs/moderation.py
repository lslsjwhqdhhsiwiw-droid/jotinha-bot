import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Moderacao(commands.Cog):
    """⚔️ Sistema de Segurança e Gestão de Comunidade"""
    
    def __init__(self, bot):
        self.bot = bot

    async def _embed_log(self, ctx, title, target, moderator, color, reason):
        embed = discord.Embed(title=title, color=color, timestamp=datetime.now())
        embed.add_field(name="👤 Alvo", value=target.mention, inline=True)
        embed.add_field(name="👮 Responsável", value=moderator.mention, inline=True)
        embed.add_field(name="📝 Motivo", value=reason or "Não especificado", inline=False)
        embed.set_footer(text=f"ID do Usuário: {target.id}")
        await ctx.send(embed=embed)

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
        embed = discord.Embed(description="🔒 **Protocolo de Segurança Ativado:** Canal trancado para interações.", color=discord.Color.red())
        await ctx.send(embed=embed)

    @commands.command(name='unlock', aliases=['destrancar'], help='Libera o envio de mensagens.')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        embed = discord.Embed(description="🔓 **Segurança Restabelecida:** Canal liberado para interações.", color=discord.Color.green())
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
            await self._embed_log(ctx, "🔇 Silenciamento Temporário", member, ctx.author, discord.Color.dark_grey(), f"{reason} (Duração: {minutes}m)")
        except Exception as e:
            await ctx.send(f"❌ Não foi possível aplicar o timeout: {e}")

async def setup(bot):
    await bot.add_cog(Moderacao(bot))
