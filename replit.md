# Overview

This is a modernized Discord bot project built in Portuguese for Brazilian users, specifically targeting young adults (20-25 years). The bot provides moderation tools, simplified music system, gaming-focused content (Free Fire and general gaming), and entertainment features with age-appropriate humor.

The bot uses a modular architecture with separate cogs (Discord.py extensions) for different functionality areas, making it easy to maintain and extend features independently. Recent major renovation focused on replacing general news with gaming content and completely overhauling the jokes system with 300+ modern jokes.

## Recent Changes (2025-09-18): Sistema de Interação Revolucionário
- **Sistema Social Avançado**: Implementado sistema completo de relacionamentos com perfis personalizados, compatibilidade avançada, speed dating e sugestões de amizade
- **Melhorias de Interação**: Novo sistema de comandos mais intuitivos com cumprimentos (!oi), agradecimentos (!obrigado) e música rápida (!m)
- **Respostas Naturais**: Sistema conversacional com detecção de sentimento, contexto por horário e memória de interações
- **Reações Inteligentes**: Bot reage automaticamente a mensagens positivas e sugere comandos relevantes
- **Ajuda Interativa**: Sistema de ajuda organizado por categorias com guia detalhado
- **Guia de Personalização**: Criado guia completo para trocar foto/avatar do bot via Discord Developer Portal
- **Integração IA-Social**: IA registra automaticamente pontos sociais e analisa conexões do servidor

# User Preferences

Preferred communication style: Simple, everyday language.
Content Focus: Gaming content (especially Free Fire), modern humor for young adults (20-25 years), simplified technical solutions over complex fixes.
Target Audience: Young Brazilian adults who enjoy gaming and modern internet culture.

# System Architecture

## Bot Framework
- **Discord.py**: Core framework using the commands extension for structured command handling
- **Cog System**: Modular architecture where each major feature is implemented as a separate cog
- **Event-driven**: Uses Discord events and command decorators for bot interactions
- **Prefix Commands**: Uses '!' as the command prefix for all bot interactions
- **Keep-Alive System**: Flask-based HTTP server on port 8080 for uptime monitoring and health checks
- **AI-Driven Administration**: Central AI system that administers and controls all other bot modules

## Core Components

### Main Bot (bot.py)
- Central bot instance with proper Discord intents configuration
- Dynamic cog loading with error handling for graceful degradation
- Status management showing help command in bot presence

### Moderation System (cogs/moderation.py)
- Permission-based commands for server administration
- Kick and ban functionality with reason logging
- Rich embed responses for moderation actions
- Built-in error handling for permission issues

### Simplified Music System (cogs/music_simple.py)
- Search-based system that sends YouTube links instead of voice playback
- Simplified approach chosen for better reliability in cloud environments
- No voice channel connectivity to avoid Discord/Replit audio issues
- Focus on music discovery rather than bot-based playback

### API Integration (cogs/api_commands.py)
- Weather data from OpenWeatherMap API
- External API request handling with timeout protection
- Environment variable configuration for API keys
- Structured error responses for API failures

### Web Scraping System
- **loja_scrapers.py**: Specialized scrapers for Brazilian e-commerce sites
- **web_scraper.py**: General web content extraction using trafilatura
- **cogs/ofertas.py**: Discord interface for deal aggregation
- BeautifulSoup for HTML parsing and data extraction

### AI Administration System (cogs/ai_brain.py) - **NEW CENTRAL SYSTEM**
- **Central AI Administrator**: Controls and manages all other bot cogs
- **Advanced Conversational AI**: Natural language processing with personality modes
- **Automatic Music Detection**: Detects music requests in normal messages and responds with YouTube links
- **Cog Management**: Can reload, enable, disable other bot modules dynamically
- **Intelligent Memory**: Persistent learning system tracking user preferences and server activity
- **Multi-personality Modes**: alegre, curioso, amigável, equilibrado, sério
- **Music Integration**: Built-in yt-dlp integration for automatic music search and response
- **Smart Channel Analysis**: Automatically configures news channels using AI analysis

### Interactive Systems (cogs/reactions.py)
- Automatic emoji reactions triggered by keywords
- Manual reaction commands for moderators
- Reaction bombing and multiple reaction features
- Configurable auto-reaction toggle system

### Advanced Administration (cogs/admin_advanced.py)
- Channel nuking with safety confirmations
- Mass moderation tools (ban/kick multiple users)
- Advanced channel management (lock/unlock, slowmode)
- Detailed server information and ban list management
- User-specific message purging capabilities

### Entertainment Commands (cogs/fun_commands.py)
- Interactive games (8-ball, dice rolling, rock-paper-scissors)
- Social features (love calculator, ship names)
- Random activities (truth/dare, random questions)
- **Renovated Jokes System**: 300+ modern jokes for young adults (20-25 years)
- Age-appropriate humor across 8 categories: university, work, tech, relationships, life, social media, gaming, food
- Probability simulator and choice maker

### Gaming Content System (cogs/gaming_news.py) - **MODERNIZED**
- **Free Fire Content**: Dedicated commands and automated content for Free Fire players
- **General Gaming News**: Broader gaming content and updates
- **Gaming Facts**: Curated facts and curiosities about gaming
- **Manual Channel Configuration**: Administrators can specify exact channels for each content type
- **AI Integration**: Works with central AI system for intelligent channel selection
- **Daily Delivery**: Automated posting **once per day** (9h, 12h, 18h) instead of multiple times
- **Three-tier Priority System**: Manual config > AI analysis > Auto-detection
- **Smart Caching**: Efficient content management and rotation

## Data Flow Architecture
- **PostgreSQL**: Banco de dados principal para economia e XP (Neon)
- **XP System**: Sistema de níveis e experiência baseado em chat
- **Economy v2**: Sistema de moedas persistente em banco de dados
- **Caching Strategy**: Temporary caching in ofertas cog and gaming news system to reduce API calls
- **Error Resilience**: Graceful degradation when individual services fail
- **Async Processing**: Non-blocking operations for web scraping and API calls

## Security Considerations
- Environment variables for sensitive API keys
- Permission checks for moderation commands
- Request headers and timeout protection for web scraping
- Input validation for user commands

# External Dependencies

## Discord Integration
- **discord.py**: Primary framework for Discord bot functionality
- **Discord API**: Real-time messaging, voice channels, and server management

## Web Scraping & Content Extraction
- **requests**: HTTP client for web scraping operations
- **BeautifulSoup4**: HTML parsing for e-commerce site scraping
- **trafilatura**: Advanced web content extraction and text processing

## Audio Processing
- **youtube_dl**: YouTube video/audio extraction and processing
- **FFmpeg**: Audio format conversion and streaming capabilities

## External APIs
- **OpenWeatherMap API**: Weather data and forecasting services

## Brazilian E-commerce Sites
- **Mercado Livre**: Product listings and pricing data
- **Amazon Brasil**: Deal aggregation and product information
- **Kabum**: Technology and electronics deals
- **Magazine Luiza**: General retail product offerings

## Development Tools
- **python-dotenv**: Environment variable management
- **asyncio**: Asynchronous programming support for concurrent operations

## Uptime & Monitoring
- **Flask**: Lightweight web framework for keep-alive HTTP server
- **Keep-Alive System**: Health check endpoints at http://localhost:8080/status
- **monitor.py**: Automated health monitoring script for bot uptime tracking