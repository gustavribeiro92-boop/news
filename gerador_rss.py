import feedparser
from feedgen.feed import FeedGenerator
import re
from datetime import datetime
import pytz

# A sua lista de portais da região
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
    'https://sb24horas.com.br/feed/',
    'https://tvthathi.com.br/feed/'
]

def buscar_imagem(entry):
    """Puxa a imagem para a miniatura do Feedzy"""
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/') or link.get('rel') == 'enclosure':
                return link.get('href', '')
    if 'description' in entry:
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.description)
        if match: return match.group(1)
    return 'https://via.placeholder.com/400x200.png?text=Noticia'

# Configuração do Super Feed
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
        
        for entry in feed.entries[:10]: # Pega as 10 mais novas de cada
            entry.portal_origem = nome_portal
            todas_noticias.append(entry)
    except Exception as e:
        pass

# Ordenar pelas mais recentes
def extrair_data(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return entry.published_parsed
    return datetime.now().timetuple()

todas_noticias.sort(key=extrair_data, reverse=True)

# Monta o arquivo XML final
for noticia in todas_noticias[:50]: # Limite de 50 para o site ficar leve
    fe = fg.add_entry()
    fe.title(f"[{noticia.portal_origem}] {noticia.title}")
    fe.link(href=noticia.link)
    
    imagem = buscar_imagem(noticia)
    if imagem:
        fe.enclosure(imagem, 0, 'image/jpeg')
        
    fe.description(noticia.get('description', ''))

fg.rss_file('feed_mestre.xml')
print("Sucesso! Super Feed atualizado.")
