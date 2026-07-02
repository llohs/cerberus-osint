import re
import requests
import datetime
from core.utils import R, D, G, Y, X, get_headers, get_proxies, progress, head_wake, head_done
from core.grimoire import grimoire_salvar
from core.config import config_load

SITES = {
    "GitHub"     : ("https://github.com/{}", "Not Found"),
    "Reddit"     : ("https://www.reddit.com/user/{}", "page not found"),
    "Twitter"    : ("https://twitter.com/{}", "this account doesn't exist"),
    "Instagram"  : ("https://www.instagram.com/{}/", "Page Not Found"),
    "TikTok"     : ("https://www.tiktok.com/@{}", "couldn't find this account"),
    "Pinterest"  : ("https://www.pinterest.com/{}/", "User not found"),
    "Twitch"     : ("https://www.twitch.tv/{}", "Sorry. Unless you"),
    "YouTube"    : ("https://www.youtube.com/@{}", "404"),
    "LinkedIn"   : ("https://www.linkedin.com/in/{}", "Page not found"),
    "Telegram"   : ("https://t.me/{}", "If you have Telegram"),
    "Medium"     : ("https://medium.com/@{}", "Page not found"),
    "GitLab"     : ("https://gitlab.com/{}", "404"),
    "Pastebin"   : ("https://pastebin.com/u/{}", "Not Found"),
    "HackerNews" : ("https://news.ycombinator.com/user?id={}", "No such user"),
    "Keybase"    : ("https://keybase.io/{}", "404"),
    "DevTo"      : ("https://dev.to/{}", "404"),
    "Replit"     : ("https://replit.com/@{}", "not found"),
    "Steam"      : ("https://steamcommunity.com/id/{}", "The specified profile could not be found"),
    "Spotify"    : ("https://open.spotify.com/user/{}", "Page not found"),
}


def soul_search(username):
    print("\n" + R + "  === SOUL SEARCH: " + username + " ===" + X + "\n")
    encontrados = []
    for site, (url, not_found_str) in SITES.items():
        try:
            link = url.format(username)
            r = requests.get(link, timeout=6, headers=get_headers(),
                             proxies=get_proxies(), allow_redirects=True)
            if r.status_code == 200 and not_found_str.lower() not in r.text.lower():
                print(G + "  [ENCONTRADO]     " + X + site.ljust(12) + " -> " + link)
                encontrados.append(link)
            else:
                print(D + "  [NÃO ENCONTRADO] " + site + X)
        except:
            print(D + "  [ERRO]           " + site + X)
    print()
    print(R + "  " + str(len(encontrados)) + " perfil(is) encontrado(s)" + X + "\n")
    return len(encontrados)


