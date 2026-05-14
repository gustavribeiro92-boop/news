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

# Validação para garantir que o GitHub enviou os dados
if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    print("🚨 Erro Crítico: O Python recebeu alguma chave vazia do GitHub!")
    print(f"Status - API_KEY: {'OK' if API_KEY else 'VAZIA'}")
    print(f"Status - API_SECRET: {'OK' if API_SECRET else 'VAZIA'}")
    print(f"Status - ACCESS_TOKEN: {'OK' if ACCESS_TOKEN else 'VAZIA'}")
    print(f"Status - ACCESS_TOKEN_SECRET: {'OK' if ACCESS_TOKEN_SECRET else 'VAZIA'}")
    exit(1)

# ==============================================================================
# 2. AUTENTICAÇÃO HÍBRIDA (Obrigatória para o plano Free do X)
# ==============================================================================
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

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
            
            print(f"Tentando disparar notícia: {titulo}")
            response = client.create_tweet(text=mensagem)
            print(f"🚀 SUCESSO! Postado no X. ID: {response.data['id']}")

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_do_arquivo} não foi encontrado.")
except Exception as e:
    print(f"Erro ao tentar enviar o tweet: {e}")
