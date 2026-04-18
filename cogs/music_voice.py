import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

# Opções para o yt-dlp (busca e extração de stream)
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
}

# Opções para o FFmpeg reconectar se a stream cair
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}


def search_yt(query: str):
    """Busca uma música no YouTube e retorna os dados."""
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            # Se não for URL, faz busca pelo texto
            if not query.startswith('http'):
                query = f"ytsearch:{query}"
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return {
                'url': info['url'],
                'title': info.get('title', 'Título Desconhecido'),
                'webpage_url': info.get('webpage_url', ''),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Desconhecido'),
            }
        except Exception as e:
            print(f"[MusicVoice] Erro na busca: {e}")
            return None


class MusicVoice(commands.Cog):
    """🎵 Engine de Áudio — Streaming do YouTube em alta performance."""

    def __init__(self, bot):
        self.bot = bot
        # Fila e estado por servidor {guild_id: deque}
        self.queues: dict[int, deque] = {}
        # Mensagem "Tocando agora" para editar depois
        self.now_playing_msg: dict[int, discord.Message] = {}

    # ─── Helpers ───────────────────────────────────────────────────────────────

    def get_queue(self, guild_id: int) -> deque:
        if guild_id not in self.queues:
            self.queues[guild_id] = deque()
        return self.queues[guild_id]

    async def _connect(self, ctx) -> discord.VoiceClient | None:
        """Conecta ou move o bot ao canal de voz do usuário."""
        if not ctx.author.voice:
            await ctx.send("❌ **Erro:** Você precisa estar em um canal de voz primeiro.")
            return None

        channel = ctx.author.voice.channel

        if ctx.voice_client:
            if ctx.voice_client.channel != channel:
                await ctx.voice_client.move_to(channel)
            return ctx.voice_client
        
        try:
            vc = await channel.connect(timeout=30.0, self_deaf=True)
            return vc
        except asyncio.TimeoutError:
            await ctx.send("❌ **Timeout:** Não consegui conectar ao canal. Tente mudar a região do canal de voz.")
            return None
        except Exception as e:
            await ctx.send(f"❌ **Erro de conexão:** {e}")
            return None

    def _play_next(self, ctx):
        """Callback: toca a próxima música da fila quando a atual termina."""
        queue = self.get_queue(ctx.guild.id)
        if queue:
            song = queue.popleft()
            self.bot.loop.create_task(self._stream(ctx, song))

    async def _stream(self, ctx, song: dict):
        """Inicia a reprodução de uma música."""
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return

        source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(source, volume=0.6)

        vc.play(source, after=lambda e: self._play_next(ctx))

        # Monta o embed "Tocando Agora"
        embed = discord.Embed(
            title="🎶 Tocando Agora",
            description=f"**[{song['title']}]({song['webpage_url']})**",
            color=0x1DB954
        )
        if song['thumbnail']:
            embed.set_thumbnail(url=song['thumbnail'])
        embed.add_field(name="👤 Canal", value=song['uploader'], inline=True)

        if song['duration']:
            mins, secs = divmod(song['duration'], 60)
            embed.add_field(name="⏱️ Duração", value=f"{mins}:{secs:02d}", inline=True)

        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )

        try:
            msg = await ctx.send(embed=embed)
            self.now_playing_msg[ctx.guild.id] = msg
        except Exception:
            pass

    # ─── Comandos ──────────────────────────────────────────────────────────────

    @commands.command(name='play', aliases=['p', 'tocar'], help='Busca e toca uma música do YouTube.')
    async def play(self, ctx, *, search: str):
        vc = await self._connect(ctx)
        if not vc:
            return

        async with ctx.typing():
            msg = await ctx.send(f"🔍 **Buscando:** `{search}`...")
            song = await self.bot.loop.run_in_executor(None, search_yt, search)

        if not song:
            await msg.edit(content="❌ **Não encontrei nada.** Tente outra música.")
            return

        queue = self.get_queue(ctx.guild.id)

        if vc.is_playing() or vc.is_paused():
            queue.append(song)
            embed = discord.Embed(
                title="📋 Adicionado à Fila",
                description=f"**[{song['title']}]({song['webpage_url']})**\nPosição na fila: **{len(queue)}**",
                color=0x5865F2
            )
            await msg.edit(content="", embed=embed)
        else:
            await msg.delete()
            await self._stream(ctx, song)

    @commands.command(name='skip', aliases=['s', 'pular'], help='Pula para a próxima música.')
    async def skip(self, ctx):
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            return await ctx.send("❌ **Erro:** Nenhuma música tocando no momento.")
        ctx.voice_client.stop()
        await ctx.send("⏭️ **Pulado!** Tocando a próxima da fila.")

    @commands.command(name='pause', aliases=['pausar'], help='Pausa a música atual.')
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ **Pausado.**")
        else:
            await ctx.send("❌ Nenhuma música tocando.")

    @commands.command(name='resume', aliases=['continuar'], help='Retoma a música pausada.')
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ **Continuando...**")
        else:
            await ctx.send("❌ A música não está pausada.")

    @commands.command(name='stop', aliases=['parar', 'dc', 'sair'], help='Para a música e desconecta o bot.')
    async def stop(self, ctx):
        if ctx.voice_client:
            self.get_queue(ctx.guild.id).clear()
            await ctx.voice_client.disconnect()
            await ctx.send("👋 **Transmissão encerrada.** Fila limpa.")
        else:
            await ctx.send("❌ Não estou conectado a nenhum canal de voz.")

    @commands.command(name='fila', aliases=['queue', 'q'], help='Mostra as músicas na fila.')
    async def queue_show(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return await ctx.send("📋 **Fila vazia.** Use `!play` para adicionar músicas.")

        embed = discord.Embed(title="📋 Fila de Reprodução", color=0x5865F2)
        lista = "\n".join(
            [f"**{i+1}.** [{s['title']}]({s['webpage_url']})" for i, s in enumerate(list(queue)[:10])]
        )
        embed.description = lista
        if len(queue) > 10:
            embed.set_footer(text=f"...e mais {len(queue)-10} músicas.")
        await ctx.send(embed=embed)

    @commands.command(name='volume', aliases=['vol'], help='Ajusta o volume (0-100).')
    async def volume(self, ctx, vol: int):
        if not (0 <= vol <= 100):
            return await ctx.send("❌ Volume deve ser entre **0** e **100**.")
        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = vol / 100
            await ctx.send(f"🔊 **Volume ajustado para `{vol}%`**")
        else:
            await ctx.send("❌ Nenhuma música tocando no momento.")

    @commands.command(name='conectar', aliases=['join', 'entrar'], help='Conecta ao canal de voz.')
    async def conectar(self, ctx):
        vc = await self._connect(ctx)
        if vc:
            await ctx.send(f"🔊 **Conectado a:** `{vc.channel.name}`")


async def setup(bot):
    await bot.add_cog(MusicVoice(bot))
