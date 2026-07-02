import os
import sys
import json
import socket
import hashlib
import random
import time
import importlib
import re
import ssl
import glob
import datetime
import subprocess
import requests

from core.utils import R, D, G, Y, C, X, get_headers, get_proxies, set_tor, is_tor, get_input, progress, head_wake, head_done, cerberus_say, QUOTES
from core.config import config_load, config_save, configure
from core.grimoire import grimoire_salvar, grimoire_listar, limpar_logs, export_html, export_markdown
from heads.head1_osint import soul_search, correlate, email_lookup
from heads.head2_recon import domain_curse, ip_recon, hellscan, ssl_checker, tech_fingerprint, subdomain_finder
from heads.head3_security import vulnscan, cve_lookup, paste_monitor, shodan_search, cloud_scan, phone_osint

LOG_DIR = os.path.expanduser("~/cerberus/logs")

ART = r"""                                                       
                    .-@W=                                             
                    #WWWW-                                            
                    *WWWWW*-.                              -++-       
            :       -WWWWWWW%.                           .#WW%-       
            **:     .WWWWWWWW%.                          +WWW=        
            :WW#-    *WWWWWWWW*                          :%WW:        
           .-#WWW#=.  %WWWWWW=#.                          .*@*-..     
          -@WWWWWWWW#:=WWWWWW: .                            .-++**+.  
       .-#WWWWWWWWWWWW%WWWWWW%--..                 .....         :*@: 
     .+WWWWWWWWWWWWWWWWWWWWWWWWWWW#*=-:::....-=+*#%@WW%#*+-.       @* 
      .=#%###++*%WWWWWWWWWWWWWWWWWWWWWWWW@@@WWWWWWWWWW@*==*#*-:::=##. 
                .-*WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW*..-++*++-   
 ..    .-+==-+#%+. =WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW%:          
 =W@@@%WWWWWWWWW%%%@WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW@:         
 .+WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW%@WWWWWWWWWWWWWW@:        
   .:..+WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW%::%WWWWW@+%WWWWWWW+:      
     .:@WWWW@#*#%@@WWWWWWWWWWWWWWWWWWWWWWW%.   =%WWWW+ .-+*%@WWW%.    
    .*W%+:...     ..::=#WWWWWWWWWWWWWWWWWW#     .=%WWW*     .=@WW*    
     .:                *WWW##=#%%@@@#+@WWW:       .@WW*       -WWW:   
                     .#WW%- .  .....  @WW*         %WW:        +WW*   
                    :%WW=            -WW@.         #WW.        .@W@.  
                 ..+WW%=             #WW*       .:-@W#         =WW@.  
               +@@WWW+            .-*WWW-       *@W@#.       :%WWW*   
               :=+=-.            .#@WWW*.       ....         .:-::    
                                  ..:-.                               
"""

TITLE = r"""    ___          _                         
  / __\___ _ __| |__   ___ _ __ _   _ ___ 
 / /  / _ \ '__| '_ \ / _ \ '__| | | / __|
/ /__|  __/ |  | |_) |  __/ |  | |_| \__ \
\____/\___|_|  |_.__/ \___|_|   \__,_|___/
                                          """

INFO_BOX = r"""+-------------------------------------------+
| [!] CERBERUS: ANALISE OSINT & SEGURANCA  |
+-------------------------------------------+
| Cerberus e uma ferramenta modular de      |
| OSINT, recon e analise de seguranca       |
| construida em Python.                     |
|                                           |
| Ele observa um alvo sob tres angulos:     |
|   -> OSINT                                |
|   -> RECON                                |
|   -> SEGURANCA                            |
|                                           |
| Cerberus transforma dados brutos em       |
| inteligencia e pontua o alvo em tres      |
| dimensoes antes de emitir um veredito.    |
+-------------------------------------------+"""


# BANNER

def show_banner():
    os.system("cls" if os.name == "nt" else "clear")

    title_lines = TITLE.split("\n")
    if title_lines and title_lines[0].strip() == "":
        title_lines = title_lines[1:]

    info_lines = INFO_BOX.split("\n")
    art_lines  = ART.split("\n")

    art_top_padding = 0
    for line in art_lines:
        if line.strip() == "":
            art_top_padding += 1
        else:
            break

    left_padding    = [""] * art_top_padding
    left_side_lines = left_padding + title_lines + [""] + info_lines
    max_left_width  = max(len(line) for line in left_side_lines)
    max_lines       = max(len(left_side_lines), len(art_lines))

    print(R)
    for i in range(max_lines):
        left_part = left_side_lines[i] if i < len(left_side_lines) else ""
        art_part  = art_lines[i]       if i < len(art_lines)       else ""
        print(f"{left_part:<{max_left_width + 4}}{art_part}")
    print(X)

    print(D + "  [+] VERSAO   : Cerberus-1.3.0" + X)
    print(D + "  [+] GITHUB   : github.com/lohjs-0/cerberus" + X)
    print(D + "  [+] FRASE    : " + random.choice(QUOTES) + X)
    print()
    print(R + "  [========================================]" + X)
    print()
    print(R + "  [ESCOLHA SEU CAMINHO]" + X)
    print()


