import os
import json
import requests

# 1. PUXANDO AS CREDENCIAIS DO COFRE
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("🚨 Erro: Credenciais do Facebook não encontradas no GitHub Secrets.")
    exit(1)

# 2. O SISTEMA DE INTELIGÊNCIA (Pontuação)
caminho_do_arquivo = 'feed_mestre.json'

try:
    with open(caminho_do_arquivo, 'r', encoding='utf-8') as arquivo:
        noticias = json.load(arquivo)
        
    if not noticias:
        print("⚠️ O arquivo de notícias está vazio.")
        exit(1)

    melhor_noticia = None
    maior_pontuacao = -1

    # Palavras que geram mais engajamento na cidade ganham +10 pontos
    palavras_ouro = ['americana', 'vagas', 'emprego', 'prefeitura', 'dae', 'gama', 'polícia', 'urgente', 'hospital']

    # Analisa as 50 notícias mais recentes do feed
    for noticia in noticias[:50]:
        pontos = 0
        titulo = str(noticia.get('titulo', '')).lower()
        
        for palavra in palavras_ouro:
            if palavra in titulo:
                pontos += 10
                
        # A notícia com a maior nota assume o primeiro lugar
        if pontos > maior_pontuacao:
            maior_pontuacao = pontos
            melhor_noticia = noticia

    if melhor_noticia:
        titulo_final = melhor_noticia.get('titulo')
        link_final = melhor_noticia.get('link')
        
        # 3. FORMATANDO O POST
        mensagem = f"📰 Destaque do Dia no Radar:\n\n{titulo_final}\n\nLeia a matéria completa acessando o Portal: {link_final}"
        
        print(f"🎯 Notícia selecionada (Nota: {maior_pontuacao}): {titulo_final}")
        
        # 4. DISPARO PARA O FACEBOOK
        url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
        payload = {
            "message": mensagem,
            "access_token": ACCESS_TOKEN
        }
        
        resposta = requests.post(url, data=payload)
        
        if resposta.status_code == 200:
            print("✅ SUCESSO! Post publicado na página do Facebook.")
        else:
            print(f"❌ Erro ao postar: {resposta.status_code}")
            print(resposta.text)

except FileNotFoundError:
    print("🚨 Erro: Arquivo feed_mestre.json não encontrado.")
except Exception as e:
    print(f"🚨 Erro inesperado: {e}")
