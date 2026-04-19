import discord
from discord.ext import commands
import random
import asyncio
from collections import defaultdict
from datetime import datetime


# ── Banco de dados de trivia ───────────────────────────────────────────────────
TRIVIA_QUESTIONS = [
    {"q": "Qual é a capital do Brasil?", "a": "brasília", "opts": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"]},
    {"q": "Quantos planetas existem no Sistema Solar?", "a": "8", "opts": ["7", "8", "9", "10"]},
    {"q": "Qual elemento químico tem símbolo 'O'?", "a": "oxigênio", "opts": ["Ouro", "Osmio", "Oxigênio", "Óxido"]},
    {"q": "Em que ano o Brasil foi descoberto?", "a": "1500", "opts": ["1492", "1500", "1510", "1488"]},
    {"q": "Qual é o maior oceano do mundo?", "a": "pacífico", "opts": ["Atlântico", "Índico", "Pacífico", "Ártico"]},
    {"q": "Quantos lados tem um hexágono?", "a": "6", "opts": ["5", "6", "7", "8"]},
    {"q": "Qual é o animal mais rápido do mundo?", "a": "guepardo", "opts": ["Leão", "Guepardo", "Falcão", "Cavalo"]},
    {"q": "Quem escreveu 'Dom Casmurro'?", "a": "machado de assis", "opts": ["José de Alencar", "Machado de Assis", "Clarice Lispector", "Carlos Drummond"]},
    {"q": "Qual é a fórmula química da água?", "a": "h2o", "opts": ["H2O", "CO2", "NaCl", "O2"]},
    {"q": "Quantos continentes existem na Terra?", "a": "7", "opts": ["5", "6", "7", "8"]},
    {"q": "Qual é o maior país do mundo em área?", "a": "rússia", "opts": ["China", "EUA", "Rússia", "Brasil"]},
    {"q": "Em que país fica a Torre Eiffel?", "a": "frança", "opts": ["Itália", "Espanha", "França", "Alemanha"]},
    {"q": "Qual é o osso mais longo do corpo humano?", "a": "fêmur", "opts": ["Tíbia", "Fêmur", "Úmero", "Rádio"]},
    {"q": "Quantas horas tem um dia?", "a": "24", "opts": ["12", "24", "48", "36"]},
    {"q": "Qual linguagem de programação usa a extensão .py?", "a": "python", "opts": ["Java", "Ruby", "Python", "Perl"]},
]

# Rastreamento de atividade para ranking: {guild_id: {user_id: int}}
activity_tracker: dict = defaultdict(lambda: defaultdict(int))


class FunCommands(commands.Cog):
    """🎭 Módulo de Entretenimento e Interação Social"""

    def __init__(self, bot):
        self.bot = bot
        # Sessões ativas de jogo da velha: {channel_id: GameState}
        self._ppt_sessions: dict = {}
        # Sessões de trivia ativas: {channel_id: bool}
        self._trivia_sessions: set = set()

    # ── Rastreamento de atividade ──────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        activity_tracker[message.guild.id][message.author.id] += 1

    # ── Comandos sociais existentes ────────────────────────────────────────────

    @commands.command(name='amor', aliases=['love'], help='Calcula a afinidade entre dois usuários.')
    async def amor(self, ctx, user1: discord.Member, user2: discord.Member = None):
        if not user2:
            user2 = user1
            user1 = ctx.author

        percentage = random.randint(0, 100)
        heart = "💔" if percentage < 50 else "💖" if percentage < 90 else "💘"
        bar_filled = round(percentage / 10)
        bar = "❤️" * bar_filled + "🖤" * (10 - bar_filled)

        embed = discord.Embed(title=f"{heart} Analisador de Afinidade", color=0xff0055)
        embed.description = (
            f"🔥 **{user1.display_name}** + **{user2.display_name}**\n"
            f"{bar}\n"
            f"Resultado: **{percentage}%**"
        )
        await ctx.send(embed=embed)

    @commands.command(name='ship', help='Verifica a compatibilidade de um casal.')
    async def ship(self, ctx, u1: discord.Member, u2: discord.Member):
        chance = random.randint(0, 100)
        await ctx.send(
            f"💞 **Matchmaking:** A compatibilidade entre **{u1.display_name}** "
            f"e **{u2.display_name}** é de `{chance}%`!"
        )

    @commands.command(name='sorte', help='Revela sua previsão astrológica do dia.')
    async def sorte(self, ctx):
        sortes = [
            "✨ Grandes oportunidades financeiras surgirão hoje.",
            "🛡️ Proteja seus segredos, alguém está observando.",
            "🚀 Sua criatividade estará em alta nas próximas horas.",
            "🤝 Um reencontro inesperado trará boas notícias.",
            "⚖️ Equilíbrio é a chave para o seu sucesso hoje.",
            "🌟 Uma surpresa agradável está a caminho!",
            "⚡ Hoje é um bom dia para tomar decisões importantes.",
            "🍀 A sorte está do seu lado — aproveite!",
        ]
        await ctx.send(f"🔮 **Oráculo:** {ctx.author.mention}, sua sorte: *{random.choice(sortes)}*")

    @commands.command(name='beijo', aliases=['kiss'], help='Demonstra afeto com um beijo.')
    async def beijo(self, ctx, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("💋 Auto-beijo? Isso que é amor próprio!")
        await ctx.send(f"💋 **Social:** {ctx.author.mention} deixou um beijo carinhoso em {member.mention}!")

    @commands.command(name='tapa', aliases=['slap'], help='Aplica uma correção física amigável.')
    async def tapa(self, ctx, member: discord.Member):
        await ctx.send(f"👋 **Ação:** {ctx.author.mention} deu um tapa pedagógico em {member.mention}!")

    @commands.command(name='abraço', aliases=['hug', 'abraco'], help='Envia um abraço virtual.')
    async def abraco(self, ctx, member: discord.Member):
        await ctx.send(f"🫂 **Social:** {ctx.author.mention} deu um abraço apertado em {member.mention}!")

    @commands.command(name='piada', help='O bot conta uma piada aleatória.')
    async def piada(self, ctx):
        piadas = [
            "Por que o computador foi ao médico? Porque estava com vírus! 🦠",
            "O que o zero disse para o oito? Belo cinto! 8️⃣",
            "Qual é o animal mais antigo? A zebra, porque está em preto e branco. 🦓",
            "Como o átomo atende o telefone? Proton! ☎️",
            "Por que o programador usa óculos escuros? Porque não suporta Java! ☕",
            "Qual é o prato favorito do hacker? Cookies! 🍪",
            "O que o HTML disse pro CSS? Para de me estilizar! 🎨",
        ]
        await ctx.send(f"🤡 **Humor:** {random.choice(piadas)}")

    @commands.command(name='cantada', help='Manda um flerte de alta performance.')
    async def cantada(self, ctx):
        cantadas = [
            "Você não é Wi-Fi, mas sinto uma conexão forte. 📶",
            "Se beleza fosse crime, você estaria em prisão perpétua. 🔒",
            "Me chama de teclado e diz que eu sou o seu tipo. ⌨️",
            "Você é o commit que faltava no meu repositório. 💻",
            "Você deve ser um ângulo de 90°, porque você é perfeito(a)! 📐",
            "Você é tão doce que até o açúcar fica com inveja. 🍬",
        ]
        await ctx.send(f"😏 **Flerte:** {random.choice(cantadas)}")

    @commands.command(name='8ball', help='Consulta a bola mágica. Uso: !8ball [pergunta]')
    async def eightball(self, ctx, *, pergunta: str):
        respostas = [
            "✅ Sim, com certeza!",
            "❌ Não, de jeito nenhum.",
            "🤔 Talvez... depende de você.",
            "🟡 Provavelmente sim.",
            "🟠 Provavelmente não.",
            "⭐ Sem dúvidas!",
            "⏳ Pergunte mais tarde.",
            "🌫️ Não está claro agora.",
            "💯 Pode contar com isso!",
            "🚫 Melhor não contar.",
        ]
        embed = discord.Embed(title="🎱 Bola Mágica", color=0x2b2d31)
        embed.add_field(name="❓ Pergunta", value=pergunta, inline=False)
        embed.add_field(name="🔮 Resposta", value=random.choice(respostas), inline=False)
        await ctx.reply(embed=embed)

    @commands.command(name='caraoucoroa', help='Decisão binária via sorteio.')
    async def caraoucoroa(self, ctx):
        resultado = random.choice(['Cara', 'Coroa'])
        emoji = "🦅" if resultado == "Cara" else "🏛️"
        await ctx.send(f"🪙 **Moeda:** Deu **{resultado}**! {emoji}")

    # ── Pedra-Papel-Tesoura ────────────────────────────────────────────────────

    @commands.command(name='ppt', aliases=['rps'], help='Pedra-papel-tesoura contra o bot ou @user. Uso: !ppt [@user]')
    async def ppt(self, ctx, opponent: discord.Member = None):
        opcoes = ["pedra", "papel", "tesoura"]
        emojis = {"pedra": "🪨", "papel": "📄", "tesoura": "✂️"}
        vence = {"pedra": "tesoura", "papel": "pedra", "tesoura": "papel"}

        if opponent and opponent != ctx.author and not opponent.bot:
            # PvP
            embed = discord.Embed(
                title="✂️ Pedra-Papel-Tesoura — PvP!",
                description=(
                    f"{ctx.author.mention} desafiou {opponent.mention}!\n\n"
                    f"{opponent.mention}, escolha: 🪨 `pedra` | 📄 `papel` | ✂️ `tesoura`\n"
                    f"*(Você tem 30 segundos)*"
                ),
                color=0x5865F2,
            )
            await ctx.send(embed=embed)

            def check_challenger(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in opcoes

            def check_opponent(m):
                return m.author == opponent and m.channel == ctx.channel and m.content.lower() in opcoes

            await ctx.send(f"{ctx.author.mention}, escolha também: 🪨 `pedra` | 📄 `papel` | ✂️ `tesoura`")
            try:
                msg1 = await self.bot.wait_for("message", check=check_challenger, timeout=30)
                msg2 = await self.bot.wait_for("message", check=check_opponent, timeout=30)
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado! Jogo cancelado.")

            c1, c2 = msg1.content.lower(), msg2.content.lower()
            if c1 == c2:
                result = "🤝 **Empate!**"
            elif vence[c1] == c2:
                result = f"🏆 **{ctx.author.display_name} venceu!**"
            else:
                result = f"🏆 **{opponent.display_name} venceu!**"

            embed = discord.Embed(title="✂️ Resultado — PPT", color=0xFFD700)
            embed.add_field(name=ctx.author.display_name, value=f"{emojis[c1]} {c1.capitalize()}", inline=True)
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(name=opponent.display_name, value=f"{emojis[c2]} {c2.capitalize()}", inline=True)
            embed.add_field(name="Resultado", value=result, inline=False)
            await ctx.send(embed=embed)

        else:
            # PvE (contra o bot)
            await ctx.send(
                f"{ctx.author.mention}, escolha: 🪨 `pedra` | 📄 `papel` | ✂️ `tesoura`\n*(30 segundos)*"
            )

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in opcoes

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:
                return await ctx.send("⏰ Tempo esgotado! Jogo cancelado.")

            player = msg.content.lower()
            bot_choice = random.choice(opcoes)

            if player == bot_choice:
                result = "🤝 **Empate!**"
                color = 0xFEE75C
            elif vence[player] == bot_choice:
                result = f"🏆 **{ctx.author.display_name} venceu!**"
                color = 0x57F287
            else:
                result = "🤖 **O bot venceu!**"
                color = 0xED4245

            embed = discord.Embed(title="✂️ Pedra-Papel-Tesoura", color=color)
            embed.add_field(name=ctx.author.display_name, value=f"{emojis[player]} {player.capitalize()}", inline=True)
            embed.add_field(name="VS", value="⚔️", inline=True)
            embed.add_field(name="Jotinha", value=f"{emojis[bot_choice]} {bot_choice.capitalize()}", inline=True)
            embed.add_field(name="Resultado", value=result, inline=False)
            await ctx.send(embed=embed)

    # ── Trivia ─────────────────────────────────────────────────────────────────

    @commands.command(name='trivia', help='Pergunta de conhecimento geral. Responda em 20 segundos!')
    async def trivia(self, ctx):
        if ctx.channel.id in self._trivia_sessions:
            return await ctx.send("⚠️ Já há uma trivia em andamento neste canal!")

        self._trivia_sessions.add(ctx.channel.id)
        q = random.choice(TRIVIA_QUESTIONS)
        opts = q["opts"][:]
        random.shuffle(opts)
        letras = ["A", "B", "C", "D"]

        embed = discord.Embed(
            title="🧠 Trivia — Conhecimento Geral",
            description=f"**{q['q']}**",
            color=0x5865F2,
        )
        for i, opt in enumerate(opts):
            embed.add_field(name=f"{letras[i]})", value=opt, inline=True)
        embed.set_footer(text="Responda com A, B, C ou D em 20 segundos!")
        await ctx.send(embed=embed)

        # Mapeia letra → opção
        letra_para_opt = {letras[i].lower(): opts[i].lower() for i in range(len(opts))}

        def check(m):
            return (
                m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.strip().lower() in ["a", "b", "c", "d"]
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=20)
            escolha = msg.content.strip().lower()
            resposta_dada = letra_para_opt.get(escolha, "")
            correta = q["a"].lower()

            if resposta_dada == correta or correta in resposta_dada:
                await ctx.send(f"✅ **Correto!** {ctx.author.mention} acertou! A resposta era **{q['a']}**. 🎉")
            else:
                await ctx.send(
                    f"❌ **Errado!** {ctx.author.mention}, a resposta correta era **{q['a']}**. Tente de novo!"
                )
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ **Tempo esgotado!** A resposta era **{q['a']}**.")
        finally:
            self._trivia_sessions.discard(ctx.channel.id)

    # ── Duelo ──────────────────────────────────────────────────────────────────

    @commands.command(name='duelo', help='Duelo de dados contra outro usuário. Uso: !duelo @user')
    async def duelo(self, ctx, opponent: discord.Member):
        if opponent == ctx.author:
            return await ctx.send("❌ Você não pode duelar contra si mesmo!")
        if opponent.bot:
            return await ctx.send("❌ Bots não aceitam duelos!")

        embed = discord.Embed(
            title="⚔️ DUELO!",
            description=f"{ctx.author.mention} desafiou {opponent.mention} para um duelo!\n\n"
                        f"{opponent.mention}, aceita o desafio? Responda `sim` ou `não` em 30s.",
            color=0xED4245,
        )
        await ctx.send(embed=embed)

        def check_accept(m):
            return (
                m.author == opponent
                and m.channel == ctx.channel
                and m.content.lower() in ["sim", "não", "nao", "s", "n"]
            )

        try:
            resp = await self.bot.wait_for("message", check=check_accept, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send(f"⏰ {opponent.mention} não respondeu. Duelo cancelado.")

        if resp.content.lower() in ["não", "nao", "n"]:
            return await ctx.send(f"🏳️ {opponent.mention} recusou o duelo. Que covarde! 😄")

        # Rola os dados
        d1 = random.randint(1, 20)
        d2 = random.randint(1, 20)

        embed = discord.Embed(title="⚔️ Resultado do Duelo", color=0xFFD700)
        embed.add_field(name=f"🎲 {ctx.author.display_name}", value=f"**{d1}** pontos", inline=True)
        embed.add_field(name="VS", value="⚔️", inline=True)
        embed.add_field(name=f"🎲 {opponent.display_name}", value=f"**{d2}** pontos", inline=True)

        if d1 > d2:
            embed.add_field(name="🏆 Vencedor", value=f"{ctx.author.mention} venceu o duelo!", inline=False)
        elif d2 > d1:
            embed.add_field(name="🏆 Vencedor", value=f"{opponent.mention} venceu o duelo!", inline=False)
        else:
            embed.add_field(name="🤝 Empate", value="Nenhum dos dois venceu!", inline=False)

        await ctx.send(embed=embed)

    # ── Roleta Russa ───────────────────────────────────────────────────────────

    @commands.command(name='roletarussiana', aliases=['roleta'], help='Jogo de risco! 1 em 6 chances de ser mutado.')
    async def roletarussiana(self, ctx):
        await ctx.send(f"🔫 {ctx.author.mention} gira o tambor... *click*...")
        await asyncio.sleep(2)

        bala = random.randint(1, 6)
        if bala == 1:
            await ctx.send(f"💥 **BANG!** {ctx.author.mention} levou! Mutado por 1 minuto como punição! 😵")
            try:
                from datetime import timedelta
                await ctx.author.timeout(timedelta(minutes=1), reason="Roleta Russa — azar!")
            except Exception:
                await ctx.send("*(Não consegui aplicar o mute, mas você perdeu moralmente!)*")
        else:
            sobreviveu = [
                f"😅 *click*... Sobreviveu! Ufa, {ctx.author.mention}! Sorte sua!",
                f"😤 {ctx.author.mention} sobreviveu! Câmara vazia. Por enquanto...",
                f"🍀 {ctx.author.mention} tem muita sorte! Câmara vazia!",
            ]
            await ctx.send(random.choice(sobreviveu))

    # ── Ranking de atividade ───────────────────────────────────────────────────

    @commands.command(name='ranking', aliases=['topativo', 'ativos'], help='Top 10 usuários mais ativos do servidor.')
    async def ranking(self, ctx):
        guild_data = activity_tracker.get(ctx.guild.id, {})
        if not guild_data:
            return await ctx.send("📊 Ainda não há dados de atividade registrados nesta sessão.")

        sorted_users = sorted(guild_data.items(), key=lambda x: x[1], reverse=True)[:10]
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        embed = discord.Embed(
            title="📊 Ranking de Atividade — Top 10",
            description="Usuários mais ativos nesta sessão:",
            color=0x5865F2,
            timestamp=datetime.now(),
        )

        lines = []
        for i, (user_id, count) in enumerate(sorted_users):
            member = ctx.guild.get_member(user_id)
            name = member.display_name if member else f"Usuário {user_id}"
            lines.append(f"{medals[i]} **{name}** — `{count}` mensagens")

        embed.description = "\n".join(lines)
        embed.set_footer(text="Dados da sessão atual (reiniciados ao reiniciar o bot)")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FunCommands(bot))