# MENU

def show_menu(target=None):
    tor_status = G + " [TOR ATIVO]" + X if is_tor() else ""
    alvo = R + "  Alvo : " + target + tor_status + X if target else D + "  Alvo : nao definido" + X
    print(alvo)
    print()
    print(D + "  >> Nao sabe por onde comecar? Tente a opcao (12) CHAIN RITUAL." + X)
    print()

    print(R + "  ┌─ COLETA / RECON ───────────────────────────────────────┐" + X)
    print(R + "  │  (1) SOUL SEARCH    -> usuario / redes sociais         │" + X)
    print(R + "  │  (2) DOMAIN CURSE   -> dominio / IP / DNS              │" + X)
    print(R + "  │  (3) HELLSCAN       -> portas / servicos               │" + X)
    print(R + "  │  (4) DORKS          -> google dorks                    │" + X)
    print(R + "  │  (5) UNDERWORLD     -> subdominios / email             │" + X)
    print(R + "  │  (6) SSL CHECK      -> certificado / TLS               │" + X)
    print(R + "  │  (7) TECH SCAN      -> stack / frameworks / CMS        │" + X)
    print(R + "  ├─ ANALISE / SEGURANCA ──────────────────────────────────┤" + X)
    print(R + "  │  (8)  VULNSCAN      -> vulnerabilidades web            │" + X)
    print(R + "  │  (9) CVE LOOKUP    -> buscar no NVD por produto        │" + X)
    print(R + "  │  (10) PASTE MONITOR -> vazamentos / pastes publicos    │" + X)
    print(R + "  │  (11) CLOUD SCAN    -> S3 / Firebase / GCP / Azure     │" + X)
    print(R + "  ├─ AUTOMACAO ────────────────────────────────────────────┤" + X)
    print(R + "  │  (12)  CHAIN RITUAL  -> pipeline completo              │" + X)
    print(R + "  ├─ RELATORIOS / VISUALIZACAO ────────────────────────────┤" + X)
    print(R + "  │  (13) GRIMOIRE      -> relatorios / listar / exportar  │" + X)
    print(R + "  │  (14) VISUALIZE    -> analisar / grafo / arvore / linha│" + X)
    print(R + "  │  (15) DASHBOARD     -> resumo de inteligencia no term. │" + X)
    print(R + "  ├─ SISTEMA ───────────────────────────────────────────────┤" + X)
    print(R + "  │  (C)  CONFIGURE     -> APIs / configuracoes            │" + X)
    print(R + "  │  (X)  TOR           -> modo anonimo / proxy            │" + X)
    print(R + "  │  (L)  CLEAR LOGS    -> apagar logs do alvo             │" + X)
    print(R + "  └────────────────────────────────────────────────────────┘" + X)
    print()
    print(R + "  (T) SET TARGET   -> trocar alvo" + X)
    print(R + "  (0) DESCEND      -> sair" + X)
    print()


# PONTUACAO

def calcular_score(portas, high_vulns, medium_vulns, subdomains, ssl_dias, perfis, cves):
    score = 0
    score += min(portas * 5, 30)
    score += min(high_vulns * 15, 40)
    score += min(medium_vulns * 5, 20)
    score += min(subdomains * 2, 20)
    if ssl_dias is None or ssl_dias < 0:
        score += 20
    elif ssl_dias < 30:
        score += 10
    score += min(perfis * 3, 15)
    score += min(cves * 5, 25)
    return min(score, 100)


