import feedparser
import re
import json
import time
import os
import email.utils
from datetime import datetime
import requests 

# ==========================================
# 1. LISTA DE FEEDS E LOGOS
# ==========================================
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
    'https://news.google.com/rss/search?q=Americana+SP&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    'https://vagas019.com.br/feed/'
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
    'sb24horas': 'https://portaldosportais.com/wp-content/uploads/2026/05/images.jpg',
    'vagas019': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo-vagas0192.webp'
}

LINK_FALLBACK_PADRAO = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

# ==========================================
# 2. INTELIGÊNCIA DAS IMAGENS
# ==========================================
IMAGENS_CATEGORIA = {
    'politica': 'https://portaldosportais.com/wp-content/uploads/2026/05/Politica-scaled.jpg',
    'infraestrutura': 'https://portaldosportais.com/wp-content/uploads/2026/05/infraestrutura-scaled.jpg',
    'dae': 'https://portaldosportais.com/wp-content/uploads/2026/05/dae.jpeg',
    'economia': 'https://portaldosportais.com/wp-content/uploads/2026/05/financas-scaled.jpg',
    'empregos': 'https://portaldosportais.com/wp-content/uploads/2026/05/pexels-mart-production-7644081-scaled.jpg',
    'educacao': 'https://portaldosportais.com/wp-content/uploads/2026/05/classroom-scaled.jpg',
    'esportes': 'https://portaldosportais.com/wp-content/uploads/2026/05/esporte-scaled.jpg',
    'eventos': 'https://portaldosportais.com/wp-content/uploads/2026/05/events-scaled.jpg',
    'saude': 'https://portaldosportais.com/wp-content/uploads/2026/05/saude-scaled.jpg',
    'policia': 'https://portaldosportais.com/wp-content/uploads/2026/05/policia-scaled.jpg',
    'frio': 'https://portaldosportais.com/wp-content/uploads/2026/05/frio.jpg',
    'americana': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana-scaled.jpg'
}

def categorizar_noticia(titulo, imagem_atual, fonte):
    t = str(titulo).lower()
    f = str(fonte).lower()
    nova_imagem = None

    if any(p in t for p in ['vagas', 'pat', 'emprego', 'estágio', 'ciee', 'contrata', 'processo seletivo']):
        nova_imagem = IMAGENS_CATEGORIA['empregos']
    elif any(p in t for p in ['indústria', 'comércio', 'economia', 'mercado', 'inflação', 'venda', 'negócio']):
        nova_imagem = IMAGENS_CATEGORIA['economia']
    elif any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe', 'tráfico', 'arma', 'violência', 'crime', 'homicídio', 'morte', 'assalto', 'tiroteio', 'drogas', 'investigação']):
        nova_imagem = IMAGENS_CATEGORIA['policia']
    elif any(p in t for p in ['câmara', 'prefeito', 'vereador', 'sardelli', 'eleição', 'projeto', 'lei', 'tce', 'tse', 'votação', 'deputado']):
        nova_imagem = IMAGENS_CATEGORIA['politica']
    elif any(p in t for p in ['dae', 'bomba', 'abastecimento', 'água', 'esgoto', 'reforma filtros', 'reservatório', 'estação de tratamento']):
        nova_imagem = IMAGENS_CATEGORIA['dae']
    elif any(p in t for p in ['saúde', 'hospital', 'hm', 'dengue', 'vacina', 'médico', 'consulta', 'ubs', 'posto de saúde', 'cuidados paliativos']):
        nova_imagem = IMAGENS_CATEGORIA['saude']
    elif any(p in t for p in ['frio', 'geada', 'inverno', 'temperatura', 'frente fria', 'mínima']):
        nova_imagem = IMAGENS_CATEGORIA['frio']
    elif any(p in t for p in ['asfalto', 'obra', 'iluminação', 'reforma', 'praça', 'infraestrutura', 'recapeamento', 'viaduto']):
        nova_imagem = IMAGENS_CATEGORIA['infraestrutura']
    elif any(p in t for p in ['escola', 'creche', 'educação', 'univesp', 'fatec', 'aluno', 'professor', 'enem', 'curso', 'aula', 'faculdade']):
        nova_imagem = IMAGENS_CATEGORIA['educacao']
    elif any(p in t for p in ['futebol', 'rio branco', 'campeonato', 'jogo', 'atleta', 'esporte', 'ginásio', 'torneio', 'medalha', 'copa', 'libertadores', 'tênis', 'atc']):
        nova_imagem = IMAGENS_CATEGORIA['esportes']
    elif any(p in t for p in ['show', 'festa', 'teatro', 'cinema', 'evento', 'exposição', 'cultura', 'aniversário', 'celebrar']):
        nova_imagem = IMAGENS_CATEGORIA['eventos']
    elif 'americana' in t:
        nova_imagem = IMAGENS_CATEGORIA['americana']

    if 'vagas019' in f or 'vagas 019' in f:
        if not nova_imagem:
            nova_imagem = IMAGENS_CATEGORIA['empregos']

    if 'novomomento' in f or 'novo momento' in f:
        return nova_imagem if nova_imagem else LINK_FALLBACK_PADRAO

    link_limpo = str(imagem_atual).lower()
    palavras_lixo = ['logo', 'default', 'padrao', 'fallback', '0addff39', 'americana-post', 'kyijbwc6', 'o-jogo', 'images.jpg', 'images.png', 'download.jpg', 'download.png', 'cropped', 'nm-site', 'sem-foto', 'placeholder', 'blank', 'thumb', 'marca', 'capa', '150x150', '300x200', '300x300', 'logo-vagas']

    is_lixo = any(lixo in link_limpo for lixo in palavras_lixo)
    is_fallback = LINK_FALLBACK_PADRAO.split('/')[-1].lower() in link_limpo

    if not imagem_atual or is_lixo or is_fallback:
        return nova_imagem if nova_imagem else LINK_FALLBACK_PADRAO

    return imagem_atual

