import feedparser
from feedgen.feed import FeedGenerator
import re
from datetime import datetime

# 1. LISTA DE FEEDS
FEEDS = [
    'https://americanapost.com.br/feed/',
    'https://difusorapiracicaba.com.br/feed/',
    'https://hjnews.com.br/feed/',
    'https://jornalojogo.com.br/feed/',
    'https://noticiadelimeira.com.br/feed/',
    'https://noticiafm.com.br/feed/',
    'https://novomomento.com.br/feed/',
    'https://portaldeamericana.com/feed/',
    'https://rapidonoar.com.br/feed/',
    'https://redefamilia.com.br/feed/',
    'https://sb24horas.com.br/feed/'
]

LINK_FALLBACK = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

# 2. O NOVO MOTOR DE BUSCA DE IMAGENS
def extrair_melhor_imagem(entry):
    candidatas = []

    # Passo A: Olha as tags oficiais de mídia (se o jornal for organizado)
    if 'media_content' in entry:
        for media in entry.media_content: candidatas.append(media.get('url', ''))
    if 'media_thumbnail' in entry:
        for media in entry.media_thumbnail: candidatas.append(media.get('url', ''))
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', '') or link.get('rel') == 'enclosure':
                candidatas.append(link.get('href', ''))

    # Passo B: Junta todo o texto da notícia para vasculhar o código HTML
    textos_html = []
    if 'summary' in entry: textos_html.append(entry.summary)
    if 'description' in entry: textos_html.append(entry.description)
    if 'content' in entry:
        for c in entry.content: textos_html.append(c.value)

    # Passo C: Captura APENAS o que estiver dentro de um <img src="...">
    for texto in textos_html:
        # Pega qualquer link que esteja dentro do atributo src da imagem
        matches = re.findall(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', texto, re.IGNORECASE)
        candidatas.extend(matches)

    # Passo D: Filtro Anti-Lixo (O segredo para não puxar ícones errados)
    for url in candidatas:
        if not url: continue
        url_limpa = url.strip()
        url_lower = url_limpa.lower()
        
        # Se for um ícone, emoji do WP, avatar de autor ou pixel de rastreio, IGNORE!
        lixos_comuns = ['avatar', 'emoji', 'icon', 'logo', 'spinner', 'gravatar', 'pixel', 'wp-includes']
        if any(lixo in url_lower for lixo in lixos_comuns):
            continue
            
        # Se sobreviveu ao filtro, achamos a imagem principal!
        return url_limpa

    # Se não sobrou nenhuma imagem real, usamos o seu logo oficial
    return LINK_FALLBACK

# 3. CONFIGURAÇÃO DO FEED
fg = FeedGenerator()
fg.title('Hub de Notícias RMC')
fg.link(href='https://seusite.com.br', rel='alternate')
fg.description('Agregador de notícias da região')
fg.language('pt-br')

todas_noticias = []
print("Puxando as notícias...")

for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        nome_portal = feed.feed.title if 'title' in feed.feed else "Portal"
        
        for entry in feed.entries[:10]:
            entry.portal_origem = nome_portal
            todas_noticias.append(entry)
    except Exception as e:
        print(f"Erro no feed {url}: {e}")

# Ordenar por data
def extrair_data(entry):
    return entry.published_parsed if hasattr(entry, 'published_parsed') and entry.published_parsed else datetime.now().timetuple()

todas_noticias.sort(key=extrair_data, reverse=True)

# 4. CONSTRUÇÃO FINAL (O que provamos que funciona)
for noticia in todas_noticias[:50]:
    fe = fg.add_entry()
    fe.title(f"[{noticia.portal_origem}] {noticia.title}")
    fe.link(href=noticia.link)
    
    # Roda nosso novo motor
    imagem_original = extrair_melhor_imagem(noticia)
    
    # Limpa as imagens antigas do texto para não poluir
    descricao_texto = noticia.get('description', '')
    if 'content' in noticia and len(noticia.content) > 0:
        descricao_texto = noticia.content[0].value # Usa o texto completo se tiver
        
    descricao_limpa = re.sub(r'<img[^>]*>', '', descricao_texto)
    
    # Aplica as regras de Proxy que sabemos que o Feedzy gosta
    if imagem_original == LINK_FALLBACK:
        imagem_forcada = LINK_FALLBACK
    else:
        url_sem_http = imagem_original.replace('https://', '').replace('http://', '')
        # Proxy wsrv.nl com output=jpg para forçar leitura de imagem
        imagem_forcada = f"https://wsrv.nl/?url={url_sem_http}&w=400&h=200&fit=cover&output=jpg"
    
    # 1. Envia como anexo oficial
    fe.enclosure(imagem_forcada, '0', 'image/jpeg')
    
    # 2. Injeta visualmente no texto (Obrigatório pro Feedzy extrair)
    nova_descricao_html = f'<img src="{imagem_forcada}" alt="Imagem" style="width:100%; max-width:400px; border-radius:8px; margin-bottom:10px;" /><br>{descricao_limpa}'
    fe.description(nova_descricao_html)

# 5. SALVAR ARQUIVO
fg.rss_file('feed_mestre.xml')
print("Sucesso! Hub gerado com a nova inteligência de imagens.")
