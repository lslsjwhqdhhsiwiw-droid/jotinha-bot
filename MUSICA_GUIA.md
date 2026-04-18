# 🎵 Guia de Comandos de Música - JOTINHA ADM

## 🛠️ Sistema Atualizado
- ✅ **yt-dlp**: Substitui o youtube-dl desatualizado
- ✅ **FFmpeg**: Instalado para processamento de áudio
- ✅ **PyNaCl**: Para codificação de voz
- ✅ **Melhor tratamento de erros**: Mensagens mais claras

## 📋 Comandos Disponíveis

### 🎶 Básicos
- `!play [URL/nome]` - Reproduz música do YouTube
- `!test_music` - Testa o sistema com música livre de direitos
- `!pause` - Pausa a música atual
- `!resume` - Retoma a reprodução
- `!stop` - Para tudo e limpa a fila
- `!skip` - Pula para a próxima música

### 📊 Informações
- `!queue` - Mostra a fila de reprodução
- `!nowplaying` (ou `!np`) - Mostra música atual
- `!volume [0-100]` - Ajusta o volume

### 🚪 Conexão
- `!disconnect` (ou `!leave`) - Desconecta do canal de voz

## 🧪 Como Testar

### 1. Teste Rápido
```
!test_music
```
Este comando usa uma música livre de direitos para testar se tudo funciona.

### 2. Teste com URL
```
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

### 3. Teste com Busca
```
!play relaxing music
```

## ⚠️ Requisitos
1. **Estar em canal de voz**: Você deve estar conectado a um canal de voz
2. **Permissões**: Bot precisa de permissão para conectar e falar
3. **Internet**: Conexão estável para baixar áudio

## 🔧 Solução de Problemas

### Erro: "Você precisa estar em um canal de voz"
- Conecte-se a um canal de voz primeiro

### Erro: "YouTube bloqueou o acesso"
- Tente outra URL
- Aguarde alguns minutos
- Use o comando `!test_music`

### Erro: "Vídeo indisponível"
- O vídeo pode estar privado ou foi removido
- Tente outro vídeo

### Bot não conecta
- Verifique se o bot tem permissões no canal
- Tente em outro canal de voz

## 💡 Dicas
- Use `!test_music` para verificar se tudo funciona
- O bot adiciona músicas à fila automaticamente
- Volume padrão é 50%
- Use URLs diretas do YouTube para melhor resultado