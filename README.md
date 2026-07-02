```
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

    ___          _                         
  / __\___ _ __| |__   ___ _ __ _   _ ___ 
 / /  / _ \ '__| '_ \ / _ \ '__| | | / __|
/ /__|  __/ |  | |_) |  __/ |  | |_| \__ \
\____/\___|_|  |_.__/ \___|_|   \__,_|___/

        ANALISE OSINT & SEGURANCA — v1.3.0
```

> Use o Cerberus apenas em sistemas que você possui ou tem permissão explícita para testar. Escaneamento não autorizado é ilegal.

---

## O que é o Cerberus?

O Cerberus é uma ferramenta modular de OSINT, recon e análise de segurança construída em Python.

Inspirado no guardião de três cabeças do submundo, ele observa um alvo sob três ângulos simultaneamente — **OSINT**, **RECON** e **SEGURANÇA** — e entrega um veredito final sobre o risco de exposição.

A maioria das ferramentas apenas despeja dados brutos. O Cerberus transforma esses dados em inteligência: interpreta os achados, explica seu impacto, mapeia a superfície de ataque visualmente, rastreia a exposição ao longo do tempo e pontua o alvo em três dimensões antes de emitir um veredito.

---

## As Três Cabeças

```
CABECA I   -> OSINT      pegada social, subdominios, vazamentos, geolocalizacao
CABECA II  -> RECON      portas, SSL/TLS, stack de tecnologia, fingerprinting
CABECA III -> SEGURANCA  vulnerabilidades, CVEs, vetores de injecao, caminhos expostos
```

Quando você executa o **CHAIN RITUAL (12)**, as três cabeças analisam o alvo em sequência e produzem um veredito pontuado:

```
======================================
         VEREDITO DO CERBERUS
======================================

CABECA I   (OSINT)     [####..............] 20/100
CABECA II  (RECON)     [######............] 30/100
CABECA III (SEGURANCA) [#############.....] 65/100

RISCO GERAL             [#######...........] 38/100

[EVIDENCIAS]
-> IP resolvido: 4.228.31.150
-> 2 porta(s) aberta(s) detectada(s)
-> 6 problema(s) de severidade MEDIA encontrado(s)
-> 5 CVE(s) associado(s) ao alvo

VEREDITO : PEQUENOS PECADOS
Algumas fraquezas encontradas. Risco baixo, mas nao desprezivel.

======================================
```

Os veredictos escalam com o risco: `ALMA LIMPA` → `PEQUENOS PECADOS` → `OBSERVAR DE PERTO` → `CONDENADO`.

---

## Instalação

```bash
curl -fsSL https://raw.githubusercontent.com/llohs/cerberus-osint/main/install.sh | bash
```

## Executar

```bash
cerberus
```

> **Nota:** O instalador coloca o Cerberus em `~/.cerberus/` e cria o comando `cerberus` em `~/.local/bin/`. Se o comando não for encontrado após a instalação, execute diretamente:
> ```bash
> cd ~/.cerberus-osint && python3 cerberus.py
> ```

---

## Solução de Problemas

### `pip3: command not found`

O instalador precisa do `pip3` para instalar as dependências Python. Se estiver faltando:

```bash
sudo apt update && sudo apt install -y python3-pip
bash install.sh
```

### `cerberus: command not found`

`~/.local/bin` pode não estar no seu `PATH`. Você pode executar diretamente:

```bash
cd ~/.cerberus && python3 cerberus.py
```

Ou adicionar ao seu PATH permanentemente:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

### `can't open file '/path/to/cerberus.py'`

Você está executando `python3 cerberus.py` no diretório errado. O instalador coloca os arquivos em `~/.cerberus/`, não na pasta que você clonou manualmente. Navegue até lá primeiro:

```bash
cd ~/.cerberus && python3 cerberus.py
```

### Usuários de WSL / Windows

Se você está rodando o Cerberus no WSL, garanta que está trabalhando dentro do sistema de arquivos Linux (`~`) e não em um caminho do Windows (`/mnt/c/...`). Rodar a partir de `/mnt/c/` pode causar problemas de permissão e resolução de caminho.