def correlate(username, target):
    print("\n" + R + "  === CORRELAÇÃO AUTOMÁTICA: " + username + " ===" + X + "\n")
    found = {}

    print(D + "  [1/5] Perfil do GitHub..." + X)
    try:
        r = requests.get("https://api.github.com/users/" + username,
                         timeout=6, headers=get_headers(), proxies=get_proxies())
        if r.status_code == 200:
            data = r.json()
            fields = [
                ("email",    "Email",       data.get("email", "")),
                ("name",     "Nome",        data.get("name", "")),
                ("blog",     "Blog/URL",    data.get("blog", "")),
                ("company",  "Empresa",     data.get("company", "")),
                ("location", "Localização", data.get("location", "")),
                ("bio",      "Bio",         data.get("bio", "")),
                ("repos",    "Repos",       str(data.get("public_repos", 0))),
                ("followers","Seguidores",  str(data.get("followers", 0))),
                ("following","Seguindo",    str(data.get("following", 0))),
                ("created",  "Criado em",   str(data.get("created_at", ""))[:10]),
                ("updated",  "Atualizado",  str(data.get("updated_at", ""))[:10]),
                ("twitter",  "Twitter",     data.get("twitter_username", "")),
                ("url",      "Perfil",      data.get("html_url", "")),
            ]
            for key, label, val in fields:
                if val and val not in ["None", "False", "0", ""]:
                    cor = G if key in ["email", "name", "blog", "twitter"] else D
                    print(cor + "  [" + label.ljust(12) + "] " + str(val)[:80] + X)
                    found[key] = val
        else:
            print(D + "  Perfil do GitHub não encontrado." + X)
    except Exception as e:
        print(D + "  [ERRO] " + str(e) + X)

    print("\n" + D + "  [2/5] Contando estrelas..." + X)
    try:
        stars = 0
        page  = 1
        while True:
            r = requests.get(
                "https://api.github.com/users/" + username + "/repos",
                params={"per_page": 100, "page": page},
                timeout=6, headers=get_headers(), proxies=get_proxies()
            )
            if r.status_code != 200:
                break
            repos_data = r.json()
            if not repos_data:
                break
            for repo in repos_data:
                stars += repo.get("stargazers_count", 0)
            if len(repos_data) < 100:
                break
            page += 1
        print(G + "  [Estrelas  ] " + str(stars) + " no total em todos os repos" + X)
        found["stars"] = str(stars)
    except Exception as e:
        print(D + "  [ERRO] " + str(e) + X)

    print("\n" + D + "  [3/5] Checando commits recentes por email..." + X)
    try:
        r = requests.get(
            "https://api.github.com/users/" + username + "/events/public",
            timeout=6, headers=get_headers(), proxies=get_proxies()
        )
        if r.status_code == 200:
            events       = r.json()
            commit_count = 0
            for event in events:
                if event.get("type") == "PushEvent":
                    payload = event.get("payload", {})
                    commits = payload.get("commits", [])
                    commit_count += len(commits)
                    for commit in commits:
                        author = commit.get("author", {})
                        email  = author.get("email", "")
                        if email and "noreply" not in email and "email" not in found:
                            print(G + "  [Email     ] " + email + " (do commit)" + X)
                            found["email"] = email
            print(D + "  [Commits   ] " + str(commit_count) + " em eventos recentes" + X)
            found["recent_commits"] = str(commit_count)
    except Exception as e:
        print(D + "  [ERRO] " + str(e) + X)

    print("\n" + D + "  [4/5] Lendo README do perfil..." + X)
    try:
        r = requests.get(
            "https://raw.githubusercontent.com/" + username + "/" + username + "/main/README.md",
            timeout=6, headers=get_headers(), proxies=get_proxies()
        )
        if r.status_code != 200:
            r = requests.get(
                "https://raw.githubusercontent.com/" + username + "/" + username + "/master/README.md",
                timeout=6, headers=get_headers(), proxies=get_proxies()
            )
        if r.status_code == 200:
            readme = r.text
            print(G + "  [README    ] Encontrado (" + str(len(readme)) + " caracteres)" + X)
            found["readme"] = readme[:200]
            emails_readme = re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", readme)
            for em in emails_readme:
                if "email" not in found or not found["email"]:
                    print(G + "  [Email     ] " + em + " (do README)" + X)
                    found["email"] = em
                else:
                    print(D + "  [Email alt ] " + em + X)
            links = re.findall(r"https?://[^\s\)\]]+", readme)
            for link in links[:5]:
                print(D + "  [Link      ] " + link + X)
        else:
            print(D + "  Nenhum README de perfil encontrado." + X)
    except Exception as e:
        print(D + "  [ERRO] " + str(e) + X)

    print("\n" + D + "  [5/5] Correlacionando com domínio/IP..." + X)
    domains_to_check = []

    if "email" in found:
        email_domain = found["email"].split("@")[-1]
        if email_domain not in ["gmail.com", "yahoo.com", "hotmail.com",
                                 "outlook.com", "proton.me", "icloud.com"]:
            domains_to_check.append(email_domain)
            print(D + "  -> Domínio do email: " + email_domain + X)

    if "blog" in found and found["blog"]:
        blog = found["blog"].replace("https://", "").replace("http://", "").rstrip("/")
        if blog and "." in blog:
            domains_to_check.append(blog)
            print(D + "  -> Domínio do blog: " + blog + X)

    for domain in list(set(domains_to_check)):
        from heads.head2_recon import domain_curse, ip_recon
        print("\n" + R + "  [AUTO] DOMAIN CURSE -> " + domain + X)
        try:
            domain_curse(domain)
        except Exception as e:
            print(D + "  [ERRO] " + str(e) + X)
        print("\n" + R + "  [AUTO] IP RECON -> " + domain + X)
        try:
            ip_recon(domain)
        except Exception as e:
            print(D + "  [ERRO] " + str(e) + X)

    if "email" in found:
        from heads.head3_security import paste_monitor
        print("\n" + R + "  [AUTO] PASTE MONITOR -> " + found["email"] + X)
        try:
            paste_monitor(found["email"])
        except Exception as e:
            print(D + "  [ERRO] " + str(e) + X)

    saida = "[CORRELAÇÃO] " + username + "\n\n"
    for k, v in found.items():
        if k != "readme":
            saida += "  " + k.ljust(15) + ": " + str(v) + "\n"
    if domains_to_check:
        saida += "\n  Domínios correlacionados:\n"
        for d in domains_to_check:
            saida += "  -> " + d + "\n"

    caminho = grimoire_salvar(username, "correlation", saida)
    print("\n" + R + "  Relatório salvo: " + X + caminho + "\n")
    return found