def nome_curto_portal(url):
    for chave in LOGOS_PORTAIS.keys():
        if chave in url:
            return chave
    return 'portal'

def extrair_melhor_imagem(entry, url):
    if entry.get('media_content'):
        return entry.media_content[0].get('url', '')
    if entry.get('links'):
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href', '')
    if entry.get('description'):
        match = re.search(r'<img [^>]*src="([^"]+)"', entry.description)
        if match: return match.group(1)
    return ''

# ==========================================
# 3. PROCESSO PRINCIPAL DE AGREGAÇÃO
# ==========================================
lista_final = []
links_processados = set()

# Carrega histórico antigo para não perder as de ontem
if os.path.exists('feed_mestre.json'):
    try:
        with open('feed_mestre.json', 'r', encoding='utf-8') as f:
            dados_antigos = json.load(f)
            for noticia in dados_antigos:
                if noticia.get('link') not in links_processados:
                    lista_final.append(noticia)
                    links_processados.add(noticia.get('link'))
    except Exception: pass

# Raspa os portais
for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        print(f"[{nome_curto_portal(url)}] Sincronizando...")
        
        for entry in feed.entries[:30]: 
            link_noticia = entry.get('link', '')
            if not link_noticia or link_noticia in links_processados:
                continue
                
            titulo_seguro = entry.get('title', 'Notícia')
            portal_nome = nome_curto_portal(url)
            imagem_original = extrair_melhor_imagem(entry, url)
            imagem_final = categorizar_noticia(titulo_seguro, imagem_original, portal_nome)
            
            # Pega a data real que o portal diz que publicou
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                timestamp_real = time.mktime(entry.published_parsed)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                timestamp_real = time.mktime(entry.updated_parsed)
            else:
                timestamp_real = time.time()
                
            data_str = datetime.fromtimestamp(timestamp_real).strftime("%d/%m/%Y %H:%M")
            
            noticia_objeto = {
                'titulo': titulo_seguro,
                'link': link_noticia,
                'imagem': imagem_final,
                'portal': portal_nome,
                'logo_portal': LOGOS_PORTAIS.get(portal_nome, LINK_FALLBACK_PADRAO),
                'timestamp': timestamp_real,
                'data': data_str
            }
            
            lista_final.append(noticia_objeto)
            links_processados.add(link_noticia)
            
    except Exception as e:
        print(f"Erro em {url}: {e}")

# Ordena a lista da mais nova para a mais velha baseada no timestamp
lista_final.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
lista_final = lista_final[:1000]

# Salva
if len(lista_final) > 0:
    with open('feed_mestre.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=4)
    print("✅ Feed principal da RMC atualizado com sucesso!")
