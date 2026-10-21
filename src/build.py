#!/usr/bin/env python3
"""Gera o site estático em ../dist a partir de dados.json.
Uso: python3 build.py"""
import json, os, re, shutil, html as H
from urllib.parse import urlparse, quote
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(os.path.dirname(AQUI), 'dist')
D = json.load(open(os.path.join(AQUI, 'dados.json'), encoding='utf-8'))
BASE = D['BASE_URL'].rstrip('/') + '/'
NOME = D['NOME']
CURTO = D['NOME_CURTO']
CID = f"{D['CIDADE']}/{D['UF']}"
e = H.escape

def dig(s): return re.sub(r'\D', '', s or '')
def zap_link(msg='Olá! Quero informações sobre o curso de vigilante.'):
    n = dig(D['WHATSAPP'])
    if len(n) <= 11: n = '55' + n
    return f'https://wa.me/{n}?text={quote(msg)}'
TEL = 'tel:+55' + dig(D['TELEFONE'])
def ok(k):
    v = D.get(k) or ''
    return isinstance(v, str) and v.strip() != '' and not v.strip().startswith('[')
IG_USER = D['INSTAGRAM'].strip('@ ') if ok('INSTAGRAM') else ''
INSTA = f'https://www.instagram.com/{IG_USER}/'
ENDER = f"{D['ENDERECO']}, {D['BAIRRO']}, {CID}, CEP {D['CEP']}"
MAPA_Q = f"{D['LAT']},{D['LNG']}" if D['LAT'] else f"{D['ENDERECO']}, {D['BAIRRO']}, {D['CIDADE']} - {D['UF']}"
MAPA_EMBED = 'https://www.google.com/maps?q=' + quote(MAPA_Q) + '&output=embed'
MAPA_LINK = 'https://www.google.com/maps/search/?api=1&query=' + quote(MAPA_Q)
PORTAL = D['PORTAL_URL']

IMG_DIR = os.path.join(AQUI, 'assets', 'img')
def tem_img(nome):
    for ext in ('.webp', '.jpg', '.jpeg', '.png', '.svg'):
        if os.path.exists(os.path.join(IMG_DIR, nome + ext)): return 'assets/img/' + nome + ext
    return None

