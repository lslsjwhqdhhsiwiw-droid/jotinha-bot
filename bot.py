import discord
from discord.ext import commands
import os
import sys
import logging
import asyncio
import traceback
from dotenv import load_dotenv

load_dotenv()

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("jotinha")

PREFIX = '!'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

COGS = [
    'cogs.moderation',
    'cogs.admin_advanced',
    'cogs.ai_brain',
    'cogs.channel_config',
    'cogs.fun_commands',
    'cogs.social_system',
]


@bot.event
async def on_ready():
    log.info(f"SISTEMA ONLINE: {bot.user} (ID: {bot.user.id})")
    print(f'SISTEMA ONLINE: {bot.user} (ID: {bot.user.id})')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{PREFIX}ajuda | JOTINHA ADM"
        )
    )
    for cog in COGS:
        try:
            await bot.load_extension(cog)
            log.info(f"✅ Módulo carregado: {cog}")
            print(f"✅ Módulo: {cog}")
        except Exception as e:
            log.error(f"❌ Falha ao carregar [{cog}]: {e}")
            print(f"❌ Falha [{cog}]: {e}")


@bot.event
async def on_disconnect():
    log.warning("⚠️  Bot desconectado do Discord. Aguardando reconexão automática...")


@bot.event
async def on_resumed():
    log.info("🔄 Sessão retomada com sucesso.")


@bot.event
async def on_error(event, *args, **kwargs):
    log.error(f"Erro não tratado no evento '{event}':\n{traceback.format_exc()}")


@bot.event
async def on_command_error(ctx, error):
    # Desempacota erros de CommandInvokeError para expor a causa raiz
    if isinstance(error, commands.CommandInvokeError):
        log.error(
            f"Erro ao executar '{ctx.command}' por {ctx.author}: "
            f"{traceback.format_exception(type(error.original), error.original, error.original.__traceback__)}"
        )
        error = error.original

    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ **Argumento faltando.** Use `{PREFIX}ajuda` para ver como usar o comando.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ **Membro não encontrado.** Mencione um usuário válido.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("🔒 **Sem permissão** para executar este comando.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ **Argumento inválido.** Verifique o comando com `{PREFIX}ajuda`.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        log.error(f"Erro inesperado: {error}")


# ── Heartbeat monitor ──────────────────────────────────────────────────────────
async def heartbeat_monitor():
    """Loga a latência do gateway a cada 5 minutos para monitoramento."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        latency_ms = round(bot.latency * 1000)
        log.info(f"💓 Heartbeat — latência: {latency_ms}ms")
        await asyncio.sleep(300)


@bot.command(name='ping')
async def ping(ctx):
    latency = round(bot.latency * 1000)
    color = 0x57F287 if latency < 200 else 0xFEE75C if latency < 400 else 0xED4245
    embed = discord.Embed(description=f"📡 **Latência:** `{latency}ms`", color=color)
    await ctx.send(embed=embed)


@bot.command(name='ajuda', aliases=['help', 'comandos'])
async def ajuda(ctx):
    embed = discord.Embed(
        title="✨ JOTINHA ADM · Painel de Controle",
        description="Arquitetura de IA para gestão e entretenimento de alto nível.",
        color=0x2b2d31
    )

    embed.add_field(
        name="🎵 MÚSICA & ÁUDIO",
        value=(
            "`!play [música]` — Busca e toca do YouTube\n"
            "`!skip` — Pula a música atual\n"
            "`!pause` / `!resume` — Pausa / Retoma\n"
            "`!stop` — Para e desconecta\n"
            "`!fila` — Ver fila de músicas\n"
            "`!volume [0-100]` — Ajusta volume\n"
            "`!conectar` — Entra na call"
        ),
        inline=False
    )

    embed.add_field(
        name="🛡️ MODERAÇÃO",
        value=(
            "`!ban @user [motivo]` — Banir\n"
            "`!kick @user` — Expulsar\n"
            "`!mute @user [min]` — Timeout\n"
            "`!clear [qtd]` — Limpar mensagens\n"
            "`!warn @user [motivo]` — Advertir (3 = kick)\n"
            "`!unwarn @user` — Remover última advertência\n"
            "`!warns @user` — Ver advertências\n"
            "`!lock` / `!unlock` — Bloquear canal\n"
            "`!nuke` — Limpar canal inteiro"
        ),
        inline=False
    )

    embed.add_field(
        name="💰 ECONOMIA",
        value=(
            "`!perfil [@user]` — Ver perfil\n"
            "`!saldo [@user]` — Ver Jotinhas\n"
            "`!daily` — Recompensa diária\n"
            "`!trabalhar` — Ganhar Jotinhas (1h)\n"
            "`!roubar @user` — Roubar (30min)\n"
            "`!apostar [valor]` — Apostar\n"
            "`!rank` — Top 10 mais ricos"
        ),
        inline=False
    )

    embed.add_field(
        name="🎮 DIVERSÃO",
        value=(
            "`!amor @u1 @u2` · `!ship @u1 @u2`\n"
            "`!sorte` · `!piada` · `!cantada`\n"
            "`!8ball [pergunta]` · `!caraoucoroa`\n"
            "`!beijo @user` · `!tapa @user` · `!abraço @user`\n"
            "`!ppt @user` — Pedra-papel-tesoura\n"
            "`!trivia` — Pergunta de conhecimento\n"
            "`!duelo @user` — Duelo de dados\n"
            "`!roletarussiana` — Jogo de risco\n"
            "`!ranking` — Top usuários mais ativos"
        ),
        inline=False
    )

    embed.add_field(
        name="🧠 IA",
        value="Mencione **@Jotinha** ou escreva `jotinha` para interagir naturalmente.",
        inline=False
    )

    if bot.user:
        embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="Powered by JOTINHA ADM · 2026")
    await ctx.send(embed=embed)


if __name__ == "__main__":
    # Keep-alive só roda no Replit (não necessário no Railway)
    if os.getenv('REPL_ID'):
        from keep_alive import keep_alive
        keep_alive()

    token = os.getenv('DISCORD_TOKEN')
    if not token:
        log.critical("DISCORD_TOKEN não encontrado. Encerrando.")
        print("❌ CRÍTICO: DISCORD_TOKEN não encontrado.")
        sys.exit(1)

    async def main():
        async with bot:
            bot.loop.create_task(heartbeat_monitor())
            await bot.start(token, reconnect=True)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot encerrado manualmente.")

