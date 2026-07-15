import os
import json
import requests
import textwrap
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# 1. PUXANDO AS CREDENCIAIS
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("🚨 Erro: Credenciais do Facebook não encontradas.")
    exit(1)

# 2. O SISTEMA DE INTELIGÊNCIA
caminho_do_arquivo = 'feed_mestre.json'

try:
    with open(caminho_do_arquivo, 'r', encoding='utf-8') as arquivo:
        noticias = json.load(arquivo)
        
    if not noticias:
        print("⚠️ O arquivo de notícias está vazio.")
        exit(1)

    melhor_noticia = None
    maior_pontuacao = -999

    cidades_vizinhas = ['nova odessa', 'sumaré', 'hortolândia', 'santa bárbara', 'sbo', 'limeira', 'campinas', 'paulínia', 'piracicaba']
    palavras_americana = ['americana', 'dae', 'gama', 'sardelli', 'hospital municipal', 'praia azul', 'zanaga']
    palavras_engajamento = ['vagas', 'emprego', 'urgente', 'polícia', 'acidente', 'trânsito', 'concurso', 'oportunidade', 'preso', 'festival']

    for noticia in noticias[:50]:
        pontos = 0
        titulo = str(noticia.get('titulo', '')).lower()
        
        tem_vizinha = any(c in titulo for c in cidades_vizinhas)
        tem_americana = any(a in titulo for a in palavras_americana)
        
        if tem_vizinha and not tem_americana:
            pontos -= 100 
            
        if tem_americana:
            pontos += 50
            
        for palavra in palavras_engajamento:
            if palavra in titulo:
                pontos += 20
                
        if pontos > maior_pontuacao:
            maior_pontuacao = pontos
            melhor_noticia = noticia

    if melhor_noticia:
        titulo_final = melhor_noticia.get('titulo')
        link_final = melhor_noticia.get('link')
        portal_nome = melhor_noticia.get('portal', 'Portal RMC')
        
        print(f"🎯 Notícia selecionada (Nota: {maior_pontuacao}): {titulo_final}")

        # 3. O ESTÚDIO DE ARTE (Gerando a Imagem com Pillow)
        print("🎨 Desenhando a arte do post...")
        
        # Download SEGURO da fonte para não ficar com letras miúdas
        font_path = "Roboto-Black.ttf"
        if not os.path.exists(font_path):
            try:
                print("Baixando fonte Roboto...")
                urllib.request.urlretrieve("https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Black.ttf", font_path)
            except Exception as e:
                print(f"Erro ao baixar a fonte: {e}")
                exit(1) # Trava o robô para não postar arte feia
        
        font_titulo = ImageFont.truetype(font_path, 60)
        font_chapeu = ImageFont.truetype(font_path, 35)
        
        # Cria um fundo 1080x1080 (Dark Mode)
        img = Image.new('RGB', (1080, 1080), color=(17, 24, 39))
        draw = ImageDraw.Draw(img)
        
        # Barra Laranja superior e inferior
        draw.rectangle([(0, 0), (1080, 25)], fill=(234, 91, 12))
        draw.rectangle([(0, 1055), (1080, 1080)], fill=(234, 91, 12))
        
        # Escrevendo o Chapéu
        draw.text((80, 120), "GIRO DA RMC", font=font_chapeu, fill=(234, 91, 12))
        
        # Quebrando o título com espaçamento adequado
        linhas_titulo = textwrap.wrap(titulo_final, width=28)
        
        y_text = 250
        for linha in linhas_titulo:
            draw.text((80, y_text), linha, font=font_titulo, fill=(255, 255, 255))
            y_text += 90 # Espaçamento correto entre as linhas
            
        # Rodapé
        y_rodape = 880
        draw.text((80, y_rodape), f"Fonte: {portal_nome}", font=font_chapeu, fill=(156, 163, 175))
        draw.text((80, y_rodape + 60), "Acesse: portaldosportais.com", font=font_chapeu, fill=(234, 91, 12))

        # Salva o arquivo gerado
        caminho_imagem = 'card_gerado.jpg'
        img.save(caminho_imagem)

        # 4. DISPARO PARA O FACEBOOK COM O NOVO TEXTO
        print("🚀 Enviando para o Facebook...")
        
        mensagem = (
            f"🗞️ O ASSUNTO DO MOMENTO NA RMC 🗞️\n\n"
            f"📰 {titulo_final}\n\n"
            f"Acesse o Portal dos Portais e confira os detalhes dessa matéria divulgada pelo {portal_nome}.\n\n"
            f"🔗 Leia completo no link abaixo:\n{link_final}\n\n"
            f"#Americana #RMC #NoticiasLocais #PortalDosPortais"
        )
        
        url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        
        payload = {
            "message": mensagem,
            "access_token": ACCESS_TOKEN
        }
        
        with open(caminho_imagem, 'rb') as foto:
            resposta = requests.post(url, data=payload, files={'source': foto})
        
        if resposta.status_code == 200:
            print("✅ SUCESSO! Card exclusivo e anti-plágio publicado.")
        else:
            print(f"❌ Erro ao postar: {resposta.status_code}")
            print(resposta.text)

except Exception as e:
    print(f"🚨 Erro inesperado: {e}")