# ---------- ícones (traço) ----------
def ico(d, fill=False):
    if fill: return f'<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="{d}"/></svg>'
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{d}</svg>'
I = {
 'zap': ico('M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.4.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z', True),
 'ig': ico('<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>'),
 'tel': ico('<path d="M5 3h3l2 5-2.5 1.5a11 11 0 0 0 7 7L16 14l5 2v3a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2Z"/>'),
 'pin': ico('<path d="M12 21s-7-6.2-7-12a7 7 0 0 1 14 0c0 5.8-7 12-7 12Z"/><circle cx="12" cy="9" r="2.5"/>'),
 'relogio': ico('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
 'email': ico('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>'),
 'escudo': ico('<path d="M12 3 20 6v6c0 5-3.4 8.4-8 9-4.6-.6-8-4-8-9V6Z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>'),
 'atualiza': ico('<path d="M20 11a8 8 0 0 0-14.6-4.5M4 3.5v4h4M4 13a8 8 0 0 0 14.6 4.5M20 20.5v-4h-4"/>'),
 'caminhao': ico('<rect x="2" y="6" width="12" height="10" rx="1"/><path d="M14 9.5h4l3 3.5v3h-7"/><circle cx="6.5" cy="17.5" r="2"/><circle cx="17" cy="17.5" r="2"/><path d="M6 11h4"/>'),
 'escolta': ico('<path d="M4 16.5 5.6 11a2 2 0 0 1 1.9-1.5h9a2 2 0 0 1 1.9 1.5l1.6 5.5"/><rect x="3" y="16" width="18" height="3.5" rx="1"/><path d="M10 6.5h4M12 4.5v2"/><circle cx="7" cy="19.5" r="1"/><circle cx="17" cy="19.5" r="1"/>'),
 'pessoa': ico('<circle cx="12" cy="7" r="3.5"/><path d="M5 21c0-4 3-6.5 7-6.5s7 2.5 7 6.5"/><path d="M15.4 6.2c.9 0 1.6.7 1.6 1.6v1.2"/>'),
 'eventos': ico('<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.4"/><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5M15.5 14.6c3 0 5.5 1.7 5.5 5"/>'),
 'raio': ico('<path d="M13 2 4.5 14H11l-1 8 8.5-12H12Z"/>'),
 'estrela': ico('<path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1-4.4-4.3 6.1-.9Z"/>'),
 'alvo': ico('<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2" fill="currentColor"/><path d="M12 1.5v3M12 19.5v3M1.5 12h3M19.5 12h3"/>'),
 'doc': ico('<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8Zm0 0v5h5M9 13h6M9 17h4"/>'),
 'upload': ico('<path d="M12 15V4m0 0L8 8m4-4 4 4M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>'),
 'confere': ico('<rect x="4" y="3" width="16" height="18" rx="2"/><path d="m8.5 12 2.5 2.5 4.5-5"/>'),
 'formatura': ico('<path d="M2 9 12 4l10 5-10 5Z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5M22 9v5"/>'),
 'celular': ico('<rect x="6" y="2" width="12" height="20" rx="2"/><path d="M11 18h2"/>'),
 'instrutor': ico('<circle cx="12" cy="6.5" r="3"/><path d="M6 21v-4a6 6 0 0 1 12 0v4M9.5 13.5 12 17l2.5-3.5"/>'),
 'ok': ico('<path d="m5 12.5 4.5 4.5L19 7"/>'),
 'menu': ico('<path d="M4 7h16M4 12h16M4 17h16"/>'),
 'calendario': ico('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/>'),
}

def marca_svg(h=52):
    return ('<svg viewBox="0 0 40 46" aria-hidden="true"><path d="M20 2 37 8.5v13C37 32 29.8 40.4 20 43 10.2 40.4 3 32 3 21.5v-13Z" fill="#0E2244" stroke="#C9A227" stroke-width="2.5"/>'
            '<circle cx="20" cy="21.5" r="9" fill="none" stroke="#E3BD43" stroke-width="2.4"/><circle cx="20" cy="21.5" r="3.4" fill="#E3BD43"/>'
            '<path d="M20 9.5v5M20 28.5v5M8 21.5h5M27 21.5h5" stroke="#E3BD43" stroke-width="2.2"/></svg>')

def logo(rodape=False):
    src = tem_img('logo-branco' if rodape else 'logo') or tem_img('logo') or tem_img('logo-grande')
    if src: return f'<img src="{src}" alt="Brasão {e(CURTO)}" width="62" height="62"><span><b>{e(CURTO)}</b><small>Academia de Segurança Privada</small></span>'
    return marca_svg() + f'<span><b>{e(CURTO)}</b><small>Formação de vigilantes</small></span>'

PAGINAS = [
    ('index.html', 'Início'), ('a-escola.html', 'A escola'), ('cursos.html', 'Cursos'), ('turmas.html', 'Turmas'),
    ('como-ser-vigilante.html', 'Como ser vigilante'), ('empresas.html', 'Empresas'), ('contato.html', 'Contato'),
]

def btn_pre(txt='Fazer pré-matrícula', cls='btn-ouro'):
    return f'<a class="btn {cls}" href="{e(PORTAL)}">{I["doc"]}{e(txt)}</a>'
def btn_zap(msg='Olá! Quero informações sobre o curso de vigilante.', txt='Falar no WhatsApp', cls='btn-zap'):
    return f'<a class="btn {cls}" target="_blank" rel="noopener" href="{e(zap_link(msg))}">{I["zap"]}{e(txt)}</a>'

def foto(nome, legenda, cap=True):
    src = tem_img(nome)
    c = f'<figcaption>{e(legenda)}</figcaption>' if cap else ''
    if src: return f'<figure class="foto"><img src="{src}" alt="{e(legenda)}" loading="lazy" width="800" height="600">{c}</figure>'
    return f'<figure class="foto"><div class="vazio">Foto: {e(legenda)}<br><small>assets/img/{nome}.jpg</small></div>{c}</figure>'

def foto_ou_brasao(nome, legenda):
    lg = tem_img('logo-grande') or tem_img('logo')
    if tem_img(nome) or not lg: return foto(nome, legenda, False)
    return f'<figure class="foto"><div class="brasao-box"><img src="{lg}" alt="Brasão da {e(NOME)}" loading="lazy" width="300" height="346"></div></figure>'

def bg(nome):
    src = tem_img(nome)
    return f'<div class="bg" style="background-image:url(\'{src}\')"></div>' if src else '<div class="bg sem-foto"></div>'

def org_ld():
    ld = {
        '@context': 'https://schema.org', '@type': ['EducationalOrganization', 'LocalBusiness'],
        '@id': BASE + '#escola', 'name': NOME, 'url': BASE, 'telephone': D['TELEFONE'],
        'image': BASE + (tem_img('fachada') or tem_img('hero') or 'assets/icone.svg'),
        'logo': BASE + (tem_img('logo') or 'assets/icone.svg'),
        'description': f'Escola de formação de vigilantes autorizada pela Polícia Federal em {CID}.',
        'address': {'@type': 'PostalAddress', 'streetAddress': D['ENDERECO'], 'addressLocality': D['CIDADE'],
                    'addressRegion': D['UF'], 'postalCode': D['CEP'], 'addressCountry': 'BR'},
        'areaServed': ['Rondonópolis', 'Mato Grosso'], 'sameAs': [INSTA] if IG_USER else [],
    }
    if D['LAT']: ld['geo'] = {'@type': 'GeoCoordinates', 'latitude': D['LAT'], 'longitude': D['LNG']}
    return ld

def pagina(arquivo, titulo, descricao, corpo, ld=None, banner=None):
    nav = ''.join(f'<li><a href="{a}"{" aria-current=\"page\"" if a == arquivo else ""}>{e(n)}</a></li>' for a, n in PAGINAS)
    canon = BASE + ('' if arquivo == 'index.html' else arquivo)
    lds = ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in [org_ld()] + (ld or []))
    ban = ''
    if banner:
        ban = (f'<section class="banner">{bg(banner[3] if len(banner) > 3 else "banner")}<div class="wrap">'
               f'<nav class="migalha" aria-label="Você está em"><a href="./">Início</a> / {e(banner[0])}</nav>'
               f'<h1>{banner[1]}</h1><p>{banner[2]}</p></div></section>')
    og = BASE + (tem_img('og') or tem_img('hero') or tem_img('fachada') or tem_img('logo') or 'assets/icone.svg')
    links_rod = ''.join(f'<li><a href="{a}">{e(n)}</a></li>' for a, n in PAGINAS[1:])
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{canon}">
<meta name="theme-color" content="#151515">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="{e(NOME)}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{og}">
<link rel="icon" href="assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="assets/img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800&family=Open+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="assets/site.css">
{lds}
</head>
<body>
<div class="topbar"><div class="wrap">
<div class="esq"><a href="{TEL}">{I["tel"]}{e(D["TELEFONE"])}</a>{f'<span class="hor">{I["relogio"]}{e(D["HORARIO"])}</span>' if ok("HORARIO") else ""}</div>
<div class="dir"><a href="{e(zap_link())}" target="_blank" rel="noopener">{I["zap"]}{e(D["WHATSAPP"])}</a>{f'<a class="ig" href="{e(INSTA)}" target="_blank" rel="noopener">{I["ig"]}Instagram</a>' if IG_USER else ""}<a class="portal" href="{e(PORTAL)}">Portal do aluno</a></div>
</div></div>
<header class="topo"><div class="wrap">
<a class="marca" href="./" aria-label="{e(NOME)}, página inicial">{logo()}</a>
<nav class="nav" aria-label="Principal"><input type="checkbox" id="menu" class="menu-chk"><label for="menu" class="menu-btn" aria-label="Abrir menu">{I["menu"]}</label><ul>{nav}</ul>{btn_pre("Pré-matrícula", "btn-ouro btn-cab")}</nav>
</div></header>
<main>
{ban}
{corpo}
</main>
<footer class="rodape">
<div class="wrap">
<div><a class="marca" href="./">{logo(True)}</a><p>Escola de formação de vigilantes autorizada pela Polícia Federal{(". Autorização nº " + e(D["AUTORIZACAO_PF"])) if ok("AUTORIZACAO_PF") else ""}.</p><p style="margin-top:.5rem">CNPJ {e(D["CNPJ"])}</p>
<div class="redes">{f'<a href="{e(INSTA)}" target="_blank" rel="noopener" aria-label="Instagram">{I["ig"]}</a>' if IG_USER else ""}<a href="{e(zap_link())}" target="_blank" rel="noopener" aria-label="WhatsApp">{I["zap"]}</a></div></div>
<div><h4>Navegação</h4><ul>{links_rod}</ul></div>
<div><h4>Atendimento</h4><ul><li>{e(D["TELEFONE"])}</li><li>WhatsApp {e(D["WHATSAPP"])}</li><li>{e(D["EMAIL"])}</li>{f'<li>{e(D["HORARIO"])}</li>' if ok("HORARIO") else ""}</ul></div>
<div><h4>Endereço</h4><ul><li>{e(ENDER)}</li><li><a href="{e(MAPA_LINK)}" target="_blank" rel="noopener">Ver no Google Maps</a></li><li><a href="{e(PORTAL)}">Portal do aluno e pré-matrícula</a></li></ul></div>
</div>
<div class="rodape-fim"><div class="wrap"><span>© {date.today().year} {e(NOME)}. Todos os direitos reservados. <a href="{e(PORTAL)}privacidade.html">Privacidade</a></span><span>FIEL Soluções em Segurança Privada</span></div></div>
</footer>
<a class="zap-flut" href="{e(zap_link())}" target="_blank" rel="noopener" aria-label="Falar no WhatsApp">{I["zap"]}</a>
</body>
</html>
'''

# ---------- conteúdo ----------
# Base legal: Lei 14.967/2024, Decreto 13.012/2026, Portaria 22/2026-CGCSP/DPA/PF
CURSOS = [
  ('Formação', 'Para quem quer começar na profissão.', [
    ('formacao', 'escudo', 'Formação de Vigilante', 'Habilita a trabalhar como vigilante. Aulas de legislação, defesa pessoal, primeiros socorros, armamento e tiro, entre outras disciplinas.', 'Mínimo de 200 horas-aula'),
    ('supervisor', 'estrela', 'Formação de Vigilante Supervisor', 'Para quem vai liderar equipes de vigilância. Exige ensino médio completo, além dos requisitos do vigilante.', 'Exige ensino médio'),
  ]),
  ('Atualização (antiga reciclagem)', 'Para vigilantes formados manterem o curso em dia e continuarem trabalhando.', [
    ('atualizacao', 'atualiza', 'Atualização de Vigilante', 'Substitui a antiga reciclagem. Deve ser feita antes do vencimento do último curso para o vigilante continuar apto a trabalhar.', 'Antes do vencimento'),
    ('atualizacao-supervisor', 'atualiza', 'Atualização de Vigilante Supervisor', 'Mantém em dia a formação do vigilante supervisor.', 'Para supervisores'),
  ]),
  ('Aperfeiçoamento (antigas extensões)', 'Especializações para áreas específicas. Exigem a formação de vigilante.', [
    ('transporte', 'caminhao', 'Transporte de Numerário', 'Para atuar em carro-forte no transporte de valores.', 'Carro-forte'),
    ('escolta', 'escolta', 'Escolta de Numerário', 'Para escolta armada de cargas e valores.', 'Antiga escolta armada'),
    ('seguranca-pessoal', 'pessoa', 'Segurança Pessoal', 'Para proteção de pessoas e autoridades.', 'Antiga segurança pessoal privada'),
    ('eventos', 'eventos', 'Segurança de Eventos', 'Para shows, estádios e grandes eventos.', 'Grandes eventos'),
    ('menor-potencial', 'raio', 'Armas de Menor Potencial Ofensivo', 'Uso de equipamentos não letais, como espargidor, bastão e arma de choque.', 'Equipamentos não letais'),
  ]),
]
TODOS = {c[0]: c for _, _, it in CURSOS for c in it}

FAQ = [
  ('Quais os requisitos para ser vigilante?', 'Ser brasileiro (nato ou naturalizado), ter no mínimo 21 anos, ensino fundamental completo, estar quite com as obrigações eleitorais e militares, não ter antecedentes por crime doloso e ser aprovado nos exames de saúde física, mental e psicológica e no curso de formação.'),
  ('Qual a escolaridade exigida?', 'Ensino fundamental completo (9º ano) para o curso de formação de vigilante, regra em vigor desde 3 de agosto de 2026. Para vigilante supervisor, ensino médio completo.'),
  ('Quanto tempo dura o curso de formação?', 'A formação tem no mínimo 200 horas-aula. As datas e o turno de cada turma estão na página Turmas.'),
  ('Mulher pode ser vigilante?', 'Sim. Os requisitos são os mesmos para homens e mulheres.'),
  ('O curso é online?', 'Não. As aulas são presenciais, e as aulas de tiro acontecem no estande. A Polícia Federal só permite aulas teóricas remotas em situações específicas.'),
  ('Já sou vigilante. Quando faço a atualização (reciclagem)?', 'Antes de vencer o seu último curso. Se vencer, você fica impedido de trabalhar até atualizar. Pelo portal da escola você acompanha a validade dos seus cursos.'),
  ('Quais documentos preciso para a matrícula?', 'Documento com foto e CPF, comprovante de residência, comprovante de escolaridade, quitação eleitoral e militar (homens) e certidões negativas criminais. A lista completa está na página Como ser vigilante, e no portal você envia tudo pelo celular.'),
  ('Quanto custa o curso?', 'Os valores e as formas de pagamento mudam por curso e por turma. Chame no WhatsApp para receber o valor atualizado.'),
  ('O certificado vale em todo o Brasil?', f'Sim. A {NOME} é autorizada pela Polícia Federal, e os cursos concluídos são registrados no sistema da PF, valendo em todo o país.'),
]
def faq_html(itens):
    return '<div class="faq">' + ''.join(f'<details><summary>{e(q)}</summary><div><p>{e(a)}</p></div></details>' for q, a in itens) + '</div>'
def faq_ld(itens):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in itens]}

def tit(pre, h2, p='', centro=False):
    return f'<div class="tit{" centro" if centro else ""}"><span class="pre">{e(pre)}</span><h2>{h2}</h2>{f"<p>{p}</p>" if p else ""}</div>'

PASSOS = f'''<ol class="passos">
<li><span class="ico">{I["celular"]}</span><b>Pré-matrícula</b><p>Preencha seus dados pelo celular, no portal da escola.</p></li>
<li><span class="ico">{I["upload"]}</span><b>Documentos</b><p>Envie a foto dos documentos e certidões direto no portal.</p></li>
<li><span class="ico">{I["confere"]}</span><b>Confirmação</b><p>A secretaria confere tudo e confirma sua vaga na turma.</p></li>
<li><span class="ico">{I["formatura"]}</span><b>Aulas e certificado</b><p>Ao concluir, seu curso é registrado na Polícia Federal.</p></li>
</ol>'''

SEM_TURMA = f'<div class="sem-turma"><p>Abrimos turmas de formação, atualização e aperfeiçoamento ao longo do ano. Chame no WhatsApp para saber as datas, os turnos e as vagas da próxima turma.</p>{btn_zap("Olá! Quais as próximas turmas?", "Consultar turmas")}</div>'

def chamada(txt='Garanta sua vaga na próxima turma', msg='Olá! Quero garantir minha vaga na próxima turma.'):
    return f'<section class="chamada"><div class="wrap"><h2>{txt}</h2><div class="acoes">{btn_zap(msg, "Chamar no WhatsApp", "btn-azul")}</div></div></section>'

def build():
    if os.path.exists(SAIDA): shutil.rmtree(SAIDA)
    shutil.copytree(os.path.join(AQUI, 'assets'), os.path.join(SAIDA, 'assets'))
    open(os.path.join(SAIDA, 'assets', 'icone.svg'), 'w').write(marca_svg().replace('<svg ', '<svg xmlns="http://www.w3.org/2000/svg" ').replace(' aria-hidden="true"', ''))
    P = {}
    cont_horario = f'<div class="cont"><span class="ico">{I["relogio"]}</span><div><small>Horário</small><span>{e(D["HORARIO"])}</span></div></div>' if ok("HORARIO") else ''
    gal = [(n, l) for n, l in [("sala", "Sala de aula"), ("estande", "Estande de tiro"), ("defesa", "Defesa pessoal"), ("pratica", "Aula prática"), ("turma", "Turma formada"), ("recepcao", "Recepção e secretaria")] if tem_img(n)]
    sec_galeria = (f'<section class="secao cinza"><div class="wrap">{tit("Estrutura", "Nossa estrutura", "Ambientes preparados para as aulas teóricas e práticas exigidas pela Polícia Federal.", True)}'
                   f'<div class="galeria">{"".join(foto(n, l) for n, l in gal)}</div></div></section>') if gal else ''
    inst = D.get('INSTRUTORES') or []
    sec_instrutores = (f'<section class="secao cinza"><div class="wrap">{tit("Equipe", "Instrutores", "Profissionais credenciados pela Polícia Federal em cada disciplina.", True)}<div class="instrutores">'
                       + ''.join(f'<div class="instrutor">{foto("instrutor-" + str(i + 1), x.get("nome", ""), False)}<div><b>{e(x.get("nome", ""))}</b><span>{e(x.get("disciplina", ""))}</span></div></div>' for i, x in enumerate(inst))
                       + '</div></div></section>') if inst else ''
    lg = tem_img('logo-grande') or tem_img('logo')
    logo_grande = f'<img class="hero-logo" src="{lg}" alt="Brasão da {e(NOME)}" width="360" height="408">' if lg else ''
    hero_src = tem_img('hero')
    hero_bg = f'<div class="hero-bg" style="background-image:url(\'{hero_src}\')"></div>' if hero_src else '<div class="hero-bg sem-foto"></div>'
    serv = [('formacao', 'Formação de Vigilante', '200 h/a'), ('atualizacao', 'Atualização', 'Antiga reciclagem'),
            ('transporte', 'Transporte de Numerário', 'Carro-forte'), ('escolta', 'Escolta de Numerário', 'Escolta armada'),
            ('seguranca-pessoal', 'Segurança Pessoal', 'Proteção de pessoas'), ('eventos', 'Segurança de Eventos', 'Grandes eventos')]
    serv_html = ''.join(f'<a class="serv" href="cursos.html#{k}">{I[TODOS[k][1]]}<b>{e(n)}</b><span>{e(s)}</span></a>' for k, n, s in serv)

    # ===== INÍCIO =====
    P['index.html'] = pagina('index.html',
        f'Curso de Vigilante em Rondonópolis/MT | {NOME}',
        'Curso de formação de vigilante, atualização (reciclagem) e aperfeiçoamentos em Rondonópolis/MT. Escola autorizada pela Polícia Federal, com estande de tiro. Faça sua pré-matrícula.',
        f'''<section class="hero">{hero_bg}<div class="wrap"><div class="hero-txt">
