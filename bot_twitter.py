import os
import json
import tweepy

# ==============================================================================
# 1. PUXANDO AS CREDENCIAIS SEGURAS DO GITHUB ACTIONS
# ==============================================================================
ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN")

# Se o GitHub esquecer de passar a chave, o script avisa antes de dar erro
if not ACCESS_TOKEN:
    print("Erro: A variável TWITTER_ACCESS_TOKEN não foi configurada no GitHub Secrets.")
    exit(1)

# ==============================================================================
# 2. CONECTANDO À API DO X
# ==============================================================================
client = tweepy.Client(bearer_token=None, access_token=ACCESS_TOKEN)

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
            # Pega a notícia mais recente
            noticia_mais_nova = noticias[0]
            titulo = noticia_mais_nova.get('titulo', 'Sem título')
            link = noticia_mais_nova.get('link', 'https://portaldosportais.com')
            
            # Monta o Tweet
            mensagem = f"🚨 Atualização no Radar Americana:\n\n{titulo}\n\nLeia mais no Portal: {link}"
            
            print(f"Disparando notícia para o X: {titulo}")
            response = client.create_tweet(text=mensagem)
            print(f"🚀 Sucesso! Tweet publicado sozinho pelo GitHub. ID: {response.data['id']}")

except FileNotFoundError:
    print(f"Erro: O arquivo {caminho_do_arquivo} não foi encontrado no repositório.")
except Exception as e:
    print(f"Erro ao tentar enviar o tweet: {e}")
