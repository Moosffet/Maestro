#!/usr/bin/env python3
"""
Organizador de Arquivos - Cria a estrutura correta do projeto
Execute: python3 organize_files.py
"""

import os
import shutil
from pathlib import Path

def create_structure():
    """Cria a estrutura de diretórios."""
    directories = [
        "cogs",
        "services",
        "utils",
        "tests",
        "data",
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Diretório criado: {directory}/")

def move_files():
    """Move arquivos para os diretórios corretos."""
    
    # Mapeamento: arquivo -> diretório
    moves = {
        # COGS
        "music.py": "cogs/",
        "favorites.py": "cogs/",
        "help.py": "cogs/",
        
        # SERVICES
        "youtube.py": "services/",
        "queue.py": "services/",
        "player.py": "services/",
        "favorites.py": "services/",  # Nota: mesmo nome em cogs e services
        
        # UTILS
        "logging.py": "utils/",
        "logger.py": "utils/",
        "errors.py": "utils/",
        "formatting.py": "utils/",
        "validation.py": "utils/",
        "persistence.py": "utils/",
        
        # TESTS
        "test_formatting.py": "tests/",
        "test_validation.py": "tests/",
        "test_persistence.py": "tests/",
    }
    
    print("\n📦 Movendo arquivos...\n")
    
    moved = 0
    for filename, directory in moves.items():
        source = Path(filename)
        
        if source.exists():
            dest = Path(directory) / filename
            shutil.move(str(source), str(dest))
            print(f"✓ {filename} → {directory}")
            moved += 1
        else:
            print(f"⊘ {filename} (não encontrado, pulando)")
    
    print(f"\n✓ {moved} arquivos movidos")

def create_init_files():
    """Cria arquivos __init__.py nos diretórios."""
    packages = ["cogs", "services", "utils", "tests"]
    
    print("\n📄 Criando __init__.py...\n")
    
    for package in packages:
        init_file = Path(package) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"✓ {package}/__init__.py criado")
        else:
            print(f"✓ {package}/__init__.py já existe")

def create_gitkeep():
    """Cria .gitkeep em data/."""
    gitkeep = Path("data") / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()
        print("\n✓ data/.gitkeep criado")

def handle_duplicates():
    """Lida com arquivos duplicados (favorites.py em cogs e services)."""
    print("\n⚠️  Verificando duplicatas...\n")
    
    cogs_fav = Path("cogs/favorites.py")
    services_fav = Path("services/favorites.py")
    
    if cogs_fav.exists() and services_fav.exists():
        print("✓ Ambos os favorites.py estão nos lugares certos")
    elif cogs_fav.exists() and not services_fav.exists():
        print("⚠️  favorites.py em cogs, mas não em services")
        print("   Se tiver arquivo services/favorites.py separado, mova manualmente")
    elif services_fav.exists() and not cogs_fav.exists():
        print("⚠️  favorites.py em services, mas não em cogs")
        print("   Se tiver arquivo cogs/favorites.py separado, mova manualmente")

def fix_imports():
    """Avisa sobre necessidade de corrigir importações."""
    print("\n🔧 PRÓXIMAS AÇÕES:\n")
    print("1. Renomear utils/logging.py → utils/logger.py:")
    print("   mv utils/logging.py utils/logger.py\n")
    print("2. Corrigir importações em todos os arquivos:")
    print("   - Procure: from utils.logging import")
    print("   - Substitua por: from utils.logger import\n")
    print("3. Ou execute o script fix_logging.py:")
    print("   python3 fix_logging.py\n")

def verify_structure():
    """Verifica se a estrutura está correta."""
    print("\n✅ Verificando estrutura...\n")
    
    expected_files = {
        "bot.py": ".",
        "config.py": ".",
        "requirements.txt": ".",
        ".env.example": ".",
        ".gitignore": ".",
        "README.md": ".",
        "cogs/__init__.py": "cogs/",
        "cogs/music.py": "cogs/",
        "cogs/favorites.py": "cogs/",
        "cogs/help.py": "cogs/",
        "services/__init__.py": "services/",
        "services/youtube.py": "services/",
        "services/queue.py": "services/",
        "services/player.py": "services/",
        "services/favorites.py": "services/",
        "utils/__init__.py": "utils/",
        "utils/errors.py": "utils/",
        "utils/formatting.py": "utils/",
        "utils/validation.py": "utils/",
        "utils/persistence.py": "utils/",
        "tests/__init__.py": "tests/",
        "tests/test_formatting.py": "tests/",
        "tests/test_validation.py": "tests/",
        "tests/test_persistence.py": "tests/",
        "data/.gitkeep": "data/",
    }
    
    missing = []
    present = []
    
    for file, location in expected_files.items():
        if Path(file).exists():
            present.append(file)
            print(f"✓ {file}")
        else:
            missing.append(file)
            print(f"✗ {file}")
    
    print(f"\n✓ Presentes: {len(present)}")
    print(f"✗ Faltando: {len(missing)}")
    
    if missing:
        print("\n⚠️  Alguns arquivos estão faltando!")
        print("Certifique-se de que baixou todos os arquivos do projeto.")
    
    return len(missing) == 0

def main():
    """Função principal."""
    print("=" * 60)
    print("🎵 Discord Music Bot - Organizador de Arquivos")
    print("=" * 60)
    print()
    
    # Cria estrutura
    print("📁 Criando diretórios...\n")
    create_structure()
    
    # Move arquivos
    move_files()
    
    # Cria __init__.py
    create_init_files()
    
    # Cria .gitkeep
    create_gitkeep()
    
    # Lida com duplicatas
    handle_duplicates()
    
    # Verifica estrutura
    all_good = verify_structure()
    
    # Próximas ações
    fix_imports()
    
    if all_good:
        print("\n🎉 PRONTO! Estrutura organizada corretamente!")
        print("\nPróximas ações:")
        print("1. python3 fix_logging.py  (corrige importações)")
        print("2. python3 bot.py          (executa o bot)")
    else:
        print("\n⚠️  Alguns arquivos estão faltando.")
        print("Verifique se baixou todos os 26 arquivos.")

if __name__ == "__main__":
    main()
