import discord
from discord.ext import commands
import random

class FunCommands(commands.Cog):
    """🎭 Módulo de Entretenimento e Interação Social"""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='amor', aliases=['love'], help='Calcula a afinidade entre dois usuários.')
    async def amor(self, ctx, user1: discord.Member, user2: discord.Member = None):
        if not user2:
            user2 = user1
            user1 = ctx.author
        
        percentage = random.randint(0, 100)
        heart = "💔" if percentage < 50 else "💖" if percentage < 90 else "💘"
        
        embed = discord.Embed(title=f"{heart} Analisador de Afinidade", color=0xff0055)
        embed.description = f"🔥 **{user1.display_name}** + **{user2.display_name}**\nResultado: **{percentage}%**"
        await ctx.send(embed=embed)

    @commands.command(name='ship', help='Verifica a compatibilidade de um casal.')
    async def ship(self, ctx, u1: discord.Member, u2: discord.Member):
        chance = random.randint(0, 100)
        await ctx.send(f"💞 **Matchmaking:** A compatibilidade entre **{u1.display_name}** e **{u2.display_name}** é de `{chance}%`!")

    @commands.command(name='sorte', help='Revela sua previsão astrológica do dia.')
    async def sorte(self, ctx):
        sortes = [
            "✨ Grandes oportunidades financeiras surgirão hoje.",
            "🛡️ Proteja seus segredos, alguém está observando.",
            "🚀 Sua criatividade estará em alta nas próximas horas.",
            "🤝 Um reencontro inesperado trará boas notícias.",
            "⚖️ Equilíbrio é a chave para o seu sucesso hoje."
        ]
        await ctx.send(f"🔮 **Oráculo:** {ctx.author.mention}, sua sorte: *{random.choice(sortes)}*")

    @commands.command(name='beijo', aliases=['kiss'], help='Demonstra afeto com um beijo.')
    async def beijo(self, ctx, member: discord.Member):
        if member == ctx.author: return await ctx.send("💋 Auto-beijo? Isso que é amor próprio!")
        await ctx.send(f"💋 **Social:** {ctx.author.mention} deixou um beijo carinhoso em {member.mention}!")

    @commands.command(name='tapa', aliases=['slap'], help='Aplica uma correção física amigável.')
    async def tapa(self, ctx, member: discord.Member):
        await ctx.send(f"👋 **Ação:** {ctx.author.mention} deu um tapa pedagógico em {member.mention}!")

    @commands.command(name='abraço', aliases=['hug', 'abraco'], help='Envia um abraço virtual.')
    async def abraco(self, ctx, member: discord.Member):
        await ctx.send(f"🫂 **Social:** {ctx.author.mention} deu um abraço apertado em {member.mention}!")

    @commands.command(name='piada', help='O bot utiliza seu banco de dados de humor.')
    async def piada(self, ctx):
        piadas = [
            "Por que o computador foi ao médico? Porque estava com vírus!",
            "O que o zero disse para o oito? Belo cinto!",
            "Qual é o animal mais antigo? A zebra, porque está em preto e branco.",
            "Como o átomo atende o telefone? Proton!"
        ]
        await ctx.send(f"🤡 **Humor:** {random.choice(piadas)}")

    @commands.command(name='cantada', help='Manda um flerte de alta performance.')
    async def cantada(self, ctx):
        cantadas = [
            "Você não é Wi-Fi, mas sinto uma conexão forte.",
            "Se beleza fosse crime, você estaria em prisão perpétua.",
            "Me chama de teclado e diz que eu sou o seu tipo.",
            "Você é o commit que faltava no meu repositório."
        ]
        await ctx.send(f"😏 **Flerte:** {random.choice(cantadas)}")

    @commands.command(name='8ball', help='Consulta a sabedoria suprema.')
    async def eightball(self, ctx, *, pergunta: str):
        respostas = ["Sim.", "Não.", "Talvez.", "Provavelmente.", "Sem dúvidas.", "Pergunte mais tarde."]
        await ctx.reply(f"🎱 **Destino:** {random.choice(respostas)}")

    @commands.command(name='caraoucoroa', help='Decisão binária via sorteio.')
    async def caraoucoroa(self, ctx):
        await ctx.send(f"🪙 **Moeda:** Deu **{random.choice(['Cara', 'Coroa'])}**!")

async def setup(bot):
    await bot.add_cog(FunCommands(bot))
