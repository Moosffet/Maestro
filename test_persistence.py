"""Testes de persistência."""

import pytest
import tempfile
from pathlib import Path
from utils.persistence import (
    atomic_write_json,
    atomic_read_json,
    atomic_write_csv_line,
    ensure_dir_exists,
)


class TestAtomicJSON:
    """Testes de leitura/escrita JSON atômica."""
    
    def test_write_and_read(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            
            # Escreve dados
            data = {"key": "value", "number": 42, "list": [1, 2, 3]}
            atomic_write_json(file_path, data)
            
            # Lê dados
            loaded = atomic_read_json(file_path)
            assert loaded == data
    
    def test_read_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "nonexistent.json"
            loaded = atomic_read_json(file_path)
            assert loaded is None
    
    def test_read_nonexistent_with_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "nonexistent.json"
            loaded = atomic_read_json(file_path, default=[])
            assert loaded == []
    
    def test_create_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "subdir" / "test.json"
            
            # Não deve existir ainda
            assert not file_path.parent.exists()
            
            # Escreve (cria diretório)
            atomic_write_json(file_path, {"test": "data"})
            
            # Agora deve existir
            assert file_path.exists()
    
    def test_overwrite_existing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.json"
            
            # Escreve primeira vez
            atomic_write_json(file_path, {"version": 1})
            
            # Escreve segunda vez (sobrescreve)
            atomic_write_json(file_path, {"version": 2})
            
            # Verifica dados atualizados
            loaded = atomic_read_json(file_path)
            assert loaded["version"] == 2


class TestAtomicCSV:
    """Testes de escrita CSV."""
    
    def test_write_csv_line(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.csv"
            
            # Escreve linha
            atomic_write_csv_line(file_path, ["col1", "col2", "col3"])
            
            # Verifica conteúdo
            with open(file_path, "r") as f:
                content = f.read()
            assert "col1" in content
            assert "col2" in content
    
    def test_write_multiple_lines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.csv"
            
            # Escreve múltiplas linhas
            atomic_write_csv_line(file_path, ["line1", "a", "b"])
            atomic_write_csv_line(file_path, ["line2", "c", "d"])
            
            # Verifica linhas
            with open(file_path, "r") as f:
                lines = f.readlines()
            assert len(lines) == 2


class TestEnsureDirExists:
    """Testes de ensure_dir_exists."""
    
    def test_create_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "new_dir"
            
            # Não deve existir
            assert not dir_path.exists()
            
            # Cria
            ensure_dir_exists(dir_path)
            
            # Agora deve existir
            assert dir_path.exists()
            assert dir_path.is_dir()
    
    def test_create_nested_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir) / "parent" / "child" / "nested"
            
            # Cria todos os níveis
            ensure_dir_exists(dir_path)
            
            # Deve existir
            assert dir_path.exists()
    
    def test_existing_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            
            # Já existe
            assert dir_path.exists()
            
            # Não deve gerar erro
            ensure_dir_exists(dir_path)
            assert dir_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
