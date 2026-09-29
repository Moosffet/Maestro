# 🚀 COMO EXECUTAR O BOT - GUIA COMPLETO

Este é o guia passo a passo para colocar o bot em funcionamento.

---

## ⚡ FORMA RÁPIDA (5 minutos)

Se você já tem Python 3.11+ e FFmpeg:

```bash
# 1. Ir para pasta do projeto
cd discord-music-bot

# 2. Criar ambiente
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar
pip install -r requirements.txt

# 4. Configurar
cp .env.example .env
nano .env
# Adicione seu token Discord em DISCORD_TOKEN=

# 5. Executar
python3 bot.py
```

---

## 📋 FORMA COMPLETA (Passo a Passo)

### Passo 1: Preparar o Sistema

#### Linux (Fedora/WSL)

```bash
# Atualizar sistema
sudo dnf update -y

# Instalar Python 3.11+
python3 --version  # Verifique se é 3.11+
# Se precisar atualizar:
sudo dnf install python3 python3-pip -y

# Instalar FFmpeg
sudo dnf install ffmpeg -y

# Verificar instalações
python3 --version
ffmpeg -version
pip3 --version
```

#### macOS

```bash
# Com Homebrew
brew install python3 ffmpeg

# Verificar
python3 --version
ffmpeg -version
```

#### Windows

- Instale Python de https://python.org
- Instale FFmpeg de https://ffmpeg.org
- Use WSL2 + Fedora para melhor compatibilidade

---

### Passo 2: Preparar Pasta do Projeto

```bash
# Clone ou extraia o projeto
cd ~
git clone https://seu-repositorio/discord-music-bot.git
# OU descompacte o ZIP
unzip discord-music-bot.zip

# Entre no diretório
cd discord-music-bot

# Verifique a estrutura
ls -la
# Deve mostrar:
# - bot.py
# - config.py
# - requirements.txt
# - .env.example
# - cogs/
# - services/
# - utils/
```

---

### Passo 3: Criar Ambiente Virtual

Um ambiente virtual isola as dependências do projeto.

```bash
# Criar ambiente
python3 -m venv .venv

# Ativar (Linux/macOS)
source .venv/bin/activate

# Ativar (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Ativar (Windows CMD)
.venv\Scripts\activate.bat
```

**Você deve ver `(.venv)` no terminal após ativar.**

---

### Passo 4: Instalar Dependências

```bash
# Certificar que está em (.venv)
which python3  # Linux/macOS - deve mostrar .venv
# ou
where python   # Windows - deve mostrar .venv

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list | grep discord
pip list | grep yt-dlp
pip list | grep python-dotenv
```

**Deve mostrar:**
- discord.py
- yt-dlp
- python-dotenv

---

### Passo 5: Obter Token Discord

**Essencial para o bot funcionar!**

1. Acesse: https://discord.com/developers/applications
2. Faça login com sua conta Discord
3. Clique em **"New Application"**
4. Dê um nome (ex: "Music Bot")
5. Clique em **"Create"**
6. Na barra lateral, clique em **"Bot"**
7. Clique em **"Add Bot"**
8. Em **"TOKEN"**, clique em **"Copy"**
9. **Guarde este token com segurança!**

---

### Passo 6: Configurar .env

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar (escolha um editor)
nano .env          # Linux/macOS
# ou
notepad .env       # Windows
# ou
code .env          # VS Code
```

**Editar estes campos:**

```
DISCORD_TOKEN=seu_token_cole_aqui
PREFIX=!
DATA_DIR=./data
PLAYLIST_LIMIT=200
IDLE_TIMEOUT=60
LOG_LEVEL=INFO
FFMPEG_PATH=ffmpeg
```

**Importante:**
- ✅ Nunca compartilhe seu token
- ✅ Nunca commite `.env` no Git
- ✅ `.gitignore` já protege `.env`

---

### Passo 7: Habilitar Intents no Discord

O bot precisa de permissões especiais.

1. Em https://discord.com/developers/applications
2. Selecione seu bot
3. Vá para **"Bot"** na barra lateral
4. Role até **"GATEWAY INTENTS"**
5. Habilite:
   - ✅ **Message Content Intent**
   - ✅ **Server Members Intent** (importante!)
   - ✅ **Voice States** (importante!)
6. Clique em **"Save Changes"**

---

### Passo 8: Convidar Bot ao Servidor

1. Ainda na página do bot
2. Vá para **"OAuth2"** → **"URL Generator"**
3. Em **"SCOPES"**, selecione: `bot`
4. Em **"PERMISSIONS"**, selecione:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Add Reactions
   - ✅ Connect (Voice)
   - ✅ Speak (Voice)
   - ✅ Manage Messages
5. Copie a URL gerada
6. Abra em navegador e convide o bot
7. Selecione o servidor
8. Autorize

**Bot deve aparecer online no servidor!**

---

### Passo 9: Executar o Bot

```bash
# Garantir que ambiente está ativado
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows

# Verificar que .env está configurado
cat .env | grep DISCORD_TOKEN

# EXECUTAR BOT
python3 bot.py
```

**Você deve ver:**

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

INFO - Bot conectado como MusicBot#1234
```

**✅ BOT ESTÁ PRONTO!**

---

## 🧪 Testar o Bot

No Discord:

```
!conectar       # Bot entra no seu canal de voz
!tocar test     # Busca e toca "test"
!pausa          # Pausa
!retomar        # Retoma
!ajuda          # Lista todos os comandos
!fila           # Mostra fila
!sair           # Bot sai
```

---

## ⚠️ Se Algo Der Errado

### Erro: "DISCORD_TOKEN não configurado"

```bash
# Verifique .env
cat .env

# Deve ter: DISCORD_TOKEN=seu_token

# Se não tiver, edite:
nano .env
```

### Erro: "FFmpeg não encontrado"

```bash
# Instale FFmpeg
sudo dnf install ffmpeg -y

# Ou configure o caminho em .env
FFMPEG_PATH=/usr/bin/ffmpeg
```

### Erro: "Module discord.py not found"

```bash
# Ative ambiente virtual
source .venv/bin/activate

# Instale dependências
pip install -r requirements.txt
```

### Erro: "No space left on device"

```bash
# Limpe cache do yt-dlp
rm -rf ~/.cache/yt-dlp

# Verifique espaço
df -h
```

### Erro: "Bot não conecta ao Discord"

1. Verifique token em `.env`
2. Verifique intents no Discord Developer Portal
3. Verifique se bot foi invitado ao servidor
4. Veja logs: `tail -f data/bot.log`

---

## 🔄 Executar Bot em Segundo Plano

Se você quer que o bot rode permanentemente:

### Linux/WSL - com `nohup`

```bash
# Iniciar em background
nohup python3 bot.py > bot.log 2>&1 &

# Parar
pkill -f "python3 bot.py"

# Ver logs
tail -f bot.log
```

### Linux/WSL - com `screen`

```bash
# Criar sessão
screen -S music-bot

# Dentro da sessão
source .venv/bin/activate
python3 bot.py

# Sair sem matar (Ctrl+A, depois D)

# Voltar à sessão
screen -r music-bot

# Listar sessões
screen -ls
```

### Linux/WSL - com `systemd` (Avançado)

```bash
# Criar arquivo de serviço
sudo nano /etc/systemd/system/music-bot.service
```

Conteúdo:
```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/home/seu_usuario/discord-music-bot
ExecStart=/home/seu_usuario/discord-music-bot/.venv/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Ativar:
```bash
sudo systemctl daemon-reload
sudo systemctl enable music-bot
sudo systemctl start music-bot
sudo systemctl status music-bot
```

---

## 📊 Verificar Status

```bash
# Ver se bot está rodando
ps aux | grep "python3 bot.py"

# Ver logs
tail -f data/bot.log

# Ver conexões de rede
netstat -an | grep ESTABLISHED

# Ver uso de memória
top -p $(pgrep -f "python3 bot.py")
```

---

## 🛑 Parar o Bot

```bash
# Se rodando normalmente
# Pressione Ctrl+C no terminal

# Se em background
pkill -f "python3 bot.py"

# Se em systemd
sudo systemctl stop music-bot
```

---

## 📚 Documentação Adicional

- **README.md** - Documentação completa
- **QUICKSTART.md** - Início rápido
- **CHECKLIST.md** - Verificação final
- **data/bot.log** - Logs da aplicação

---

## 🎉 Pronto!

Seu bot está **100% funcional** e pronto para usar! 🎵

**Divirta-se!** 🎶
