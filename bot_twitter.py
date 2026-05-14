import os
import json
import tweepy

# ==============================================================================
# 1. PUXANDO O TOKEN SEGURO DO GITHUB ACTIONS
# ==============================================================================
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")

if not ACCESS_TOKEN:
    print("Erro: A variável TWITTER_ACCESS_TOKEN não foi configurada no GitHub Secrets.")
    exit(1)

# ==============================================================================
# 2. CONECTANDO VIA OAUTH 2.0 PURO (Forçando o Tweepy a usar apenas o Token)
# ==============================================================================
# Passamos o token direto no parâmetro 'bearer_token' para ignorar as chaves antigas
client = tweepy.Client(bearer_token=ACCESS_TOKEN)

# ==============================================================================
# 3. LER O JSON E DISPARAR
# ==============================================================================
caminho_do_arquivo = 'feed_mestre.json'

try:
    with open(caminho_do_arquivo, 'r', encoding='utf-8') as arquivo:
        noticias = json.load(arquivo)
        
        if not noticias:
            print("O arquivo feed_mestre.json está vazio.")
        else:
            # Pega a notícia mais recente (posição 0)
            noticia_mais_nova = noticias[0]
            titulo = noticia_mais_nova.get('titulo', 'Sem título')
            link = noticia_mais_nova.get('link', 'https://portaldosportais.com')
            
            # Monta a mensagem limpa
            mensagem = f"🚨 Atualização no Radar Americana:\n\n{titulo}\n\nLeia mais no Portal: {link}"
            
            print(f"Disparando notícia para o X: {titulo}")
            
            # Executa a postagem
            response = client.create_tweet(text=mensagem)
            print(f"🚀 Sucesso total! Tweet publicado sozinhovelo GitHub. ID: {response.data['id']}")

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_do_arquivo} não foi encontrado no repositório.")
except Exception as e:
    print(f"Erro ao tentar enviar o tweet: {e}")
