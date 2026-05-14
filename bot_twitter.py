import os
import json
import tweepy

# ==============================================================================
# 1. PUXANDO AS 4 CREDENCIAIS EXATAS DO SEU GITHUB SECRETS
# ==============================================================================
API_KEY = os.environ.get("TWITTER_API_KEY")
API_SECRET = os.environ.get("TWITTER_API_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    print("🚨 Erro Crítico: O Python recebeu alguma chave vazia do GitHub!")
    exit(1)

# ==============================================================================
# 2. AUTENTICAÇÃO FORÇADA VIA API V1.1 (A mais estável para o Plano Free)
# ==============================================================================
auth = tweepy.OAuth1UserHandler(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

# ==============================================================================
# 3. LEITURA DO JSON E DISPARO DO TWEET
# ==============================================================================
caminho_do_arquivo = 'feed_mestre.json'

try:
    with open(caminho_do_arquivo, 'r', encoding='utf-8') as arquivo:
        noticias = json.load(arquivo)
        
        if not noticias:
            print("O arquivo feed_mestre.json está vazio.")
        else:
            # Pega a notícia na posição 0 (a mais recente)
            noticia_mais_nova = noticias[0]
            titulo = noticia_mais_nova.get('titulo', 'Sem título')
            link = noticia_mais_nova.get('link', 'https://portaldosportais.com')
            
            # Formatação do post
            mensagem = f"🚨 Atualização no Radar:\n\n{titulo}\n\nLeia mais: {link}"
            
            print(f"Tentando disparar notícia via API v1.1: {titulo}")
            
            # Força o disparo usando o método clássico de update_status
            response = api.update_status(status=mensagem)
            print(f"🚀 SUCESSO! Postado no X. ID do Tweet: {response.id}")

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_do_arquivo} não foi encontrado.")
except Exception as e:
    print(f"Erro ao tentar enviar o tweet: {e}")
