import feedparser
from feedgen.feed import FeedGenerator
import re
from datetime import datetime
import pytz

# 1. Lista de Feeds
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

def buscar_imagem(entry):
    """Um buscador de imagens muito mais agressivo para o WordPress"""
    
    # 1. Tenta pegar a "Featured Image" que o WordPress moderno usa no XML
    if 'post-thumbnail' in entry:
        return entry.get('post-thumbnail')
        
    if hasattr(entry, 'media_thumbnail') and len(entry.media_thumbnail) > 0:
         return entry.media_thumbnail[0].get('url', '')

    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    
    # 2. Tenta caçar no enclosure
    if 'links' in entry:
        for link in entry.links:
            if link.get('type', '').startswith('image/') or link.get('rel') == 'enclosure':
                return link.get('href', '')
                
    # 3. Caça no conteúdo completo (content:encoded do WordPress)
    if 'content' in entry and len(entry.content) > 0:
        texto_conteudo = entry.content[0].value
        # Busca a primeira tag <img> e pega o src
        match = re.search(r'<img[^>]+src="([^">]+)"', texto_conteudo)
        if match: 
            img_url = match.group(1)
            # Evita puxar emojis ou icones minusculos do site
            if "emoji" not in img_url and "avatar" not in img_url:
                return img_url
        
    # 4. Caça na descrição resumida
    if 'description' in entry:
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.description)
        if match: 
            img_url = match.group(1)
            if "emoji" not in img_url and "avatar" not in img_url:
                return img_url
        
    # 5. Fallback: Se realmente não houver foto, usa a sua
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
    
    # Removemos as tags de imagem quebradas que alguns sites mandam na descrição limpa
    descricao_limpa = re.sub(r'<img[^>]*>', '', descricao_texto)
    
    if imagem_original:
        if imagem_original == LINK_FALLBACK:
            imagem_forcada = imagem_original
        else:
            url_limpa = imagem_original.replace('https://', '').replace('http://', '')
            imagem_forcada = f"https://wsrv.nl/?url={url_limpa}&w=400&h=200&fit=cover&output=jpg"
        
        # Envia a enclosure corretamente pro WordPress
        fe.enclosure(imagem_forcada, '0', 'image/jpeg')
        
        # Só injeta na descrição se NÃO for o Feedzy nativo (para não duplicar). 
        # Vamos deixar limpo para o leitor RSS nativo do WP funcionar melhor.
        fe.description(descricao_limpa)
    else:
        fe.description(descricao_limpa)

# 5. Gera o arquivo
fg.rss_file('feed_mestre.xml')
print("Sucesso! Super Feed atualizado com buscador agressivo.")