def judgment(osint_score, recon_score, sec_score, findings):
    overall = int((osint_score + recon_score + sec_score) / 3)
    if overall >= 75:
        verdict     = "CONDENADO"
        verdict_msg = "Esta alma esta fortemente exposta. Acao imediata necessaria."
        cor         = R
    elif overall >= 50:
        verdict     = "OBSERVAR DE PERTO"
        verdict_msg = "Vulnerabilidades significativas detectadas. Monitore e aja."
        cor         = Y
    elif overall >= 25:
        verdict     = "PEQUENOS PECADOS"
        verdict_msg = "Algumas fraquezas encontradas. Risco baixo, mas nao desprezivel."
        cor         = Y
    else:
        verdict     = "ALMA LIMPA"
        verdict_msg = "Nenhuma ameaca significativa detectada."
        cor         = G

    def bar(score):
        filled = int(score / 5)
        empty  = 20 - filled
        return "[" + "█" * filled + "░" * empty + "] " + str(score) + "/100"

    print()
    print(R + "  ======================================" + X)
    print(R + "         VEREDITO DO CERBERUS           " + X)
    print(R + "  ======================================" + X)
    print()
    print(D + "  CABECA I   (OSINT)     " + X + R + bar(osint_score) + X)
    print(D + "  CABECA II  (RECON)     " + X + R + bar(recon_score) + X)
    print(D + "  CABECA III (SEGURANCA) " + X + R + bar(sec_score) + X)
    print()
    print(D + "  RISCO GERAL            " + X + cor + bar(overall) + X)
    print()
    if findings:
        print(R + "  [EVIDENCIAS]" + X)
        for f in findings:
            print(D + "  -> " + f + X)
    print()
    print(cor + "  VEREDITO : " + verdict + X)
    print(D + "  " + verdict_msg + X)
    print()
    print(R + "  ======================================" + X)
    print()


# RITUAL EM CADEIA

def chain_ritual(target):
    findings     = []
    portas       = 0
    high_vulns   = 0
    medium_vulns = 0
    subdomains   = 0
    perfis       = 0
    cves_count   = 0
    ssl_dias     = None

    print()
    print(R + "  ======================================" + X)
    cerberus_say(R + "  [CERBERUS] Os portoes se abrem para: " + target + X)
    print(R + "  ======================================" + X)
    print()
    time.sleep(0.5)

    head_wake(1)
    user = input(R + "  Usuario para buscar (Enter para pular): " + X).strip()
    if user:
        progress("SOUL SEARCH", 1.0, head=1)
        p      = soul_search(user)
        perfis = p if p else 0
        if perfis:
            findings.append(str(perfis) + " perfil(is) social(is) encontrado(s) para: " + user)
    else:
        print(D + "  [SOUL SEARCH] pulado" + X + "\n")

    progress("DOMAIN CURSE", 1.5, head=1)
    domain_curse(target)

    progress("IP RECON", 1.0, head=1)
    try:
        ip_addr = socket.gethostbyname(target)
        ip_recon(ip_addr)
        findings.append("IP resolvido: " + ip_addr)
    except:
        ip_recon(target)

    progress("SUBDOMAIN SCAN", 1.5, head=1)
    s          = subdomain_finder(target)
    subdomains = s if s else 0
    if subdomains:
        findings.append(str(subdomains) + " subdominio(s) exposto(s)")

    progress("PASTE MONITOR", 1.0, head=1)
    paste_monitor(target)
    head_done(1)

    head_wake(2)
    progress("HELLSCAN", 2.0, head=2)
    p      = hellscan(target)
    portas = p if p else 0
    if portas:
        findings.append(str(portas) + " porta(s) aberta(s) detectada(s)")

    progress("SSL CHECK", 1.5, head=2)
    d        = ssl_checker(target)
    ssl_dias = d if d else None
    if ssl_dias is not None and ssl_dias < 30:
        findings.append("Certificado SSL expira em " + str(ssl_dias) + " dia(s)")
    elif ssl_dias is None:
        findings.append("Certificado SSL invalido ou inacessivel")

    progress("TECH SCAN", 1.5, head=2)
    tech_fingerprint(target)
    head_done(2)

    head_wake(3)
    progress("VULNSCAN", 2.0, head=3)
    result = vulnscan(target)
    if result:
        _, high_vulns, medium_vulns = result
        if high_vulns:
            findings.append(str(high_vulns) + " vulnerabilidade(s) de severidade ALTA encontrada(s)")
        if medium_vulns:
            findings.append(str(medium_vulns) + " problema(s) de severidade MEDIA encontrado(s)")

    progress("CVE LOOKUP", 1.5, head=3)
    cerberus_say(D + "  [CABECA III] Consultando o livro dos pecados..." + X)
    try:
        r = requests.get(
            "https://services.nvd.nist.gov/rest/json/cves/2.0",
            params={"keywordSearch": target, "resultsPerPage": 5},
            headers=get_headers(), timeout=10
        )
        cves       = r.json().get("vulnerabilities", [])
        cves_count = len(cves)
        if cves_count:
            findings.append(str(cves_count) + " CVE(s) associado(s) ao alvo")
            print(R + "  [CVEs ENCONTRADOS: " + str(cves_count) + "]" + X)
            for item in cves[:3]:
                print(D + "  -> " + item["cve"].get("id", "?") + X)
        else:
            print(D + "  Nenhum CVE diretamente associado." + X)
    except:
        pass
    head_done(3)

    osint_score = calcular_score(0, 0, 0, subdomains, None, perfis, 0)
    recon_score = calcular_score(portas, 0, 0, 0, ssl_dias, 0, 0)
    sec_score   = calcular_score(0, high_vulns, medium_vulns, 0, None, 0, cves_count)

    judgment(osint_score, recon_score, sec_score, findings)
    export_html()