```bash
# Recomendado: copie para a home do Linux primeiro
cp -r /mnt/c/Users/<voce>/cerberus ~/.cerberus
cd ~/.cerberus && python3 cerberus.py
```

---

## Menu

```
  ┌─ COLETA / RECON ────────────────────────────────────────┐
  │  (1) SOUL SEARCH    -> usuario / redes sociais           │
  │  (2) DOMAIN CURSE   -> dominio / IP / DNS                │
  │  (3) HELLSCAN       -> portas / servicos                 │
  │  (4) DORKS          -> google dorks                      │
  │  (5) UNDERWORLD     -> subdominios / email                │
  │  (6) SSL CHECK      -> certificado / TLS                 │
  │  (7) TECH SCAN      -> stack / frameworks / CMS          │
  ├─ ANALISE / SEGURANCA ───────────────────────────────────┤
  │  (8)  VULNSCAN      -> vulnerabilidades web              │
  │  (9)  CVE LOOKUP    -> buscar no NVD por produto         │
  │  (10) PASTE MONITOR -> vazamentos / pastes publicos      │
  │  (11) CLOUD SCAN    -> S3 / Firebase / GCP / Azure       │
  ├─ AUTOMACAO ──────────────────────────────────────────────┤
  │  (12) CHAIN RITUAL  -> pipeline completo                 │
  ├─ RELATORIOS / VISUALIZACAO ─────────────────────────────┤
  │  (13) GRIMOIRE      -> relatorios / listar / exportar    │
  │  (14) VISUALIZE     -> analisar / grafo / arvore / linha │
  │  (15) DASHBOARD     -> resumo de inteligencia no terminal│
  ├─ SISTEMA ────────────────────────────────────────────────┤
  │  (C)  CONFIGURE     -> APIs / configuracoes              │
  │  (X)  TOR           -> modo anonimo / proxy              │
  │  (L)  CLEAR LOGS    -> apagar logs do alvo               │
  └────────────────────────────────────────────────────────┘

  (T) SET TARGET   -> trocar alvo
  (0) DESCEND      -> sair
```

---

## Módulos

### Coleta / Recon (1–7)

| # | Módulo | Descrição |
|---|---|---|
| 1 | SOUL SEARCH | Busca de usuário em plataformas sociais |
| 2 | DOMAIN CURSE | `[a]` WHOIS, registros DNS, cabeçalhos HTTP — `[b]` Geolocalização de IP |
| 3 | HELLSCAN | Scanner de portas — 15 portas comuns |
| 4 | DORKS | 9 dorks do Google pré-definidos + entrada personalizada |
| 5 | UNDERWORLD | `[a]` Localizador de subdomínios (enriquecido: IP, status, HTTPS, título, tecnologia, ASN) — `[b]` OSINT de email |
| 6 | SSL CHECK | Validade do certificado, auditoria de versão TLS, HSTS |
| 7 | TECH SCAN | Fingerprinting de stack — CMS, frameworks, CDN, analytics |

### Análise / Segurança (8–11)

| # | Módulo | Descrição |
|---|---|---|
| 8 | VULNSCAN | Cabeçalhos, SQLi, XSS, LFI, redirecionamentos, caminhos admin |
| 9 | CVE LOOKUP | Consulta em tempo real ao NVD por produto ou ID de CVE |
| 10 | PASTE MONITOR | Busca de pastes públicos e vazamentos |
| 11 | CLOUD SCAN | Verificação de buckets/recursos expostos — S3, Firebase, GCP, Azure |

### Automação (12)

| # | Módulo | Descrição |
|---|---|---|
| 12 | CHAIN RITUAL | Pipeline completo pelas três cabeças + Veredito |

### Relatórios / Visualização (13–15)

| # | Módulo | Descrição |
|---|---|---|
| 13 | GRIMOIRE | Gerenciador de relatórios — listar e navegar pelos scans salvos |
| 14 | VISUALIZE | Visão unificada de inteligência — analisar, árvore, linha do tempo, grafo HTML |
| 15 | DASHBOARD | Resumo de inteligência no terminal para todos os alvos |

### Sistema (C / X / L)

