import os
import glob
import datetime
from core.utils import R, D, G, Y, X, get_headers, get_proxies

LOG_DIR = os.path.expanduser("~/cerberus/logs")


def grimoire_salvar(target, modulo, conteudo):
    target = target.replace("http://", "").replace("https://", "").replace("/", "_")
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome = target + "_" + modulo + "_" + timestamp + ".txt"
    caminho = os.path.join(LOG_DIR, nome)
    with open(caminho, "w") as f:
        f.write("CERBERUS - " + modulo.upper() + "\n")
        f.write("Alvo    : " + target + "\n")
        f.write("Data    : " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n")
        f.write("=" * 45 + "\n\n")
        f.write(conteudo)
    return caminho


def grimoire_listar():
    arquivos = sorted(os.listdir(LOG_DIR)) if os.path.exists(LOG_DIR) else []
    if not arquivos:
        print("\n" + D + "  Nenhum relatório salvo ainda." + X + "\n")
        return
    print("\n" + R + "  === GRIMOIRE ===" + X + "\n")
    for i, nome in enumerate(arquivos, 1):
        print(D + "  [" + str(i) + "] " + nome + X)
    print()
    print(D + "  Use (16) EXPORTAR HTML para gerar relatório visual." + X + "\n")


def limpar_logs(target=None):
    if not os.path.exists(LOG_DIR):
        print("\n" + D + "  Nenhum log encontrado." + X + "\n")
        return

    todos = sorted(os.listdir(LOG_DIR))
    targets_disp = sorted(set(f.split("_")[0] for f in todos if f.endswith(".txt")))

    if not targets_disp:
        print("\n" + D + "  Nenhum log encontrado." + X + "\n")
        return

    print("\n" + R + "  === LIMPAR LOGS ===" + X + "\n")
    print(D + "  Alvos disponíveis:" + X + "\n")
    for i, t in enumerate(targets_disp, 1):
        count = len([f for f in todos if f.split("_")[0] == t])
        print(R + "  [" + str(i) + "] " + t + X + D + " (" + str(count) + " arquivo(s))" + X)
    print(R + "  [0] TODOS os alvos" + X + "\n")

    escolha = input(R + "  Escolha o alvo para deletar: " + X).strip()

    if escolha == "0":
        arquivos = [f for f in todos if f.endswith(".txt")]
        label = "TODOS"
    else:
        try:
            t_escolhido = targets_disp[int(escolha) - 1]
        except:
            print(R + "  Opção inválida." + X + "\n")
            return
        arquivos = [f for f in todos if f.split("_")[0] == t_escolhido and f.endswith(".txt")]
        label = t_escolhido

    if not arquivos:
        print(D + "  Nenhum arquivo encontrado." + X + "\n")
        return

    print("\n" + D + "  Arquivos a deletar:" + X)
    for f in arquivos:
        print(D + "  -> " + f + X)

    confirm = input("\n" + R + "  Deletar " + str(len(arquivos)) + " arquivo(s) de [" + label + "]? [s/N]: " + X).strip().lower()
    if confirm in ["s", "y"]:
        for f in arquivos:
            os.remove(os.path.join(LOG_DIR, f))
        print(G + "  " + str(len(arquivos)) + " arquivo(s) deletado(s)." + X + "\n")
    else:
        print(D + "  Cancelado." + X + "\n")


def export_html():
    if not os.path.exists(LOG_DIR):
        print("\n" + D + "  Nenhum relatório salvo ainda." + X + "\n")
        return
    arquivos = sorted(os.listdir(LOG_DIR))
    if not arquivos:
        print("\n" + D + "  Nenhum relatório salvo ainda." + X + "\n")
        return
    print("\n" + R + "  === EXPORTAR HTML ===" + X + "\n")
    reports = []
    for nome in arquivos:
        try:
            with open(os.path.join(LOG_DIR, nome), "r") as f:
                reports.append((nome, f.read()))
        except:
            pass
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.expanduser("~/cerberus/reports/cerberus_report_" + timestamp + ".html")
    os.makedirs(os.path.dirname(html_path), exist_ok=True)
    targets_dict = {}
    for nome, conteudo in reports:
        key = nome.split("_")[0]
        targets_dict.setdefault(key, []).append((nome, conteudo))
    cards = ""
    for target_key, target_reports in targets_dict.items():
        cards += '<div class="ts"><div class="th"><h2>&#9760; ' + target_key.upper() + '</h2></div>\n'
        for nome, conteudo in target_reports:
            modulo = nome.split("_")[1] if len(nome.split("_")) > 1 else "relatorio"
            linhas_html = ""
            for linha in conteudo.split("\n"):
                ll = linha.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if any(x in linha for x in ["[FOUND]", "[OPEN]", "[OK]"]):
                    linhas_html += '<span class="ok">' + ll + '</span>\n'
                elif any(x in linha for x in ["[VULN]", "[MISSING]", "[!]", "HIGH", "CRITICAL"]):
                    linhas_html += '<span class="vl">' + ll + '</span>\n'
                elif any(x in linha for x in ["MEDIUM", "WARNING", "[?]"]):
                    linhas_html += '<span class="wn">' + ll + '</span>\n'
                else:
                    linhas_html += ll + "\n"
            cards += '<div class="rc"><div class="rh" onclick="t(this)"><span>' + nome + '</span><span class="b">' + modulo.upper() + '</span></div>'
            cards += '<div class="rb"><pre>' + linhas_html + '</pre></div></div>\n'
        cards += "</div>\n"

    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RELATÓRIO CERBERUS """ + timestamp + """</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{background:#080808;color:#c00;font-family:'Share Tech Mono',monospace;padding:20px}
.hd{text-align:center;padding:25px 0;border-bottom:1px solid #300;margin-bottom:20px}
.hd h1{color:#c00;font-size:1.3em;letter-spacing:4px;margin-top:8px}
.hd p{color:#400;font-size:.8em;margin-top:4px}
.st{display:flex;gap:12px;justify-content:center;margin-bottom:20px;flex-wrap:wrap}
.sb{background:#0f0000;border:1px solid #300;padding:8px 18px;border-radius:3px;text-align:center}
.sb .n{font-size:1.6em;color:#c00}.sb .l{font-size:.7em;color:#400}
.ts{margin-bottom:20px;border:1px solid #300;border-radius:3px;overflow:hidden}
.th{background:#150000;padding:10px 16px;border-bottom:1px solid #300}
.th h2{color:#c00;font-size:.95em;letter-spacing:2px}
.rc{border-bottom:1px solid #1a0000}.rc:last-child{border-bottom:none}
.rh{padding:9px 16px;background:#0d0000;cursor:pointer;display:flex;justify-content:space-between;align-items:center}
.rh:hover{background:#180000}.rh span{color:#800;font-size:.85em}
.b{background:#2a0000;color:#c00;padding:2px 7px;border-radius:2px;font-size:.72em}
.rb{padding:12px 16px;background:#060000;display:none}
.rb pre{color:#600;font-size:.75em;line-height:1.6;white-space:pre-wrap;word-break:break-all}
.ok{color:#0c4!important}.vl{color:#c00!important}.wn{color:#c80!important}
.ft{text-align:center;margin-top:20px;padding-top:15px;border-top:1px solid #1a0000}
.ft p{color:#300;font-size:.75em}
</style>
</head>
<body>
<div class="hd">
<h1>&#9760; RELATÓRIO DE INTELIGÊNCIA CERBERUS</h1>
<p>""" + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + """ | github.com/llohs</p>
</div>
<div class="st">
<div class="sb"><div class="n">""" + str(len(reports)) + """</div><div class="l">RELATÓRIOS</div></div>
<div class="sb"><div class="n">""" + str(len(targets_dict)) + """</div><div class="l">ALVOS</div></div>
<div class="sb"><div class="n">""" + timestamp[:8] + """</div><div class="l">DATA</div></div>
</div>
""" + cards + """
<div class="ft"><p>CERBERUS v1.3.0 | Use apenas em alvos autorizados</p></div>
<script>
function t(el){const b=el.nextElementSibling;b.style.display=b.style.display==='block'?'none':'block'}
document.querySelector('.rh')&&t(document.querySelector('.rh'));
</script>
</body></html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(G + "  Relatório HTML gerado!" + X)
    print(R + "  Arquivo: " + X + html_path + "\n")


def export_markdown(target):
    base = target.replace("http://", "").replace("https://", "").replace("/", "_")
    pattern = os.path.join(LOG_DIR, base + "*.txt")
    arquivos = sorted(glob.glob(pattern))
    if not arquivos:
        print("\n" + R + "  Nenhum relatório encontrado para: " + target + X)
        print(D + "  Execute o CHAIN RITUAL primeiro." + X + "\n")
        return
    print("\n" + R + "  === EXPORTAR MARKDOWN: " + target + " ===" + X + "\n")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.expanduser("~/cerberus/reports/" + base + "_" + timestamp + ".md")
    os.makedirs(os.path.dirname(out), exist_ok=True)

    md  = "# 🔱 RELATÓRIO CERBERUS\n\n"
    md += "**Alvo:** `" + target + "`  \n"
    md += "**Data:** " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "  \n"
    md += "**Ferramenta:** Cerberus v1.3.0 | github.com/llohs  \n\n"
    md += "---\n\n"

    sections = {
        "domain_curse":     "## 🌐 Domínio / WHOIS / DNS",
        "ip_recon":         "## 📍 Geolocalização de IP",
        "hellscan":         "## 🔥 Varredura de Portas",
        "ssl_checker":      "## 🔒 SSL / TLS",
        "tech_fingerprint": "## 🧬 Fingerprint de Tecnologia",
        "vulnscan":         "## ⚠️ Varredura de Vulnerabilidades",
        "cloud_scan":       "## ☁️ Varredura de Cloud Storage",
        "subdomains":       "## 🕸️ Subdomínios",
        "soul":             "## 👤 Perfis Sociais",
        "paste_monitor":    "## 🔍 Monitor de Pastes / Vazamentos",
        "shodan":           "## 📡 Shodan",
        "correlation":      "## 🔗 Correlação",
        "intelligence":     "## 🧠 Análise de Inteligência",
        "timeline":         "## 📅 Linha do Tempo",
    }

    covered = set()
    for modulo, header in sections.items():
        matches = [f for f in arquivos if modulo in f]
        if not matches:
            continue
        md += header + "\n\n"
        for arq in matches[-1:]:
            try:
                with open(arq) as f:
                    linhas = f.readlines()
                for linha in linhas[4:]:
                    l = linha.strip()
                    if not l or l.startswith("="):
                        continue
                    if "[FOUND]" in l or "[OPEN]" in l or "[OK]" in l:
                        md += "- ✅ `" + l.replace("[FOUND]", "").replace("[OPEN]", "").replace("[OK]", "").strip() + "`\n"
                    elif "[VULN]" in l or "[CRITICAL]" in l or "[MISSING]" in l:
                        md += "- 🚨 `" + l.replace("[VULN]", "").replace("[CRITICAL]", "").replace("[MISSING]", "").strip() + "`\n"
                    elif "[!]" in l:
                        md += "- ⚠️ `" + l.replace("[!]", "").strip() + "`\n"
                    else:
                        md += "- " + l + "\n"
                covered.add(modulo)
            except:
                pass
        md += "\n"

    md += "---\n\n## 📊 Resumo\n\n"
    md += "| Módulo | Status |\n|--------|--------|\n"
    for modulo, header in sections.items():
        status = "✅ Concluído" if modulo in covered else "⬜ Não executado"
        md += "| " + header.replace("## ", "") + " | " + status + " |\n"
    md += "\n---\n*Gerado por Cerberus v1.3.0*\n"

    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(G + "  Relatório Markdown gerado!" + X)
    print(R + "  Arquivo: " + X + out + "\n")
