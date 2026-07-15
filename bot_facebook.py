import os
import json
import requests
import textwrap
import random
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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
        
        # Formatando o nome do portal com letras maiúsculas
        portal_nome = str(melhor_noticia.get('portal', 'Portal RMC')).title()
        
        print(f"🎯 Notícia selecionada (Nota: {maior_pontuacao}): {titulo_final}")

        # 3. O ESTÚDIO DE ARTE
        print("🎨 Desenhando a arte do post...")
        
        font_path = "fonte.ttf"
        if not os.path.exists(font_path):
            print("🚨 Erro: O arquivo 'fonte.ttf' não foi encontrado no repositório!")
            exit(1)
            
        font_titulo = ImageFont.truetype(font_path, 55)
        font_chapeu = ImageFont.truetype(font_path, 35)
        
        img = Image.new('RGB', (1080, 1080), color=(17, 24, 39))
        draw = ImageDraw.Draw(img)
        
        draw.rectangle([(0, 0), (1080, 1080)], outline=(234, 91, 12), width=20)
        
        url_logo = "https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_mdib1mdib1mdib1m.png"
        try:
            req_logo = requests.get(url_logo)
            img_logo = Image.open(BytesIO(req_logo.content)).convert("RGBA")
            img_logo.thumbnail((300, 300), Image.Resampling.LANCZOS)
            logo_w, logo_h = img_logo.size
            x_logo = (1080 - logo_w) // 2
            img.paste(img_logo, (x_logo, 80), img_logo)
            y_start_text = 80 + logo_h + 80
        except Exception as e:
            print(f"⚠️ Aviso: Não conseguiu baixar o logo: {e}")
            y_start_text = 200

        linhas_titulo = textwrap.wrap(titulo_final, width=28)
        y_text = y_start_text
        
        for linha in linhas_titulo:
            bbox = draw.textbbox((0, 0), linha, font=font_titulo)
            w_linha = bbox[2] - bbox[0]
            x_text = (1080 - w_linha) / 2
            # AQUI ESTÁ O NEGRITO TURBINADO: stroke_width=2
            draw.text((x_text, y_text), linha, font=font_titulo, fill=(255, 255, 255), stroke_width=2, stroke_fill=(255, 255, 255))
            y_text += 85 
            
        y_rodape = 900
        texto_fonte = f"Fonte: {portal_nome}"
        bbox_fonte = draw.textbbox((0, 0), texto_fonte, font=font_chapeu)
        w_fonte = bbox_fonte[2] - bbox_fonte[0]
        draw.text(((1080 - w_fonte) / 2, y_rodape), texto_fonte, font=font_chapeu, fill=(156, 163, 175))

        texto_site = "Acesse: portaldosportais.com"
        bbox_site = draw.textbbox((0, 0), texto_site, font=font_chapeu)
        w_site = bbox_site[2] - bbox_site[0]
        draw.text(((1080 - w_site) / 2, y_rodape + 60), texto_site, font=font_chapeu, fill=(234, 91, 12))

        caminho_imagem = 'card_gerado.jpg'
        img.save(caminho_imagem)

        # 4. DISPARO PARA O FACEBOOK COM ROLETA DE TEXTOS
        print("🚀 Enviando para o Facebook...")
        
        opcoes_chapeu = [
            "🗞️ O ASSUNTO DO MOMENTO NA RMC 🗞️",
            "🚨 DESTAQUE DA NOSSA REGIÃO 🚨",
            "🔥 NOTÍCIA QUENTE NO RADAR 🔥",
            "🗣️ GIRO DE NOTÍCIAS DE AMERICANA E RMC 🗣️",
            "📌 FIQUE POR DENTRO 📌"
        ]
        
        chapeu_sorteado = random.choice(opcoes_chapeu)
        
        mensagem = (
            f"{chapeu_sorteado}\n\n"
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
            print("✅ SUCESSO! Card dinâmico publicado.")
        else:
            print(f"❌ Erro ao postar: {resposta.status_code}")
            print(resposta.text)

except Exception as e:
    print(f"🚨 Erro inesperado: {e}")