# DORKS

DORKS_PRESET = {
    "1": ("Paineis admin",       "inurl:admin/login.php"),
    "2": ("Arquivos de backup",  "intitle:index.of backup"),
    "3": ("Config exposta",      "intitle:index.of web.config"),
    "4": ("Erros SQL",           "intext:sql syntax near"),
    "5": ("Paginas de login",    "inurl:login.php"),
    "6": ("phpMyAdmin",          "inurl:phpmyadmin"),
    "7": ("Admin WordPress",     "inurl:wp-admin"),
    "8": ("Redirecionamentos abertos", "inurl:redirect?url="),
    "9": ("Cameras expostas",    "inurl:view/index.shtml"),
}

def dorks():
    print("\n" + R + "  === DORKS ===" + X + "\n")
    for k, (nome, dork) in DORKS_PRESET.items():
        print(D + "  (" + k + ") " + nome.ljust(20) + " -> " + dork + X)
    print(R + "  (0) Dork personalizado" + X + "\n")
    op = get_input("  Escolha: ")
    if op == "0":
        query = input(R + "  Digite o dork: " + X)
        limit = input(R + "  Resultados? [20]: " + X) or "20"
    elif op in DORKS_PRESET:
        nome, query = DORKS_PRESET[op]
        limit = input(R + "  Resultados? [20]: " + X) or "20"
        print("\n" + D + "  Dork: " + query + X + "\n")
    else:
        print(R + "  Opcao invalida." + X + "\n")
        return
    try:
        limit = int(limit)
    except:
        limit = 20
    print("\n" + R + "  Buscando..." + X + "\n")
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": 1},
            headers=get_headers(), proxies=get_proxies(), timeout=8
        )
        resultados = []
        for item in r.json().get("RelatedTopics", []):
            if "FirstURL" in item:
                resultados.append(item["FirstURL"])
            elif "Topics" in item:
                for sub in item["Topics"]:
                    if "FirstURL" in sub:
                        resultados.append(sub["FirstURL"])
        resultados = resultados[:limit]
    except:
        resultados = []
    saida = "Dork: " + query + "\n\n"
    if not resultados:
        print(D + "  Nenhum resultado encontrado." + X + "\n")
        return
    for i, url in enumerate(resultados, 1):
        linha = "  [" + str(i).zfill(2) + "] " + url
        print(G + linha + X)
        saida += linha + "\n"
    print()
    caminho = grimoire_salvar("dorks", query.replace(" ", "_")[:30], saida)
    print(R + "  Relatorio salvo: " + X + caminho + "\n")


# CONTROLE TOR