def email_lookup():
    print("\n" + R + "  === CONSULTA DE EMAIL ===" + X + "\n")
    email = input(R + "  Email: " + X).strip()
    if "@" not in email:
        print(R + "  Email inválido." + X + "\n")
        return
    domain = email.split("@")[1]
    saida  = "[CONSULTA DE EMAIL] " + email + "\n\n"

    print(R + "  [VERIFICAÇÃO DE VAZAMENTOS]" + X)
    try:
        r = requests.get(
            "https://leakcheck.io/api/public?check=" + email,
            timeout=8, headers={"User-Agent": "Cerberus-OSINT"}, proxies=get_proxies()
        )
        data = r.json()
        if data.get("success"):
            found = data.get("found", 0)
            if found > 0:
                print(Y + "  [!] Encontrado em " + str(found) + " vazamento(s):" + X)
                for s in data.get("sources", []):
                    linha = "  -> " + s.get("name", "?") + " (" + s.get("date", "?") + ")"
                    print(Y + linha + X)
                    saida += linha + "\n"
            else:
                print(G + "  [OK] Não encontrado em nenhum vazamento conhecido." + X)
        else:
            print(D + "  " + data.get("error", "Verificação falhou.") + X)
    except Exception as e:
        print(D + "  [VAZAMENTOS] Erro: " + str(e) + X)

    print()
    print(R + "  [GRAVATAR]" + X)
    try:
        import hashlib
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        r = requests.get("https://www.gravatar.com/" + email_hash + ".json",
                         timeout=5, proxies=get_proxies())
        if r.status_code == 200:
            entry  = r.json()["entry"][0]
            nome   = entry.get("displayName", "N/A")
            perfil = entry.get("profileUrl", "N/A")
            print(G + "  [ENCONTRADO] Nome   : " + nome + X)
            print(G + "  [ENCONTRADO] Perfil : " + perfil + X)
            saida += "  Gravatar: " + nome + " -- " + perfil + "\n"
        else:
            print(D + "  Nenhum perfil do Gravatar encontrado." + X)
    except Exception as e:
        print(D + "  [GRAVATAR] Erro: " + str(e) + X)

    print()
    print(R + "  [MX DO DOMÍNIO]" + X)
    try:
        r = requests.get("https://dns.google/resolve?name=" + domain + "&type=MX", timeout=5)
        for a in r.json().get("Answer", []):
            linha = "  MX : " + a["data"]
            print(D + linha + X)
            saida += linha + "\n"
    except Exception as e:
        print(D + "  [MX] Erro: " + str(e) + X)

    print()
    caminho = grimoire_salvar(email.replace("@", "_at_"), "email_lookup", saida)
    print(R + "  Relatório salvo: " + X + caminho + "\n")
