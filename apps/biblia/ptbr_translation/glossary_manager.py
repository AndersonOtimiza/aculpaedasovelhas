import json
from pathlib import Path
from typing import Dict

def load_glossary(file_path: str = None) -> Dict[str, str]:
    """
    Carrega o glossário grego de um arquivo JSON.
    Se nenhum caminho for fornecido, tenta carregar do local padrão.
    """
    if file_path is None:
        # Caminho padrão relativo a este arquivo
        current_dir = Path(__file__).parent
        file_path = current_dir / "glossary" / "greek_glossary.json"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Aviso: Arquivo de glossário não encontrado em {file_path}. Retornando dicionário vazio.")
        return {}
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar o arquivo JSON do glossário em {file_path}.")
        return {}

# Instância global do glossário para uso fácil
GREEK_GLOSSARY = load_glossary()