<span class="selo-pf">{I["escudo"]}Autorizada pela Polícia Federal</span>
<h1>Curso de vigilante <span>em Rondonópolis</span></h1>
<p class="lead">Formação, atualização (reciclagem) e aperfeiçoamentos, com aulas práticas no estande de tiro e instrutores credenciados pela Polícia Federal.</p>
<div class="acoes">{btn_pre()}{btn_zap(cls="btn-borda")}</div>
</div>{logo_grande}
</div></section>

<section class="servicos" aria-label="Cursos"><div class="wrap"><div class="grade">{serv_html}</div></div></section>

<section class="secao"><div class="wrap duas">
<div>{tit("Sobre a escola", f"Formando vigilantes em {e(D['CIDADE'])}")}
<div class="texto"><p>A <strong>{e(NOME)}</strong> prepara profissionais para a segurança privada com cursos autorizados pela Polícia Federal, do primeiro curso de formação às atualizações e especializações.</p>
<p>As aulas unem teoria e prática: legislação, defesa pessoal, primeiros socorros e armamento e tiro no estande da própria escola.</p></div>
<ul class="lista-dif">
<li><span class="ico">{I["escudo"]}</span><div><b>Autorização da Polícia Federal</b><span>{("Nº " + e(D["AUTORIZACAO_PF"]) + ". ") if ok("AUTORIZACAO_PF") else ""}Certificado válido em todo o Brasil.</span></div></li>
<li><span class="ico">{I["alvo"]}</span><div><b>Estande de tiro próprio</b><span>Aulas práticas de armamento e tiro dentro da escola.</span></div></li>
<li><span class="ico">{I["instrutor"]}</span><div><b>Instrutores credenciados</b><span>Equipe com credenciamento na Polícia Federal.</span></div></li>
</ul>
<div class="acoes" style="margin-top:1.75rem"><a class="btn btn-azul" href="a-escola.html">Conheça a escola</a></div>
</div>
<div class="foto-moldura">{foto_ou_brasao("fachada", "Fachada da escola")}</div>
</div></section>

