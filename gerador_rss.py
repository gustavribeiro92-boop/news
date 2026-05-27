import feedparser
import re
import json
import time
import os
import calendar
import random
from datetime import datetime, timezone, timedelta
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
    'https://novomomento.com.br/feed/atom/',
    'https://portaldeamericana.com/feed/',
    'https://rapidonoar.com.br/feed/',
    'https://redefamilia.com.br/feed/',
    'https://sb24horas.com.br/feed/',
    'https://news.google.com/rss/search?q=Americana+SP+when:2d&hl=pt-BR&gl=BR&ceid=BR:pt-419',
    'https://vagas019.com.br/feed/'
]

LOGOS_PORTAIS = {
    'americana post': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana-post.png',
    'difusorapiracicaba': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo_font_white.svg',
    'hjnews': 'https://portaldosportais.com/wp-content/uploads/2026/05/KYiJBWc6_400x400.jpg',
    'jornalojogo': 'https://portaldosportais.com/wp-content/uploads/2026/05/O-JOGO_LOGO.png',
    'noticiadelimeira': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo.svg',
    'noticia fm': 'https://portaldosportais.com/wp-content/uploads/2026/05/LogoNoticia_2024_512x512-2.png',
    'novo momento': 'https://portaldosportais.com/wp-content/uploads/2026/05/0addff39-logo-1.png',
    'portal de americana': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo.avif',
    'rapidonoar': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo-rapido-no-ar-300.png',
    'redefamilia': 'https://portaldosportais.com/wp-content/uploads/2026/05/logotipo.png',
    'sb24horas': 'https://portaldosportais.com/wp-content/uploads/2026/05/images.jpg',
    'vagas019': 'https://portaldosportais.com/wp-content/uploads/2026/05/logo-vagas0192.webp'
}

LINK_FALLBACK_PADRAO = 'https://portaldosportais.com/wp-content/uploads/2026/05/americana.jpg'

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
    'frio': 'https://portaldosportais.com/wp-content/uploads/2026/05/pexels-ammy-singh-294201421-14965455-scaled.jpg',
    'transito': 'https://portaldosportais.com/wp-content/uploads/2026/05/transito-scaled.jpg',
    'campinas': 'https://portaldosportais.com/wp-content/uploads/2026/05/download.jpg',
    'sbo': 'https://portaldosportais.com/wp-content/uploads/2026/05/images-1.jpg',
    'americana': 'https://portaldosportais.com/wp-content/uploads/2026/05/americana.jpg'
}

def categorizar_noticia(titulo, imagem_atual, fonte):
    t = str(titulo).lower()
    f = str(fonte).lower()
    nova_imagem = None

    if any(p in t for p in ['vagas', 'pat', 'emprego', 'estágio', 'ciee', 'contrata', 'processo seletivo', 'trabalho']):
        nova_imagem = IMAGENS_CATEGORIA['empregos']
    elif any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe', 'tráfico', 'arma', 'violência', 'crime', 'homicídio', 'morre', 'morte', 'assalto', 'tiroteio', 'drogas', 'investigação', 'morreu', 'atropelado', 'corpo', 'vítima', 'fatal', 'incêndio', 'bombeiros']):
        nova_imagem = IMAGENS_CATEGORIA['policia']
    elif any(p in t for p in ['câmara', 'prefeito', 'prefeitura', 'vereador', 'sardelli', 'eleição', 'projeto', 'lei', 'tce', 'tse', 'votação', 'deputado', 'lula', 'bolsonaro', 'tarcísio', 'governo']):
        nova_imagem = IMAGENS_CATEGORIA['politica']
    elif any(p in t for p in ['asfalto', 'obra', 'iluminação', 'reforma', 'praça', 'infraestrutura', 'recapeamento', 'viaduto', 'trânsito', 'rodovia']):
        nova_imagem = IMAGENS_CATEGORIA['infraestrutura']
    
    if 'vagas019' in f or 'vagas 019' in f:
        if not nova_imagem: nova_imagem = IMAGENS_CATEGORIA['empregos']

    link_limpo = str(imagem_atual).lower()
    palavras_lixo = ['logo', 'logotipo', 'default', 'padrao', 'fallback', '0addff39', 'americana-post', 'kyijbwc6', 'o-jogo', 'images.jpg', 'images.png', 'download.jpg', 'download.png', 'cropped', 'nm-site', 'sem-foto', 'placeholder', 'blank', 'thumb', 'marca', 'capa']
    
    is_lixo = any(lixo in link_limpo for lixo in palavras_lixo)
    is_fallback = LINK_FALLBACK_PADRAO.split('/')[-1].lower() in link_limpo
    
    if not imagem_atual or is_lixo or is_fallback:
        return nova_imagem if nova_imagem else IMAGENS_CATEGORIA['americana']
    return imagem_atual

def nome_curto_portal(url):
    if 'americanapost' in url: return 'americana post'
    if 'difusorapiracicaba' in url: return 'difusorapiracicaba'
    if 'hjnews' in url: return 'hjnews'
    if 'jornalojogo' in url: return 'jornalojogo'
    if 'noticiadelimeira' in url: return 'noticiadelimeira'
    if 'noticiafm' in url: return 'noticia fm'
    if 'novomomento' in url: return 'novo momento'
    if 'portaldeamericana' in url: return 'portal de americana'
    if 'rapidonoar' in url: return 'rapidonoar'
    if 'redefamilia' in url: return 'redefamilia'
    if 'sb24horas' in url: return 'sb24horas'
    if 'vagas019' in url: return 'vagas019'
    return 'portal'

def extrair_melhor_imagem(entry):
    if hasattr(entry, 'media_content') and entry.media_content:
        return entry.media_content[0].get('url', '')
    if hasattr(entry, 'links'):
        for link in entry.links:
            if 'image' in link.get('type', ''): return link.get('href', '')
    html_alvo = getattr(entry, 'summary', '') + getattr(entry, 'description', '')
    match = re.search(r'<img [^>]*src=["\']([^"\']+)["\']', html_alvo)
    return match.group(1) if match else ''

# ==========================================
# 3. PROCESSO PRINCIPAL
# ==========================================
lista_final = []
assinaturas_processadas = set()

if os.path.exists('feed_mestre.json'):
    try:
        with open('feed_mestre.json', 'r', encoding='utf-8') as f:
            dados_antigos = json.load(f)
            for noticia in dados_antigos:
                assinatura = f"{noticia.get('titulo')}-{noticia.get('link')}"
                lista_final.append(noticia)
                assinaturas_processadas.add(assinatura)
    except: pass

for url in FEEDS:
    portal_nome = nome_curto_portal(url)
    try:
        resposta = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        feed = feedparser.parse(resposta.content)
        for entry in feed.entries[:30]: 
            link = entry.get('link', entry.get('id', ''))
            titulo = entry.get('title', 'Sem Título')
            assinatura_nova = f"{titulo}-{link}"
            
            if assinatura_nova in assinaturas_processadas: continue
                
            img = categorizar_noticia(titulo, extrair_melhor_imagem(entry), portal_nome)
            
            noticia_obj = {
                'titulo': titulo, 'link': link, 'imagem': img, 
                'portal': portal_nome, 'data': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'timestamp': time.time()
            }
            lista_final.append(noticia_obj)
            assinaturas_processadas.add(assinatura_nova)
    except Exception as e: print(f"Erro em {portal_nome}: {e}")

lista_final.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
lista_final = lista_final[:2000]

with open('feed_mestre.json', 'w', encoding='utf-8') as f:
    json.dump(lista_final, f, ensure_ascii=False, indent=4)
print("🎉 Hub atualizado com sucesso!")
