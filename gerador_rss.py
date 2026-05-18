import feedparser
import re
import json
import time
import os
import calendar
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
    'https://novomomento.com.br/feed/atom/',  # 🚀 A PORTA DOS FUNDOS (Desvia do cache travado)
    'https://portaldeamericana.com/feed/',
    'https://rapidonoar.com.br/feed/',
    'https://redefamilia.com.br/feed/',
    'https://sb24horas.com.br/feed/',
    'https://news.google.com/rss/search?q=Americana+SP&hl=pt-BR&gl=BR&ceid=BR:pt-419',
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

LINK_FALLBACK_PADRAO = 'https://portaldosportais.com/wp-content/uploads/2026/05/Gemini_Generated_Image_wk6240wk6240wk62-1.png'

# ==========================================
# 2. INTELIGÊNCIA DAS IMAGENS (Dicionário Massivo)
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
    elif any(p in t for p in ['indústria', 'comércio', 'economia', 'mercado', 'inflação', 'venda', 'negócio', 'imposto', 'mega-sena', 'prêmio']):
        nova_imagem = IMAGENS_CATEGORIA['economia']
    elif any(p in t for p in ['gama', 'polícia', 'pm', 'preso', 'furto', 'roubo', 'acidente', 'baep', 'guarda', 'golpe', 'tráfico', 'arma', 'violência', 'crime', 'homicídio', 'morte', 'assalto', 'tiroteio', 'drogas', 'investigação', 'morreu', 'atropelado', 'corpo', 'vítima', 'fatal', 'incêndio', 'bombeiros']):
        nova_imagem = IMAGENS_CATEGORIA['policia']
    elif any(p in t for p in ['câmara', 'prefeito', 'prefeitura', 'vereador', 'sardelli', 'eleição', 'projeto', 'lei', 'tce', 'tse', 'votação', 'deputado', 'lula', 'bolsonaro', 'tarcísio', 'governo']):
        nova_imagem = IMAGENS_CATEGORIA['politica']
    elif any(p in t for p in ['dae', 'bomba', 'abastecimento', 'água', 'esgoto', 'reforma filtros', 'reservatório', 'estação de tratamento', 'vazamento']):
        nova_imagem = IMAGENS_CATEGORIA['dae']
    elif any(p in t for p in ['saúde', 'hospital', 'hm', 'dengue', 'vacina', 'médico', 'consulta', 'ubs', 'posto de saúde', 'cuidados paliativos', 'doença', 'paciente', 'medicamento']):
        nova_imagem = IMAGENS_CATEGORIA['saude']
    elif any(p in t for p in ['frio', 'geada', 'inverno', 'temperatura', 'frente fria', 'chuva', 'clima', 'tempo']):
        nova_imagem = IMAGENS_CATEGORIA['frio']
    elif any(p in t for p in ['asfalto', 'obra', 'iluminação', 'reforma', 'praça', 'infraestrutura', 'recapeamento', 'viaduto', 'trânsito', 'rodovia']):
        nova_imagem = IMAGENS_CATEGORIA['infraestrutura']
    elif any(p in t for p in ['escola', 'creche', 'educação', 'univesp', 'fatec', 'aluno', 'professor', 'enem', 'curso', 'aula', 'faculdade', 'cei']):
        nova_imagem = IMAGENS_CATEGORIA['educacao']
    elif any(p in t for p in ['futebol', 'rio branco', 'campeonato', 'jogo', 'atleta', 'esporte', 'ginásio', 'torneio', 'medalha', 'copa', 'libertadores', 'tênis', 'sesi']):
        nova_imagem = IMAGENS_CATEGORIA['esportes']
    elif any(p in t for p in ['show', 'festa', 'teatro', 'cinema', 'evento', 'exposição', 'cultura', 'aniversário', 'celebrar', 'festival', 'sinfônica']):
        nova_imagem = IMAGENS_CATEGORIA['eventos']
    elif any(p in t for p in ['rodovia', 'anhanguera', 'sp-304', 'trânsito', 'pedágio', 'motorista', 'ônibus']):
        nova_imagem = IMAGENS_CATEGORIA['transito']
    elif 'campinas' in t:
        nova_imagem = IMAGENS_CATEGORIA['campinas']
    elif any(p in t for p in ['santa bárbara', 'sbo']):
        nova_imagem = IMAGENS_CATEGORIA['sbo']

    if 'vagas019' in f or 'vagas 019' in f:
        if not nova_imagem:
            nova_imagem = IMAGENS_CATEGORIA['empregos']

    link_limpo = str(imagem_atual).lower()
    
    # TRATOR IMPLACÁVEL V2 (Resgatado do seu histórico)
    palavras_lixo = ['logo', 'logotipo', 'default', 'padrao', 'fallback', '0addff39', 'americana-post', 'kyijbwc6', 'o-jogo', 'images.jpg', 'images.png', 'download.jpg', 'download.png', 'cropped', 'nm-site', 'sem-foto', 'placeholder', 'blank', 'thumb', 'marca', 'capa', '150x150', '300x200', '300x300', 'logo-vagas', 'icon', 'avatar']
    
    is_lixo = any(lixo in link_limpo for lixo in palavras_lixo)
    is_fallback = LINK_FALLBACK_PADRAO.split('/')[-1].lower() in link_limpo
    is_logo_nosso = any(logo.split('/')[-1].lower() in link_limpo for logo in LOGOS_PORTAIS.values())

    # Se a foto é lixo ou um logo repetido, usa a Categoria. Se não tiver categoria, usa a de Americana.
    if not imagem_atual or is_lixo or is_fallback or is_logo_nosso:
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
    if 'news.google' in url: return 'Google Notícias'
    return 'portal'

