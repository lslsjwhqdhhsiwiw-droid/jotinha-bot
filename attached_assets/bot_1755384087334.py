import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Define o prefixo dos comandos do seu bot (ex: !kick, !play)
PREFIX = '!'

# Define as intents que seu bot precisará.
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Cria a instância do bot com o prefixo e as intents
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Evento: quando o bot está pronto e online
@bot.event
async def on_ready():
    print(f'Bot logado como {bot.user} (ID: {bot.user.id})')
    print('Bot pronto para uso!')
    await bot.change_presence(activity=discord.Game(name=f'{PREFIX}ajuda'))

    # Carrega as cogs
    try:
        await bot.load_extension('cogs.moderation')
        print("Cog de moderação carregada.")
    except Exception as e:
        print(f"Erro ao carregar cog de moderação: {e}")

    try:
        await bot.load_extension('cogs.music')
        print("Cog de música carregada.")
    except Exception as e:
        print(f"Erro ao carregar cog de música: {e}")

    try:
        await bot.load_extension('cogs.api_commands')
        print("Cog de comandos de API carregada.")
    except Exception as e:
        print(f"Erro ao carregar cog de API: {e}")
    try:
        await bot.load_extension('cogs.ofertas')
        print("Cog de ofertas carregada.")
    except Exception as e:
        print(f"Erro ao carregar cog de ofertas: {e}")


# Evento: quando um novo membro entra no servidor (exemplo de boas-vindas)
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='boas-vindas👋') # Altere 'geral' para o nome do seu canal de boas-vindas
    if channel:
        await channel.send(f'Boas-vindas, {member.mention}! Esperamos que goste do nosso servidor!')

# Comando simples de "ping"
@bot.command(name='ping', help='Responde com Pong! e a latência do bot.')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

# Comando de ajuda (o help padrão do discord.py é bom, mas você pode personalizar)
@bot.command(name='ajuda', help='Mostra a lista de comandos disponíveis.')
async def ajuda(ctx):
    embed = discord.Embed(
        title="Comandos do Bot",
        description="Aqui estão os comandos que você pode usar:",
        color=discord.Color.blue()
    )
    for command in bot.commands:
        embed.add_field(name=f"`{PREFIX}{command.name}`", value=command.help or "Sem descrição.", inline=False)
    await ctx.send(embed=embed)

# Execute o bot com seu token.
bot.run(os.getenv('DISCORD_TOKEN'))