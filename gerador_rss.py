import feedparser
import re
import json
import time
import os
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

LOGOS_PORTAIS = {
    'americanapost': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana-post.png',
    'difusorapiracicaba': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo_font_white.svg',
    'hjnews': 'https://portaldosportais.com/wp-content/uploads/2026/05/KYiJBWc6_400x400.jpg',
    'jornalojogo': 'https://portaldosportais.com/wp-content/uploads/2026/05/O-JOGO_LOGO.png',
    'noticiadelimeira': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo.svg',
    'noticiafm': 'https://portaldosportais.com/wp-content/uploads/2026/05/LogoNoticia_2024_512x512-2.png',
    'novomomento': 'https://portaldosportais.com/wp-content/uploads/2026/05/0addff39-logo-1.png',
    'portaldeamericana': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo.avif',
    'rapidonoar': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo-rapido-no-ar-300.png',
    'redefamilia': 'https://portaldosportais.com/wp-content/uploads/2026/05/logotipo.png',
    'sb24horas': 'https://portaldosportais.com/wp-content/uploads/2026/05/images.jpg'
}

LINK_FALLBACK_PADRAO = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

# FUNÇÃO PARA DEIXAR OS NOMES DOS PORTAIS CURTOS E BONITOS
def nome_curto_portal(link_noticia):
    if 'americanapost' in link_noticia: return 'Americana Post'
    if 'difusorapiracicaba' in link_noticia: return 'Difusora FM'
    if 'hjnews' in link_noticia: return 'HJ News'
    if 'jornalojogo' in link_noticia: return 'O Jogo'
    if 'noticiadelimeira' in link_noticia: return 'Notícia de Limeira'
    if 'noticiafm' in link_noticia: return 'Notícia FM'
    if 'novomomento' in link_noticia: return 'Novo Momento'
    if 'portaldeamericana' in link_noticia: return 'Portal de Americana'
    if 'rapidonoar' in link_noticia: return 'Rápido no Ar'
    if 'redefamilia' in link_noticia: return 'Rede Família'
    if 'sb24horas' in link_noticia: return 'SB24Horas'
    return 'Portal RMC'

def extrair_melhor_imagem(entry, url_feed):
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

    # Retorna o logo específico do portal caso não encontre imagem na notícia
    for chave, link_logo in LOGOS_PORTAIS.items():
        if chave in url_feed.lower().replace('.', ''):
            return link_logo
            
    return LINK_FALLBACK_PADRAO

# CARREGAR E CORRIGIR A MEMÓRIA
historico_noticias = {}
if os.path.exists('feed_mestre.json'):
    try:
        with open('feed_mestre.json', 'r', encoding='utf-8') as f:
            dados_antigos = json.load(f)
            for noticia in dados_antigos:
                # 1. Corrige o nome gigante
                noticia['portal'] = nome_curto_portal(noticia['link'])
                
                # 2. Se tiver o logo velho genérico, atualiza para o novo logo oficial
                if noticia['imagem'] == LINK_FALLBACK_PADRAO:
                    for chave, link_logo in LOGOS_PORTAIS.items():
                        if chave in noticia['link']:
                            noticia['imagem'] = link_logo
                            break
                            
                historico_noticias[noticia['link']] = noticia
    except:
        print("Iniciando novo banco de dados...")

# PUXAR AS NOVIDADES
print("Puxando as novas notícias...")
for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:100]:
            link_noticia = entry.link
            
            if link_noticia in historico_noticias:
                continue
            
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                timestamp_absoluto = time.mktime(entry.published_parsed)
                data_formatada = datetime(*entry.published_parsed[:6]).strftime("%d/%m/%Y às %H:%M")
            else:
                timestamp_absoluto = datetime.now().timestamp()
                data_formatada = datetime.now().strftime("%d/%m/%Y às %H:%M")
            
            imagem_original = extrair_melhor_imagem(entry, url)
            
            if imagem_original in LOGOS_PORTAIS.values() or imagem_original == LINK_FALLBACK_PADRAO:
                imagem_final = imagem_original
            else:
                url_sem_http = imagem_original.replace('https://', '').replace('http://', '')
                imagem_final = f"https://wsrv.nl/?url={url_sem_http}&w=400&h=200&fit=cover&output=jpg"

            historico_noticias[link_noticia] = {
                "portal": nome_curto_portal(link_noticia),
                "titulo": entry.title,
                "link": link_noticia,
                "data": data_formatada,
                "imagem": imagem_final,
                "timestamp": timestamp_absoluto
            }
    except Exception as e:
        print(f"Erro no feed {url}: {e}")

# ORDENAR E SALVAR
lista_final = list(historico_noticias.values())
lista_final.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
lista_final = lista_final[:1000]

with open('feed_mestre.json', 'w', encoding='utf-8') as f:
    json.dump(lista_final, f, ensure_ascii=False, indent=4)

print(f"Sucesso! Acervo atualizado com {len(lista_final)} notícias.")
