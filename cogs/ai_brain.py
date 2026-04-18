import discord
from discord.ext import commands
import random


class CerebroIA(commands.Cog):
    """🧠 Sistema de IA Avançada Humanizada"""

    def __init__(self, bot):
        self.bot = bot

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

        # Remove pontuação para comparação limpa
        clean = "".join(c for c in content_lower if c.isalnum() or c.isspace()).strip()

        # ── Cumprimentos ──
        greetings = {'oi', 'olá', 'ola', 'oii', 'oiii', 'hey', 'bom dia', 'boa tarde', 'boa noite', 'jotinha'}
        if clean in greetings:
            responses = [
                f"Olá, {message.author.display_name}! Protocolos ativos. Como posso auxiliar?",
                f"Saudações! Estou pronto. O que deseja?",
                f"Sistema online. Olá, {message.author.mention}! 👋",
                f"Oi! Minha base de dados está pronta para você.",
            ]
            await message.reply(random.choice(responses))
            return

        # ── Piada ──
        if 'piada' in clean:
            piadas = [
                "Por que o computador foi ao médico? Porque estava com vírus! 🦠",
                "O que o zero disse para o oito? Belo cinto! 8️⃣",
                "Qual é o animal mais antigo? A zebra, porque está em preto e branco. 🦓",
                "Por que o dev vai ao psicólogo? Porque tem muitos bugs na cabeça. 🐛",
                "O que o bot disse pra IA? Você é meu tipo... de dado! 🤖",
            ]
            await message.reply(f"😂 Aqui vai uma piada:\n\n*{random.choice(piadas)}*")
            return

        # ── Saldo ──
        if 'saldo' in clean or 'jotinhas' in clean:
            social_cog = self.bot.get_cog('SistemaSocial')
            if social_cog:
                try:
                    user_data = social_cog.get_user(message.author.id)
                    await message.reply(
                        f"💰 **Status Financeiro:** Você possui **{user_data['coins']} Jotinhas**.\n"
                        f"📊 Nível **{user_data['level']}** | ✨ XP **{user_data['xp']}**"
                    )
                    return
                except Exception:
                    pass

        # ── Ajuda / Comandos ──
        if 'ajuda' in clean or 'comandos' in clean or 'help' in clean:
            ctx = await self.bot.get_context(message)
            cmd = self.bot.get_command('ajuda')
            if cmd:
                await ctx.invoke(cmd)
            return

        # ── Tapa social ──
        if 'tapa' in clean:
            alvos = [m for m in message.mentions if m != bot_user]
            if alvos:
                await message.reply(f"👋 **{message.author.display_name}** aplicou um tapa em **{alvos[0].display_name}**!")
            else:
                await message.reply("🤖 Sem tapas em mim, por favor! Uso `!tapa @alguém`.")
            return

        # ── Beijo social ──
        if 'beijo' in clean:
            alvos = [m for m in message.mentions if m != bot_user]
            if alvos:
                await message.reply(f"💋 **{message.author.display_name}** mandou um beijo para **{alvos[0].display_name}**!")
            else:
                await message.reply("😅 Para quem é o beijo? Mencione alguém! `!beijo @alguém`")
            return

        # ── Música ──
        music_keywords = ['toca', 'tocar', 'play', 'música', 'musica', 'bota']
        if any(kw in clean for kw in music_keywords):
            await message.reply(
                "🎵 **Motor de Áudio:** Para tocar uma música use:\n"
                "`!play [nome da música ou link do YouTube]`\n"
                "Exemplo: `!play Bohemian Rhapsody`"
            )
            return

        # ── Resposta padrão ──
        padrao = [
            "Interessante... Minha IA está analisando sua mensagem. 🧠",
            "Processando dados... Como posso ajudar especificamente?",
            f"Estou aqui, {message.author.display_name}! Use `!ajuda` para ver todos os comandos.",
            "Sistema em operação. Me diga o que precisa! ⚡",
        ]
        await message.reply(random.choice(padrao))


async def setup(bot):
    await bot.add_cog(CerebroIA(bot))
