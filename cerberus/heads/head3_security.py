import re
import socket
import requests
import urllib.parse as _up
from core.utils import R, D, G, Y, X, get_headers, get_proxies
from core.grimoire import grimoire_salvar
from core.config import config_load


def vulnscan(target):
    base = target if target.startswith("http") else "https://" + target
    print("\n" + R + "  === VULNSCAN: " + base + " ===" + X + "\n")
    saida  = "[VULNSCAN] " + base + "\n\n"
    issues = []

    print(D + "  [1/7] Cabeçalhos de segurança..." + X)
    try:
        r = requests.get(base, timeout=6, headers=get_headers(), proxies=get_proxies())
        for h in ["X-Frame-Options", "X-Content-Type-Options", "Strict-Transport-Security",
                  "Content-Security-Policy", "X-XSS-Protection", "Referrer-Policy"]:
            if h not in r.headers:
                print(Y + "  [AUSENTE] " + h + X)
                saida += "  [AUSENTE] " + h + "\n"
                issues.append(("medium", "Cabeçalho ausente: " + h))
            else:
                print(D + "  [OK]      " + h + X)
    except Exception as e:
        print(R + "  [ERRO] " + str(e) + X)
    print()

    print(D + "  [2/7] Injeção SQL..." + X)
    sqli_found = False
    try:
        test_url = base.rstrip("/") + ("&" if "?" in base else "?") + "id="
        for p in ["'", '"', "' OR 1=1--"]:
            r = requests.get(test_url + _up.quote(p), timeout=5,
                             headers=get_headers(), proxies=get_proxies())
            for err in ["sql syntax", "mysql_fetch", "ORA-", "syntax error"]:
                if err.lower() in r.text.lower():
                    print(R + "  [VULN] SQLi: " + p + X)
                    saida += "  [VULN] SQLi: " + p + "\n"
                    issues.append(("high", "SQLi: " + p))
                    sqli_found = True
        if not sqli_found:
            print(G + "  Nenhuma SQLi óbvia detectada." + X)
    except Exception as e:
        print(R + "  [ERRO] " + str(e) + X)
    print()

    print(D + "  [3/7] Redirecionamento aberto..." + X)
    redirect_found = False
    try:
        for param in ["redirect", "url", "next", "return", "goto"]:
            test = base.rstrip("/") + ("&" if "?" in base else "?") + param + "=https://evil.com"
            r = requests.get(test, timeout=5, headers=get_headers(),
                             proxies=get_proxies(), allow_redirects=False)
            if "evil.com" in r.headers.get("Location", ""):
                print(R + "  [VULN] Redirecionamento aberto: ?" + param + X)
                saida += "  [VULN] Redirecionamento aberto: ?" + param + "\n"
                issues.append(("high", "Redirecionamento aberto: ?" + param))
                redirect_found = True
        if not redirect_found:
            print(G + "  Nenhum redirecionamento aberto encontrado." + X)
    except Exception as e:
        print(R + "  [ERRO] " + str(e) + X)
    print()

    print(D + "  [4/7] Caminhos de admin expostos..." + X)
    try:
        for path in ["/admin", "/admin/login", "/wp-admin", "/phpmyadmin",
                     "/dashboard", "/panel", "/cpanel", "/login", "/api/admin"]:
            r = requests.get(base.rstrip("/") + path, timeout=4,
                             headers=get_headers(), proxies=get_proxies())
            if r.status_code in [200, 401, 403]:
                print(Y + "  [" + str(r.status_code) + "] " + path + X)
                saida += "  [" + str(r.status_code) + "] " + path + "\n"
                issues.append(("medium", "Exposto: " + path))
            else:
                print(D + "  [---] " + path + X)
    except Exception as e:
        print(R + "  [ERRO] " + str(e) + X)
    print()

    print(D + "  [5/7] XSS refletido..." + X)
    xss_found = False
    try:
        test_url = base.rstrip("/") + ("&" if "?" in base else "?") + "q="
        for p in ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
                  "'><svg onload=alert(1)>"]:
            r = requests.get(test_url + _up.quote(p), timeout=5,
                             headers=get_headers(), proxies=get_proxies())
            if p.lower() in r.text.lower():
                print(R + "  [VULN] XSS: " + p[:40] + X)
                saida += "  [VULN] XSS: " + p[:40] + "\n"
                issues.append(("high", "XSS: " + p[:40]))
                xss_found = True
                break
        if not xss_found:
            print(G + "  Nenhum XSS refletido encontrado." + X)
    except Exception as e:
        print(R + "  [ERRO] " + str(e) + X)
    print()

    print(D + "  [6/7] LFI + Listagem de diretórios..." + X)
    lfi_found = False
    try:
        test_url = base.rstrip("/") + ("&" if "?" in base else "?") + "file="
        for p in ["../../etc/passwd", "../../../../etc/passwd"]:
            r = requests.get(test_url + _up.quote(p), timeout=5,
                             headers=get_headers(), proxies=get_proxies())
            if "root:x:" in r.text or "daemon:" in r.text:
                print(R + "  [VULN] LFI: " + p + X)
                saida += "  [VULN] LFI: " + p + "\n"
                issues.append(("high", "LFI: " + p))
                lfi_found = True
                break
        if not lfi_found:
            print(G + "  Nenhum LFI detectado." + X)
        for path in ["/images/", "/uploads/", "/files/", "/backup/", "/static/"]:
            r = requests.get(base.rstrip("/") + path, timeout=4,
                             headers=get_headers(), proxies=get_proxies())
            if r.status_code == 200 and (
                "index of" in r.text.lower() or "parent directory" in r.text.lower()
            ):
                print(Y + "  [ABERTO] Listagem de diretório: " + path + X)
                saida += "  [ABERTO] Listagem de diretório: " + path + "\n"
                issues.append(("medium", "Listagem de diretório: " + path))
    except Exception as e:
        print(R + "  [ERRO] " + str(e) + X)
    print()

    print(D + "  [7/7] Arquivos sensíveis expostos..." + X)
    sensitive = [
        "/.env", "/.env.backup", "/.env.local", "/.git/config", "/.git/HEAD",
        "/wp-config.php", "/wp-config.php.bak", "/config.php", "/config.yml",
        "/config.yaml", "/database.yml", "/settings.py", "/local_settings.py",
        "/.htpasswd", "/.htaccess", "/composer.json", "/package.json",
        "/Dockerfile", "/docker-compose.yml", "/id_rsa", "/id_rsa.pub",
        "/server.key", "/backup.sql", "/dump.sql", "/db.sql",
    ]
    sensitive_found = False
    for path in sensitive:
        try:
            r = requests.get(base.rstrip("/") + path, timeout=4,
                             headers=get_headers(), proxies=get_proxies())
            if r.status_code == 200 and len(r.text) > 10:
                indicators = ["DB_", "SECRET", "PASSWORD", "API_KEY", "TOKEN",
                              "mysql", "postgres", "redis", "[core]", "<?php",
                              "private", "BEGIN RSA", "PRIVATE KEY"]
                matched = any(ind.lower() in r.text.lower() for ind in indicators)
                if matched:
                    print(R + "  [CRÍTICO] " + path + " EXPOSTO com conteúdo sensível!" + X)
                    saida += "  [CRÍTICO] " + path + " exposto\n"
                    issues.append(("critical", "Arquivo sensível exposto: " + path))
                    sensitive_found = True
                else:
                    print(Y + "  [ENCONTRADO] " + path + " acessível (status 200)" + X)
                    saida += "  [ENCONTRADO] " + path + "\n"
                    issues.append(("medium", "Arquivo acessível: " + path))
                    sensitive_found = True
            else:
                print(D + "  [---] " + path + X)
        except:
            print(D + "  [---] " + path + X)
    if not sensitive_found:
        print(G + "  Nenhum arquivo sensível exposto." + X)

    print()
    print(R + "  === RESUMO ===" + X)
    critical = [i for i in issues if i[0] == "critical"]
    high     = [i for i in issues if i[0] == "high"]
    medium   = [i for i in issues if i[0] == "medium"]
    if not issues:
        print(G + "  Nenhuma vulnerabilidade encontrada." + X)
    else:
        print(R + "  CRÍTICO : " + str(len(critical)) + X)
        print(R + "  ALTO    : " + str(len(high)) + X)
        print(Y + "  MÉDIO   : " + str(len(medium)) + X)
    saida += "\nRESUMO\nCRÍTICO: " + str(len(critical)) + \
             "  ALTO: " + str(len(high)) + \
             "  MÉDIO: " + str(len(medium)) + "\n"
    print()
    caminho = grimoire_salvar(target, "vulnscan", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")
    return len(critical), len(high), len(medium)


def cve_lookup():
    print("\n" + R + "  === CONSULTA DE CVE ===" + X + "\n")
    print(D + "  [1] Buscar por produto/versão" + X)
    print(D + "  [2] CVE específico (ex: CVE-2021-44228)" + X + "\n")
    op    = input(R + "  Escolha: " + X).strip()
    saida = ""

    if op == "1":
        produto = input(R + "  Produto (ex: apache 2.4.49): " + X).strip()
        print("\n" + D + "  Consultando NVD..." + X + "\n")
        try:
            r     = requests.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"keywordSearch": produto, "resultsPerPage": 10},
                headers=get_headers(), timeout=10
            )
            items = r.json().get("vulnerabilities", [])
            saida = "[CVE] " + produto + "\n\n"
            if not items:
                print(D + "  Nenhum CVE encontrado." + X + "\n")
                return
            for item in items:
                cve    = item["cve"]
                cve_id = cve.get("id", "?")
                desc   = cve.get("descriptions", [{}])[0].get("value", "N/A")[:100]
                score  = sev = "N/A"
                for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                    if key in cve.get("metrics", {}):
                        m     = cve["metrics"][key][0].get("cvssData", {})
                        score = str(m.get("baseScore", "N/A"))
                        sev   = m.get("baseSeverity", m.get("severity", "N/A"))
                        break
                cor = R if sev in ["CRITICAL", "HIGH"] else Y if sev == "MEDIUM" else D
                print(cor + "  [" + cve_id + "] " + score + " (" + sev + ")" + X)
                print(D + "  " + desc + X + "\n")
                saida += "[" + cve_id + "] " + score + " " + sev + "\n" + desc + "\n\n"
        except Exception as e:
            print(R + "  Erro: " + str(e) + X)

    elif op == "2":
        cve_id = input(R + "  ID do CVE: " + X).strip().upper()
        print("\n" + D + "  Consultando NVD..." + X + "\n")
        try:
            r     = requests.get(
                "https://services.nvd.nist.gov/rest/json/cves/2.0",
                params={"cveId": cve_id}, headers=get_headers(), timeout=10
            )
            items = r.json().get("vulnerabilities", [])
            saida = "[CVE] " + cve_id + "\n\n"
            if not items:
                print(D + "  CVE não encontrado." + X + "\n")
                return
            cve    = items[0]["cve"]
            desc   = cve.get("descriptions", [{}])[0].get("value", "N/A")
            score  = sev = vector = "N/A"
            for key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                if key in cve.get("metrics", {}):
                    m      = cve["metrics"][key][0].get("cvssData", {})
                    score  = str(m.get("baseScore", "N/A"))
                    sev    = m.get("baseSeverity", m.get("severity", "N/A"))
                    vector = m.get("vectorString", "N/A")
                    break
            cor = R if sev in ["CRITICAL", "HIGH"] else Y if sev == "MEDIUM" else G
            for chave, val in [("ID", cve_id), ("Score", score + " (" + sev + ")"), ("Vetor", vector)]:
                print(cor + "  " + chave.ljust(8) + ": " + val + X)
            print(D + "\n  " + desc[:300] + X)
            refs = cve.get("references", [])
            if refs:
                print("\n" + R + "  [REFERÊNCIAS]" + X)
                for ref in refs[:5]:
                    print(D + "  -> " + ref.get("url", "") + X)
                    saida += "  -> " + ref.get("url", "") + "\n"
        except Exception as e:
            print(R + "  Erro: " + str(e) + X)

    print()
    if saida:
        caminho = grimoire_salvar("cve", "lookup", saida)
        print(R + "  Relatório salvo: " + X + caminho + "\n")


