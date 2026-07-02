#!/usr/bin/env bash

R='\033[0;31m'
DR='\033[2;31m'
BR='\033[1;31m'
G='\033[0;32m'
Y='\033[0;33m'
D='\033[2;37m'
W='\033[1;37m'
BL='\033[5m'
X='\033[0m'

REPO="https://github.com/lohjs-0/cerberus-osint.git"
INSTALL_DIR="$HOME/.cerberus-osint"
BIN_DIR="$HOME/.local/bin"
CMD="cerberus"

type_out() {
    local text="$1"
    local delay="${2:-0.04}"
    local color="${3:-$D}"
    echo -ne "${color}"
    for ((i=0; i<${#text}; i++)); do
        echo -ne "${text:$i:1}"
        sleep "$delay"
    done
    echo -e "${X}"
}

glitch_line() {
    local text="$1"
    local glitch_chars=('█' '▓' '░' '▒' '╬' '╪' '╫' '╩' '╦' '#' '@' '%')
    local len=${#text}
    for pass in 1 2 3; do
        echo -ne "\r${R}"
        for ((i=0; i<len; i++)); do
            if (( RANDOM % 3 == 0 )); then
                echo -ne "${glitch_chars[$((RANDOM % ${#glitch_chars[@]}))]}";
            else
                echo -ne "${text:$i:1}"
            fi
        done
        echo -ne "${X}"
        sleep 0.07
    done
    echo -e "\r${R}${text}${X}"
}

flicker() {
    local text="$1"
    for i in 1 2 3; do
        echo -ne "\r${DR}${text}${X}"
        sleep 0.08
        echo -ne "\r${BR}${text}${X}"
        sleep 0.08
    done
    echo -e "\r${R}${text}${X}"
}

progress_bar() {
    local label="$1"
    local duration="${2:-2}"
    local steps=25
    local delay
    delay=$(echo "scale=4; $duration / $steps" | bc)
    for ((i=0; i<=steps; i++)); do
        local filled=$(printf '█%.0s' $(seq 1 $i))
        local empty=$(printf '░%.0s' $(seq 1 $((steps - i))))
        local pct=$(( (i * 100) / steps ))
        printf "\r${DR}  %-16s ${R}[${filled}${D}${empty}${R}] ${W}%3d%%${X}" "$label" "$pct"
        sleep "$delay"
    done
    echo ""
}


clear
sleep 0.2

echo ""
echo ""
sleep 0.6

type_out "  em algum lugar entre os vivos e os mortos..." 0.03 "$DR"
sleep 0.8
type_out "  uma porta se abre." 0.06 "$R"
sleep 1.2

clear

for i in $(seq 1 6); do
    echo -e "${DR}  $(head -c 60 /dev/urandom | tr -dc 'A-Z0-9!@#$%^&*' | head -c 50)${X}"
    sleep 0.06
done

sleep 0.2
clear

ART=(
"                    .-@W=                                             "
"                    #WWWW-                                            "
"                    *WWWWW*-.                              -++-       "
"            :       -WWWWWWW%.                           .#WW%-       "
"            **:     .WWWWWWWW%.                          +WWW=        "
"            :WW#-    *WWWWWWWW*                          :%WW:        "
"           .-#WWW#=.  %WWWWWW=#.                          .*@*-..     "
"          -@WWWWWWWW#:=WWWWWW: .                            .-++**+.  "
"       .-#WWWWWWWWWWWW%WWWWWW%--..                 .....         :*@: "
"     .+WWWWWWWWWWWWWWWWWWWWWWWWWWW#*=-:::....-=+*#%@WW%#*+-.       @*"
"      .=#%###++*%WWWWWWWWWWWWWWWWWWWWWWWW@@@WWWWWWWWWW@*==*#*-:::=##."
"                .-*WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW*..-++*++-  "
" ..    .-+==-+#%+. =WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW%:         "
" =W@@@%WWWWWWWWW%%%@WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW@:        "
" .+WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW%@WWWWWWWWWWWWWW@:       "
"   .:..+WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW%::%WWWWW@+%WWWWWWW+:     "
"     .:@WWWW@#*#%@@WWWWWWWWWWWWWWWWWWWWWWW%.   =%WWWW+ .-+*%@WWW%.   "
"    .*W%+:...     ..::=#WWWWWWWWWWWWWWWWWW#     .=%WWW*     .=@WW*    "
"     .:                *WWW##=#%%@@@#+@WWW:       .@WW*       -WWW:   "
"                     .#WW%- .  .....  @WW*         %WW:        +WW*   "
"                    :%WW=            -WW@.         #WW.        .@W@.  "
"                 ..+WW%=             #WW*       .:-@W#         =WW@.  "
"               +@@WWW+            .-*WWW-       *@W@#.       :%WWW*   "
"               :=+=-.            .#@WWW*.       ....         .:-::    "
"                                  ..:-.                               "
)

echo ""
for line in "${ART[@]}"; do
    echo -e "${R}${line}${X}"
    sleep 0.035
done

sleep 0.3

echo ""
TITLE_LINES=(
"    ___          _                         "
"  / __\\___ _ __| |__   ___ _ __ _   _ ___ "
" / /  / _ \\ '__| '_ \\ / _ \\ '__| | | / __|"
"/ /__|  __/ |  | |_) |  __/ |  | |_| \\__ \\"
"\\____/\\___|_|  |_.__/ \\___|_|   \\__,_|___/ "
)

for line in "${TITLE_LINES[@]}"; do
    glitch_line "$line"
    sleep 0.05
done

sleep 0.4

echo ""
flicker "  ══════════════════════════════════════"
sleep 0.1
flicker "  TRÊS CABEÇAS.  UM SÓ JULGAMENTO.  SEM PIEDADE."
sleep 0.1
flicker "  ══════════════════════════════════════"
echo ""
sleep 0.6

type_out "  a besta desperta..." 0.05 "$DR"
sleep 0.4
type_out "  vinculando-se à sua máquina..." 0.04 "$R"
sleep 0.8

echo ""

if [[ "$OSTYPE" == "linux-android"* ]] || [ -d "/data/data/com.termux" ]; then
    ENV="termux"
    BIN_DIR="$PREFIX/bin"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ENV="linux"
else
    ENV="desconhecido"
fi

echo -e "${DR}  [+] ambiente        : ${R}${ENV}${X}"
sleep 0.15
echo -e "${DR}  [+] pasta instalação: ${D}${INSTALL_DIR}${X}"
sleep 0.15
echo -e "${DR}  [+] pasta comando   : ${D}${BIN_DIR}${X}"
sleep 0.15
echo ""
sleep 0.5

echo -e "${DR}  ▶ CABEÇA I   ${R}verificando dependências...${X}"
sleep 0.3

MISSING=()
for dep in python3 git curl; do
    echo -ne "${DR}    procurando por ${dep}...${X}"
    sleep 0.3
    if ! command -v "$dep" &>/dev/null; then
        echo -e " ${R}[AUSENTE]${X}"
        MISSING+=("$dep")
    else
        echo -e " ${G}[OK]${X}"
    fi
done

if [ ${#MISSING[@]} -ne 0 ]; then
    echo ""
    type_out "  [!] dentes faltando: ${MISSING[*]}" 0.03 "$R"
    type_out "  [~] fazendo eles crescerem de novo..." 0.03 "$Y"
    echo ""
    if [ "$ENV" = "termux" ]; then
        pkg install -y "${MISSING[@]}"
    elif command -v apt &>/dev/null; then
        sudo apt update -qq && sudo apt install -y "${MISSING[@]}"
    else
        echo -e "${R}  [!] não foi possível instalar automaticamente. instale manualmente: ${MISSING[*]}${X}"
        exit 1
    fi
fi

echo ""
echo -e "${G}  [✓] CABEÇA I completa — todas as dependências satisfeitas.${X}"
echo ""
sleep 0.5

echo -e "${DR}  ▶ CABEÇA II  ${R}abrindo os portões...${X}"
sleep 0.3

progress_bar "clonando" 1.8

if [ -d "$INSTALL_DIR/.git" ]; then
    echo -e "${Y}  [~] o cerberus já ronda por aqui. atualizando...${X}"
    git -C "$INSTALL_DIR" pull --quiet
else
    git clone --quiet "$REPO" "$INSTALL_DIR"
fi

if [ $? -ne 0 ]; then
    echo -e "${R}  [!] falha ao abrir os portões.${X}"
    exit 1
fi

echo ""
echo -e "${G}  [✓] CABEÇA II completa — repositório pronto.${X}"
echo ""
sleep 0.5

echo -e "${DR}  ▶ CABEÇA III ${R}alimentando a besta...${X}"
sleep 0.3

progress_bar "instalando" 2.0

if command -v pip3 &>/dev/null; then
    PIP="pip3"
elif command -v pip &>/dev/null; then
    PIP="pip"
else
    type_out "  [~] pip não encontrado. instalando..." 0.03 "$Y"
    if [ "$ENV" = "termux" ]; then
        pkg install -y python
    elif command -v apt &>/dev/null; then
        sudo apt install -y python3-pip
    fi
    PIP="pip3"
fi

if [ "$ENV" = "termux" ]; then
    $PIP install --quiet requests python-whois 2>/dev/null
else
    $PIP install --quiet "requests[socks]" python-whois --break-system-packages 2>/dev/null \
    || $PIP install --quiet "requests[socks]" python-whois 2>/dev/null
fi

echo ""
echo -e "${G}  [✓] CABEÇA III completa — pacotes instalados.${X}"
echo ""
sleep 0.5

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/$CMD" << CMDEOF
#!/usr/bin/env bash
cd "$INSTALL_DIR" && python3 cerberus.py "\$@"
CMDEOF

chmod +x "$BIN_DIR/$CMD"

SHELL_RC="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
fi

if ! grep -q "$BIN_DIR" "$SHELL_RC" 2>/dev/null; then
    echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"
fi

export PATH="$BIN_DIR:$PATH"

sleep 0.3
echo ""

type_out "  o ritual está completo." 0.05 "$DR"
sleep 0.5
type_out "  o cerberus está vinculado à sua máquina." 0.04 "$R"
sleep 0.4

echo ""

for i in 3 2 1; do
    echo -ne "\r${DR}  despertando em ${R}${i}${DR}...${X}"
    sleep 0.8
done
echo ""
sleep 0.3

clear

echo ""
for line in "${ART[@]}"; do
    echo -e "${R}${line}${X}"
done

echo ""
flicker "  ══════════════════════════════════════"
sleep 0.05

echo -e "${BR}${BL}          ⚠  O CERBERUS ESTÁ VIVO  ⚠         ${X}"

flicker "  ══════════════════════════════════════"
echo ""
sleep 0.3

echo -e "${G}  [✓] instalado   ${D}→  ${R}cerberus${X}"
echo -e "${G}  [✓] versão      ${D}→  ${R}v1.3.0${X}"
echo -e "${G}  [✓] local       ${D}→  ${D}${INSTALL_DIR}${X}"
echo ""
echo -e "${DR}  ──────────────────────────────────────${X}"
echo ""
echo -e "${D}  execute: ${R}cerberus${X}"
echo ""
echo -e "${DR}  use apenas em alvos autorizados.${X}"
echo -e "${DR}  todas as almas passam por aqui.${X}"
echo ""

if ! command -v cerberus &>/dev/null; then
    echo -e "${Y}  [!] se 'cerberus' ainda não for encontrado, execute:${X}"
    echo -e "${D}      source ~/${SHELL_RC##*/}${X}"
    echo -e "${D}      ou: cd ${INSTALL_DIR} && python3 cerberus.py${X}"
    echo ""
fi
