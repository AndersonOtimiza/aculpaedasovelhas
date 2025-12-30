#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Belem Bible AnC - Tradução do Novo Testamento Completo
Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)
Autor: Anderson Belem Costa (Belem, AnC)

Sistema de tradução para textos gregos do Nestle 1904
"""

import json
import csv
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict, field


# ============================================================================
# CONFIGURAÇÃO DOS LIVROS DO NT
# ============================================================================

NT_BOOKS = [
    # Evangelhos
    {"id": 40, "name": "Matthew", "name_pt": "Mateus", "code": "Matt", "chapters": 28},
    {"id": 41, "name": "Mark", "name_pt": "Marcos", "code": "Mark", "chapters": 16},
    {"id": 42, "name": "Luke", "name_pt": "Lucas", "code": "Luke", "chapters": 24},
    {"id": 43, "name": "John", "name_pt": "João", "code": "John", "chapters": 21},
    
    # Atos
    {"id": 44, "name": "Acts", "name_pt": "Atos", "code": "Acts", "chapters": 28},
    
    # Epístolas Paulinas
    {"id": 45, "name": "Romans", "name_pt": "Romanos", "code": "Rom", "chapters": 16},
    {"id": 46, "name": "1_Corinthians", "name_pt": "1 Coríntios", "code": "1Cor", "chapters": 16},
    {"id": 47, "name": "2_Corinthians", "name_pt": "2 Coríntios", "code": "2Cor", "chapters": 13},
    {"id": 48, "name": "Galatians", "name_pt": "Gálatas", "code": "Gal", "chapters": 6},
    {"id": 49, "name": "Ephesians", "name_pt": "Efésios", "code": "Eph", "chapters": 6},
    {"id": 50, "name": "Philippians", "name_pt": "Filipenses", "code": "Phil", "chapters": 4},
    {"id": 51, "name": "Colossians", "name_pt": "Colossenses", "code": "Col", "chapters": 4},
    {"id": 52, "name": "1_Thessalonians", "name_pt": "1 Tessalonicenses", "code": "1Thess", "chapters": 5},
    {"id": 53, "name": "2_Thessalonians", "name_pt": "2 Tessalonicenses", "code": "2Thess", "chapters": 3},
    {"id": 54, "name": "1_Timothy", "name_pt": "1 Timóteo", "code": "1Tim", "chapters": 6},
    {"id": 55, "name": "2_Timothy", "name_pt": "2 Timóteo", "code": "2Tim", "chapters": 4},
    {"id": 56, "name": "Titus", "name_pt": "Tito", "code": "Titus", "chapters": 3},
    {"id": 57, "name": "Philemon", "name_pt": "Filemom", "code": "Phlm", "chapters": 1},
    
    # Epístolas Gerais
    {"id": 58, "name": "Hebrews", "name_pt": "Hebreus", "code": "Heb", "chapters": 13},
    {"id": 59, "name": "James", "name_pt": "Tiago", "code": "Jas", "chapters": 5},
    {"id": 60, "name": "1_Peter", "name_pt": "1 Pedro", "code": "1Pet", "chapters": 5},
    {"id": 61, "name": "2_Peter", "name_pt": "2 Pedro", "code": "2Pet", "chapters": 3},
    {"id": 62, "name": "1_John", "name_pt": "1 João", "code": "1John", "chapters": 5},
    {"id": 63, "name": "2_John", "name_pt": "2 João", "code": "2John", "chapters": 1},
    {"id": 64, "name": "3_John", "name_pt": "3 João", "code": "3John", "chapters": 1},
    {"id": 65, "name": "Jude", "name_pt": "Judas", "code": "Jude", "chapters": 1},
    
    # Apocalipse
    {"id": 66, "name": "Revelation", "name_pt": "Apocalipse", "code": "Rev", "chapters": 22},
]


# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================

@dataclass
class GreekWord:
    """Palavra grega com análise morfológica"""
    position: int
    book_code: str
    chapter: int
    verse: int
    parse: str
    text_surface: str
    text_normalized: str
    text_lemma: str
    lemma: str
    strong: str = ""
    translation: str = ""
    gloss: str = ""


# ============================================================================
# CARREGAMENTO DO GLOSSÁRIO
# ============================================================================

def load_greek_glossary() -> Dict[str, str]:
    """Carrega o glossário grego-português"""
    glossary_path = Path(__file__).parent / "glossary" / "greek_glossary.json"
    
    if not glossary_path.exists():
        print(f"⚠️ Glossário não encontrado: {glossary_path}")
        return {}
    
    with open(glossary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


GREEK_GLOSSARY = load_greek_glossary()


# ============================================================================
# PROCESSAMENTO DO NESTLE 1904
# ============================================================================

def parse_nestle_line(row: Dict[str, str], target_book_code: str) -> Optional[GreekWord]:
    """Parse uma linha do formato Nestle1904 CSV"""
    bcv = row.get('BCV', '')
    parts = bcv.split()
    
    if len(parts) < 2:
        return None
    
    book_code = parts[0]
    
    # Filtrar apenas o livro desejado
    if book_code != target_book_code:
        return None
    
    chapter_verse = parts[1].split(':')
    if len(chapter_verse) < 2:
        return None
    
    chapter = int(chapter_verse[0])
    verse = int(chapter_verse[1])
    
    return GreekWord(
        position=0,
        book_code=book_code,
        chapter=chapter,
        verse=verse,
        parse=row.get('func_morph', ''),
        text_surface=row.get('text', ''),
        text_normalized=row.get('normalized', ''),
        text_lemma=row.get('lemma', ''),
        lemma=row.get('lemma', ''),
        strong=row.get('strongs', '')
    )


def load_nestle_book(filepath: str, book_code: str) -> Dict[int, Dict[int, List[GreekWord]]]:
    """Carrega um livro do Nestle1904 e organiza por capítulo/versículo"""
    chapters = {}
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = parse_nestle_line(row, book_code)
            if word:
                if word.chapter not in chapters:
                    chapters[word.chapter] = {}
                if word.verse not in chapters[word.chapter]:
                    chapters[word.chapter][word.verse] = []
                chapters[word.chapter][word.verse].append(word)
    
    return chapters


# ============================================================================
# TRADUÇÃO
# ============================================================================

def translate_word(word: GreekWord) -> str:
    """Traduz palavra grega usando glossário"""
    # Tentar traduzir pelo lema
    if word.lemma in GREEK_GLOSSARY:
        return GREEK_GLOSSARY[word.lemma]
    
    # Tentar pela forma normalizada
    if word.text_normalized in GREEK_GLOSSARY:
        return GREEK_GLOSSARY[word.text_normalized]
    
    # Tentar pela forma de superfície
    if word.text_surface in GREEK_GLOSSARY:
        return GREEK_GLOSSARY[word.text_surface]
    
    # Se não encontrar, retornar entre colchetes
    return f"[{word.text_surface}]"


def translate_verse(words: List[GreekWord]) -> Dict:
    """Traduz versículo completo (método Ipísis Iliteris)"""
    translations = []
    greek_text = []
    word_data = []
    
    for i, word in enumerate(words):
        word.position = i + 1
        word.translation = translate_word(word)
        translations.append(word.translation)
        greek_text.append(word.text_surface)
        
        word_data.append({
            "position": word.position,
            "book_code": word.book_code,
            "chapter": word.chapter,
            "verse": word.verse,
            "parse": word.parse,
            "text_surface": word.text_surface,
            "text_normalized": word.text_normalized,
            "text_lemma": word.text_lemma,
            "lemma": word.lemma,
            "strong": word.strong,
            "translation": word.translation,
            "gloss": word.gloss
        })
    
    return {
        "chapter": words[0].chapter,
        "verse": words[0].verse,
        "greek_text": " ".join(greek_text),
        "literal_translation": " ".join(translations),
        "readable_translation": " ".join(translations),
        "words": word_data
    }


# ============================================================================
# GERAÇÃO DE ARQUIVOS
# ============================================================================

def save_chapter_json(book_info: Dict, chapter_num: int, verses: List[Dict], output_dir: Path):
    """Salva capítulo individual em JSON"""
    chapter_data = {
        "book": book_info["name"],
        "book_pt": book_info["name_pt"],
        "testament": "NT",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA",
        "source": "Nestle 1904 Greek New Testament",
        "chapters": [{
            "chapter": chapter_num,
            "verses": verses
        }]
    }
    
    output_file = output_dir / f"{book_info['name']}_Chapter_{chapter_num:02d}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def save_book_json(book_info: Dict, chapters_data: Dict[int, List[Dict]], output_dir: Path):
    """Salva livro completo em JSON"""
    total_verses = sum(len(v) for v in chapters_data.values())
    
    book_data = {
        "book_id": book_info["id"],
        "book_name": book_info["name"],
        "book_name_pt": book_info["name_pt"],
        "testament": "NT",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA",
        "source": "Nestle 1904 Greek New Testament",
        "total_chapters": len(chapters_data),
        "total_verses": total_verses,
        "chapters": []
    }
    
    for chapter_num in sorted(chapters_data.keys()):
        chapter_verses = chapters_data[chapter_num]
        book_data["chapters"].append({
            "chapter": chapter_num,
            "verses": chapter_verses
        })
    
    output_file = output_dir / f"{book_info['name']}_Complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    return output_file


# ============================================================================
# PROCESSO PRINCIPAL
# ============================================================================

def translate_book(book_id: int, save_chapters: bool = True):
    """Traduz um livro específico do NT"""
    # Encontrar informações do livro
    book_info = None
    for book in NT_BOOKS:
        if book["id"] == book_id:
            book_info = book
            break
    
    if not book_info:
        print(f"❌ Livro não encontrado: ID {book_id}")
        return None
    
    print("=" * 70)
    print(f"📖 Traduzindo: {book_info['name_pt']} ({book_info['name']})")
    print("=" * 70)
    print()
    
    # Caminhos
    source_file = Path(__file__).parent.parent / "sources" / "nt_nestle1904" / "Nestle1904-master" / "morph" / "Nestle1904.csv"
    output_dir = Path(__file__).parent / "NT"
    output_dir.mkdir(exist_ok=True)
    
    if not source_file.exists():
        print(f"❌ Arquivo não encontrado: {source_file}")
        return None
    
    # Carregar glossário
    print(f"📚 Glossário carregado: {len(GREEK_GLOSSARY)} termos")
    
    # Carregar e processar livro
    print(f"📖 Carregando: {source_file.name} (livro: {book_info['code']})")
    chapters = load_nestle_book(str(source_file), book_info["code"])
    
    if not chapters:
        print(f"⚠️ Nenhum dado encontrado para {book_info['code']}")
        return None
    
    total_verses = sum(len(verses) for ch in chapters.values() for verses in ch.values())
    print(f"✓ {len(chapters)} capítulos, {total_verses} versículos")
    print()
    
    # Traduzir cada capítulo
    translated_chapters = {}
    
    for chapter_num in sorted(chapters.keys()):
        chapter_verses = chapters[chapter_num]
        translated_verses = []
        
        for verse_num in sorted(chapter_verses.keys()):
            words = chapter_verses[verse_num]
            translated_verse = translate_verse(words)
            translated_verses.append(translated_verse)
        
        translated_chapters[chapter_num] = translated_verses
        
        if save_chapters:
            save_chapter_json(book_info, chapter_num, translated_verses, output_dir)
        
        # Mostrar progresso
        pct = (chapter_num / len(chapters)) * 100
        print(f"\r  Capítulo {chapter_num}/{len(chapters)} ({pct:.0f}%)", end="")
    
    print()
    print()
    
    # Salvar livro completo
    output_file = save_book_json(book_info, translated_chapters, output_dir)
    print(f"✓ Livro salvo: {output_file.name}")
    
    # Estatísticas
    print()
    print("=" * 70)
    print(f"✅ {book_info['name_pt']} traduzido!")
    print(f"   📊 {len(chapters)} capítulos | {total_verses} versículos")
    print("=" * 70)
    
    return output_file


def translate_all_nt():
    """Traduz todos os 27 livros do Novo Testamento"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + "BÍBLIA BELEM AnC — TRADUÇÃO DO NOVO TESTAMENTO".center(68) + "║")
    print("║" + "Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    completed = []
    failed = []
    
    for book in NT_BOOKS:
        try:
            result = translate_book(book["id"], save_chapters=True)
            if result:
                completed.append(book["name_pt"])
        except Exception as e:
            print(f"❌ Erro em {book['name_pt']}: {e}")
            failed.append(book["name_pt"])
        print()
    
    # Resumo final
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + "RESUMO DA TRADUÇÃO DO NOVO TESTAMENTO".center(68) + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║  ✅ Livros traduzidos: {len(completed)}/27".ljust(69) + "║")
    if failed:
        print(f"║  ❌ Livros com erro: {len(failed)}".ljust(69) + "║")
        for book in failed:
            print(f"║     - {book}".ljust(69) + "║")
    print("╚" + "═" * 68 + "╝")


# ============================================================================
# CLI
# ============================================================================

def main():
    import sys
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--all":
            translate_all_nt()
        elif arg.isdigit():
            book_id = int(arg)
            translate_book(book_id)
        elif arg == "--list":
            print("Livros do Novo Testamento:")
            for book in NT_BOOKS:
                print(f"  {book['id']:2d}. {book['name_pt']} ({book['name']}) - {book['chapters']} caps")
        else:
            print(f"Uso: python {sys.argv[0]} [BOOK_ID | --all | --list]")
            print("  BOOK_ID: ID do livro (40-66)")
            print("  --all: Traduzir todos os 27 livros")
            print("  --list: Listar todos os livros")
    else:
        # Default: listar livros
        print("Uso: python translate_nt.py [BOOK_ID | --all | --list]")
        print("Use --list para ver os livros disponíveis")


if __name__ == "__main__":
    main()