def tor_control():
    TOR_PROXY = {"http": "socks5h://127.0.0.1:9150", "https": "socks5h://127.0.0.1:9150"}
    print("\n" + R + "  === TOR / PROXY ===" + X + "\n")
    status = G + "ATIVO" + X if is_tor() else D + "INATIVO" + X
    print("  Modo Tor: " + status + "\n")
    print(R + "  [1] Ativar Tor" + X)
    print(R + "  [2] Desativar Tor" + X)
    print(R + "  [3] Verificar IP do Tor" + X)
    print(R + "  [4] Iniciar daemon do Tor" + X)
    print(R + "  [9] Voltar" + X + "\n")
    op = get_input("  Escolha: ")
    if op == "1":
        try:
            print(D + "  Conectando pelo Tor (pode levar 30s)..." + X)
            r    = requests.get("https://check.torproject.org/api/ip", proxies=TOR_PROXY, timeout=30)
            data = r.json()
            set_tor(True)
            print(G + "  [TOR ATIVO] IP: " + data.get("IP", "?") + X + "\n")
        except:
            set_tor(True)
            print(Y + "  Modo Tor ativado (nao verificado)." + X + "\n")
    elif op == "2":
        set_tor(False)
        print(D + "  Tor DESATIVADO." + X + "\n")
    elif op == "3":
        try:
            r    = requests.get("https://check.torproject.org/api/ip", proxies=get_proxies(), timeout=8)
            data = r.json()
            cor  = G if data.get("IsTor") else Y
            print(cor + "  IP     : " + data.get("IP", "?") + X)
            print(cor + "  E Tor  : " + str(data.get("IsTor", False)) + X + "\n")
        except Exception as e:
            print(R + "  Erro: " + str(e) + X + "\n")
    elif op == "4":
        try:
            subprocess.Popen(["tor"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            print(G + "  Tor iniciado. Agora ative com [1]." + X + "\n")
        except Exception as e:
            print(R + "  Erro: " + str(e) + X + "\n")


# DASHBOARD

def dashboard():
    os.system("cls" if os.name == "nt" else "clear")
    print(R + "  === CERBERUS DASHBOARD ===" + X + "\n")
    if not os.path.exists(LOG_DIR):
        print(D + "  Nenhum dado ainda. Execute o RITUAL EM CADEIA primeiro." + X + "\n")
        return
    arquivos = [f for f in os.listdir(LOG_DIR) if f.endswith(".txt")]
    if not arquivos:
        print(D + "  Nenhum relatorio encontrado." + X + "\n")
        return

    targets     = {}
    total_vulns = 0
    total_ports = 0
    total_subs  = 0
    total_leaks = 0

    for nome in arquivos:
        t = nome.split("_")[0]
        targets.setdefault(t, []).append(nome)

    for nome in arquivos:
        try:
            with open(os.path.join(LOG_DIR, nome)) as f:
                c = f.read()
            total_vulns += c.count("[VULN]") + c.count("[CRÍTICO]")
            total_ports += c.count("[ABERTO]")
            total_subs  += c.count("[ENCONTRADO]") if "subdomain" in nome else 0
            total_leaks += c.count("[ENCONTRADO]") if "paste" in nome else 0
        except:
            pass

    print(R + "  ┌─────────────────────────────────────┐" + X)
    print(R + "  │       RESUMO DE INTELIGENCIA         │" + X)
    print(R + "  ├──────────────┬──────────────────────┤" + X)
    for label, val, cor in [
        ("Alvos",         str(len(targets)),    G),
        ("Relatorios",    str(len(arquivos)),   D),
        ("Vulns",         str(total_vulns),     R if total_vulns > 0 else G),
        ("Portas Abertas",str(total_ports),     R if total_ports > 0 else G),
        ("Subdominios",   str(total_subs),      D),
        ("Vazamentos",    str(total_leaks),     R if total_leaks > 0 else G),
    ]:
        print(R + "  │ " + X + D + label.ljust(12) + X + R + " │ " + X + cor + val.ljust(20) + X + R + " │" + X)
    print(R + "  └──────────────┴──────────────────────┘" + X)
    print()
    print(R + "  [ALVOS]" + X + "\n")

    for t, files in sorted(targets.items()):
        vulns = ports = subs = 0
        modulos   = []
        last_scan = ""
        for nome in files:
            try:
                with open(os.path.join(LOG_DIR, nome)) as f:
                    c = f.read()
                vulns += c.count("[VULN]") + c.count("[CRÍTICO]")
                ports += c.count("[ABERTO]")
                subs  += c.count("[ENCONTRADO]") if "subdomain" in nome else 0
            except:
                pass
            mod = nome.replace(t + "_", "").split("_2")[0]
            if mod not in modulos:
                modulos.append(mod)
            m = re.search(r"(\d{8}_\d{6})", nome)
            if m and m.group(1) > last_scan:
                last_scan = m.group(1)

        risk     = R + "ALTO  " + X if vulns > 3 else (R + "MED   " + X if vulns > 0 or ports > 3 else G + "BAIXO " + X)
        scan_fmt = last_scan[6:8] + "/" + last_scan[4:6] + "/" + last_scan[:4] if last_scan else "?"

        print(D + "  ┌─ " + X + R + t + X)
        print(D + "  │  Risco   : " + X + risk)
        print(D + "  │  Vulns   : " + X + (R if vulns > 0 else G) + str(vulns) + X + D + "  Portas: " + X + str(ports) + D + "  Subs: " + X + str(subs))
        print(D + "  │  Modulos : " + X + D + ", ".join(modulos[:5]) + ("..." if len(modulos) > 5 else "") + X)
        print(D + "  │  Ultimo  : " + X + D + scan_fmt + X)
        print(D + "  └" + "─" * 38 + X)
        print()

    input(R + "  [Pressione ENTER para voltar]" + X)


# EXPORTAR GRAFO

def export_graph():
    if not os.path.exists(LOG_DIR):
        print("\n" + D + "  Nenhum relatorio salvo ainda." + X + "\n")
        return

    targets_disp = sorted(set(
        nome.split("_")[0] for nome in os.listdir(LOG_DIR)
        if os.path.isfile(os.path.join(LOG_DIR, nome))
    ))

    if not targets_disp:
        print("\n" + D + "  Nenhum relatorio encontrado." + X + "\n")
        return

    print("\n" + R + "  === GRAFO DE INTELIGENCIA ===" + X + "\n")
    print(D + "  Alvos disponiveis:" + X + "\n")
    for i, t in enumerate(targets_disp, 1):
        count = len([f for f in os.listdir(LOG_DIR) if f.split("_")[0] == t])
        print(R + "  [" + str(i) + "] " + t + X + D + " (" + str(count) + " arquivos)" + X)
    print(R + "  [0] Todos os alvos" + X + "\n")

    escolha = input(R + "  Filtrar alvo: " + X).strip()
    if escolha == "0" or escolha == "":
        filter_target = None
    else:
        try:
            filter_target = targets_disp[int(escolha) - 1]
        except:
            filter_target = escolha

    nodes    = []
    edges    = []
    node_ids = {}

    def add_node(label, group, title=""):
        if label not in node_ids:
            nid = len(node_ids) + 1
            node_ids[label] = nid
            nodes.append({"id": nid, "label": label, "group": group, "title": title})
        return node_ids[label]

    for nome in sorted(os.listdir(LOG_DIR)):
        caminho = os.path.join(LOG_DIR, nome)
        if not os.path.isfile(caminho):
            continue
        target = nome.split("_")[0]
        if filter_target and target != filter_target:
            continue
        try:
            with open(caminho) as f:
                conteudo = f.read()
        except:
            continue

        tid = add_node(target, "target")

        if "soul" in nome:
            for linha in conteudo.splitlines():
                if "[ENCONTRADO]" in linha and "->" in linha:
                    site = linha.split("->")[0].replace("[ENCONTRADO]", "").strip()
                    url  = linha.split("->")[-1].strip()
                    sid  = add_node(site, "social", url)
                    edges.append({"from": tid, "to": sid, "label": "perfil"})

        if "subdomains" in nome:
            for linha in conteudo.splitlines():
                if "[ENCONTRADO]" in linha and "->" in linha:
                    sub = linha.split("[ENCONTRADO]")[-1].strip().split("->")[0].strip()
                    ip  = linha.split("->")[-1].strip()
                    sid = add_node(sub, "subdomain", ip)
                    edges.append({"from": tid, "to": sid, "label": "sub"})

        if "hellscan" in nome:
            for linha in conteudo.splitlines():
                if "[ABERTO]" in linha and "->" in linha:
                    porta = linha.replace("[ABERTO]", "").strip().split("->")[0].strip()
                    serv  = linha.split("->")[-1].strip()
                    pid   = add_node(porta, "port", serv)
                    edges.append({"from": tid, "to": pid, "label": "porta"})

        if "vulnscan" in nome:
            for linha in conteudo.splitlines():
                if "[VULN]" in linha:
                    vuln = linha.replace("[VULN]", "").strip()[:30]
                    vid  = add_node(vuln, "vuln")
                    edges.append({"from": tid, "to": vid, "label": "vuln"})

        if "tech_fingerprint" in nome:
            for linha in conteudo.splitlines():
                if "[ENCONTRADO]" in linha:
                    tech = linha.replace("[ENCONTRADO]", "").strip()
                    if tech:
                        techid = add_node(tech, "tech")
                        edges.append({"from": tid, "to": techid, "label": "tech"})

        if "ip_recon" in nome:
            for linha in conteudo.splitlines():
                if "ISP" in linha and ":" in linha:
                    isp = linha.split(":")[-1].strip()
                    if isp and isp != "None":
                        ispid = add_node(isp, "isp")
                        edges.append({"from": tid, "to": ispid, "label": "ISP"})

        if "ssl_checker" in nome:
            for linha in conteudo.splitlines():
                if "Issued by" in linha and ":" in linha:
                    ca = linha.split(":")[-1].strip()
                    if ca and ca != "N/A":
                        caid = add_node(ca, "ssl")
                        edges.append({"from": tid, "to": caid, "label": "SSL CA"})

    import json as _json
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    label     = filter_target if filter_target else "all"
    out       = os.path.expanduser("~/cerberus/reports/graph_" + label + "_" + timestamp + ".html")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    legend = [
        ("target",    "#c00", "Alvo principal"),
        ("social",    "#0c4", "Perfis sociais"),
        ("subdomain", "#44f", "Subdominios"),
        ("port",      "#f44", "Portas abertas"),
        ("vuln",      "#ff0", "Vulnerabilidades"),
        ("tech",      "#f0f", "Tecnologias"),
        ("isp",       "#0ff", "ISP / ASN"),
        ("ssl",       "#fa0", "SSL / CA"),
    ]
    legend_html = ""
    for grp, cor, nome_l in legend:
        legend_html += f'<div class="li"><span style="background:{cor}"></span>{nome_l}</div>'
      
html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GRAFO CERBERUS</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

:root {
  --red:    #c00;
  --red-hi: #f00;
  --bg:     #080808;
  --bg-hd:  #0a0000;
  --border: #300;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: var(--bg);
  font-family: 'Share Tech Mono', monospace;
  color: var(--red);
  overflow: hidden;
}

#hd {
  padding: 10px 16px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 6px;
  background: linear-gradient(90deg, #100000, var(--bg-hd));
}

#hd h1 {
  font-size: .9em;
  letter-spacing: 3px;
  color: var(--red-hi);
  text-shadow: 0 0 8px rgba(255,0,0,.3);
}

#hd h1 small {
  color: #600;
  font-weight: normal;
  letter-spacing: 1px;
}

