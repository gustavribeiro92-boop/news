import feedparser
from feedgen.feed import FeedGenerator
import re
from datetime import datetime
import pytz

# 1. A sua lista de portais da região (TV Thathi removida)
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

# Link da sua imagem padrão
LINK_FALLBACK = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

def buscar_imagem(entry):
    """Caça a imagem em todos os buracos possíveis do RSS"""
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/') or link.get('rel') == 'enclosure':
                return link.get('href', '')
                
    if 'content' in entry and len(entry.content) > 0:
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.content[0].value)
        if match: return match.group(1)
        
    if 'description' in entry:
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.description)
        if match: return match.group(1)
        
    # 5. O SEU FALLBACK (Caso o site não mande nenhuma imagem)
    return LINK_FALLBACK

# 2. Configuração do Super Feed
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

# 3. Ordenar pelas mais recentes
def extrair_data(entry):
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        return entry.published_parsed
    return datetime.now().timetuple()

todas_noticias.sort(key=extrair_data, reverse=True)

# 4. Monta o arquivo XML final
for noticia in todas_noticias[:50]:
    fe = fg.add_entry()
    fe.title(f"[{noticia.portal_origem}] {noticia.title}")
    fe.link(href=noticia.link)
    
    imagem_original = buscar_imagem(noticia)
    descricao_texto = noticia.get('description', '')
    
    if imagem_original:
        # Se for a sua imagem de fallback, não precisa do proxy wsrv.nl
        if imagem_original == LINK_FALLBACK:
            imagem_forcada = imagem_original
        else:
            # Proxy para quebrar proteção de Hotlink nos sites da região
            url_limpa = imagem_original.replace('https://', '').replace('http://', '')
            imagem_forcada = f"https://wsrv.nl/?url={url_limpa}&w=400&h=200&fit=cover"
        
        # Anexa para o Feedzy
        fe.enclosure(imagem_forcada, 0, 'image/jpeg')
        
        # Injeta no texto para garantir que vai renderizar na tela
        nova_descricao = f'<img src="{imagem_forcada}" alt="Imagem da notícia" style="width:100%; max-width:400px; border-radius:8px; margin-bottom:10px;" /><br>{descricao_texto}'
        fe.description(nova_descricao)
    else:
        fe.description(descricao_texto)

# 5. Gera o arquivo
fg.rss_file('feed_mestre.xml')
print("Sucesso! Super Feed atualizado com imagens forçadas.")
