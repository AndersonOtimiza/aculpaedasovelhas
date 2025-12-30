#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Belem Bible AnC - Tradução do Antigo Testamento
Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)
Autor: Anderson Belem Costa (Belem, AnC)

Sistema de tradução para textos hebraicos do Westminster Leningrad Codex (WLC)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
import unicodedata


# ============================================================================
# CONFIGURAÇÃO DOS LIVROS DO AT
# ============================================================================

OT_BOOKS = [
    # Pentateuco
    {"id": 1, "name": "Genesis", "name_pt": "Gênesis", "chapters": 50, "file": "Genesis.txt"},
    {"id": 2, "name": "Exodus", "name_pt": "Êxodo", "chapters": 40, "file": "Exodus.txt"},
    {"id": 3, "name": "Leviticus", "name_pt": "Levítico", "chapters": 27, "file": "Leviticus.txt"},
    {"id": 4, "name": "Numbers", "name_pt": "Números", "chapters": 36, "file": "Numbers.txt"},
    {"id": 5, "name": "Deuteronomy", "name_pt": "Deuteronômio", "chapters": 34, "file": "Deuteronomy.txt"},
    
    # Históricos
    {"id": 6, "name": "Joshua", "name_pt": "Josué", "chapters": 24, "file": "Joshua.txt"},
    {"id": 7, "name": "Judges", "name_pt": "Juízes", "chapters": 21, "file": "Judges.txt"},
    {"id": 8, "name": "Ruth", "name_pt": "Rute", "chapters": 4, "file": "Ruth.txt"},
    {"id": 9, "name": "1_Samuel", "name_pt": "1 Samuel", "chapters": 31, "file": "Samuel_1.txt"},
    {"id": 10, "name": "2_Samuel", "name_pt": "2 Samuel", "chapters": 24, "file": "Samuel_2.txt"},
    {"id": 11, "name": "1_Kings", "name_pt": "1 Reis", "chapters": 22, "file": "Kings_1.txt"},
    {"id": 12, "name": "2_Kings", "name_pt": "2 Reis", "chapters": 25, "file": "Kings_2.txt"},
    {"id": 13, "name": "1_Chronicles", "name_pt": "1 Crônicas", "chapters": 29, "file": "Chronicles_1.txt"},
    {"id": 14, "name": "2_Chronicles", "name_pt": "2 Crônicas", "chapters": 36, "file": "Chronicles_2.txt"},
    {"id": 15, "name": "Ezra", "name_pt": "Esdras", "chapters": 10, "file": "Ezra.txt"},
    {"id": 16, "name": "Nehemiah", "name_pt": "Neemias", "chapters": 13, "file": "Nehemiah.txt"},
    {"id": 17, "name": "Esther", "name_pt": "Ester", "chapters": 10, "file": "Esther.txt"},
    
    # Poéticos
    {"id": 18, "name": "Job", "name_pt": "Jó", "chapters": 42, "file": "Job.txt"},
    {"id": 19, "name": "Psalms", "name_pt": "Salmos", "chapters": 150, "file": "Psalms.txt"},
    {"id": 20, "name": "Proverbs", "name_pt": "Provérbios", "chapters": 31, "file": "Proverbs.txt"},
    {"id": 21, "name": "Ecclesiastes", "name_pt": "Eclesiastes", "chapters": 12, "file": "Ecclesiastes.txt"},
    {"id": 22, "name": "Song_of_Songs", "name_pt": "Cânticos", "chapters": 8, "file": "Song_of_Songs.txt"},
    
    # Profetas Maiores
    {"id": 23, "name": "Isaiah", "name_pt": "Isaías", "chapters": 66, "file": "Isaiah.txt"},
    {"id": 24, "name": "Jeremiah", "name_pt": "Jeremias", "chapters": 52, "file": "Jeremiah.txt"},
    {"id": 25, "name": "Lamentations", "name_pt": "Lamentações", "chapters": 5, "file": "Lamentations.txt"},
    {"id": 26, "name": "Ezekiel", "name_pt": "Ezequiel", "chapters": 48, "file": "Ezekiel.txt"},
    {"id": 27, "name": "Daniel", "name_pt": "Daniel", "chapters": 12, "file": "Daniel.txt"},
    
    # Profetas Menores
    {"id": 28, "name": "Hosea", "name_pt": "Oseias", "chapters": 14, "file": "Hosea.txt"},
    {"id": 29, "name": "Joel", "name_pt": "Joel", "chapters": 3, "file": "Joel.txt"},
    {"id": 30, "name": "Amos", "name_pt": "Amós", "chapters": 9, "file": "Amos.txt"},
    {"id": 31, "name": "Obadiah", "name_pt": "Obadias", "chapters": 1, "file": "Obadiah.txt"},
    {"id": 32, "name": "Jonah", "name_pt": "Jonas", "chapters": 4, "file": "Jonah.txt"},
    {"id": 33, "name": "Micah", "name_pt": "Miqueias", "chapters": 7, "file": "Micah.txt"},
    {"id": 34, "name": "Nahum", "name_pt": "Naum", "chapters": 3, "file": "Nahum.txt"},
    {"id": 35, "name": "Habakkuk", "name_pt": "Habacuque", "chapters": 3, "file": "Habakkuk.txt"},
    {"id": 36, "name": "Zephaniah", "name_pt": "Sofonias", "chapters": 3, "file": "Zephaniah.txt"},
    {"id": 37, "name": "Haggai", "name_pt": "Ageu", "chapters": 2, "file": "Haggai.txt"},
    {"id": 38, "name": "Zechariah", "name_pt": "Zacarias", "chapters": 14, "file": "Zechariah.txt"},
    {"id": 39, "name": "Malachi", "name_pt": "Malaquias", "chapters": 4, "file": "Malachi.txt"},
]