#hd p { font-size: .7em; color: #500; letter-spacing: 1px; }

#legend {
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  padding: 7px 16px;
  border-bottom: 1px solid #200;
  background: var(--bg-hd);
}

.li {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: .68em;
  color: #900;
  letter-spacing: 1px;
}

.li span {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 4px currentColor;
}

#mynetwork {
  width: 100vw;
  height: calc(100vh - 72px);
  background: radial-gradient(circle at center, #0c0000 0%, #060606 80%);
}

#info {
  position: fixed;
  bottom: 14px;
  right: 14px;
  background: #0d0000;
  border: 1px solid #400;
  padding: 10px 14px;
  font-size: .72em;
  color: #d33;
  border-radius: 4px;
  display: none;
  max-width: 240px;
  word-break: break-all;
  z-index: 99;
  box-shadow: 0 0 14px rgba(255,0,0,.12);
  line-height: 1.6;
}

#info b   { color: #f55; letter-spacing: 1px; }
#info small { color: #700; }

#cls, #search {
  position: fixed;
  bottom: 14px;
  background: #1a0000;
  border: 1px solid #500;
  padding: 7px 14px;
  font-size: .72em;
  color: var(--red);
  border-radius: 4px;
  z-index: 99;
  font-family: inherit;
  transition: background .12s, border-color .12s;
}