| Tecla | Módulo | Descrição |
|---|---|---|
| C | CONFIGURE | Chaves de API e configurações |
| X | TOR | Modo anônimo — ativar/desativar proxy Tor, verificar IP |
| L | CLEAR LOGS | Apagar todos os logs salvos de um alvo |

---

## VISUALIZE — Submenu (14)

Todos os recursos de inteligência e visualização estão unificados em um único menu:

```
=== VISUALIZAR ===

[1] ANALYZE       -> relatorio de inteligencia
[2] TREE          -> arvore de descoberta
[3] TIMELINE      -> linha do tempo de exposicao
[4] INTEL GRAPH   -> grafo visual em HTML
[9] Voltar
```

---

## Camada de Inteligência

Em vez de apenas listar achados brutos, **VISUALIZE → ANALYZE** os interpreta:

```
[ALTA] SUPERFICIE ADMINISTRATIVA EXPOSTA
  Possivel painel administrativo exposto.
  Motivos:
    - /wp-admin retornou HTTP 200/401/403
    - /phpmyadmin retornou HTTP 200/401/403
    - Cabecalho Content-Security-Policy ausente
  Severidade: ALTA

[MEDIA] SUPERFICIE DE ATAQUE AMPLA
  Grande superficie de ataque detectada.
  Motivos:
    - 36 subdominio(s) exposto(s)
    - Stack de tecnologia identificado: Shopify
    - Cada subdominio e um ponto de entrada em potencial
  Severidade: MEDIA
```

---

## Localizador de Subdomínios — Saída Enriquecida

Cada subdomínio descoberto é enriquecido com dados ao vivo:

```
[ENCONTRADO] api.github.com
├─ IP       : 20.201.28.148
├─ Status   : 200
├─ HTTPS    : Sim
├─ Titulo   : github · build and ship software on a single, c
├─ Tech     : github.com
└─ ASN      : 8075 / Microsoft Corporation

[ENCONTRADO] ssh.github.com
├─ IP       : 20.201.28.152
├─ Status   : 200
├─ HTTPS    : Nao
├─ Titulo   : github - change is constant. github keep
├─ Tech     : github.com
└─ ASN      : 8075 / Microsoft Corporation
```

Executa em paralelo (10 threads) fazendo resolução DNS, sondagem HTTP e consulta ASN via ipwho.is.

*(Obs.: os rótulos exatos desse bloco serão confirmados quando eu traduzir o `head2_recon.py`.)*

---

## Árvore de Descoberta

**VISUALIZE → TREE** mapeia tudo que foi encontrado em uma visão estruturada:

```
example.com
|-- [SUBDOMINIOS] 18 encontrado(s)
|   |-- api.example.com -> 4.228.31.149
|   |-- admin.example.com -> 185.199.110.133
|   `-- ssh.example.com -> 20.201.28.152
|-- [PORTAS ABERTAS] 2 encontrada(s)
|   |-- 22 -> SSH
|   `-- 443 -> HTTPS
|-- [CAMINHOS ADMIN] 6 encontrado(s)
|   |-- /wp-admin
|   |-- /dashboard
|   `-- /login
`-- [STACK TECNOLOGICO] 1 detectada(s)
    `-- Shopify
```

---

## Linha do Tempo de Exposição

**VISUALIZE → TIMELINE** constrói um histórico cronológico de tudo que foi encontrado:

```
-- 2007 ------------------------------------
|  Dominio registrado
|  Registrador: MarkMonitor, Inc.

-- 2026 ------------------------------------
|  [06/06/2026] VulnScan: ALTO=1 MEDIO=1
|  [06/06/2026] 18 subdominio(s) mapeado(s)
|  [06/06/2026] Varredura: HELLSCAN
|  [06/06/2026] Varredura: SSL_CHECKER
|  [06/06/2026] SSL expira em: 57 dias
`-------------------------------------------
```

---

## Dashboard

**DASHBOARD (15)** fornece um resumo de inteligência no terminal para todos os alvos escaneados:

```
  ┌─────────────────────────────────────┐
  │       RESUMO DE INTELIGENCIA         │
  ├──────────────┬──────────────────────┤
  │ Alvos         │ 3                    │
  │ Relatorios    │ 17                   │
  │ Vulns         │ 4                    │
  │ Portas Abertas│ 9                    │
  │ Subdominios   │ 36                   │
  │ Vazamentos    │ 0                    │
  └──────────────┴──────────────────────┘
```