# ============================================================================
# ESTRUTURAS DE DADOS
# ============================================================================

@dataclass
class HebrewWord:
    """Palavra hebraica com análise"""
    position: int
    text: str
    text_clean: str  # Sem cantilação
    translation: str = ""
    transliteration: str = ""
    strong: str = ""
    morphology: str = ""


@dataclass
class Verse:
    """Versículo completo"""
    chapter: int
    verse: int
    hebrew_text: str
    hebrew_words: List[str] = field(default_factory=list)
    literal_translation: str = ""
    readable_translation: str = ""
    words: List[Dict] = field(default_factory=list)


# ============================================================================
# CARREGAMENTO DO GLOSSÁRIO
# ============================================================================

def load_hebrew_glossary() -> Dict[str, str]:
    """Carrega o glossário hebraico-português"""
    glossary_path = Path(__file__).parent / "glossary" / "hebrew_glossary.json"
    
    if not glossary_path.exists():
        print(f"⚠️ Glossário não encontrado: {glossary_path}")
        return {}
    
    with open(glossary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


HEBREW_GLOSSARY = load_hebrew_glossary()


# ============================================================================
# PROCESSAMENTO DO TEXTO HEBRAICO
# ============================================================================

def remove_cantillation(text: str) -> str:
    """Remove marcas de cantilação e acentos massoréticos"""
    # Cantilação: U+0591-U+05AF
    # Pontuação: U+05B0-U+05BD, U+05BF, U+05C1-U+05C2, U+05C4-U+05C5, U+05C7
    result = []
    for char in text:
        code = ord(char)
        # Manter apenas consoantes (U+05D0-U+05EA) e vogais essenciais
        if code < 0x0591 or code > 0x05C7:
            result.append(char)
        elif 0x05B0 <= code <= 0x05BC:  # Manter vogais
            result.append(char)
    return ''.join(result)


def clean_hebrew_word(word: str) -> str:
    """Limpa palavra hebraica para busca no glossário"""
    # Remover pontuação
    cleaned = word.strip('׃.,;:!?־–—')
    # Remover cantilação para comparação
    cleaned = remove_cantillation(cleaned)
    # Normalizar Unicode
    cleaned = unicodedata.normalize('NFC', cleaned)
    return cleaned


def parse_wlc_line(line: str) -> Optional[Tuple[int, int, str]]:
    """
    Faz parse de uma linha do WLC
    Formato: ‫ VERSE  ׃CHAPTER   TEXTO_HEBRAICO ‬
    Retorna: (chapter, verse, hebrew_text) ou None se for linha de metadados
    """
    # Remover marcadores Unicode RTL/LTR
    line = line.strip()
    line = line.replace('\u202a', '').replace('\u202b', '').replace('\u202c', '')
    line = line.replace('\u200f', '').replace('\u200e', '')
    
    # Ignorar linhas de metadados
    if line.startswith('xxxx') or not line:
        return None
    
    # Padrão: número versículo, ׃, número capítulo, texto
    # Exemplo: ‫ 1  ׃1   בְּרֵאשִׁית בָּרָא...
    
    # Extrair números
    match = re.search(r'(\d+)\s*׃\s*(\d+)\s+(.*?)(?:׃|פ|ס)?\s*$', line)
    if match:
        verse = int(match.group(1))
        chapter = int(match.group(2))
        text = match.group(3).strip()
        return (chapter, verse, text)
    
    return None


def load_wlc_book(filepath: Path) -> Dict[int, List[Verse]]:
    """Carrega um livro do WLC e organiza por capítulo"""
    chapters = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_wlc_line(line)
            if parsed:
                chapter, verse_num, hebrew_text = parsed
                
                if chapter not in chapters:
                    chapters[chapter] = []
                
                # Separar palavras
                words = hebrew_text.split()
                
                verse = Verse(
                    chapter=chapter,
                    verse=verse_num,
                    hebrew_text=hebrew_text,
                    hebrew_words=words
                )
                chapters[chapter].append(verse)
    
    return chapters


# ============================================================================
# TRADUÇÃO
# ============================================================================

def translate_word(word: str, glossary: Dict[str, str]) -> str:
    """Traduz uma palavra hebraica usando o glossário"""
    cleaned = clean_hebrew_word(word)
    
    # Busca direta
    if cleaned in glossary:
        return glossary[cleaned]
    
    # Busca sem vogais
    consonants_only = ''.join(c for c in cleaned if ord(c) >= 0x05D0 and ord(c) <= 0x05EA)
    if consonants_only in glossary:
        return glossary[consonants_only]
    
    # Retornar original entre colchetes se não encontrado
    return f"[{word}]"


def translate_verse(verse: Verse, glossary: Dict[str, str]) -> Verse:
    """Traduz um versículo completo"""
    translations = []
    word_data = []
    
    for i, word in enumerate(verse.hebrew_words):
        translation = translate_word(word, glossary)
        translations.append(translation)
        
        word_data.append({
            "position": i + 1,
            "hebrew": word,
            "hebrew_clean": clean_hebrew_word(word),
            "translation": translation
        })
    
    verse.literal_translation = " ".join(translations)
    verse.readable_translation = verse.literal_translation  # Por enquanto igual
    verse.words = word_data
    
    return verse


def translate_chapter(chapter_verses: List[Verse], glossary: Dict[str, str]) -> List[Dict]:
    """Traduz um capítulo inteiro"""
    translated = []
    
    for verse in chapter_verses:
        translated_verse = translate_verse(verse, glossary)
        translated.append({
            "chapter": translated_verse.chapter,
            "verse": translated_verse.verse,
            "hebrew_text": translated_verse.hebrew_text,
            "literal_translation": translated_verse.literal_translation,
            "readable_translation": translated_verse.readable_translation,
            "words": translated_verse.words
        })
    
    return translated


# ============================================================================
# GERAÇÃO DE ARQUIVOS
# ============================================================================

def save_book_json(book_info: Dict, chapters_data: Dict[int, List[Dict]], output_dir: Path):
    """Salva livro completo em JSON"""
    book_data = {
        "book_id": book_info["id"],
        "book": book_info["name"],
        "book_pt": book_info["name_pt"],
        "testament": "OT",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA",
        "source": "Westminster Leningrad Codex (WLC)",
        "total_chapters": book_info["chapters"],
        "chapters": []
    }
    
    for chapter_num in sorted(chapters_data.keys()):
        chapter_verses = chapters_data[chapter_num]
        book_data["chapters"].append({
            "chapter": chapter_num,
            "verses": chapter_verses
        })
    
    # Salvar arquivo do livro completo
    output_file = output_dir / f"{book_info['name']}_Complete.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def save_chapter_json(book_info: Dict, chapter_num: int, verses: List[Dict], output_dir: Path):
    """Salva capítulo individual em JSON"""
    chapter_data = {
        "book": book_info["name"],
        "book_pt": book_info["name_pt"],
        "testament": "OT",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA",
        "source": "Westminster Leningrad Codex (WLC)",
        "chapter": chapter_num,
        "verses": verses
    }
    
    output_file = output_dir / f"{book_info['name']}_Chapter_{chapter_num:02d}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    return output_file


# ============================================================================
# PROCESSO PRINCIPAL
# ============================================================================

def translate_book(book_id: int, save_chapters: bool = True):
    """Traduz um livro específico do AT"""
    # Encontrar informações do livro
    book_info = None
    for book in OT_BOOKS:
        if book["id"] == book_id:
            book_info = book
            break
    
    if not book_info:
        print(f"❌ Livro não encontrado: ID {book_id}")
        return
    
    print("=" * 70)
    print(f"📖 Traduzindo: {book_info['name_pt']} ({book_info['name']})")
    print("=" * 70)
    print()
    
    # Caminhos
    source_file = Path(__file__).parent.parent / "sources" / "hebrew_wlc" / "TextFiles" / book_info["file"]
    output_dir = Path(__file__).parent / "OT"
    output_dir.mkdir(exist_ok=True)
    
    if not source_file.exists():
        print(f"❌ Arquivo não encontrado: {source_file}")
        return
    
    # Carregar glossário
    glossary = HEBREW_GLOSSARY
    print(f"📚 Glossário carregado: {len(glossary)} termos")
    
    # Carregar e processar livro
    print(f"📖 Carregando: {source_file.name}")
    chapters = load_wlc_book(source_file)
    total_verses = sum(len(v) for v in chapters.values())
    print(f"✓ {len(chapters)} capítulos, {total_verses} versículos")
    print()
    
    # Traduzir cada capítulo
    translated_chapters = {}
    for chapter_num in sorted(chapters.keys()):
        chapter_verses = chapters[chapter_num]
        translated = translate_chapter(chapter_verses, glossary)
        translated_chapters[chapter_num] = translated
        
        if save_chapters:
            save_chapter_json(book_info, chapter_num, translated, output_dir)
        
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


def translate_all_ot():
    """Traduz todos os 39 livros do Antigo Testamento"""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + "BÍBLIA BELEM AnC — TRADUÇÃO DO ANTIGO TESTAMENTO".center(68) + "║")
    print("║" + "Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    completed = []
    failed = []
    
    for book in OT_BOOKS:
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
    print("║" + "RESUMO DA TRADUÇÃO".center(68) + "║")
    print("╠" + "═" * 68 + "╣")
    print(f"║  ✅ Livros traduzidos: {len(completed)}/39".ljust(69) + "║")
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
            translate_all_ot()
        elif arg.isdigit():
            book_id = int(arg)
            translate_book(book_id)
        elif arg == "--list":
            print("Livros do Antigo Testamento:")
            for book in OT_BOOKS:
                print(f"  {book['id']:2d}. {book['name_pt']} ({book['name']}) - {book['chapters']} caps")
        else:
            print(f"Uso: python {sys.argv[0]} [BOOK_ID | --all | --list]")
            print("  BOOK_ID: ID do livro (1-39)")
            print("  --all: Traduzir todos os 39 livros")
            print("  --list: Listar todos os livros")
    else:
        # Default: traduzir Gênesis
        translate_book(1)


if __name__ == "__main__":
    main()
