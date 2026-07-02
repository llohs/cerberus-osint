import os
import re
import glob
import datetime
from core.utils import R, D, G, Y, X
from core.grimoire import grimoire_salvar, LOG_DIR


# ─────────────────────────────────────────────
#  ANALYZE
# ─────────────────────────────────────────────


SEV_PT = {"CRITICAL": "CRÍTICA", "HIGH": "ALTA", "MEDIUM": "MÉDIA", "LOW": "BAIXA"}


def analyze(target):
    base     = target.replace("http://", "").replace("https://", "").replace("/", "_")
    pattern  = os.path.join(LOG_DIR, base + "*.txt")
    arquivos = sorted(glob.glob(pattern))
    if not arquivos:
        print("\n" + R + "  Nenhum relatório encontrado para: " + target + X)
        print(D + "  Execute o RITUAL EM CADEIA primeiro." + X + "\n")
        return

    print("\n" + R + "  === ANÁLISE DE INTELIGÊNCIA: " + target + " ===" + X + "\n")

    portas_abertas   = []
    vulns_high       = []
    headers_missing  = []
    subdomains_found = []
    techs_found      = []
    cves_found       = []
    ssl_issue        = False
    admin_paths      = []
    pastes_found     = []

    for arq in arquivos:
        with open(arq, "r") as f:
            conteudo = f.read()
            linhas   = conteudo.splitlines()
        for linha in linhas:
            l = linha.strip()
            if "[ABERTO]" in l and "->" in l:
                portas_abertas.append(l.split("->")[-1].strip())
            if "[VULN] SQLi" in l:
                vulns_high.append("SQL Injection detectada")
            if "[VULN] XSS" in l:
                vulns_high.append("Cross-Site Scripting (XSS) detectado")
            if "[VULN] LFI" in l:
                vulns_high.append("Local File Inclusion (LFI) detectado")
            if "[VULN] Redirecionamento aberto" in l:
                vulns_high.append("Redirecionamento aberto detectado")
            if "[AUSENTE]" in l:
                h = l.replace("[AUSENTE]", "").strip()
                headers_missing.append(h)
            if "[200]" in l and "/" in l:
                p = l.split("]")[-1].strip()
                if p not in admin_paths:
                    admin_paths.append(p)
            if "[ENCONTRADO]" in l and "->" in l and "subdomain" in arq:
                sub = l.split("[ENCONTRADO]")[-1].strip().split("->")[0].strip()
                subdomains_found.append(sub)
            if "[ENCONTRADO]" in l and "subdomain" not in arq and "soul" not in arq:
                tech = l.replace("[ENCONTRADO]", "").strip()
                techs_found.append(tech)
            if "CVE-" in l:
                found = re.findall(r"CVE-\d{4}-\d+", l)
                cves_found.extend(found)
            if "[VULN]" in l and ("TLSv1.0" in l or "TLSv1.1" in l):
                ssl_issue = True
            if "invalid" in l.lower() and "cert" in l.lower():
                ssl_issue = True
            if "[ENCONTRADO]" in l and "paste" in arq:
                pastes_found.append(l)

    vulns_high      = list(set(vulns_high))
    headers_missing = list(set(headers_missing))
    cves_found      = list(set(cves_found))
    techs_found     = list(set(techs_found))
    inteligencia    = []

    if admin_paths:
        msg  = "Possível painel administrativo exposto.\n"
        msg += "  Motivos:\n"
        for p in admin_paths[:3]:
            msg += "    - Caminho " + p + " retornou HTTP 200/401/403\n"
        if headers_missing:
            msg += "    - " + str(len(headers_missing)) + " cabeçalho(s) de segurança ausente(s)\n"
        msg += "  Severidade: " + SEV_PT["HIGH"]
        inteligencia.append(("HIGH", "SUPERFÍCIE ADMINISTRATIVA EXPOSTA", msg))

    xss = [v for v in vulns_high if "XSS" in v]
    csp = [h for h in headers_missing if "Content-Security-Policy" in h]
    if xss and csp:
        msg  = "Alto risco de XSS confirmado.\n"
        msg += "  Motivos:\n"
        msg += "    - Payload de XSS refletido aceito pelo servidor\n"
        msg += "    - Cabeçalho Content-Security-Policy ausente\n"
        msg += "  Severidade: " + SEV_PT["HIGH"]
        inteligencia.append(("HIGH", "SUPERFÍCIE DE ATAQUE XSS", msg))

    sqli = [v for v in vulns_high if "SQL" in v]
    if sqli:
        msg  = "Vetor de injeção SQL identificado.\n"
        msg += "  Motivos:\n"
        msg += "    - Servidor retornou erro SQL na entrada injetada\n"
        msg += "    - Camada de banco de dados exposta à entrada do usuário\n"
        msg += "  Impacto: exfiltração de dados, bypass de autenticação\n"
        msg += "  Severidade: " + SEV_PT["CRITICAL"]
        inteligencia.append(("CRITICAL", "INJEÇÃO SQL", msg))

    if ssl_issue:
        msg  = "Configuração de SSL/TLS fraca ou quebrada.\n"
        msg += "  Motivos:\n"
        msg += "    - Versão obsoleta de TLS (1.0/1.1) suportada\n"
        msg += "    - Expõe usuários a ataques MITM\n"
        msg += "  Severidade: " + SEV_PT["MEDIUM"]
        inteligencia.append(("MEDIUM", "TLS FRACO", msg))

    if len(subdomains_found) > 3 and techs_found:
        msg  = "Grande superfície de ataque detectada.\n"
        msg += "  Motivos:\n"
        msg += "    - " + str(len(subdomains_found)) + " subdomínio(s) exposto(s)\n"
        msg += "    - Stack de tecnologia identificado: " + ", ".join(techs_found[:4]) + "\n"
        msg += "    - Cada subdomínio é um ponto de entrada em potencial\n"
        msg += "  Severidade: " + SEV_PT["MEDIUM"]
        inteligencia.append(("MEDIUM", "SUPERFÍCIE DE ATAQUE AMPLA", msg))

    if cves_found:
        msg  = "Vulnerabilidades conhecidas associadas a este alvo.\n"
        msg += "  Motivos:\n"
        for c in cves_found[:5]:
            msg += "    - " + c + " registrado\n"
        msg += "  Severidade: " + SEV_PT["HIGH"]
        inteligencia.append(("HIGH", "CVEs CONHECIDOS", msg))

    risky = [p for p in portas_abertas if any(x in p for x in ["Telnet", "FTP", "SMB", "RDP"])]
    if risky:
        msg  = "Serviços de risco expostos à internet.\n"
        msg += "  Motivos:\n"
        for s in risky:
            msg += "    - " + s + " está aberto e acessível\n"
        msg += "  Severidade: " + SEV_PT["HIGH"]
        inteligencia.append(("HIGH", "SERVIÇOS DE RISCO", msg))

    if pastes_found:
        msg  = "Dados do alvo encontrados em sites públicos de paste.\n"
        msg += "  Motivos:\n"
        msg += "    - " + str(len(pastes_found)) + " paste(s) referenciam este alvo\n"
        msg += "    - Possível vazamento de credenciais ou dados\n"
        msg += "  Severidade: " + SEV_PT["HIGH"]
        inteligencia.append(("HIGH", "VAZAMENTO DE DADOS DETECTADO", msg))

    if not inteligencia and headers_missing:
        msg  = "Cabeçalhos de segurança não configurados.\n"
        msg += "  Ausentes: " + ", ".join(headers_missing[:3]) + "\n"
        msg += "  Severidade: " + SEV_PT["MEDIUM"]
        inteligencia.append(("MEDIUM", "CABEÇALHOS AUSENTES", msg))

    if not inteligencia:
        print(G + "  Nenhuma ameaça significativa identificada nos relatórios salvos." + X + "\n")
        return

    ordem = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    inteligencia.sort(key=lambda x: ordem.get(x[0], 9))

    for sev, titulo, msg in inteligencia:
        cor = R if sev in ["CRITICAL", "HIGH"] else Y
        print(cor + "  +--[" + SEV_PT.get(sev, sev) + "] " + titulo + X)
        for linha in msg.split("\n"):
            print(D + "  |  " + linha + X)
        print(D + "  +" + "-" * 40 + X)
        print()

    saida = "[INTELIGÊNCIA] " + target + "\n\n"
    for sev, titulo, msg in inteligencia:
        saida += "[" + SEV_PT.get(sev, sev) + "] " + titulo + "\n" + msg + "\n\n"

    caminho = grimoire_salvar(target, "intelligence", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")


# ─────────────────────────────────────────────
#  TREE VIEW
# ─────────────────────────────────────────────

def tree_view(target):
    base = target.replace("http://", "").replace("https://", "").replace("/", "_")
    print("\n" + R + "  === ÁRVORE DE DESCOBERTA: " + target + " ===" + X + "\n")

    subdomains = {}
    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*subdomains*.txt"))):
        with open(arq) as f:
            for linha in f:
                if "[ENCONTRADO]" in linha and "->" in linha:
                    partes = linha.strip().split("[ENCONTRADO]")[-1].strip()
                    sub    = partes.split("->")[0].strip()
                    ip     = partes.split("->")[-1].strip() if "->" in partes else "?"
                    subdomains[sub] = ip

    portas = {}
    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*hellscan*.txt"))):
        with open(arq) as f:
            for linha in f:
                if "[ABERTO]" in linha and "->" in linha:
                    l       = linha.strip().replace("[ABERTO]", "").strip()
                    porta   = l.split("->")[0].strip()
                    servico = l.split("->")[-1].strip()
                    portas[porta] = servico

    paths = []
    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*vulnscan*.txt"))):
        with open(arq) as f:
            for linha in f:
                if "[200]" in linha or "[401]" in linha or "[403]" in linha:
                    found = re.findall(r"/\S+", linha)
                    if found:
                        paths.extend(found)

    techs = []
    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*tech_fingerprint*.txt"))):
        with open(arq) as f:
            for linha in f:
                if "[ENCONTRADO]" in linha:
                    t = linha.replace("[ENCONTRADO]", "").strip()
                    if t:
                        techs.append(t)
    techs = list(set(techs))

    total = len(subdomains) + len(portas) + len(paths) + len(techs)
    if total == 0:
        print(D + "  Nenhum dado encontrado. Execute o RITUAL EM CADEIA primeiro." + X + "\n")
        return

    print(D + "  " + target + X)

    if subdomains:
        items = list(subdomains.items())
        print(D + "  +-- [SUBDOMÍNIOS] " + str(len(items)) + " encontrado(s)" + X)
        for i, (sub, ip) in enumerate(items):
            prefixo = "  |   +-- " if i < len(items) - 1 else "  |   `-- "
            print(G + prefixo + sub + X + D + " -> " + ip + X)

    if portas:
        items         = list(portas.items())
        ultimo_branch = not paths and not techs
        print(D + ("  `-- " if ultimo_branch else "  +-- ") + "[PORTAS ABERTAS] " + str(len(items)) + " encontrada(s)" + X)
        for i, (porta, servico) in enumerate(items):
            p       = "      " if ultimo_branch else "  |   "
            prefixo = p + ("`-- " if i == len(items) - 1 else "+-- ")
            print(R + prefixo + porta + X + D + " -> " + servico + X)

    if paths:
        paths         = list(set(paths))
        ultimo_branch = not techs
        print(D + ("  `-- " if ultimo_branch else "  +-- ") + "[CAMINHOS ADMIN] " + str(len(paths)) + " encontrado(s)" + X)
        for i, p in enumerate(paths):
            pr      = "      " if ultimo_branch else "  |   "
            prefixo = pr + ("`-- " if i == len(paths) - 1 else "+-- ")
            print(Y + prefixo + p + X)

    if techs:
        print(D + "  `-- [STACK TECNOLÓGICO] " + str(len(techs)) + " detectada(s)" + X)
        for i, t in enumerate(techs):
            prefixo = "      `-- " if i == len(techs) - 1 else "      +-- "
            print(R + prefixo + t + X)

    print()


# ─────────────────────────────────────────────
#  TIMELINE
# ─────────────────────────────────────────────

def timeline(target):
    base    = target.replace("http://", "").replace("https://", "").replace("/", "_")
    print("\n" + R + "  === LINHA DO TEMPO DE EXPOSIÇÃO: " + target + " ===" + X + "\n")
    eventos = []

    try:
        for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*domain_curse*.txt")))[:1]:
            with open(arq) as f:
                conteudo = f.read()
            m = re.search(r"Created\s*:\s*(\d{2}/\d{2}/\d{4})", conteudo)
            if m:
                partes = m.group(1).split("/")
                eventos.append((partes[2], partes[1], "Domínio registrado", "INFO"))
            m = re.search(r"Expires\s*:\s*(\d{2}/\d{2}/\d{4})", conteudo)
            if m:
                partes = m.group(1).split("/")
                eventos.append((partes[2], partes[1], "Domínio expira", "INFO"))
            m = re.search(r"Registrar\s*:\s*(.+)", conteudo)
            if m:
                eventos.append(("----", "--", "Registrador: " + m.group(1).strip(), "INFO"))
    except:
        pass

    scans_vistos = set()
    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*.txt"))):
        nome = os.path.basename(arq)
        m    = re.search(r"(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})", nome)
        if m:
            ano    = m.group(1); mes = m.group(2); dia = m.group(3)
            hora   = m.group(4) + ":" + m.group(5)
            modulo = nome.replace(base + "_", "").split("_" + m.group(0))[0]
            if modulo not in scans_vistos:
                scans_vistos.add(modulo)
                eventos.append((ano, mes, "[" + dia + "/" + mes + "/" + ano + " " + hora + "] Varredura: " + modulo.upper(), "SCAN"))

    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*vulnscan*.txt")))[-1:]:
        m_arq = re.search(r"(\d{4})(\d{2})(\d{2})", os.path.basename(arq))
        ano   = m_arq.group(1) if m_arq else "????"; mes = m_arq.group(2) if m_arq else "??"; dia = m_arq.group(3) if m_arq else "??"
        with open(arq) as f:
            conteudo = f.read()
        high = len(re.findall(r"\[VULN\]", conteudo))
        med  = len(re.findall(r"\[AUSENTE\]", conteudo))
        if high or med:
            eventos.append((ano, mes, "[" + dia + "/" + mes + "/" + ano + "] VulnScan: ALTO=" + str(high) + " MÉDIO=" + str(med), "HIGH" if high else "MEDIUM"))

    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*ssl_checker*.txt")))[-1:]:
        m_arq = re.search(r"(\d{4})(\d{2})(\d{2})", os.path.basename(arq))
        ano   = m_arq.group(1) if m_arq else "????"; mes = m_arq.group(2) if m_arq else "??"; dia = m_arq.group(3) if m_arq else "??"
        with open(arq) as f:
            conteudo = f.read()
        m = re.search(r"Expiration.*?:\s*(.+)", conteudo)
        if m:
            eventos.append((ano, mes, "[" + dia + "/" + mes + "/" + ano + "] SSL expira em: " + m.group(1).strip(), "INFO"))
        if "[VULN]" in conteudo:
            eventos.append((ano, mes, "[" + dia + "/" + mes + "/" + ano + "] TLS fraco detectado", "MEDIUM"))

    for arq in sorted(glob.glob(os.path.join(LOG_DIR, base + "*subdomains*.txt")))[-1:]:
        m_arq = re.search(r"(\d{4})(\d{2})(\d{2})", os.path.basename(arq))
        ano   = m_arq.group(1) if m_arq else "????"; mes = m_arq.group(2) if m_arq else "??"; dia = m_arq.group(3) if m_arq else "??"
        with open(arq) as f:
            linhas = f.readlines()
        subs = [l for l in linhas if "[ENCONTRADO]" in l]
        if subs:
            eventos.append((ano, mes, "[" + dia + "/" + mes + "/" + ano + "] " + str(len(subs)) + " subdomínio(s) mapeado(s)", "MEDIUM"))

    if not eventos:
        print(D + "  Nenhum dado de linha do tempo. Execute o RITUAL EM CADEIA primeiro." + X + "\n")
        return

    vistos         = set()
    eventos_unicos = []
    for e in eventos:
        if e[2] not in vistos:
            vistos.add(e[2])
            eventos_unicos.append(e)

    ordem_sev = {"HIGH": 0, "MEDIUM": 1, "SCAN": 2, "INFO": 3}
    eventos_unicos.sort(key=lambda x: (x[0] + x[1], ordem_sev.get(x[3], 9)))

    sev_timeline_pt = {"HIGH": "ALTO", "MEDIUM": "MÉDIO", "SCAN": "SCAN", "INFO": "INFO"}

    ano_atual = ""
    for ano, mes, desc, sev in eventos_unicos:
        cor = R if sev == "HIGH" else Y if sev == "MEDIUM" else G if sev == "SCAN" else D
        if ano != ano_atual and ano != "----":
            ano_atual = ano
            print(R + "  -- " + ano + " " + "-" * 30 + X)
        print(cor + "  |  " + desc + X)
    print(D + "  `" + "-" * 38 + X)
    print()

    saida = "[LINHA DO TEMPO] " + target + "\n\n"
    for ano, mes, desc, sev in eventos_unicos:
        saida += "[" + sev_timeline_pt.get(sev, sev) + "] " + desc + "\n"

    caminho = grimoire_salvar(target, "timeline", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")