<section class="secao azul"><div class="wrap">
{tit("Matrículas abertas", "Próximas turmas", "Consulte as datas da próxima turma no WhatsApp.")}
<div class="turmas">{SEM_TURMA}</div>
<div class="acoes" style="margin-top:2rem"><a class="btn btn-borda" href="turmas.html">Ver todas as turmas</a></div>
</div></section>

<section class="secao cinza"><div class="wrap">
{tit("Passo a passo", "Como fazer sua matrícula", "Tudo começa pelo celular. Sem fila e sem papelada.", True)}
{PASSOS}
<div class="acoes" style="margin-top:2.25rem;justify-content:center">{btn_pre()}</div>
</div></section>

{chamada()}

<section class="faixa-foto">{bg("empresas")}<div class="wrap">
<span class="tit" style="margin:0"><span class="pre">Para empresas</span></span>
<h2>Formação e atualização para a sua equipe de vigilantes</h2>
<p>Atendemos empresas de segurança privada e serviços orgânicos de segurança.</p>
<ul>
<li>{I["ok"]}Turmas organizadas conforme a necessidade da empresa</li>
<li>{I["ok"]}Aviso de vencimento dos cursos dos seus vigilantes</li>
<li>{I["ok"]}Cadastro e envio de documentos pelo portal</li>
<li>{I["ok"]}Atendimento direto com a secretaria</li>
</ul>
<div class="acoes" style="margin-top:.75rem"><a class="btn btn-ouro" href="empresas.html">Saiba mais</a>{btn_zap("Olá! Represento uma empresa e quero falar sobre turmas para nossos vigilantes.", "Falar com a escola", "btn-borda")}</div>
</div></section>

