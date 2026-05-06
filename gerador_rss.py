import feedparser
import re
import json
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

# 2. MOTOR DE BUSCA DE IMAGENS BLINDADO
def extrair_melhor_imagem(entry):
    candidatas = []
    if 'media_content' in entry:
        for m in entry.media_content: candidatas.append(m.get('url', ''))
    if 'media_thumbnail' in entry:
        for m in entry.media_thumbnail: candidatas.append(m.get('url', ''))
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', '') or link.get('rel') == 'enclosure':
                candidatas.append(link.get('href', ''))

    textos_html = []
    if 'summary' in entry: textos_html.append(entry.summary)
    if 'description' in entry: textos_html.append(entry.description)
    if 'content' in entry:
        for c in entry.content: textos_html.append(c.value)

    for texto in textos_html:
        matches = re.findall(r'<img[^>]+src=["\'](https?://[^"\']+)["\']', texto, re.IGNORECASE)
        candidatas.extend(matches)

    for url in candidatas:
        if not url: continue
        url_limpa = url.strip()
        lixos = ['avatar', 'emoji', 'icon', 'logo', 'spinner', 'gravatar', 'pixel', 'wp-includes']
        if not any(lixo in url_limpa.lower() for lixo in lixos):
            return url_limpa

    return LINK_FALLBACK

# 3. EXTRAÇÃO E ORGANIZAÇÃO
todas_noticias = []
print("Puxando as notícias para o JSON...")

for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        nome_portal = feed.feed.title if 'title' in feed.feed else "Portal"
        
        for entry in feed.entries[:10]:
            entry.portal_origem = nome_portal
            # Tenta extrair a data
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry.data_sort = entry.published_parsed
                data_formatada = datetime(*entry.published_parsed[:6]).strftime("%d/%m/%Y")
            else:
                entry.data_sort = datetime.now().timetuple()
                data_formatada = datetime.now().strftime("%d/%m/%Y")
            
            entry.data_amigavel = data_formatada
            todas_noticias.append(entry)
    except Exception as e:
        print(f"Erro no feed {url}: {e}")

# Ordenar da mais nova para a mais velha
todas_noticias.sort(key=lambda x: x.data_sort, reverse=True)

# 4. MONTAGEM DO ARQUIVO JSON
dados_json = []

for noticia in todas_noticias[:50]:
    imagem_original = extrair_melhor_imagem(noticia)
    
    if imagem_original == LINK_FALLBACK:
        imagem_final = LINK_FALLBACK
    else:
        url_sem_http = imagem_original.replace('https://', '').replace('http://', '')
        # Proxy wsrv.nl para garantir que os jornais não bloqueiem a imagem no seu site
        imagem_final = f"https://wsrv.nl/?url={url_sem_http}&w=400&h=200&fit=cover&output=jpg"

    # Monta o "pacote" da notícia limpo e organizado
    dados_json.append({
        "portal": noticia.portal_origem,
        "titulo": noticia.title,
        "link": noticia.link,
        "data": noticia.data_amigavel,
        "imagem": imagem_final
    })

# 5. SALVAR ARQUIVO JSON
with open('feed_mestre.json', 'w', encoding='utf-8') as f:
    json.dump(dados_json, f, ensure_ascii=False, indent=4)

print("Sucesso! JSON gerado com perfeição.")