#cls { left: 14px; cursor: pointer; }
#cls:hover { background: #2a0000; border-color: #700; }

#search {
  left: 130px;
  width: 165px;
  border-color: #400;
  color: #a00;
  outline: none;
  cursor: text;
}

#search::placeholder { color: #500; }
#search:focus { border-color: #700; }
</style>
</head>
<body>

<div id="hd">
  <h1>&#9760; GRAFO CERBERUS &nbsp;<small>""" + (filter_target or "TODOS OS ALVOS") + """</small></h1>
  <p>""" + str(len(nodes)) + """ nos &nbsp;·&nbsp; """ + str(len(edges)) + """ conexoes &nbsp;·&nbsp; """ + timestamp + """</p>
</div>

<div id="legend">""" + legend_html + """</div>
<div id="mynetwork"></div>
<div id="info"></div>

<button id="cls" onclick="network.fit()">&#8635; resetar visualizacao</button>
<input id="search" type="text" placeholder="buscar no...">

<script>
var nodesDS = new vis.DataSet(""" + _json.dumps(nodes) + """);
var edgesDS = new vis.DataSet(""" + _json.dumps(edges) + """);

var options = {
  nodes: {
    shape: "dot", size: 12,
    font: { color: "#c00", size: 11, face: "monospace" },
    borderWidth: 2
  },
  edges: {
    color: { color: "#300", highlight: "#f00" },
    font: { color: "#500", size: 9, face: "monospace", align: "middle" },
    smooth: { type: "dynamic" },
    arrows: { to: { enabled: true, scaleFactor: 0.4 } }
  },
  groups: {
    target:    { color: { background: "#c00", border: "#f00" }, shape: "star", size: 22 },
    social:    { color: { background: "#030", border: "#0c4" } },
    subdomain: { color: { background: "#001a66", border: "#44f" } },
    port:      { color: { background: "#4d0000", border: "#f44" } },
    vuln:      { color: { background: "#333300", border: "#ff0" } },
    tech:      { color: { background: "#330033", border: "#f0f" } },
    isp:       { color: { background: "#003333", border: "#0ff" } },
    ssl:       { color: { background: "#332200", border: "#fa0" } }
  },
  physics: {
    stabilization: { iterations: 300 },
    forceAtlas2Based: {
      gravitationalConstant: -80,
      centralGravity: 0.02,
      springLength: 90,
      springConstant: 0.08,
      damping: 0.4
    },
    solver: "forceAtlas2Based"
  },
  interaction: { hover: true, tooltipDelay: 100, zoomView: true, dragView: true }
};

var network = new vis.Network(
  document.getElementById("mynetwork"),
  { nodes: nodesDS, edges: edgesDS },
  options
);

