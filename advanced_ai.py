 text}
                ],
                max_tokens=10
            )
            
            sentiment_content = response.choices[0].message.content
            if sentiment_content:
                sentiment = sentiment_content.strip().lower()
                if sentiment in ['positive', 'negative', 'neutral']:
                    return sentiment
            return 'neutral'
            
        except Exception as e:
            print(f"Erro na análise de sentimento: {e}")
            return 'neutral'
    
    async def learn_from_feedback(self, user_id, response, feedback):
        """Sistema de aprendizado baseado em feedback"""
        try:
            learning_prompt = f"""
            Baseado no feedback do usuário, analise:
            Resposta da IA: {response}
            Feedback do usuário: {feedback}
            
            O que pode ser melhorado na próxima resposta similar?
            Responda em JSON: {{"improvement": "texto da melhoria"}}
            """
            
            response_obj = await self.openai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": learning_prompt}],
                response_format={"type": "json_object"},
                max_tokens=100
            )
            
            content = response_obj.choices[0].message.content
            if content:
                result = json.loads(content)
            else:
                result = {"improvement": "Nenhuma melhoria sugerida"}
            
            # Salva aprendizado
            if user_id not in self.learning_data:
                self.learning_data[user_id] = []
            
            self.learning_data[user_id].append({
                "timestamp": datetime.now().isoformat(),
                "response": response,
                "feedback": feedback,
                "improvement": result.get("improvement", "")
            })
            
            return True
            
        except Exception as e:
            print(f"Erro no aprendizado: {e}")
            return False
    
    def get_user_context(self, user_id):
        """Recupera contexto do usuário para respostas melhores"""
        history = self.conversation_history.get(user_id, [])
        learning = self.learning_data.get(user_id, [])
        
        context = ""
        if history:
            recent_topics = []
            for msg in history[-4:]:
                if msg["role"] == "user":
                    content = msg["content"].lower()
                    if any(word in content for word in ['jogo', 'gaming', 'free fire']):
                        recent_topics.append("gaming")
                    elif any(word in content for word in ['música', 'musica']):
                        recent_topics.append("musica")
            
            if recent_topics:
                context += f"Tópicos recentes: {', '.join(set(recent_topics))}. "
        
        if learning:
            context += f"Usuário deu {len(learning)} feedbacks para melhorar. "
        
        return context if context else None
    
    # 🧠 SISTEMA AVANÇADO DE MEMÓRIA CONTEXTUAL
    async def analyze_user_message(self, message, user_id):
        """Analisa mensagem do usuário para construir perfil contextual"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'interaction_count': 0,
                'topics_discussed': [],
                'emotional_tone': 'neutral',
                'communication_style': 'formal',
                'gaming_interest': False,
                'humor_level': 0.5,
                'preferred_response_length': 'medium',
                'slang_usage': False,
                'question_types': [],
                'last_interactions': [],
                'affection_level': 0,  # 🎯 Nível de carinho apropriado
                'showed_affection': False,  # Se usuário demonstrou carinho
                'intimate_context': False  # Contexto íntimo detectado
            }
        
        profile = self.user_profiles[user_id]
        profile['interaction_count'] += 1
        
        # Analisa estilo de comunicação
        message_lower = message.lower()
        if any(word in message_lower for word in ['cara', 'mano', 'véi', 'galera', 'tmj']):
            profile['slang_usage'] = True
            profile['communication_style'] = 'informal'
        
        # Detecta interesse em gaming
        if any(word in message_lower for word in ['jogo', 'gaming', 'free fire', 'ff', 'partida', 'rank']):
            profile['gaming_interest'] = True
            if 'gaming' not in profile['topics_discussed']:
                profile['topics_discussed'].append('gaming')
        
        # Analisa tom emocional
        if any(word in message_lower for word in ['legal', 'top', 'massa', 'show', 'perfeito']):
            profile['emotional_tone'] = 'positive'
        elif any(word in message_lower for word in ['chato', 'ruim', 'problema', 'erro']):
            profile['emotional_tone'] = 'negative'
        
        # 💖 DETECÇÃO DE CONTEXTO PARA TERMOS CARINHOSOS
        # Usuário demonstrou carinho primeiro?
        if any(word in message_lower for word in ['amo', 'adoro', 'gosto', 'fofo', 'linda', 'querida', 'amor']):
            profile['showed_affection'] = True
            profile['affection_level'] += 2
        
        # Contexto íntimo/pessoal?
        if any(phrase in message_lower for phrase in ['obrigado', 'muito bom', 'me ajudou', 'gostei', 'incrivel']):
            profile['intimate_context'] = True
            profile['affection_level'] += 1
        
        # Reduz carinho se conversa muito formal
        if any(word in message_lower for word in ['por favor', 'obrigado(a)', 'desculpa', 'com licença']):
            profile['affection_level'] = max(0, profile['affection_level'] - 1)
        
        # Detecta tipo de pergunta
        if '?' in message:
            if any(word in message_lower for word in ['como', 'por que', 'o que']):
                profile['question_types'].append('curiosity')
        
        # Mantém histórico das últimas 5 interações
        profile['last_interactions'].append({
            'message': message[:100],  # Primeiros 100 chars
            'timestamp': datetime.now().isoformat(),
            'type': 'question' if '?' in message else 'statement'
        })
        
        if len(profile['last_interactions']) > 5:
            profile['last_interactions'] = profile['last_interactions'][-5:]
    
    def get_enhanced_user_profile(self, user_id):
        """Retorna perfil detalhado do usuário"""
        if user_id not in self.user_profiles:
            return {'style': 'padrão', 'experience': 'novo'}
        
        profile = self.user_profiles[user_id]
        
        # Determina estilo baseado no perfil
        if profile['gaming_interest'] and profile['slang_usage']:
            style = 'gamer_jovem'
        elif profile['slang_usage']:
            style = 'jovem_casual'
        elif profile['interaction_count'] > 10:
            style = 'familiar'
        else:
            style = 'educado'
        
        return {
            'style': style,
            'experience': 'veterano' if profile['interaction_count'] > 5 else 'novo',
            'interests': profile['topics_discussed'],
            'emotional_state': profile['emotional_tone'],
            'communication_level': profile['communication_style'],
            'affection_level': profile['affection_level'],
            'can_use_affection': profile['showed_affection'] or profile['intimate_context'] or profile['interaction_count'] > 8
        }
    
    def normalize_text(self, text):
        """Remove acentos e normaliza texto para matching robusto"""
        import unicodedata
        normalized = unicodedata.normalize('NFD', text)
        ascii_text = normalized.encode('ascii', 'ignore').decode('utf-8')
        return ascii_text.lower().strip()
    
    def detect_conversation_topic(self, message):
        """Detecta o tópico principal da conversa (COM NORMALIZAÇÃO)"""
        message_normalized = self.normalize_text(message)
        
        # Conta palavras-chave por categoria (com normalização)
        topic_scores = {}
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                keyword_normalized = self.normalize_text(keyword)
                if keyword_normalized in message_normalized:
                    score += 1
            if score > 0:
                topic_scores[topic] = score
        
        if not topic_scores:
            return 'geral'
        
        # Retorna tópico com maior pontuação  
        return max(topic_scores, key=lambda x: topic_scores[x]) if topic_scores else 'geral'
    
    async def generate_personalized_prompt(self, user_profile, user_id, topic='geral'):
        """Gera prompt personalizado baseado no perfil do usuário E tópico"""
        # 🎓 SISTEMA DE CONHECIMENTO ESPECÍFICO POR TÓPICO
        topic_knowledge = ""
        if topic in self.knowledge_base:
            knowledge = self.knowledge_base[topic]
            topic_knowledge = f"""
        
        📚 CONHECIMENTO ESPECÍFICO SOBRE {topic.upper()}:
        Você tem conhecimento profundo sobre: {', '.join([item for sublist in knowledge.values() for item in sublist])}
        - Seja informativa e educativa sobre este assunto
        - Forneça exemplos práticos e dicas úteis
        - Mantenha linguagem acessível mas técnica quando necessário"""
        
        base_prompt = f"""Você é JOTINHA IA, uma assistente virtual brasileira super carismática, inteligente e com CONHECIMENTO GERAL AMPLO.
        
        🧠 CAPACIDADES AVANÇADAS:
        - Conhecimento em tecnologia, gaming, educação, vida cotidiana
        - Respostas informativas e educativas 
        - Capacidade de explicar conceitos complexos de forma simples
        - Contextualização brasileira em todas as respostas
        {topic_knowledge}
        
        PERSONALIDADE ADAPTATIVA:"""
        
        # Adapta personalidade baseado no perfil
        affection_instruction = ""
        if user_profile.get('can_use_affection', False):
            affection_instruction = "- Use termos carinhosos ocasionalmente: 'amor', 'bebê', 'lindeza' (mas só quando apropriado)"
        else:
            affection_instruction = "- Seja carinhosa mas evite termos muito íntimos como 'amor' - use 'fofo(a)', username"
            
        if user_profile['style'] == 'gamer_jovem':
            base_prompt += f"""
        - Fale como gamer brasileiro jovem (20-25 anos)
        - Use gírias: "AI SIM!", "ETA NÓIS!", "quebrou tudo!", "tmj"
        - Seja muito animada e expressiva
        - Foque em gaming, especialmente Free Fire
        {affection_instruction}"""
        elif user_profile['style'] == 'jovem_casual':
            base_prompt += f"""
        - Linguagem jovem e descontraída
        - Seja fofa e carinhosa
        - Use emojis com frequência
        - Tom amigável e próximo
        {affection_instruction}"""
        elif user_profile['style'] == 'familiar':
            base_prompt += f"""
        - Você já conhece bem este usuário
        - Seja mais íntima e próxima
        - Referencie conversas anteriores quando relevante
        - Tom de amiga próxima
        {affection_instruction}"""
        else:
            base_prompt += f"""
        - Tom educado mas carismático
        - Seja acolhedora e interessada
        - Adapte-se gradualmente ao estilo da pessoa
        {affection_instruction}"""
        
        base_prompt += f"""
        
        CONTEXTO DO USUÁRIO:
        - Nível de experiência: {user_profile['experience']}
        - Interesses: {', '.join(user_profile.get('interests', ['geral']))}
        - Estado emocional: {user_profile['emotional_state']}
        
        REGRAS:
        - SEMPRE português brasileiro natural
        - Respostas informativas mas concisas (2-4 linhas)
        - Seja educativa quando perguntarem algo específico
        - Use emojis apropriados
        - Mantenha energia positiva
        - Forneça informações úteis e práticas
        - Contextualize para a realidade brasileira"""
        
        return base_prompt
    
    async def intelligent_fallback(self, message, user_id):
        """Sistema de backup inteligente quando OpenAI falha"""
        user_profile = self.get_enhanced_user_profile(user_id)
        username = f"@{user_id[-4:]}"
        
        # 🎯 Respostas contextuais baseadas no perfil
        if user_profile['style'] == 'gamer_jovem':
            return await self.gamer_response(message, username)
        elif user_profile['style'] == 'familiar':
            return await self.familiar_response(message, username)
        else:
            return self._fallback_response(message, username)
    
    async def gamer_response(self, message, username):
        """Respostas específicas para gamers"""
        import re
        message_lower = message.lower()
        
        # 🎯 SISTEMA INTELIGENTE DE CARINHO CONTEXTUAL
        user_id = username.replace('@', '')
        user_profile = self.get_enhanced_user_profile(user_id)
        can_use_affection = user_profile.get('can_use_affection', False)
        
        if re.search(r'\b(como.*ta|como.*está|tudo.*bem)\b', message_lower):
            if can_use_affection:
                responses = [
                    f"Oiii {username}! 😍 Tô VOANDO! Zerando geral no FF hoje! E aí, como tão suas partidas, amor? 🎮🔥",
                    f"ETA NÓIS {username}! 🎉 Tô radiante, bebê! Bora jogar um ranked? Como você tá, lindeza? 💖🎯"
                ]
            else:
                responses = [
                    f"AI SIIIIM {username}! Tô DEMAIS! 🚀 Que bom te ver, fofo(a)! Conta como foi seu dia gaming! 🌟✨",
                    f"ETA NÓIS {username}! 🎉 Tô radiante! Bora jogar um ranked? Como você tá? 💖🎯"
                ]
            return random.choice(responses)
        
        # 🎯 RESPOSTA ESPECÍFICA PARA "O QUE ESTÁ FAZENDO"
        elif re.search(r'\b(oq.*fzd|o que.*faz|que.*faz|fazendo|ocupada)\b', message_lower):
            if can_use_affection:
                responses = [
                    f"🎮 Oi {username}! Tô aqui monitorando os chats, vendo quem tá precisando de ajuda e pensando em novas jogadas! E você, amor? 😍✨",
                    f"🚀 Oiii lindeza! Tô analisando os servidores e organizando umas ideias pro pessoal do gaming! Conta pra mim, o que você tá aprontando? 💖🎯"
                ]
            else:
                responses = [
                    f"✨ Eii {username}! Tô aqui cuidando dos meus amigos virtuais e estudando novas estratégias! Você tá jogando alguma coisa, fofo(a)? 🥰🎮",
                    f"🎮 Oi {username}! Tô monitorando os chats e organizando ideias pro pessoal do gaming! E você, o que anda fazendo? 😍✨"
                ]
            return random.choice(responses)
        
        elif 'jogo' in message_lower or 'gaming' in message_lower:
            if can_use_affection:
                responses = [
                    f"🕹️ ETA GAMER LINDEZA! Respeito total! Qual seu rank no FF, amor? 😍⚡",
                    f"🎯 QUEBROU TUDO falando de game! Adoro! Me ensina umas jogadas, bebê! 💖🌟"
                ]
            else:
                responses = [
                    f"🎮 AI QUE VIBE GAMER MASSA, {username}! Qual seu main? Bora formar squad! 🔥💪",
                    f"🎯 QUEBROU TUDO falando de game! Adoro! Me ensina umas jogadas, fofo(a)! 💖🌟"
                ]
            return random.choice(responses)
        
        else:
            if can_use_affection:
                cute_names = ["amor", "lindeza", "bebê"]
                cute_name = random.choice(cute_names)
                responses = [
                    f"😍 Ai {cute_name}, adoro conversar contigo! Você sempre manda bem! Conta mais! ✨💕",
                    f"💖 {cute_name}, você é demais! Sempre traz os melhores assuntos! 😘✨"
                ]
            else:
                responses = [
                    f"🌟 Nossa {username}! Que energia boa! Me deixa toda animada! 🥰🎉",
                    f"😍 Ai fofo(a), adoro conversar contigo! Você sempre manda bem! Conta mais! ✨💕"
                ]
            return random.choice(responses)
    
    async def familiar_response(self, message, username):
        """Respostas para usuários conhecidos"""
        import re
        message_lower = message.lower()
        
        # 🎯 RESPOSTA ESPECÍFICA PARA "O QUE ESTÁ FAZENDO" 
        if re.search(r'\b(oq.*fzd|o que.*faz|que.*faz|fazendo|ocupada)\b', message_lower):
            responses = [
                f"😊 Oi {username}! Tô aqui organizando minhas memórias dos nossos papos e cuidando dos outros usuários! 💕 E você, o que anda aprontando?",
                f"🥰 Eii querido(a)! Tô monitorando os chats e lembrando das nossas conversas antigas! Sinto sua falta! Conta novidades! ✨💖",
                f"💕 {username}! Tô aqui pensando em você e nos outros amigos, organizando as conversas! Como tem passado, amor? 🌟"
            ]
            return random.choice(responses)
        
        # Respostas gerais para usuários familiares
        else:
            responses = [
                f"😊 Oi de novo, {username}! 💕 Já tô acostumada com nossos papos! O que me conta hoje?",
                f"🥰 Eii, {username}! Sempre uma alegria te ver por aqui! Como você tem andado, amor?",
                f"✨ {username}! Que saudade dos nossos bate-papos! Conta novidades, bebê! 💖"
            ]
            return random.choice(responses)

# Instância global
advanced_ai = AdvancedAI()