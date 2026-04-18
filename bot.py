import discord
from discord.ext import commands
import os
import asyncio
import logging
import re

PREFIX = '!'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

COGS = [
    'cogs.moderation',
    'cogs.admin_advanced',
    'cogs.ai_brain',
    'cogs.channel_config',
    'cogs.music_voice',
    'cogs.fun_commands',
    'cogs.social_system',
]


@bot.event
async def on_ready():
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
            print(f"✅ Módulo: {cog}")
        except Exception as e:
            print(f"❌ Falha [{cog}]: {e}")


@bot.event
async def on_command_error(ctx, error):
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
            "`!warn @user` — Advertir\n"
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
            "`!beijo @user` · `!tapa @user` · `!abraço @user`"
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


def validate_token(token: str | None) -> tuple[bool, str]:
    """
    Validate the Discord token and return (is_valid, reason).

    A Discord bot token has three Base64url-encoded segments separated by dots:
      <user_id_b64>.<timestamp_b64>.<hmac_b64>
    The full token is typically 70–80 characters long.
    """
    if not token:
        return False, "token is empty or not set"

    token = token.strip()

    if not token:
        return False, "token is blank (only whitespace)"

    parts = token.split('.')
    if len(parts) != 3:
        return False, (
            f"token has {len(parts)} segment(s) separated by '.', expected 3 — "
            "this is not a valid Discord bot token format"
        )

    # Each segment must be non-empty Base64url characters
    b64url_re = re.compile(r'^[A-Za-z0-9_\-]+$')

    for i, part in enumerate(parts):
        if not part:
            return False, f"segment {i + 1} of the token is empty"
        if not b64url_re.match(part):
            return False, (
                f"segment {i + 1} contains characters outside the Base64url "
                "alphabet — the token may have been copied incorrectly"
            )

    if len(token) < 50:
        return False, (
            f"token is only {len(token)} characters long; "
            "Discord bot tokens are typically 70–80 characters"
        )

    return True, "ok"


def redact_token(token: str) -> str:
    """Return a redacted view showing only the first 10 and last 5 characters."""
    if len(token) <= 15:
        return "*" * len(token)
    return f"{token[:10]}{'*' * (len(token) - 15)}{token[-5:]}"


if __name__ == "__main__":
    # Configure logging so Railway captures structured output
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    log = logging.getLogger("bot.startup")

    log.info("=== JOTINHA ADM — startup ===")

    # Keep-alive só roda no Replit (não necessário no Railway)
    if os.getenv('REPL_ID'):
        from keep_alive import keep_alive
        keep_alive()
        log.info("keep_alive thread started (Replit environment detected)")

    # ── Token validation ──────────────────────────────────────────────────────
    raw_token = os.getenv('DISCORD_TOKEN')

    log.info("Checking DISCORD_TOKEN environment variable…")

    if raw_token is None:
        log.critical(
            "DISCORD_TOKEN is not set in the environment. "
            "Go to Railway → your service → Variables and add DISCORD_TOKEN."
        )
        raise SystemExit(1)

    token = raw_token.strip()

    # Report basic token metadata without exposing the full secret
    log.info("DISCORD_TOKEN is present — length: %d character(s)", len(token))
    if len(token) >= 15:
        log.info("Token preview (redacted): %s", redact_token(token))
    else:
        log.warning("Token is suspiciously short (%d chars); preview suppressed", len(token))

    if len(raw_token) != len(token):
        log.warning(
            "Leading/trailing whitespace was stripped from DISCORD_TOKEN "
            "(%d → %d chars). Check the Railway variable for accidental spaces.",
            len(raw_token), len(token),
        )

    is_valid, reason = validate_token(token)
    if not is_valid:
        log.critical(
            "DISCORD_TOKEN failed format validation: %s. "
            "Regenerate the token at https://discord.com/developers/applications "
            "and update the Railway variable.",
            reason,
        )
        raise SystemExit(1)

    log.info("Token format looks valid — attempting to connect to Discord…")

    bot.run(token, log_handler=None)  # log_handler=None keeps our own logging config
