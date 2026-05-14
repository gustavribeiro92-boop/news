import os
import json
import requests
import base64

# ==============================================================================
# 1. PUXANDO AS CREDENCIAIS DO SEU GITHUB SECRETS
# ==============================================================================
CLIENT_ID = os.environ.get("TWITTER_ACCESS_TOKEN")
REFRESH_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

if not CLIENT_ID or not REFRESH_TOKEN:
    print("🚨 Erro: Chaves de autenticação não foram encontradas no GitHub.")
    exit(1)

# ==============================================================================
# 2. PASSO OBRIGATÓRIO: FORMATAR O CABEÇALHO BÁSICO EXIGIDO PELO X (OAuth 2.0)
# ==============================================================================
print("🔄 Conectando ao X e renovando o token de acesso...")

# O plano Gratuito exige o Client ID enviado no formato Basic Auth para validar
autenticacao_basica = base64.b64encode(f"{CLIENT_ID}:".encode("utf-8")).decode("utf-8")

url_token = "https://api.twitter.com/2/oauth2/token"
headers_token = {
    "Authorization": f"Basic {autenticacao_basica}",
    "Content-Type": "application/x-www-form-urlencoded"
}
dados_token = {
    "refresh_token": REFRESH_TOKEN,
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID
}

# Faz a requisição oficial de renovação
resposta_token = requests.post(url_token, data=dados_token, headers=headers_token)

if resposta_token.status_code != 200:
    print(f"🚨 Erro na autenticação do X (Status {resposta_token.status_code}):")
    print(resposta_token.text)
    exit(1)

dados_recebidos = resposta_token.json()
access_token_valido = dados_recebidos["access_token"]
print("🔑 Autenticação efetuada com sucesso! Token gerado para este minuto.")

# ==============================================================================
# 3. DISPARANDO A NOTÍCIA MAIS RECENTE
# ==============================================================================
caminho_do_arquivo = 'feed_mestre.json'

try:
    with open(caminho_do_arquivo, 'r', encoding='utf-8') as arquivo:
        noticias = json.load(arquivo)
        
        if not noticias:
            print("O arquivo feed_mestre.json está vazio.")
        else:
            noticia_mais_nova = noticias[0]
            titulo = noticia_mais_nova.get('titulo', 'Sem título')
            link = noticia_mais_nova.get('link', 'https://portaldosportais.com')
            
            mensagem = f"🚨 Atualização no Radar:\n\n{titulo}\n\nLeia mais: {link}"
            
            print(f"Preparando postagem: {titulo}")
            
            headers_tweet = {
                "Authorization": f"Bearer {access_token_valido}",
                "Content-Type": "application/json",
            }
            payload = {"text": mensagem}
            
            url_tweet = "https://api.twitter.com/2/tweets"
            resposta_tweet = requests.post(url_tweet, json=payload, headers=headers_tweet)
            
            if resposta_tweet.status_code == 201:
                print(f"🚀 VERDE! Tweet publicado com sucesso! ID: {resposta_tweet.json()['data']['id']}")
            else:
                print(f"🚨 O Twitter recusou o post. Status: {resposta_tweet.status_code}")
                print(resposta_tweet.text)

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_do_arquivo} não foi encontrado.")
except Exception as e:
    print(f"Erro inesperado: {e}")