network.on("click", function(p) {
  var el = document.getElementById("info");
  if (p.nodes.length) {
    var n = nodesDS.get(p.nodes[0]);
    el.style.display = "block";
    el.innerHTML = "<b>" + n.group.toUpperCase() + "</b><br>" + n.label +
      (n.title ? "<br><small>" + n.title + "</small>" : "");
  } else {
    el.style.display = "none";
  }
});

document.getElementById("search").addEventListener("keydown", function(e) {
  if (e.key !== "Enter") return;
  var q = e.target.value.trim().toLowerCase();
  if (!q) return;
  var match = nodesDS.get().find(n => (n.label || "").toLowerCase().includes(q));
  if (match) {
    network.focus(match.id, { scale: 1.4, animation: { duration: 500, easingFunction: "easeInOutQuad" } });
    network.selectNodes([match.id]);
    var el = document.getElementById("info");
    el.style.display = "block";
    el.innerHTML = "<b>" + match.group.toUpperCase() + "</b><br>" + match.label +
      (match.title ? "<br><small>" + match.title + "</small>" : "");
  } else {
    e.target.style.borderColor = "#a00";
    setTimeout(() => e.target.style.borderColor = "#400", 400);
  }
});
</script>
</body>
</html>"""

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(G + "  Grafo gerado!" + X)
    print(R + "  Arquivo: " + X + out)
    print(D + "  Servir: cd ~/cerberus/reports && python -m http.server 8080" + X + "\n")


# MENU VISUALIZAR

def visualize_menu(target):
    from modules.visualize import analyze, tree_view, timeline
    print("\n" + R + "  === VISUALIZAR ===" + X + "\n")
    print(R + "  [1] ANALYZE       -> relatorio de inteligencia" + X)
    print(R + "  [2] TREE          -> arvore de descoberta" + X)
    print(R + "  [3] TIMELINE      -> linha do tempo de exposicao" + X)
    print(R + "  [4] INTEL GRAPH   -> grafo visual em HTML" + X)
    print(R + "  [9] Voltar" + X + "\n")
    sub = get_input("  Escolha: ")
    if sub == "1":
        analyze(target)
    elif sub == "2":
        tree_view(target)
    elif sub == "3":
        timeline(target)
    elif sub == "4":
        export_graph()
    elif sub == "9":
        return
    
# CORRELACIONAR
def correlate_run(username, target):
    correlate(username, target)


# MAIN
def main():
    def show_intro():
        intro = os.path.join(os.path.dirname(__file__), "intro.sh")
        if os.path.exists(intro):
            subprocess.run(["bash", intro])
    show_intro()
    show_banner()
    target = None

    while True:
        if not target:
            print(R + "\n  [CERBERUS] Defina seu alvo primeiro." + X)
            target = input(R + "  Alvo: " + X).strip()
            if not target:
                continue

        show_menu(target)
        choice = get_input()

        if choice == "0":
            print("\n" + R + "  Todas as almas foram julgadas. Ate logo." + X + "\n")
            break
        elif choice == "t":
            target = input(R + "  Definir alvo: " + X).strip()
        elif choice == "1":
            user = input(R + "  Usuario: " + X).strip()
            soul_search(user)
        elif choice == "2":
            print("\n" + R + "  [a] WHOIS de dominio / DNS / Cabecalhos" + X)
            print(R + "  [b] Geolocalizacao de IP" + X + "\n")
            sub = get_input("  Escolha: ")
            if sub == "a":
                domain_curse(target)
            elif sub == "b":
                ip_recon(target)
        elif choice == "3":
            hellscan(target)
        elif choice == "4":
            dorks()
        elif choice == "5":
            print("\n" + R + "  [a] Localizador de subdominios" + X)
            print(R + "  [b] Busca de email" + X + "\n")
            sub = get_input("  Escolha: ")
            if sub == "a":
                subdomain_finder(target)
            elif sub == "b":
                email_lookup()
        elif choice == "6":
            ssl_checker(target)
        elif choice == "7":
            tech_fingerprint(target)
        elif choice == "8":
            vulnscan(target)
        elif choice == "9":
            cve_lookup()
        elif choice == "10":
            paste_monitor(target)
        elif choice == "11":
            cloud_scan(target)
        elif choice == "12":
            chain_ritual(target)
        elif choice == "13":
            grimoire_listar()
        elif choice == "14":
            visualize_menu(target)
        elif choice == "15":
            dashboard()
        elif choice == "c":
            configure()
        elif choice == "x":
            tor_control()
        elif choice == "l":
            limpar_logs()
        else:
            print(R + "\n  Opcao invalida." + X + "\n")

if __name__ == "__main__":
    main()