<section class="secao cinza"><div class="wrap">
{tit("Dúvidas", "Perguntas frequentes", "", True)}
{faq_html(FAQ[:5])}
<div class="acoes" style="margin-top:2rem;justify-content:center"><a class="btn btn-azul" href="como-ser-vigilante.html">Ver requisitos e mais perguntas</a></div>
</div></section>

<section class="secao" style="padding-bottom:0"><div class="wrap">
{tit("Localização", "Venha conhecer a escola", "", True)}
<div class="contato-grade" style="margin-bottom:2rem">
<div class="cont"><span class="ico">{I["pin"]}</span><div><small>Endereço</small><span>{e(ENDER)}</span></div></div>
{cont_horario}
</div></div>
<iframe class="mapa" src="{e(MAPA_EMBED)}" title="Mapa com a localização da escola" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
</section>
''')

    # ===== A ESCOLA =====
    P['a-escola.html'] = pagina('a-escola.html',
        f'A Escola: Estrutura, Estande de Tiro e Instrutores | {NOME}',
        f'Conheça a {NOME}, escola de formação de vigilantes em Rondonópolis/MT autorizada pela Polícia Federal: salas, estande de tiro e instrutores credenciados.',
        f'''<section class="secao"><div class="wrap duas">
<div>{tit("Quem somos", "Escola autorizada pela Polícia Federal")}
<div class="texto"><p>A <strong>{e(NOME)}</strong> funciona com autorização da Polícia Federal e segue as normas da segurança privada. Cada turma, aluno e certificado é registrado no sistema da PF.</p>
<p>Nosso compromisso é formar vigilantes preparados para o mercado de trabalho, com disciplina, técnica e conhecimento da legislação.</p></div>
<div class="autoriza" style="margin-top:1.75rem">{I["escudo"]}<div><small>Autorização de funcionamento</small><b>{e(D["AUTORIZACAO_PF"]) if ok("AUTORIZACAO_PF") else "Polícia Federal"}</b><small>{("Polícia Federal, " + e(CID)) if ok("AUTORIZACAO_PF") else e(CID)}</small></div></div>
</div>
<div class="foto-moldura">{foto_ou_brasao("fachada", "Fachada da escola")}</div>
</div></section>