def extrair_melhor_imagem(entry):
    if 'media_content' in entry and len(entry.media_content) > 0:
        return entry.media_content[0].get('url', '')
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''):
                return link.get('href', '')
    html_alvo = ""
    if 'description' in entry: html_alvo += entry.description
    if 'summary' in entry: html_alvo += entry.summary
    if 'content' in entry:
        for c in entry.content: html_alvo += c.value
    if html_alvo:
        match = re.search(r'<img [^>]*src=["\']([^"\']+)["\']', html_alvo)
        if match: return match.group(1)
    return ''

# ==========================================
# 3. PROCESSO PRINCIPAL DE AGREGAÇÃO
# ==========================================
lista_final = []
links_processados = set()

if os.path.exists('feed_mestre.json'):
    try:
        with open('feed_mestre.json', 'r', encoding='utf-8') as f:
            dados_antigos = json.load(f)
            for noticia in dados_antigos:
                if noticia.get('link') not in links_processados:
                    lista_final.append(noticia)
                    links_processados.add(noticia.get('link'))
    except Exception: pass

# O Disfarce Perfeito resgatado
headers_navegador = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
}

for url in FEEDS:
    portal_nome = nome_curto_portal(url)
    try:
        print(f"📡 [{portal_nome}] Puxando dados...")
        
        # 🚀 A MÁGICA DE DISTINÇÃO (O Google não gosta de disfarce)
        if 'news.google' in url:
            feed = feedparser.parse(url)
        else:
            resposta = requests.get(url, headers=headers_navegador, timeout=15)
            if resposta.status_code != 200:
                print(f"  ❌ Falha: Status {resposta.status_code}")
                continue
            feed = feedparser.parse(resposta.content)
            
        print(f"  ✅ Sincronizado: {len(feed.entries)} entradas.")
        
        for entry in feed.entries[:30]: 
            link_noticia = entry.get('link', '')
            if not link_noticia or link_noticia in links_processados:
                continue
                
            titulo_seguro = entry.get('title', 'Notícia')
            imagem_original = extrair_melhor_imagem(entry)
            imagem_final = categorizar_noticia(titulo_seguro, imagem_original, portal_nome)
            
            # OTIMIZADOR DE IMAGENS (wsrv.nl)
            todas_nossas_imagens = list(LOGOS_PORTAIS.values()) + list(IMAGENS_CATEGORIA.values()) + [LINK_FALLBACK_PADRAO]
            if not any(nossa.split('/')[-1] in imagem_final for nossa in todas_nossas_imagens) and 'wsrv.nl' not in imagem_final:
                url_sem_http = imagem_final.replace('https://', '').replace('http://', '')
                imagem_final = f"https://wsrv.nl/?url={url_sem_http}&w=400&h=200&fit=cover&output=jpg"
            
            # Fuso Horário de Brasília
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                timestamp_utc = calendar.timegm(entry.published_parsed)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                timestamp_utc = calendar.timegm(entry.updated_parsed)
            else:
                timestamp_utc = time.time()
                
            timestamp_br = timestamp_utc - (3 * 3600)
            data_str = datetime.utcfromtimestamp(timestamp_br).strftime("%d/%m/%Y %H:%M")
            
            noticia_objeto = {
                'titulo': titulo_seguro,
                'link': link_noticia,
                'imagem': imagem_final,
                'portal': portal_nome,
                'logo_portal': LOGOS_PORTAIS.get(portal_nome, LINK_FALLBACK_PADRAO),
                'timestamp': timestamp_br,
                'data': data_str
            }
            
            lista_final.append(noticia_objeto)
            links_processados.add(link_noticia)
            
    except Exception as e:
        print(f"🚨 Erro no portal {portal_nome}: {e}")

lista_final.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
lista_final = lista_final[:1000]

# Trava de Segurança Máxima
if len(lista_final) > 0:
    with open('feed_mestre.json', 'w', encoding='utf-8') as f:
        json.dump(lista_final, f, ensure_ascii=False, indent=4)
    print("🎉 Hub de Notícias atualizado! Motor Híbrido ativado.")
