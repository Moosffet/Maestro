# ✅ Checklist de Verificação Final

Use este checklist para garantir que tudo está funcionando corretamente.

## 📋 Instalação

- [ ] Python 3.11+ instalado: `python3 --version`
- [ ] FFmpeg instalado: `ffmpeg -version`
- [ ] Ambiente virtual criado: `.venv` existe
- [ ] Dependências instaladas: `pip list | grep discord`
- [ ] `.env` criado e preenchido
- [ ] Token Discord válido em `.env`

## 🔐 Segurança

- [ ] `.env` NÃO está em `.gitignore`? Adicione!
- [ ] `.env` NÃO contém token? (deve estar apenas no arquivo local)
- [ ] `.gitignore` contém `.env`? ✓
- [ ] `.env.example` existe e está vazio/exemplo? ✓
- [ ] Token nunca foi commitado? `git log --name-status | grep .env`

## 🤖 Configuração Discord

- [ ] Bot criado no Discord Developer Portal
- [ ] Token copiado para `.env`
- [ ] Message Content Intent habilitada
- [ ] Voice States Intent habilitada
- [ ] Bot convidado ao servidor com permissões corretas
- [ ] Bot aparece online no servidor

## 🚀 Inicialização

- [ ] Ambiente virtual ativado: `source .venv/bin/activate`
- [ ] Bot inicia sem erros: `python3 bot.py`
- [ ] Banner exibido corretamente
- [ ] "Bot conectado como..." aparece
- [ ] Nenhum error traceback

## 🎵 Comandos Básicos

No Discord, execute:

### Conexão
- [ ] `!conectar` - Bot entra no seu canal de voz
- [ ] `!sair` - Bot sai do canal

### Reprodução
- [ ] `!tocar test` - Busca e toca uma música
- [ ] `!pausa` - Pausa a música
- [ ] `!retomar` - Retoma música pausada
- [ ] `!proximo` - Pula para próxima
- [ ] `!voltar` - Volta para anterior

### Fila
- [ ] `!fila` - Mostra fila (sem erros)
- [ ] `!ouvindoagora` - Mostra música tocando
- [ ] `!repetir` - Ativa loop
- [ ] `!embaralhar` - Embaralha fila

### Favoritos
- [ ] `!favoritos add https://youtube.com/...` - Adiciona favorito
- [ ] `!favoritos lista` - Lista favoritos
- [ ] `!favoritos rem 1` - Remove favorito
- [ ] `!tocar favorito 1` - Toca favorito

### Ajuda
- [ ] `!ajuda` - Lista todos os comandos
- [ ] `!ajuda conectar` - Mostra ajuda de comando específico

## 📊 Persistência

- [ ] Diretório `data/` criado
- [ ] Arquivo `data/favorites.json` existe após adicionar favorito
- [ ] Arquivo `data/favorites_audit.csv` criado
- [ ] Favoritos persistem após reiniciar bot
- [ ] Nenhuma corrupção de JSON (verificar conteúdo)

## 📝 Logging

- [ ] Arquivo `data/bot.log` criado
- [ ] Logs contêm informações relevantes
- [ ] Nenhuma informação sensível (token, IDs reais) exposta
- [ ] Níveis de log funcionam (DEBUG, INFO, WARNING, ERROR)

## ⚙️ Configuração

- [ ] `PREFIX` em `.env` funciona (mudou para algo como `?` e funciona)
- [ ] `PLAYLIST_LIMIT` respeita limite (tente playlist >200 vídeos)
- [ ] `IDLE_TIMEOUT` desconecta após inatividade
- [ ] `LOG_LEVEL` controla verbosidade de logs
- [ ] `FFMPEG_PATH` aponta para ffmpeg correto

## 🧪 Testes Unitários (Opcional)

```bash
# Executar testes
python3 -m pytest tests/ -v

# Ou rodar testes individuais
python3 tests/test_formatting.py
python3 tests/test_validation.py
python3 tests/test_persistence.py
```

- [ ] Todos os testes de `formatting` passam
- [ ] Todos os testes de `validation` passam
- [ ] Todos os testes de `persistence` passam

## 🔧 Troubleshooting Final

Se algo não funciona, execute:

```bash
# Verifica ambiente
python3 -c "import discord; import yt_dlp; print('✓ Imports OK')"

# Verifica FFmpeg
ffmpeg -encoders | grep libopus

# Verifica diretórios
ls -la data/

# Verifica .env
cat .env | grep -v '^#' | grep -v '^$'

# Vê últimas linhas do log
tail -50 data/bot.log
```

---

## 📊 Status Final

Quando tudo está funcionando, você deve ver:

```
✓ Python
✓ Discord Token
✓ FFmpeg
✓ Diretório de dados
✓ Configuração carregada

🚀 Iniciando bot...

INFO - Bot conectado como MusicBot#1234
INFO - Entrou no servidor: Seu Servidor (123456789)
```

---

## 🎉 Sucesso!

Se todas as caixas estão marcadas, seu bot está **100% funcional**! 

**Próximas ações:**
1. Customize os comandos conforme necessário
2. Adicione mais funcionalidades nos `cogs`
3. Configure avançado (BGUtil, cookies, etc.)
4. Publique em repositório Git

---

**Última verificação:** Data/Hora: _______________

**Responsável:** ____________________________

**Notas:** ___________________________________