{sec_galeria}
<section class="secao"><div class="wrap{" duas" if tem_img("estande-2") else ""}">
{f'<div class="foto-moldura">{foto("estande-2", "Aula no estande de tiro", False)}</div>' if tem_img("estande-2") else ""}
<div>{tit("Prática de tiro", "Estande de tiro")}
<div class="texto"><p>As aulas de armamento e tiro acontecem no estande da própria escola, com acompanhamento de instrutor de armamento e tiro credenciado pela Polícia Federal e todos os equipamentos de segurança.</p></div>
<div class="acoes" style="margin-top:1.75rem">{btn_pre()}</div></div>
</div></section>

{sec_instrutores}
{chamada()}
''', None, ('A escola', 'A escola', f'Estrutura completa em {e(D["CIDADE"])} para formar vigilantes preparados para o mercado.', 'banner-escola'))

    # ===== CURSOS =====
    blocos = ''
    for grupo, sub, itens in CURSOS:
        blocos += f'<div class="grupo-tit"><h3>{e(grupo)}</h3></div><p class="grupo-sub">{e(sub)}</p><div class="cursos-grade">'
        for k, ic, n, d, m in itens:
            blocos += f'<article class="curso-card" id="{k}"><span class="ico">{I[ic]}</span><span class="meta">{e(m)}</span><h3>{e(n)}</h3><p>{e(d)}</p></article>'
        blocos += '</div>'
    cursos_ld = {'@context': 'https://schema.org', '@type': 'ItemList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'item': {'@type': 'Course', 'name': c[2], 'description': c[3], 'provider': {'@id': BASE + '#escola'}, 'inLanguage': 'pt-BR'}}
        for i, c in enumerate(TODOS.values())]}
    P['cursos.html'] = pagina('cursos.html',
        f'Cursos para Vigilantes: Formação, Reciclagem e Extensões | {NOME}',
        'Formação de vigilante, atualização (reciclagem), vigilante supervisor e aperfeiçoamentos: transporte e escolta de numerário, segurança pessoal, eventos e armas não letais. Rondonópolis/MT.',
        f'''<section class="secao cinza"><div class="wrap">{blocos}