def paste_monitor(target):
    print("\n" + R + "  === MONITOR DE PASTE / VAZAMENTO: " + target + " ===" + X + "\n")
    saida      = "[PASTE MONITOR] " + target + "\n\n"
    encontrados = []

    print(D + "  Buscando em fontes públicas..." + X + "\n")
    dorks_paste = [
        'site:pastebin.com "' + target + '"',
        '"' + target + '" password leaked',
        '"' + target + '" dump site:paste.ee',
    ]
    for dork in dorks_paste:
        try:
            r = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": dork, "format": "json", "no_html": 1},
                headers=get_headers(), proxies=get_proxies(), timeout=8
            )
            for item in r.json().get("RelatedTopics", []):
                if "FirstURL" in item and target.lower() in item.get("Text", "").lower():
                    url = item["FirstURL"]
                    encontrados.append(url)
                    print(R + "  [ENCONTRADO] " + url + X)
                    saida += "  [ENCONTRADO] " + url + "\n"
        except:
            pass

    if "@" in target:
        print(R + "  [HAVEIBEENPWNED]" + X)
        try:
            r = requests.get(
                "https://haveibeenpwned.com/api/v3/breachedaccount/" + target,
                headers={**get_headers(), "hibp-api-key": ""},
                proxies=get_proxies(), timeout=6
            )
            if r.status_code == 200:
                breaches = r.json()
                print(R + "  [!] " + str(len(breaches)) + " vazamento(s) encontrado(s)!" + X)
                for b in breaches[:5]:
                    linha = "  -> " + b.get("Name", "?") + " (" + b.get("BreachDate", "?") + ")"
                    print(Y + linha + X)
                    saida += linha + "\n"
            elif r.status_code == 404:
                print(G + "  [OK] Não encontrado em vazamentos conhecidos." + X)
            elif r.status_code == 401:
                print(D + "  [HIBP] Chave de API necessária." + X)
        except Exception as e:
            print(D + "  [HIBP] Erro: " + str(e) + X)

    if not encontrados:
        print(D + "  Nenhum paste público encontrado." + X)

    print("\n" + R + "  " + str(len(encontrados)) + " resultado(s)" + X + "\n")
    caminho = grimoire_salvar(target, "paste_monitor", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")


def shodan_search(target):
    print("\n" + R + "  === SHODAN: " + target + " ===" + X + "\n")
    cfg     = config_load()
    api_key = cfg.get("apis", {}).get("shodan", "")
    if not api_key:
        print(R + "  [!] Chave de API do Shodan não configurada." + X)
        print(D + "  Configure em: menu (8) -> [2] Shodan" + X + "\n")
        return
    saida = "[SHODAN] " + target + "\n\n"
    try:
        ip = socket.gethostbyname(target)
    except:
        ip = target
    print(D + "  IP: " + ip + X + "\n")
    try:
        r = requests.get(
            "https://api.shodan.io/shodan/host/" + ip,
            params={"key": api_key}, timeout=8
        )
        if r.status_code == 404:
            print(D + "  Nenhum dado do Shodan para este IP." + X + "\n")
            return
        if r.status_code == 401:
            print(R + "  Chave de API inválida." + X + "\n")
            return
        d = r.json()
        print(R + "  [INFO GERAL]" + X)
        for chave, val in [
            ("IP",         d.get("ip_str")),
            ("Org",        d.get("org")),
            ("ISP",        d.get("isp")),
            ("País",       d.get("country_name")),
            ("Cidade",     d.get("city")),
            ("SO",         d.get("os", "N/A")),
            ("Hostnames",  ", ".join(d.get("hostnames", []))),
            ("Tags",       ", ".join(d.get("tags", []))),
        ]:
            if val:
                linha = "  " + chave.ljust(12) + ": " + str(val)
                print(D + linha + X)
                saida += linha + "\n"
        print("\n" + R + "  [PORTAS / SERVIÇOS]" + X)
        saida += "\n[PORTAS]\n"
        todos_vulns = []
        for item in d.get("data", []):
            porta   = item.get("port", "?")
            transp  = item.get("transport", "tcp")
            produto = item.get("product", "")
            versao  = item.get("version", "")
            vulns   = list(item.get("vulns", {}).keys())
            todos_vulns.extend(vulns)
            linha = "  [" + str(porta) + "/" + transp + "] " + produto + " " + versao
            print(G + linha + X)
            saida += linha + "\n"
            for v in vulns:
                print(R + "    [VULN] " + v + X)
                saida += "    [VULN] " + v + "\n"
        if todos_vulns:
            print("\n" + R + "  [CVEs: " + str(len(set(todos_vulns))) + "]" + X)
            for v in set(todos_vulns):
                print(R + "  -> " + v + X)
    except Exception as e:
        print(R + "  Erro: " + str(e) + X)
    print()
    caminho = grimoire_salvar(target, "shodan", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")


def cloud_scan(target):
    base = target.replace("http://", "").replace("https://", "").rstrip("/")
    name = base.replace("www.", "").split(".")[0]
    print("\n" + R + "  === SCAN DE NUVEM: " + base + " ===" + X + "\n")
    saida = "[CLOUD SCAN] " + base + "\n\n"
    found = []

    print(D + "  [1/3] Buckets S3..." + X)
    s3_candidates = [
        name, name + "-backup", name + "-dev", name + "-prod",
        name + "-staging", name + "-assets", name + "-static",
        name + "-media", name + "-files", name + "-data",
        name + "-public", name + "-private", name + "-uploads",
        name + "-logs", name + "-config",
    ]
    for bucket in s3_candidates:
        url = "https://" + bucket + ".s3.amazonaws.com"
        try:
            r = requests.get(url, timeout=5, headers=get_headers(), proxies=get_proxies())
            if r.status_code == 200:
                print(R + "  [CRÍTICO] S3 PÚBLICO: " + url + X)
                saida += "  [CRÍTICO] S3 público: " + url + "\n"
                found.append(("CRITICAL", "S3 público: " + url))
                if "<ListBucketResult" in r.text:
                    print(R + "  [CRÍTICO] Listagem de bucket HABILITADA!" + X)
            elif r.status_code == 403:
                print(Y + "  [EXISTE]   S3 privado: " + url + X)
                saida += "  [EXISTE] S3 privado: " + url + "\n"
                found.append(("MEDIUM", "S3 existe (privado): " + url))
            else:
                print(D + "  [---] " + bucket + X)
        except:
            print(D + "  [---] " + bucket + X)

    print("\n" + D + "  [2/3] Firebase..." + X)
    firebase_candidates = [
        name, name + "-default-rtdb", name + "-prod",
        name + "-dev", name + "-app", name + "-db",
    ]
    for fb in firebase_candidates:
        url = "https://" + fb + ".firebaseio.com/.json"
        try:
            r = requests.get(url, timeout=5, headers=get_headers(), proxies=get_proxies())
            if r.status_code == 200:
                print(R + "  [CRÍTICO] Firebase ABERTO: " + url + X)
                print(R + "  [CRÍTICO] Tamanho dos dados: " + str(len(r.text)) + " bytes" + X)
                saida += "  [CRÍTICO] Firebase aberto: " + url + "\n"
                found.append(("CRITICAL", "Firebase aberto: " + url))
            elif r.status_code in [401, 403]:
                print(Y + "  [EXISTE]   Firebase protegido: " + fb + ".firebaseio.com" + X)
                saida += "  [EXISTE] Firebase protegido: " + fb + "\n"
                found.append(("LOW", "Firebase existe: " + fb))
            else:
                print(D + "  [---] " + fb + X)
        except:
            print(D + "  [---] " + fb + X)

    print("\n" + D + "  [3/3] GCP Storage / Azure Blob..." + X)
    gcp_url = "https://storage.googleapis.com/" + name
    try:
        r = requests.get(gcp_url, timeout=5, headers=get_headers(), proxies=get_proxies())
        if r.status_code == 200:
            print(R + "  [CRÍTICO] GCP Storage PÚBLICO: " + gcp_url + X)
            saida += "  [CRÍTICO] GCP público: " + gcp_url + "\n"
            found.append(("CRITICAL", "GCP público: " + gcp_url))
        elif r.status_code == 403:
            print(Y + "  [EXISTE]   Bucket GCP existe: " + name + X)
            saida += "  [EXISTE] GCP: " + name + "\n"
        else:
            print(D + "  [---] GCP: " + name + X)
    except:
        print(D + "  [---] GCP: " + name + X)

    azure_url = "https://" + name + ".blob.core.windows.net"
    try:
        r = requests.get(azure_url, timeout=5, headers=get_headers(), proxies=get_proxies())
        if r.status_code == 200 or "BlobServiceProperties" in r.text:
            print(R + "  [CRÍTICO] Azure Blob PÚBLICO: " + azure_url + X)
            saida += "  [CRÍTICO] Azure público: " + azure_url + "\n"
            found.append(("CRITICAL", "Azure público: " + azure_url))
        elif r.status_code in [400, 403]:
            print(Y + "  [EXISTE]   Blob Azure existe: " + name + X)
            saida += "  [EXISTE] Azure: " + name + "\n"
        else:
            print(D + "  [---] Azure: " + name + X)
    except:
        print(D + "  [---] Azure: " + name + X)

    print()
    print(R + "  === RESUMO ===" + X)
    critical = [f for f in found if f[0] == "CRITICAL"]
    medium   = [f for f in found if f[0] == "MEDIUM"]
    low      = [f for f in found if f[0] == "LOW"]
    if not found:
        print(G + "  Nenhum armazenamento em nuvem exposto encontrado." + X)
    else:
        if critical: print(R + "  CRÍTICO : " + str(len(critical)) + X)
        if medium:   print(Y + "  MÉDIO   : " + str(len(medium)) + X)
        if low:      print(D + "  BAIXO   : " + str(len(low)) + X)

    saida += "\nRESUMO\nCRÍTICO: " + str(len(critical)) + \
             "  MÉDIO: " + str(len(medium)) + "\n"
    print()
    caminho = grimoire_salvar(target, "cloud_scan", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")
    return len(critical)


def phone_osint():
    print("\n" + R + "  === OSINT DE TELEFONE ===" + X + "\n")
    numero = input(R + "  Telefone (ex: +5511999999999): " + X).strip()
    if not numero.startswith("+"):
        print(R + "  Use o formato internacional: +55..." + X + "\n")
        return
    saida  = "[PHONE OSINT] " + numero + "\n\n"
    paises = {
        "+55": "Brasil", "+1": "EUA/Canadá", "+44": "Reino Unido",
        "+351": "Portugal", "+54": "Argentina", "+34": "Espanha",
        "+49": "Alemanha", "+33": "França", "+81": "Japão",
        "+86": "China", "+91": "Índia", "+7": "Rússia",
    }
    pais = "Desconhecido"
    for prefixo, nome in sorted(paises.items(), key=lambda x: -len(x[0])):
        if numero.startswith(prefixo):
            pais = nome
            break
    print(R + "  [INFO BÁSICA]" + X)
    for chave, val in [("Número", numero), ("País", pais)]:
        linha = "  " + chave.ljust(12) + ": " + val
        print(D + linha + X)
        saida += linha + "\n"
    if numero.startswith("+55") and len(numero) >= 5:
        ddd  = numero[3:5]
        ddds = {
            "11": "São Paulo", "19": "Campinas", "21": "Rio de Janeiro",
            "31": "Belo Horizonte", "41": "Curitiba", "51": "Porto Alegre",
            "61": "Brasília", "71": "Salvador", "81": "Recife",
            "85": "Fortaleza", "92": "Manaus",
        }
        regiao = ddds.get(ddd, "DDD desconhecido")
        tipo   = "Celular" if len(numero) == 14 else "Fixo" if len(numero) == 13 else "Desconhecido"
        for chave, val in [("DDD", ddd + " -> " + regiao), ("Tipo", tipo)]:
            linha = "  " + chave.ljust(12) + ": " + val
            print(D + linha + X)
            saida += linha + "\n"
    cfg     = config_load()
    api_key = cfg.get("apis", {}).get("numverify", "")
    if api_key:
        print("\n" + R + "  [API NUMVERIFY]" + X)
        try:
            r = requests.get(
                "http://apilayer.net/api/validate",
                params={"access_key": api_key, "number": numero, "format": 1},
                timeout=6
            )
            d = r.json()
            if d.get("valid"):
                for k, v in [("Operadora", "carrier"), ("Tipo", "line_type"),
                              ("País", "country_name")]:
                    val  = str(d.get(v, "N/A"))
                    linha = "  " + k.ljust(15) + ": " + val
                    print(D + linha + X)
                    saida += linha + "\n"
        except Exception as e:
            print(D + "  Erro: " + str(e) + X)
    else:
        print("\n" + Y + "  [!] Configure a API NumVerify no menu (8) para dados da operadora." + X)
    print()
    caminho = grimoire_salvar(numero.replace("+", ""), "phone_osint", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")
