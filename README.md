# 🎵 Discord Music Bot v2.0

Bot musical completo para Discord com suporte a YouTube, playlists, favoritos e gerenciamento avançado de fila.

## ✨ Características

- ✅ Reprodução de músicas do YouTube
- ✅ Busca automática no YouTube
- ✅ Suporte a playlists
- ✅ Sistema de favoritos com persistência
- ✅ Fila avançada (loop, shuffle, voltar)
- ✅ Controle de volume
- ✅ Gerenciamento por servidor (cada servidor tem sua própria fila)
- ✅ Auditoria de ações
- ✅ Logging estruturado
- ✅ Sem token hardcoded (seguro para Git)
- ✅ Configurável via .env

## 📋 Pré-requisitos

- **Python 3.11+**
- **FFmpeg**
- **WSL2** com **Fedora** (ou Linux nativo)
- **Discord Bot Token**

## 🚀 Instalação no WSL + Fedora

### 1. Atualizar Fedora

```bash
sudo dnf update -y
```

### 2. Instalar Python 3.11+

```bash
# Verifica versão
python3 --version

# Se < 3.11, instala manualmente (Fedora 37+ já tem)
sudo dnf install python3 python3-pip python3-dev -y
```

### 3. Instalar FFmpeg

```bash
sudo dnf install ffmpeg -y

# Verifica instalação
ffmpeg -version
```

### 4. Clonar Projeto (ou descompactar)

```bash
cd ~
git clone https://github.com/seu-usuario/discord-music-bot.git
cd discord-music-bot
```

Ou extrair arquivo ZIP:
```bash
unzip discord-music-bot.zip
cd discord-music-bot
```

### 5. Criar Ambiente Virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 6. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 7. Configurar .env

```bash
# Copia exemplo
cp .env.example .env

# Edita (seu editor favorito)
nano .env
```

**Configure:**
```
DISCORD_TOKEN=seu_token_aqui
PREFIX=!
DATA_DIR=./data
PLAYLIST_LIMIT=200
IDLE_TIMEOUT=60
LOG_LEVEL=INFO
```

### 8. Executar Bot

```bash
python3 bot.py
```

Você deve ver:
```
╔══════════════════════════════════════════════╗
║     🎵 Discord Music Bot v2.0               ║
║     Refatoração Completa                    ║
╚══════════════════════════════════════════════╝

📋 Validando ambiente...

✓ Python
✓ Discord Token
✓ FFmpeg
✓ Diretório de dados
✓ Configuração carregada
  Prefix: !
  Data dir: ./data
  Playlist limit: 200
  Idle timeout: 60s

🚀 Iniciando bot...
```

---

## 🔧 Configuração do Discord Bot

### Passo 1: Criar Aplicação

1. Acesse: https://discord.com/developers/applications
2. Clique em **"New Application"**
3. Dê um nome (ex: "Music Bot")
4. Clique em **"Create"**

### Passo 2: Criar Bot

1. Vá para **"Bot"** na barra lateral
2. Clique em **"Add Bot"**
3. Em **"TOKEN"**, clique em **"Copy"**
4. Cole no seu `.env`:
   ```
   DISCORD_TOKEN=<token_aqui>
   ```

⚠️ **NÃO** compartilhe este token!

### Passo 3: Configurar Intents

1. Em **"Bot"**, role até **"GATEWAY INTENTS"**
2. Ative:
   - ✓ **Message Content Intent**
   - ✓ **Voice States**
   - ✓ **Server Members Intent** (opcional)

### Passo 4: Configurar Permissões

1. Vá para **"OAuth2"** > **"URL Generator"**
2. Em **"SCOPES"**, selecione:
   - ✓ `bot`
3. Em **"PERMISSIONS"**, selecione:
   - ✓ Send Messages
   - ✓ Embed Links
   - ✓ Add Reactions
   - ✓ Connect (Voice)
   - ✓ Speak (Voice)
   - ✓ Manage Messages (para reações em fila)

4. Copie a URL gerada em **"GENERATED URL"**
5. Abra em navegador e convide bot ao seu servidor

---

## 💻 Comandos

### 🎶 Reprodução

| Comando | Aliases | Uso |
|---------|---------|-----|
| `!conectar` | `!j` | Conecta ao seu canal de voz |
| `!tocar` | `!p` | `!tocar <nome\|URL\|favorito N>` |
| `!pausa` | — | Pausa a música |
| `!retomar` | `!r` | Retoma música pausada |
| `!proximo` | `!s` | Pula para próxima música |
| `!pular` | `!jmp` | `!pular <posição>` |
| `!parar` | — | Para e limpa fila |
| `!limpar` | `!cl` | Limpa fila (mantém atual) |

### 📊 Fila

| Comando | Aliases | Uso |
|---------|---------|-----|
| `!fila` | `!q` | `!fila [página]` - Mostra fila |
| `!ouvindoagora` | `!np` | Mostra música tocando |
| `!repetir` | `!l` | `!repetir [off\|song\|queue]` |
| `!embaralhar` | `!sh` | Embaralha fila |
| `!voltar` | `!b, !prev` | Volta para música anterior |

### 🔊 Controles

