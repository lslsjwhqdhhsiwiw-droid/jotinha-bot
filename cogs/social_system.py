import discord
from discord.ext import commands
import os
import psycopg2
from psycopg2.extras import DictCursor
import random
from datetime import datetime, timedelta


class SistemaSocial(commands.Cog):
    """⭐ Sistema de XP e Economia Profissional (PostgreSQL)"""

    def __init__(self, bot):
        self.bot = bot
        self.db_url = os.getenv('DATABASE_URL')
        self._setup_db()

    def _setup_db(self):
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                coins BIGINT DEFAULT 1000,
                xp BIGINT DEFAULT 0,
                level INTEGER DEFAULT 1,
                last_daily TIMESTAMP,
                last_work TIMESTAMP,
                last_rob TIMESTAMP,
                last_msg TIMESTAMP
            )
        """)
        # Adiciona colunas novas se não existirem (migração segura)
        for col, coltype in [('last_work', 'TIMESTAMP'), ('last_rob', 'TIMESTAMP')]:
            try:
                cur.execute(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {coltype}")
            except Exception:
                pass
        conn.commit()
        cur.close()
        conn.close()

    def _conn(self):
        return psycopg2.connect(self.db_url, cursor_factory=DictCursor)

    def get_user(self, user_id: int) -> dict:
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
        if not user:
            cur.execute("INSERT INTO users (user_id) VALUES (%s) RETURNING *", (user_id,))
            user = cur.fetchone()
            conn.commit()
        cur.close()
        conn.close()
        return dict(user)

    def update_user(self, user_id: int, **kwargs):
        conn = psycopg2.connect(self.db_url)
        cur = conn.cursor()
        set_clause = ", ".join(f"{k} = %s" for k in kwargs)
        cur.execute(
            f"UPDATE users SET {set_clause} WHERE user_id = %s",
            list(kwargs.values()) + [user_id]
        )
        conn.commit()
        cur.close()
        conn.close()

    # ── XP por mensagem ────────────────────────────────────────────────────────

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user = self.get_user(message.author.id)
        new_xp = user['xp'] + random.randint(5, 15)
        new_level = int(new_xp ** (1 / 3))
        updates = {"xp": new_xp}

        if new_level > user['level']:
            updates["level"] = new_level
            await message.channel.send(
                f"🎊 **LEVEL UP!** {message.author.mention} subiu para o **Nível {new_level}**! 🚀"
            )

        self.update_user(message.author.id, **updates)

    # ── Comandos ───────────────────────────────────────────────────────────────

    @commands.command(name='perfil', help='Mostra seu perfil completo.')
    async def profile(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user = self.get_user(member.id)

        embed = discord.Embed(title=f"👤 Perfil — {member.display_name}", color=0x5865F2)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📊 Nível", value=f"**{user['level']}**", inline=True)
        embed.add_field(name="✨ XP", value=f"{user['xp']:,}", inline=True)
        embed.add_field(name="💰 Jotinhas", value=f"**{user['coins']:,}**", inline=True)
        embed.set_footer(text="Continue interagindo para subir de nível!")
        await ctx.send(embed=embed)

    @commands.command(name='saldo', aliases=['coins', 'money', 'carteira'], help='Mostra seu saldo.')
    async def balance(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user = self.get_user(member.id)

        embed = discord.Embed(title="💳 Carteira Digital", color=0xF1C40F)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.description = f"Saldo de {member.mention}"
        embed.add_field(name="💵 Jotinhas", value=f"**{user['coins']:,}**", inline=True)
        embed.add_field(name="📊 Nível", value=f"**{user['level']}**", inline=True)
        embed.set_footer(text="Use !daily para coletar recompensa diária!")
        await ctx.send(embed=embed)

    @commands.command(name='daily', help='Recompensa diária de Jotinhas.')
    async def daily(self, ctx):
        user = self.get_user(ctx.author.id)
        now = datetime.now()
        last = user.get('last_daily')

        if last and (now - last) < timedelta(days=1):
            wait = timedelta(days=1) - (now - last)
            h, r = divmod(int(wait.total_seconds()), 3600)
            m, _ = divmod(r, 60)
            return await ctx.reply(f"⏰ Recompensa já coletada! Volte em **{h}h {m}m**.")

        ganho = random.randint(400, 700)
        self.update_user(ctx.author.id, coins=user['coins'] + ganho, last_daily=now)
        await ctx.reply(f"✅ **Recompensa Diária:** +**{ganho} Jotinhas**! Seu saldo: `{user['coins'] + ganho:,}`")

    @commands.command(name='trabalhar', aliases=['work'], help='Trabalhe para ganhar Jotinhas (cooldown: 1h).')
    async def work(self, ctx):
        user = self.get_user(ctx.author.id)
        now = datetime.now()
        last = user.get('last_work')

        if last and (now - last) < timedelta(hours=1):
            wait = timedelta(hours=1) - (now - last)
            m, s = divmod(int(wait.total_seconds()), 60)
            return await ctx.reply(f"⏳ Você está cansado! Descanse por **{m}m {s}s**.")

        jobs = ["desenvolvedor de software", "designer gráfico", "streamer", "investidor", "engenheiro de IA"]
        ganho = random.randint(150, 500)
        self.update_user(ctx.author.id, coins=user['coins'] + ganho, last_work=now)
        await ctx.reply(f"👷 **Trabalho concluído!** Você atuou como *{random.choice(jobs)}* e recebeu **{ganho} Jotinhas**!")

    @commands.command(name='roubar', aliases=['rob'], help='Tente roubar Jotinhas (cooldown: 30min).')
    async def rob(self, ctx, member: discord.Member):
        if member == ctx.author:
            return await ctx.send("❌ Você não pode se roubar!")

        user = self.get_user(ctx.author.id)
        target = self.get_user(member.id)
        now = datetime.now()
        last = user.get('last_rob')

        if last and (now - last) < timedelta(minutes=30):
            wait = timedelta(minutes=30) - (now - last)
            m, s = divmod(int(wait.total_seconds()), 60)
            return await ctx.reply(f"🚔 A polícia está de olho! Espere **{m}m {s}s**.")

        if target['coins'] < 500:
            return await ctx.send("❌ A vítima está pobre demais para valer o risco!")

        if random.random() < 0.55:
            roubo = int(target['coins'] * random.uniform(0.10, 0.25))
            self.update_user(ctx.author.id, coins=user['coins'] + roubo, last_rob=now)
            self.update_user(member.id, coins=target['coins'] - roubo)
            await ctx.send(f"🥷 **Golpe bem-sucedido!** Você roubou **{roubo:,} Jotinhas** de {member.mention}!")
        else:
            multa = 300
            self.update_user(ctx.author.id, coins=max(0, user['coins'] - multa), last_rob=now)
            await ctx.send(f"👮 **FLAGRANTE!** Você foi pego e pagou **{multa} Jotinhas** de multa!")

    @commands.command(name='apostar', aliases=['bet', 'gamble'], help='Aposte Jotinhas. Uso: !apostar [valor]')
    async def bet(self, ctx, amount: int):
        user = self.get_user(ctx.author.id)
        if amount <= 0:
            return await ctx.send("❌ O valor deve ser maior que zero.")
        if amount > user['coins']:
            return await ctx.send(f"❌ Saldo insuficiente! Você tem apenas **{user['coins']:,} Jotinhas**.")

        if random.random() < 0.45:
            self.update_user(ctx.author.id, coins=user['coins'] + amount)
            await ctx.send(f"🎉 **VITÓRIA!** Você ganhou **{amount:,} Jotinhas**! Saldo: `{user['coins'] + amount:,}`")
        else:
            self.update_user(ctx.author.id, coins=user['coins'] - amount)
            await ctx.send(f"📉 **Derrota...** Você perdeu **{amount:,} Jotinhas**. Saldo: `{user['coins'] - amount:,}`")

    @commands.command(name='rank', aliases=['top', 'ranking'], help='Top 10 mais ricos do servidor.')
    async def leaderboard(self, ctx):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("SELECT user_id, coins, level FROM users ORDER BY coins DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        embed = discord.Embed(title="🏆 Ranking de Fortuna — Top 10", color=0xFFD700)
        lines = []
        for i, row in enumerate(rows):
            u = self.bot.get_user(row['user_id'])
            name = u.name if u else f"Usuário {row['user_id']}"
            lines.append(f"{medals[i]} **{name}** • Lvl {row['level']} • `{row['coins']:,}` Jotinhas")

        embed.description = "\n".join(lines) if lines else "Nenhum registro ainda."
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(SistemaSocial(bot))
