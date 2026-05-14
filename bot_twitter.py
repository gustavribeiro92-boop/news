import os
import json
import requests

# ==============================================================================
# 1. CREDENCIAIS DO OAUTH 2.0 (DO COFRE DO GITHUB)
# ==============================================================================
CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
REFRESH_TOKEN = os.environ.get("TWITTER_REFRESH_TOKEN")

if not CLIENT_ID or not REFRESH_TOKEN:
    print("🚨 Erro: TWITTER_CLIENT_ID ou TWITTER_REFRESH_TOKEN não configurados no GitHub.")
    exit(1)

# ==============================================================================
# 2. PASSO DA MAGIA: USAR O REFRESH TOKEN PARA PEGAR UM ACCESS TOKEN VÁLIDO
# ==============================================================================
print("🔄 Renovando credenciais com o servidor do X...")
url_token = "https://api.twitter.com/2/oauth2/token"
dados_token = {
    "refresh_token": REFRESH_TOKEN,
    "grant_type": "refresh_token",
    "client_id": CLIENT_ID,
}

resposta_token = requests.post(url_token, data=dados_token)

if resposta_token.status_code != 200:
    print(f"🚨 Erro ao renovar o token: {resposta_token.status_code}")
    print(resposta_token.text)
    exit(1)

# Pega o token válido gerado agora
dados_recebidos = resposta_token.json()
access_token_valido = dados_recebidos["access_token"]
print("🔑 Nova chave de acesso gerada com sucesso!")

# ==============================================================================
# 3. LER O JSON E FAZER O DISPARO VIA POST PURO
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
            
            print(f"Postando notícia: {titulo}")
            
            # Cabeçalho de autorização oficial da API v2
            headers = {
                "Authorization": f"Bearer {access_token_valido}",
                "Content-Type": "application/json",
            }
            payload = {"text": mensaje}
            
            # Envia o POST para a rota de Tweets da API v2
            url_tweet = "https://api.twitter.com/2/tweets"
            resposta_tweet = requests.post(url_tweet, json=payload, headers=headers)
            
            if resposta_tweet.status_code == 201:
                print(f"🚀 SUCESSO TOTAL! Postado no X. ID: {resposta_tweet.json()['data']['id']}")
            else:
                print(f"🚨 Falha no envio do Tweet. Status: {resposta_tweet.status_code}")
                print(resposta_tweet.text)

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_do_arquivo} não foi encontrado.")
except Exception as e:
    print(f"Erro inesperado: {e}")
