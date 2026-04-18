# 🤖 JOTINHA ADM - Guia Completo de Comandos

## 📋 Comandos Básicos
- `!ping` - Testa latência do bot
- `!ajuda` - Mostra lista de comandos disponíveis

## 🛡️ Moderação Básica
- `!kick @membro [motivo]` - Expulsa um membro
- `!ban @membro [motivo]` - Bane um membro
- `!unban nome#discriminador` - Desbane um usuário
- `!mute @membro [tempo] [motivo]` - Silencia temporariamente
- `!unmute @membro` - Remove silenciamento
- `!clear [quantidade]` - Apaga mensagens (max 100)

## ⚔️ Administração Avançada
- `!nuke` - **CUIDADO!** Apaga TODAS as mensagens do canal
- `!slowmode [segundos]` - Define modo lento (0-21600s)
- `!lock` - Bloqueia canal para @everyone
- `!unlock` - Desbloqueia canal
- `!massban @user1 @user2 @user3` - Bane múltiplos usuários
- `!masskick @user1 @user2 @user3` - Expulsa múltiplos usuários
- `!banlist` - Mostra lista de usuários banidos
- `!serverinfo` - Informações detalhadas do servidor
- `!purge_user @membro [limite]` - Remove mensagens de um usuário específico

## 🎵 Música
- `!play [URL/nome]` - Reproduz música do YouTube
- `!pause` - Pausa música atual
- `!resume` - Retoma reprodução
- `!stop` - Para música e limpa fila
- `!skip` - Pula para próxima música
- `!queue` - Mostra fila de reprodução
- `!volume [0-100]` - Ajusta volume
- `!disconnect` - Desconecta do canal de voz
- `!nowplaying` - Mostra música atual

## 🌐 APIs e Informações
- `!clima [cidade]` - Consulta clima
- `!cotacao [moeda]` - Cotação de moedas (USD, EUR, etc.)
- `!cep [número]` - Consulta informações de CEP
- `!piada` - Piada aleatória
- `!fato` - Fato curioso aleatório

## 🛒 Ofertas de Lojas
- `!ofertas` - Busca ofertas de todas as lojas
- `!mercadolivre` ou `!ml` - Ofertas do Mercado Livre
- `!amazon` - Ofertas da Amazon Brasil
- `!kabum` - Ofertas da Kabum
- `!magalu` - Ofertas do Magazine Luiza
- `!ofertas_cache` - Mostra último cache de ofertas

## 🎭 Sistema de Reações
- `!reagir [ID_mensagem] [emoji]` - Adiciona reação a mensagem
- `!reagir_multiplo [ID_mensagem] [quantidade]` - Múltiplas reações
- `!reacao_bomba [ID_mensagem]` - "Bomba" de reações (8 emojis)
- `!toggle_auto_react` - Liga/desliga reações automáticas
- `!limpar_reacoes [ID_mensagem]` - Remove todas as reações
- `!reacoes_info` - Informações sobre sistema de reações

### 🎯 Palavras que Triggam Reações Automáticas:
bot, obrigado, valeu, legal, top, perfeito, incrível, parabéns, festa, pizza, hambúrguer, café, cerveja, futebol, música, jogo, amor, triste

## 🎮 Comandos Divertidos
- `!8ball [pergunta]` - Bola mágica 8
- `!dado [lados]` - Rola um dado (padrão: 6 lados)
- `!dados [quantidade] [lados]` - Rola múltiplos dados
- `!escolher opção1 opção2 opção3...` - Escolhe entre opções
- `!verdade` - Pergunta de verdade
- `!desafio` - Recebe um desafio
- `!rps [pedra/papel/tesoura]` - Pedra, papel, tesoura
- `!coinflip` - Cara ou coroa
- `!amor @pessoa1 @pessoa2` - Calculadora de amor
- `!ship @pessoa1 @pessoa2` - Cria ship names
- `!pergunta` - Pergunta aleatória para quebrar gelo
- `!simulador [evento]` - Simula chances de algo acontecer

## 🔒 Permissões Necessárias

### Comandos de Moderação:
- **Kick**: Expulsar membros
- **Ban**: Banir membros
- **Mute/Clear**: Gerenciar mensagens

### Comandos de Admin Avançado:
- **Nuke/Lock/Unlock**: Gerenciar canais
- **Massban/Masskick**: Banir/Expulsar membros
- **Slowmode**: Gerenciar canais

### Comandos de Reação:
- **Reagir**: Gerenciar mensagens
- **Toggle Auto-React**: Gerenciar servidor

## 💡 Dicas de Uso

1. **Reações Automáticas**: O bot reage automaticamente quando você menciona certas palavras
2. **Keep-Alive**: Bot tem sistema para ficar sempre online
3. **Cache de Ofertas**: Ofertas são salvas temporariamente para acesso rápido
4. **Segurança**: Comandos perigosos como `!nuke` pedem confirmação
5. **Cooldowns**: Alguns comandos têm tempo de espera para evitar spam

## 🆘 Em Caso de Problemas

- Use `!ping` para testar se o bot está respondendo
- Verifique suas permissões para comandos de moderação
- Comandos de música precisam que você esteja em um canal de voz
- APIs externas podem estar temporariamente indisponíveis

---
*Bot desenvolvido para comunidades brasileiras com funcionalidades completas de moderação, entretenimento e informação.*