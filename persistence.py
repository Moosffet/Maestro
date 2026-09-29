"""
Gravação atômica de dados.
Protege contra corrupção por interrupção ou gravações simultâneas.
Usa arquivo temporário + os.replace() para atomicidade.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional
import logging


logger = logging.getLogger(__name__)


def atomic_write_json(
    file_path: Path,
    data: Any,
    indent: int = 2,
) -> None:
    """
    Escreve JSON de forma atômica (segura contra interrupções).
    
    Usa padrão: escreve em arquivo temporário, depois troca (renomeia).
    Isso garante que o arquivo nunca fica corrompido parcialmente.
    
    Args:
        file_path: Caminho do arquivo JSON.
        data: Dados a escrever.
        indent: Indentação do JSON.
        
    Raises:
        IOError: Se falhar.
    """
    file_path = Path(file_path)
    
    # Cria diretório se não existir
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Cria arquivo temporário no mesmo diretório (garante mesmo filesystem)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=".tmp_",
        suffix=".json",
    )
    
    try:
        # Escreve no arquivo temporário
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        # Força escrita para disco
        os.fsync(os.open(temp_path, os.O_RDONLY))
        
        # Renomeia (atômico no Linux)
        os.replace(temp_path, file_path)
        
        logger.debug(f"JSON escrito atomicamente: {file_path}")
    
    except Exception as e:
        # Remove arquivo temporário em caso de erro
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        
        logger.error(f"Erro ao escrever JSON {file_path}: {e}")
        raise IOError(f"Falha ao escrever {file_path}: {e}") from e


def atomic_read_json(file_path: Path, default: Optional[Any] = None) -> Any:
    """
    Lê JSON com tratamento de erros.
    
    Args:
        file_path: Caminho do arquivo JSON.
        default: Valor padrão se arquivo não existir ou for inválido.
        
    Returns:
        Dados carregados ou default.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.debug(f"Arquivo JSON não existe: {file_path}")
        return default
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON corrompido em {file_path}: {e}")
        return default
    
    except Exception as e:
        logger.error(f"Erro ao ler {file_path}: {e}")
        return default


def atomic_write_csv_line(
    file_path: Path,
    values: list[str],
) -> None:
    """
    Adiciona linha a arquivo CSV de forma atômica.
    
    Args:
        file_path: Caminho do arquivo CSV.
        values: Valores para escrever (uma linha).
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Escapa aspas e cria linha CSV
    escaped_values = [
        f'"{v.replace(chr(34), chr(34) + chr(34))}"' if v else '""'
        for v in values
    ]
    line = ",".join(escaped_values) + "\n"
    
    try:
        # Append é mais seguro para logs
        with open(file_path, "a", encoding="utf-8", newline="") as f:
            f.write(line)
        
        logger.debug(f"Linha adicionada a CSV: {file_path}")
    
    except Exception as e:
        logger.error(f"Erro ao escrever CSV {file_path}: {e}")
        raise IOError(f"Falha ao escrever {file_path}: {e}") from e


def backup_file(file_path: Path) -> Optional[Path]:
    """
    Cria backup de arquivo (adiciona .backup).
    
    Args:
        file_path: Arquivo a fazer backup.
        
    Returns:
        Caminho do backup ou None se falhar.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        return None
    
    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
    
    try:
        import shutil
        shutil.copy2(file_path, backup_path)
        logger.debug(f"Backup criado: {backup_path}")
        return backup_path
    
    except Exception as e:
        logger.error(f"Erro ao fazer backup de {file_path}: {e}")
        return None


def ensure_dir_exists(path: Path) -> Path:
    """
    Garante que diretório existe.
    
    Args:
        path: Caminho do diretório.
        
    Returns:
        Path do diretório.
        
    Raises:
        PermissionError: Se não conseguir criar.
    """
    path = Path(path)
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except PermissionError as e:
        raise PermissionError(f"Sem permissão para criar {path}: {e}") from e
    except Exception as e:
        raise OSError(f"Erro ao criar {path}: {e}") from e


# Tests
if __name__ == "__main__":
    import tempfile
    
    # Testa gravação atômica
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.json"
        
        # Escreve dados
        test_data = {"key": "value", "number": 42}
        atomic_write_json(test_file, test_data)
        
        # Lê dados
        loaded = atomic_read_json(test_file)
        assert loaded == test_data, f"Dados não batem: {loaded} != {test_data}"
        
        # Testa leitura de arquivo inexistente
        assert atomic_read_json(Path(tmpdir) / "inexistente.json") is None
        
        print("✅ Todos os testes de persistência passaram!")
