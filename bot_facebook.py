import os
import json
import requests
import textwrap
import random
from PIL import Image, ImageDraw, ImageFont

# 1. PUXANDO AS CREDENCIAIS
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
ACCESS_TOKEN = os.environ.get("FACEBOOK_ACCESS_TOKEN")

if not PAGE_ID or not ACCESS_TOKEN:
    print("🚨 Erro: Credenciais do Facebook não encontradas.")
    exit(1)

# 2. A MEMÓRIA DO ROBÔ (Lendo o Histórico)
ARQUIVO_HISTORICO = 'historico_postados.txt'
postados = []

if os.path.exists(ARQUIVO_HISTORICO):
    with open(ARQUIVO_HISTORICO, 'r', encoding='utf-8') as f:
        postados = f.read().splitlines()

# 3. O SISTEMA DE INTELIGÊNCIA
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
        link_atual = noticia.get('link')
        
        if link_atual in postados:
            continue
            
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

    if not melhor_noticia:
        print("⚠️ Nenhuma notícia nova para postar (todas do topo já foram publicadas).")
        exit(0)

    # LIMPADOR DE TÍTULOS
    titulo_bruto = melhor_noticia.get('titulo')
    if " - " in titulo_bruto:
        titulo_final = titulo_bruto.rsplit(' - ', 1)[0]
    else:
        titulo_final = titulo_bruto

    link_final = melhor_noticia.get('link')
    portal_nome = str(melhor_noticia.get('portal', 'Portal RMC')).title()
    
    print(f"🎯 Notícia selecionada (Nota: {maior_pontuacao}): {titulo_final}")

    # 4. O ESTÚDIO DE ARTE
    print("🎨 Desenhando a arte do post usando o Template do Canva...")
    
    font_path = "fonte.ttf"
    if not os.path.exists(font_path):
        print("🚨 Erro: O arquivo 'fonte.ttf' não foi encontrado no repositório!")
        exit(1)
        
    # Mantivemos a fonte grande (70), pois a nova fonte será mais larga
    font_titulo = ImageFont.truetype(font_path, 70)
    font_chapeu = ImageFont.truetype(font_path, 35)
    
    template_path = "template.png"
    if not os.path.exists(template_path):
        print("🚨 Erro: O arquivo 'template.png' não foi encontrado no repositório! Suba a arte do Canva.")
        exit(1)
        
    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)

    linhas_titulo = textwrap.wrap(titulo_final, width=22)
    
    y_text = 350
    
    for linha in linhas_titulo:
        bbox = draw.textbbox((0, 0), linha, font=font_titulo)
        w_linha = bbox[2] - bbox[0]
        x_text = (1080 - w_linha) / 2
        
        # TEXTO BRANCO PURO (Limpo e elegante)
        draw.text((x_text, y_text), linha, font=font_titulo, fill=(255, 255, 255))
        
        y_text += 90 
        
    y_rodape = 950
    texto_fonte = f"Fonte: {portal_nome}"
    bbox_fonte = draw.textbbox((0, 0), texto_fonte, font=font_chapeu)
    w_fonte = bbox_fonte[2] - bbox_fonte[0]
    draw.text(((1080 - w_fonte) / 2, y_rodape), texto_fonte, font=font_chapeu, fill=(200, 200, 200))

    caminho_imagem = 'card_gerado.jpg'
    img.save(caminho_imagem)

    # 5. DISPARO PARA O FACEBOOK
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
        f"👉 Confira os detalhes dessa matéria e fique por dentro de tudo o que acontece na região.\n\n"
        f"🔗 Acesse agora: https://portaldosportais.com\n\n"
        f"#Americana #NoticiasLocais #PortalDosPortais"
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
        
        with open(ARQUIVO_HISTORICO, 'a', encoding='utf-8') as f:
            f.write(link_final + '\n')
            
    else:
        print(f"❌ Erro ao postar: {resposta.status_code}")
        print(resposta.text)

except Exception as e:
    print(f"🚨 Erro inesperado: {e}")
