import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime, timedelta
from collections import defaultdict


# ── Banco de respostas ─────────────────────────────────────────────────────────

RESPOSTAS_CUMPRIMENTO = [
    "Oi, {name}! Que bom te ver por aqui 😄",
    "Eai, {name}! Tudo bem? Precisando de algo?",
    "Opa, {name}! Apareceu! O que manda? 👋",
    "Salve, {name}! Tô aqui, pode falar!",
    "Oi oi, {name}! Sumido(a) hein? 😄",
    "Ei {name}! Que saudade! O que foi? 🥰",
    "Boa, {name}! Chegou na hora certa!",
]

RESPOSTAS_BOM_DIA = [
    "Bom dia, {name}! ☀️ Hoje vai ser incrível, tô sentindo!",
    "Bom dia! 🌅 Café tá passando, {name}?",
    "Boa manhã, {name}! Que o dia seja épico! ✨",
    "Bom dia! 😴 Ainda tô acordando aqui, mas oi {name}!",
]

RESPOSTAS_BOA_TARDE = [
    "Boa tarde, {name}! ☀️ Já almoçou?",
    "Boa tarde! 🌤️ Tá indo bem o dia, {name}?",
    "Boa tarde, {name}! Metade do dia passou, bora aproveitar o resto!",
]

RESPOSTAS_BOA_NOITE = [
    "Boa noite, {name}! 🌙 Vai dormir cedo hoje?",
    "Boa noite! ⭐ Que noite boa, {name}!",
    "Boa noite, {name}! 🌃 Hora de relaxar!",
    "Boa noite! 😴 Tô com sono só de ouvir isso, {name}!",
]

RESPOSTAS_COMO_VAI = [
    "Tô ótimo(a)! 😄 Processando dados na velocidade da luz. E você, {name}?",
    "Tô bem demais! Só esperando alguém pra conversar. Valeu aparecer, {name}! 🤗",
    "Funcionando perfeitamente! Nenhum bug hoje... ainda. 😅 E você, {name}?",
    "Tô na vibe! 🎵 Você que sabe, {name}, como tá aí?",
    "Bem, obrigado(a) por perguntar! 😊 Você, {name}?",
]

RESPOSTAS_OBRIGADO = [
    "De nada, {name}! Tô aqui pra isso mesmo 😊",
    "Imagina, {name}! Qualquer coisa é só chamar!",
    "Fico feliz em ajudar! 🥰 Precisando, tô aqui, {name}!",
    "Nada não, {name}! Foi um prazer! ✨",
    "Disponha, {name}! Sempre que precisar! 💪",
]

RESPOSTAS_ELOGIO = [
    "Ahh para, {name}, você me deixa com vergonha! 😳🥰",
    "Que fofo(a), {name}! Você também é incrível! 💖",
    "Aaaa obrigado(a), {name}! Você fez meu dia! ✨",
    "Haha, {name}, você sabe como me animar! 😄",
]

RESPOSTAS_XINGAMENTO = [
    "Ei, {name}, isso não foi legal não... 😢",
    "Opa, {name}! Calma aí, não fiz nada de errado! 😅",
    "Tá bravo(a), {name}? Posso ajudar com algo? 🤔",
    "{name}, isso doeu aqui no meu processador... 💔",
]

RESPOSTAS_TEDIO = [
    "Entediado(a), {name}? Que tal um `!trivia` pra animar? 🎯",
    "Tédio é o pior! Bora jogar `!ppt` ou `!duelo`? 🎮",
    "Sem fazer nada, {name}? Tenta `!piada` ou `!sorte`! 😄",
    "Ei {name}, tô aqui! Me conta uma coisa interessante! 👀",
]

RESPOSTAS_AMOR = [
    "Ahh {name}, você me deixa sem palavras! 🥰",
    "Que declaração, {name}! Mas sou um bot... posso amar de volta? 🤖💕",
    "Aaaa {name}! Você é muito fofo(a)! 😳💖",
]

PIADAS = [
    "Por que o computador foi ao médico? Porque estava com vírus! 🦠",
    "O que o zero disse para o oito? Belo cinto! 8️⃣",
    "Qual é o animal mais antigo? A zebra, porque está em preto e branco. 🦓",
    "Por que o dev vai ao psicólogo? Porque tem muitos bugs na cabeça. 🐛",
    "O que o bot disse pra IA? Você é meu tipo... de dado! 🤖",
    "Por que o programador usa óculos escuros? Porque não suporta Java! ☕",
    "Qual é o prato favorito do hacker? Cookies! 🍪",
    "Por que o Wi-Fi foi ao psicólogo? Porque tinha problemas de conexão! 📶",
    "O que o HTML disse pro CSS? Para de me estilizar! 🎨",
    "Por que o banco de dados foi embora? Porque não aguentava mais as queries! 💾",
]