<p class="nota" style="margin-top:2.5rem;max-width:80ch">Os cursos seguem a Lei 14.967/2024 (Estatuto da Segurança Privada), o Decreto 13.012/2026 e as portarias da Polícia Federal. Desde 2026 a antiga reciclagem se chama atualização, e as extensões se chamam aperfeiçoamento.</p>
</div></section>
<section class="secao"><div class="wrap">
{tit("Matrícula", "Quer fazer um destes cursos?", "Faça a pré-matrícula pelo celular ou chame no WhatsApp para saber valores e datas.")}
<div class="acoes">{btn_pre()}{btn_zap("Olá! Quero saber mais sobre os cursos.")}</div>
</div></section>
{chamada()}
''', [cursos_ld], ('Cursos', 'Cursos para vigilantes', 'Formação, atualização (antiga reciclagem) e aperfeiçoamentos (antigas extensões), conforme as normas da Polícia Federal.', 'banner-cursos'))

    # ===== TURMAS =====
    P['turmas.html'] = pagina('turmas.html',
        f'Próximas Turmas do Curso de Vigilante em Rondonópolis | {NOME}',
        'Datas, turnos e vagas das próximas turmas de formação e atualização de vigilantes em Rondonópolis/MT. Garanta sua vaga pela pré-matrícula online.',
        f'''<section class="secao cinza"><div class="wrap">
{tit("Matrículas abertas", "Turmas com inscrições abertas", "Abrimos novas turmas ao longo do ano.")}
<div class="turmas">{SEM_TURMA}</div>
</div></section>
<section class="secao"><div class="wrap">{tit("Passo a passo", "Como garantir sua vaga", "", True)}{PASSOS}</div></section>
{chamada()}
''', None, ('Turmas', 'Próximas turmas', 'Consulte as datas, os turnos e as vagas da próxima turma.', 'banner-turmas'))

    # ===== COMO SER VIGILANTE =====
    req = ['Ser brasileiro, nato ou naturalizado', 'Ter no mínimo 21 anos', 'Ter ensino fundamental completo (9º ano)',
           'Estar quite com as obrigações eleitorais e militares', 'Não ter antecedentes por crime doloso',
           'Ser aprovado nos exames de saúde física, mental e psicológica', 'Ser aprovado no curso de formação de vigilante']
    docs = ['Documento de identidade com foto e CPF', 'Comprovante de residência', 'Comprovante de escolaridade',
            'Título de eleitor e quitação eleitoral', 'Certificado de reservista (homens)',
            'Certidões negativas criminais das Justiças Federal, Estadual, Militar da União, Militar Estadual e Eleitoral, dos locais onde morou nos últimos 5 anos',
            'Laudos de aptidão física, mental e psicológica', 'Foto 3x4 recente']
    P['como-ser-vigilante.html'] = pagina('como-ser-vigilante.html',
        f'Como Ser Vigilante em 2026: Requisitos e Documentos | {NOME}',
        'Requisitos para ser vigilante em 2026: idade mínima de 21 anos, ensino fundamental completo, certidões e exames. Veja documentos e perguntas frequentes. Curso em Rondonópolis/MT.',
        f'''<section class="secao cinza"><div class="wrap duas" style="align-items:start">
