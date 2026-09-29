# ⚡ Guia Rápido - Discord Music Bot

**Tempo estimado: 5-10 minutos**

## 1️⃣ Pré-requisitos

Verifique se tem tudo:

```bash
# Python 3.11+
python3 --version

# FFmpeg
ffmpeg -version

# Pip (gerenciador de pacotes Python)
pip3 --version
```

Se falta alguma coisa, instale (Fedora):

```bash
sudo dnf install python3 python3-pip ffmpeg
```

## 2️⃣ Obter Token Discord

1. Acesse: https://discord.com/developers/applications
2. Clique **"New Application"** e dê um nome
3. Vá para **"Bot"** e clique **"Add Bot"**
4. Copie o **TOKEN** (não compartilhe!)
5. Vá para **"OAuth2" → "URL Generator"**
6. Selecione:
   - Scope: `bot`
   - Permissions: `Send Messages`, `Connect`, `Speak`, `Add Reactions`
7. Copie a URL e abra para convidar bot ao seu servidor

## 3️⃣ Setup do Projeto

```bash
# Entrar no projeto
cd discord-music-bot

# Criar ambiente virtual
python3 -m venv .venv

# Ativar
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Copiar exemplo de .env
cp .env.example .env

# Editar .env
nano .env
```

**Configurar .env:**
```
DISCORD_TOKEN=seu_token_aqui
PREFIX=!
DATA_DIR=./data
LOG_LEVEL=INFO
```

## 4️⃣ Executar

```bash
# Garantir que ambiente está ativado
source .venv/bin/activate

# Iniciar bot
python3 bot.py
```

**Deve mostrar:**
```
✓ Python
✓ Discord Token
✓ FFmpeg
✓ Diretório de dados
✓ Configuração carregada

🚀 Iniciando bot...
```

## 5️⃣ Testar Comandos

No Discord:

```
!conectar          # Conecta ao seu canal de voz
!tocar music name  # Busca e toca
!fila              # Mostra fila
!ajuda             # Lista de comandos
```

---

## 🆘 Troubleshooting Rápido

| Problema | Solução |
|----------|---------|
| "Token not found" | Verifique `.env` - adicione `DISCORD_TOKEN=seu_token` |
| "FFmpeg not found" | `sudo dnf install ffmpeg` |
| "Module not found" | Ative `.venv`: `source .venv/bin/activate` |
| "Bot não conecta" | Verifique token e intents no Discord Developer Portal |
| "Sem permissão" | Recrie URL de convite com scopes corretos |

---

## 📚 Próximos Passos

- Leia `README.md` para documentação completa
- Use `!ajuda` no Discord para lista de comandos
- Verifique logs: `tail -f data/bot.log`

---

**Pronto!** 🎉 Bot está rodando! 🎵