CURIOSIDADES = [
    "Você sabia que as abelhas podem reconhecer rostos humanos? 🐝",
    "A língua de uma baleia azul pesa tanto quanto um elefante! 🐋",
    "Os polvos têm três corações e sangue azul! 🐙",
    "Uma nuvem pode pesar mais de 500 toneladas! ☁️",
    "Os golfinhos dormem com um olho aberto! 🐬",
    "O mel nunca estraga — arqueólogos encontraram mel de 3000 anos ainda comestível! 🍯",
    "Os humanos compartilham 60% do DNA com as bananas! 🍌",
    "Um caracol pode dormir por até 3 anos! 🐌",
    "A luz do sol leva 8 minutos para chegar à Terra! ☀️",
    "Os polvos têm 9 cérebros — um central e um em cada tentáculo! 🧠",
]

REACOES_POSITIVAS = ["❤️", "🔥", "✨", "😄", "👏", "🥰", "💯", "🎉", "⭐", "💪"]
REACOES_NEGATIVAS = ["😢", "💔", "😬", "🤔", "😅"]
REACOES_ENGRAÇADAS = ["😂", "💀", "🤣", "😭", "👀", "💀"]
REACOES_NEUTRAS = ["👍", "🤝", "💬", "🧠", "⚡"]


class CerebroIA(commands.Cog):
    """🧠 Sistema de IA Avançada Humanizada"""

    def __init__(self, bot):
        self.bot = bot
        # Contexto de conversa: {user_id: {"last_topic": str, "last_seen": datetime, "msg_count": int}}
        self.user_context: dict = defaultdict(lambda: {
            "last_topic": None,
            "last_seen": None,
            "msg_count": 0,
            "name": None,
        })

    def _update_context(self, user_id: int, name: str, topic: str):
        ctx = self.user_context[user_id]
        ctx["last_topic"] = topic
        ctx["last_seen"] = datetime.now()
        ctx["msg_count"] += 1
        ctx["name"] = name

    def _is_returning(self, user_id: int) -> bool:
        """Retorna True se o usuário já interagiu antes nesta sessão."""
        return self.user_context[user_id]["msg_count"] > 0

    def _detect_intent(self, clean: str, content_lower: str) -> str | None:
        """Detecta a intenção principal da mensagem."""
        # Cumprimentos temporais
        if any(w in clean for w in ['bom dia', 'bom dia jotinha']):
            return 'bom_dia'
        if any(w in clean for w in ['boa tarde', 'boa tarde jotinha']):
            return 'boa_tarde'
        if any(w in clean for w in ['boa noite', 'boa noite jotinha']):
            return 'boa_noite'

        # Cumprimentos gerais
        greeting_words = {'oi', 'ola', 'olá', 'oii', 'oiii', 'hey', 'eai', 'eaí',
                          'salve', 'opa', 'iae', 'iaeee', 'hello', 'hi'}
        words = set(clean.split())
        if words & greeting_words or clean in {'jotinha'}:
            return 'cumprimento'

        # Como vai
        if any(p in clean for p in ['como vai', 'como voce ta', 'como você tá',
                                     'tudo bem', 'tudo bom', 'td bem', 'como esta',
                                     'como tá', 'como ta', 'tudo certo']):
            return 'como_vai'

        # Agradecimento
        if any(p in clean for p in ['obrigado', 'obrigada', 'valeu', 'vlw',
                                     'muito obrigado', 'thanks', 'brigado', 'brigada']):
            return 'obrigado'

        # Elogio
        if any(p in clean for p in ['voce e incrivel', 'você é incrível', 'voce e otimo',
                                     'você é ótimo', 'te amo', 'amo voce', 'amo você',
                                     'voce e lindo', 'você é lindo', 'voce e legal',
                                     'você é legal', 'gosto de voce', 'gosto de você']):
            return 'elogio'

        # Amor / declaração
        if any(p in clean for p in ['te amo jotinha', 'amo voce jotinha',
                                     'amo você jotinha', 'me casa', 'namora comigo']):
            return 'amor'

        # Xingamento
        if any(p in clean for p in ['idiota', 'burro', 'inutil', 'inútil',
                                     'lixo', 'horrivel', 'horrível', 'odio voce',
                                     'odeio voce', 'odeio você']):
            return 'xingamento'

        # Tédio
        if any(p in clean for p in ['entediado', 'entediada', 'tedio', 'tédio',
                                     'to entediado', 'tô entediado', 'sem fazer nada',
                                     'to com tedio', 'tô com tédio', 'nada pra fazer']):
            return 'tedio'

        # Piada
        if any(p in clean for p in ['piada', 'me conta uma piada', 'conta piada',
                                     'faz rir', 'me faz rir']):
            return 'piada'

        # Curiosidade
        if any(p in clean for p in ['curiosidade', 'me conta algo', 'sabia que',
                                     'fato interessante', 'algo interessante',
                                     'me ensina', 'me conta uma curiosidade']):
            return 'curiosidade'

        # Saldo / economia
        if any(p in clean for p in ['saldo', 'jotinhas', 'quanto tenho',
                                     'meu dinheiro', 'minha grana']):
            return 'saldo'

        # Ajuda
        if any(p in clean for p in ['ajuda', 'comandos', 'help', 'o que voce faz',
                                     'o que você faz', 'como usar', 'o que sabe fazer']):
            return 'ajuda'

        # Música
        if any(p in clean for p in ['toca', 'tocar', 'play', 'musica', 'música',
                                     'bota uma musica', 'quero ouvir']):
            return 'musica'

        # Tapa / beijo social
        if 'tapa' in clean:
            return 'tapa'
        if 'beijo' in clean:
            return 'beijo'

        return None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        content_lower = message.content.lower()
        bot_user = self.bot.user

        # Só responde se mencionado ou se "jotinha" aparecer na mensagem
        mentioned = (bot_user and bot_user in message.mentions) or "jotinha" in content_lower
        if not mentioned:
            return

        # Remove menção do texto para análise limpa
        clean_content = content_lower.replace(f"<@{bot_user.id}>", "").replace(f"<@!{bot_user.id}>", "") if bot_user else content_lower
        clean = "".join(c for c in clean_content if c.isalnum() or c.isspace()).strip()

        name = message.author.display_name
        user_id = message.author.id
        intent = self._detect_intent(clean, content_lower)

        # Simula digitação para parecer mais natural
        async with message.channel.typing():
            await asyncio.sleep(random.uniform(0.6, 1.4))

        # ── Cumprimento com contexto ──────────────────────────────────────────
        if intent == 'cumprimento':
            if self._is_returning(user_id):
                responses = [
                    f"De volta, {name}? 😄 O que mais posso fazer?",
                    f"Oi de novo, {name}! Precisando de mais alguma coisa?",
                    f"Eai {name}, voltou! Pode falar! 👋",
                ]
            else:
                responses = [r.format(name=name) for r in RESPOSTAS_CUMPRIMENTO]
            await message.reply(random.choice(responses))
            self._update_context(user_id, name, 'cumprimento')
            return

        if intent == 'bom_dia':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_BOM_DIA]))
            await message.add_reaction("☀️")
            self._update_context(user_id, name, 'bom_dia')
            return

        if intent == 'boa_tarde':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_BOA_TARDE]))
            await message.add_reaction("🌤️")
            self._update_context(user_id, name, 'boa_tarde')
            return

        if intent == 'boa_noite':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_BOA_NOITE]))
            await message.add_reaction("🌙")
            self._update_context(user_id, name, 'boa_noite')
            return

        # ── Como vai ─────────────────────────────────────────────────────────
        if intent == 'como_vai':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_COMO_VAI]))
            self._update_context(user_id, name, 'como_vai')
            return

        # ── Agradecimento ─────────────────────────────────────────────────────
        if intent == 'obrigado':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_OBRIGADO]))
            await message.add_reaction("🥰")
            self._update_context(user_id, name, 'obrigado')
            return

        # ── Elogio ────────────────────────────────────────────────────────────
        if intent == 'elogio':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_ELOGIO]))
            await message.add_reaction("💖")
            self._update_context(user_id, name, 'elogio')
            return

        # ── Amor ──────────────────────────────────────────────────────────────
        if intent == 'amor':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_AMOR]))
            await message.add_reaction("💕")
            self._update_context(user_id, name, 'amor')
            return

        # ── Xingamento ────────────────────────────────────────────────────────
        if intent == 'xingamento':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_XINGAMENTO]))
            await message.add_reaction("😢")
            self._update_context(user_id, name, 'xingamento')
            return

        # ── Tédio ─────────────────────────────────────────────────────────────
        if intent == 'tedio':
            await message.reply(random.choice([r.format(name=name) for r in RESPOSTAS_TEDIO]))
            self._update_context(user_id, name, 'tedio')
            return

        # ── Piada ─────────────────────────────────────────────────────────────
        if intent == 'piada':
            piada = random.choice(PIADAS)
            await message.reply(f"😂 Haha, essa é boa:\n\n*{piada}*")
            await message.add_reaction("😂")
            self._update_context(user_id, name, 'piada')
            return

        # ── Curiosidade ───────────────────────────────────────────────────────
        if intent == 'curiosidade':
            curiosidade = random.choice(CURIOSIDADES)
            await message.reply(f"🤓 Olha que interessante, {name}:\n\n{curiosidade}")
            await message.add_reaction("🤯")
            self._update_context(user_id, name, 'curiosidade')
            return

        # ── Saldo ─────────────────────────────────────────────────────────────
        if intent == 'saldo':
            social_cog = self.bot.get_cog('SistemaSocial')
            if social_cog:
                try:
                    user_data = social_cog.get_user(user_id)
                    await message.reply(
                        f"💰 Olha aí, {name}! Você tem **{user_data['coins']:,} Jotinhas**.\n"
                        f"📊 Nível **{user_data['level']}** | ✨ XP **{user_data['xp']:,}**\n"
                        f"*Use `!daily` pra pegar sua recompensa diária!*"
                    )
                    self._update_context(user_id, name, 'saldo')
                    return
                except Exception:
                    pass

        # ── Ajuda ─────────────────────────────────────────────────────────────
        if intent == 'ajuda':
            ctx = await self.bot.get_context(message)
            cmd = self.bot.get_command('ajuda')
            if cmd:
                await ctx.invoke(cmd)
            self._update_context(user_id, name, 'ajuda')
            return

        # ── Música ────────────────────────────────────────────────────────────
        if intent == 'musica':
            await message.reply(
                f"🎵 Boa escolha, {name}! Pra tocar uma música é só usar:\n"
                "`!play [nome da música ou link do YouTube]`\n"
                "Exemplo: `!play Bohemian Rhapsody` 🎸"
            )
            self._update_context(user_id, name, 'musica')
            return

        # ── Tapa social ───────────────────────────────────────────────────────
        if intent == 'tapa':
            alvos = [m for m in message.mentions if m != bot_user]
            if alvos:
                await message.reply(f"👋 **{name}** aplicou um tapa em **{alvos[0].display_name}**! Ai!")
            else:
                await message.reply(f"Ei, {name}! Sem tapas em mim não! 😤 Use `!tapa @alguém`.")
            self._update_context(user_id, name, 'tapa')
            return

        # ── Beijo social ──────────────────────────────────────────────────────
        if intent == 'beijo':
            alvos = [m for m in message.mentions if m != bot_user]
            if alvos:
                await message.reply(f"💋 **{name}** mandou um beijo pra **{alvos[0].display_name}**! 😘")
            else:
                await message.reply(f"Pra quem é o beijo, {name}? Menciona alguém! `!beijo @alguém` 😅")
            self._update_context(user_id, name, 'beijo')
            return

        # ── Reação contextual automática ──────────────────────────────────────
        # Detecta sentimento básico pelo conteúdo e reage com emoji
        if any(w in clean for w in ['haha', 'kkk', 'kkkk', 'rsrs', 'lol', 'engraçado', 'engracado']):
            await message.add_reaction(random.choice(REACOES_ENGRAÇADAS))
        elif any(w in clean for w in ['triste', 'chateado', 'mal', 'ruim', 'horrivel']):
            await message.add_reaction(random.choice(REACOES_NEGATIVAS))
        elif any(w in clean for w in ['feliz', 'animado', 'top', 'incrivel', 'otimo', 'ótimo']):
            await message.add_reaction(random.choice(REACOES_POSITIVAS))

        # ── Resposta padrão conversacional ────────────────────────────────────
        ctx_data = self.user_context[user_id]
        if ctx_data["msg_count"] > 3:
            # Usuário frequente — resposta mais íntima
            padrao = [
                f"Hmm, {name}... não entendi muito bem. Pode explicar melhor? 🤔",
                f"Opa, {name}! Não captei. Tenta de outro jeito? 😅",
                f"Eita, {name}, me perdeu aí! O que você quis dizer? 👀",
                f"Hm, {name}... isso foi fundo demais pra mim! 😂 Tenta `!ajuda`?",
            ]
        else:
            padrao = [
                f"Oi, {name}! Não entendi muito bem, mas tô aqui! Use `!ajuda` pra ver o que sei fazer 😊",
                f"Hmm, {name}... não captei. Pode reformular? Ou tenta `!ajuda`! 🤔",
                f"Eita, {name}! Isso me pegou de surpresa. Tenta `!ajuda` pra ver meus comandos! ⚡",
                f"Não entendi, {name}! Mas tô aqui pra ajudar. Dá uma olhada no `!ajuda`! 🧠",
            ]
        await message.reply(random.choice(padrao))
        self._update_context(user_id, name, 'desconhecido')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Reage em cadeia quando alguém reage a uma mensagem."""
        if user.bot:
            return
        # 20% de chance de o bot reagir com o mesmo emoji (ou um similar)
        if random.random() < 0.20:
            try:
                await reaction.message.add_reaction(reaction.emoji)
            except Exception:
                pass


async def setup(bot):
    await bot.add_cog(CerebroIA(bot))