<div class="caixa"><h3>Requisitos</h3><ul class="check">{"".join(f"<li>{e(x)}</li>" for x in req)}</ul><p class="nota">Base: Lei 14.967/2024, art. 28, e Portaria 22/2026 da Polícia Federal.</p></div>
<div class="caixa"><h3>Documentos para a matrícula</h3><ul class="check">{"".join(f"<li>{e(x)}</li>" for x in docs)}</ul><p class="nota">A secretaria confirma a lista atual antes da sua turma. No portal você envia a foto de cada documento.</p></div>
</div></section>
<section class="secao"><div class="wrap">{tit("Dúvidas", "Perguntas frequentes", "", True)}{faq_html(FAQ)}
<div class="acoes" style="margin-top:2.25rem;justify-content:center">{btn_pre()}{btn_zap("Olá! Tenho uma dúvida sobre os requisitos.")}</div></div></section>
{chamada()}
''', [faq_ld(FAQ)], ('Como ser vigilante', 'Como ser vigilante', 'Requisitos, documentos e respostas para as dúvidas de quem quer entrar na profissão.', 'banner-requisitos'))

    # ===== EMPRESAS =====
    vant = [('calendario', 'Controle de vencimentos', 'Sua empresa vê quando vence o curso de cada vigilante e recebe aviso antes do prazo.'),
            ('upload', 'Documentos online', 'A empresa cadastra os vigilantes e envia os documentos pelo portal. A escola confere e confirma.'),
            ('eventos', 'Turmas para a sua equipe', 'Turmas de atualização e aperfeiçoamento organizadas conforme a necessidade da empresa.'),
            ('tel', 'Atendimento direto', 'Um contato na secretaria para matrículas, pagamentos e certificados.')]
    P['empresas.html'] = pagina('empresas.html',
        f'Atualização e Formação de Vigilantes para Empresas | {NOME}',
        'Atualização (reciclagem) e aperfeiçoamento de vigilantes para empresas de segurança e segurança orgânica em Rondonópolis/MT. Controle de vencimentos e documentos pelo portal.',
        f'''<section class="secao cinza"><div class="wrap">
{tit("Soluções corporativas", "Como atendemos sua empresa", "Para empresas de segurança privada e serviços orgânicos de segurança.", True)}
<div class="cursos-grade">{"".join(f'<article class="curso-card"><span class="ico">{I[i]}</span><h3>{e(t)}</h3><p>{e(d)}</p></article>' for i, t, d in vant)}</div>
<div class="acoes" style="margin-top:2.25rem;justify-content:center">{btn_zap("Olá! Represento uma empresa e quero falar sobre turmas para nossos vigilantes.", "Falar com a escola")}<a class="btn btn-azul" href="{e(PORTAL)}">Acessar o portal da empresa</a></div>
</div></section>
{chamada("Solicite uma proposta para a sua equipe", "Olá! Quero uma proposta de turma para os vigilantes da minha empresa.")}
''', None, ('Empresas', 'Para empresas', 'Formação, atualização e aperfeiçoamento para equipes de vigilantes.', 'banner-empresas'))

    # ===== CONTATO =====
    P['contato.html'] = pagina('contato.html',
        f'Contato e Endereço | {NOME}, Rondonópolis/MT',
        f'Endereço, telefone, WhatsApp e horário da {NOME}, escola de vigilantes em Rondonópolis/MT.',
        f'''<section class="secao cinza"><div class="wrap duas" style="align-items:start">
<div>{tit("Atendimento", "Fale com a escola")}
<div class="contato-grade" style="grid-template-columns:1fr">
<div class="cont"><span class="ico">{I["zap"]}</span><div><small>WhatsApp</small><a href="{e(zap_link())}" target="_blank" rel="noopener">{e(D["WHATSAPP"])}</a></div></div>
<div class="cont"><span class="ico">{I["tel"]}</span><div><small>Telefone</small><a href="{TEL}">{e(D["TELEFONE"])}</a></div></div>
<div class="cont"><span class="ico">{I["email"]}</span><div><small>E-mail</small><span>{e(D["EMAIL"])}</span></div></div>
{(chr(60) + 'div class="cont"><span class="ico">' + I["ig"] + '</span><div><small>Instagram</small><a href="' + e(INSTA) + '" target="_blank" rel="noopener">@' + e(IG_USER) + '</a></div></div>') if IG_USER else ""}
{cont_horario}
</div>
<div class="acoes" style="margin-top:1.5rem">{btn_zap()}{btn_pre()}</div>
</div>
<div class="caixa" style="padding:0;overflow:hidden"><iframe class="mapa" src="{e(MAPA_EMBED)}" title="Mapa com a localização da escola" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
<div style="padding:1.25rem 1.4rem;display:grid;gap:.75rem"><div class="cont" style="box-shadow:none;padding:0"><span class="ico">{I["pin"]}</span><div><small>Endereço</small><span>{e(ENDER)}</span></div></div>
<a class="btn btn-azul" href="{e(MAPA_LINK)}" target="_blank" rel="noopener">Como chegar</a></div></div>
</div></section>
''', None, ('Contato', 'Contato', 'Chame no WhatsApp, ligue ou venha conhecer a escola.', 'banner-contato'))

    # ===== 404 =====
    p404 = pagina('404.html', f'Página não encontrada | {NOME}', 'Página não encontrada.',
        f'<section class="secao"><div class="wrap">{tit("Erro 404", "Página não encontrada", "O endereço pode ter mudado. Volte para o início ou chame no WhatsApp.")}<div class="acoes"><a class="btn btn-azul" href="./">Voltar ao início</a>{btn_zap()}</div></div></section>')
    P['404.html'] = p404.replace('<head>', '<head>\n<base href="' + urlparse(BASE).path + '">', 1).replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"', 1)

    for nome, conteudo in P.items():
        open(os.path.join(SAIDA, nome), 'w', encoding='utf-8').write(conteudo)
    hoje = date.today().isoformat()
    urls = ''.join(f'<url><loc>{BASE + ("" if a == "index.html" else a)}</loc><lastmod>{hoje}</lastmod></url>' for a, _ in PAGINAS)
    open(os.path.join(SAIDA, 'sitemap.xml'), 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    open(os.path.join(SAIDA, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    open(os.path.join(SAIDA, '.nojekyll'), 'w').write('')
    if D.get('DOMINIO'): open(os.path.join(SAIDA, 'CNAME'), 'w').write(D['DOMINIO'] + '\n')
    print('ok:', len(P), 'páginas em', SAIDA)

build()