---

## Exportação de Grafo

**VISUALIZE → INTEL GRAPH** gera uma visualização HTML interativa (vis-network) ligando alvos aos seus subdomínios, portas abertas, vulnerabilidades, tecnologias, ISP e CA SSL em um grafo de nós navegável.

Servir localmente:
```bash
cd ~/cerberus/reports && python -m http.server 8080
```

---

## Verificações do VULNSCAN

| Verificação | Método |
|---|---|
| Cabeçalhos de Segurança | 6 cabeçalhos de resposta críticos |
| Injeção SQL | `?id=` com payloads comuns |
| Redirecionamento Aberto | `?redirect=`, `?url=`, `?next=`, etc. |
| Caminhos Admin | `/admin`, `/dashboard`, `/login`, etc. |
| XSS Refletido | `?q=` com payloads de script/img/svg |
| LFI | `?file=` com payloads de path traversal |
| Listagem de Diretório | `/uploads/`, `/backup/`, `/static/`, etc. |

---

## Tech Fingerprint — O Que Ele Detecta

**CMS:** WordPress, Joomla, Drupal, Magento, Shopify, Wix, Ghost

**Frameworks:** React, Vue.js, Angular, Next.js, jQuery, Bootstrap, Tailwind

**Servidores:** Apache, Nginx, IIS

**CDN/Infra:** Cloudflare, AWS CloudFront, Vercel, Netlify

**Linguagens:** PHP, ASP.NET, Python/Django, Node.js/Express

**Analytics:** Google Analytics, Google Tag Manager, Hotjar, Facebook Pixel

**Segurança:** reCAPTCHA, hCaptcha

---

## IP Recon — Cascata de Fallback

```
1. ipwho.is     -> primario
2. ip-api.com   -> alternativa
3. ipapi.co     -> ultimo recurso
```

---

## Tor / Modo Anônimo

**TOR (X)** alterna o roteamento pelo Tor (`socks5h://127.0.0.1:9150`) e verifica o IP de saída via `check.torproject.org`. Quando ativo, `[TOR ATIVO]` aparece ao lado do alvo no menu.

```
[1] Ativar Tor
[2] Desativar Tor
[3] Verificar IP do Tor
[4] Iniciar daemon do Tor
```

---

## APIs Opcionais

| API | Usado em | Tier gratuito | Link |
|---|---|---|---|
| Shodan | CHAIN RITUAL / internos | Sim (limitado) | account.shodan.io |
| NumVerify | CHAIN RITUAL / internos | 100 req/mês | numverify.com |

Configure via **(C) CONFIGURE**.

---

## Requisitos

```bash
pip install requests[socks] python-whois
```

`requests[socks]` é necessário para suporte ao Tor.

---

## Estrutura do Projeto

```
cerberus/
|-- cerberus.py            # Ponto de entrada principal — menu, chain ritual, pontuacao
|-- README.md
|-- core/
|   |-- utils.py           # Cores, helpers, progresso, frases
|   |-- config.py          # Carregar/salvar/configurar
|   `-- grimoire.py        # Salvar/listar/exportar relatorios (HTML, Markdown)
|-- heads/
|   |-- head1_osint.py     # Busca de alma, correlacionar, busca de email
|   |-- head2_recon.py     # Dominio, IP, hellscan, SSL, tech, subdominios
|   `-- head3_security.py  # Vulnscan, CVE, monitor de paste, Shodan, cloud, telefone
|-- modules/
|   `-- visualize.py       # Analisar, arvore, linha do tempo (modulo unificado de inteligencia)
|-- logs/                  # Auto-criado — relatorios de scan (.txt)
|-- reports/               # Auto-criado — exports HTML/MD
`-- config/
    `-- settings.json      # Chaves de API e preferencias
```

---

## Aviso Legal

Esta ferramenta é apenas para fins educacionais e testes de segurança autorizados.
A autora não se responsabiliza por uso indevido.

---

**github.com/llohs/cerberu-osint**