| Comando | Aliases | Uso |
|---------|---------|-----|
| `!volume` | `!vol` | `!volume <0-100>` |
| `!sair` | `!dc` | Desconecta do canal |

### ⭐ Favoritos

| Comando | Uso |
|---------|-----|
| `!favoritos add <URL>` | Adiciona música aos favoritos |
| `!favoritos rem <número>` | Remove favorito |
| `!favoritos lista` | Lista todos favoritos |
| `!tocar favorito <número>` | Toca um favorito |

### ❓ Ajuda

| Comando | Aliases |
|---------|---------|
| `!ajuda` | `!help, !?` |

---

## 📁 Estrutura do Projeto

```
discord-music-bot/
├── bot.py                  # Inicialização principal
├── config.py              # Configuração centralizada
├── requirements.txt       # Dependências Python
├── .env                   # Configuração (NÃO comitir!)
├── .env.example          # Modelo de .env
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Este arquivo
│
├── data/                 # Dados do bot (criado em runtime)
│   ├── favorites.json    # Favoritos salvos
│   └── favorites_audit.csv # Log de ações
│
├── cogs/                 # Comandos Discord
│   ├── music.py         # Comandos musicais
│   ├── favorites.py     # Comandos de favoritos
│   └── help.py          # Comando de ajuda
│
├── services/            # Lógica de negócio
│   ├── youtube.py       # Integração yt-dlp
│   ├── player.py        # Reprodução de áudio
│   ├── queue.py         # Gerenciamento de fila
│   └── favorites.py     # Gerenciamento de favoritos
│
└── utils/               # Utilitários
    ├── formatting.py    # Formatação de strings
    ├── validation.py    # Validação de entrada
    ├── logging.py       # Sistema de logging
    ├── persistence.py   # Gravação atômica
    └── errors.py        # Exceções customizadas
```

---

## 🔐 Segurança

✅ **Token seguro:**
- Armazenado em `.env` (não versionado)
- Carregado via `python-dotenv`
- Nunca exposto em logs

✅ **Proteção de dados:**
- Gravação atômica com arquivo temporário
- Proteção contra corrupção
- Auditoria de ações

✅ **Seguro para publicar:**
- `.gitignore` protege `.env`
- Projeto pronto para GitHub público

---

## 🐛 Troubleshooting

### ❌ "DISCORD_TOKEN não configurado"

```bash
# Verifica .env
cat .env | grep DISCORD_TOKEN

# Se vazio, configure:
nano .env
# Adicione: DISCORD_TOKEN=seu_token
```

### ❌ "FFmpeg não encontrado"

```bash
# Instala FFmpeg
sudo dnf install ffmpeg -y

# Verifica
ffmpeg -version
```

### ❌ "Modulo discord.py não encontrado"

```bash
# Ativa ambiente virtual
source .venv/bin/activate

# Instala dependências
pip install -r requirements.txt
```

### ❌ "Erro ao conectar ao Discord"

1. Verifique token em `.env`
2. Verifique intents no Discord Developer Portal
3. Verifique permissões do bot no servidor

### ❌ "Bot não toca música"

1. Verifique se bot está em um canal de voz: `!conectar`
2. Verifique FFmpeg: `ffmpeg -version`
3. Verifique logs: `tail -f data/bot.log`

### ❌ "yt-dlp: ERROR - No space left on device"

Disco cheio. Limpe:
```bash
# Limpa cache
rm -rf ~/.cache/yt-dlp

# Verifica espaço
df -h
```

---

## 📊 Logs

Logs são salvos em `data/bot.log` com níveis:
- `DEBUG` - Informações detalhadas
- `INFO` - Eventos normais
- `WARNING` - Avisos
- `ERROR` - Erros

Visualize em tempo real:
```bash
tail -f data/bot.log
```

Configure nível em `.env`:
```
LOG_LEVEL=DEBUG  # Mais verboso
LOG_LEVEL=ERROR  # Menos verboso
```

---

## 🧪 Testes

Execute testes unitários:
```bash
# Testes de formatação
python3 -m utils.formatting

# Testes de validação
python3 -m utils.validation

# Testes de persistência
python3 -m utils.persistence
```

---

## 🔄 Atualizar Bot

```bash
# Ativa ambiente virtual
source .venv/bin/activate

# Atualiza dependências
pip install --upgrade -r requirements.txt

# Reinicia bot
python3 bot.py
```

---

## 📝 Configuração Avançada

### BGUtil (Bypass de Geo-bloqueio)

Se videos não carregam por geo-bloqueio:

```bash
# .env
BGUTIL_URL=http://seu-bgutil-server:4416
```

### Cookies para YouTube

Se precisa autenticação:

```bash
# Gera arquivo de cookies
yt-dlp --cookies-from-browser firefox --write-cookies cookies.txt "https://www.youtube.com"

# .env
COOKIES_FILE=./cookies.txt
```

---

## 🤝 Contribuição

Encontrou um bug? Abra uma issue!

---

## 📄 Licença

MIT License - Veja LICENSE para detalhes

---

## 🆘 Suporte

- 📖 Comando: `!ajuda`
- 🔗 Discord.py Docs: https://discordpy.readthedocs.io
- 🎥 yt-dlp: https://github.com/yt-dlp/yt-dlp

---

**Versão:** 2.0 | **Última atualização:** 2024
