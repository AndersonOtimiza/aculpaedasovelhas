#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Belem Bible AnC - Tradução de Apocalipse (Revelação)
Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)
Autor: Anderson Belem Costa (Belem, AnC)
"""

import json
import re
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, asdict


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


from glossary_manager import GREEK_GLOSSARY


import csv

def parse_nestle_line(row: Dict[str, str]) -> GreekWord:
    """Parse uma linha do formato Nestle1904 CSV"""
    bcv = row['BCV']
    parts = bcv.split()
    book_code = parts[0]
    
    # Filtrar apenas Apocalipse (Rev)
    if book_code != "Rev":
        return None
    
    chapter_verse = parts[1].split(':')
    chapter = int(chapter_verse[0])
    verse = int(chapter_verse[1])
    
    return GreekWord(
        position=0,  # Será calculado depois
        book_code=book_code,
        chapter=chapter,
        verse=verse,
        parse=row['func_morph'],
        text_surface=row['text'],
        text_normalized=row['normalized'],
        text_lemma=row['lemma'],
        lemma=row['lemma'],
        strong=row['strongs']
    )


def load_nestle_file(filepath: str) -> Dict[int, List[GreekWord]]:
    """Carrega arquivo Nestle1904 e organiza por versículo"""
    verses = {}
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            word = parse_nestle_line(row)
            if word:
                verse_key = (word.chapter * 1000) + word.verse
                if verse_key not in verses:
                    verses[verse_key] = []
                verses[verse_key].append(word)
    
    return verses


def translate_word(word: GreekWord) -> str:
    """Traduz palavra grega usando glossário"""
    # Tentar traduzir pela forma normalizada
    if word.text_lemma in GREEK_GLOSSARY:
        return GREEK_GLOSSARY[word.text_lemma]
    
    # Tentar pelo lema
    if word.lemma in GREEK_GLOSSARY:
        return GREEK_GLOSSARY[word.lemma]
    
    # Se não encontrar, retornar transliteração
    return f"[{word.text_surface}]"


def translate_verse(words: List[GreekWord]) -> Dict:
    """Traduz versículo completo (método Ipísis Iliteris)"""
    # Traduzir cada palavra mantendo ordem original
    translations = []
    greek_text = []
    
    for i, word in enumerate(words):
        word.position = i + 1
        word.translation = translate_word(word)
        translations.append(word.translation)
        greek_text.append(word.text_surface)
    
    # Tradução literal (ordem original, sem ajustes)
    literal = " ".join(translations)
    
    # Tradução legível (TEA = ajustes mínimos)
    readable = make_readable_tea(translations, words)
    
    return {
        "chapter": words[0].chapter,
        "verse": words[0].verse,
        "greek_text": " ".join(greek_text),
        "literal_translation": literal,
        "readable_translation": readable,
        "words": [asdict(w) for w in words]
    }


def make_readable_tea(translations: List[str], words: List[GreekWord]) -> str:
    """
    Ajustes mínimos para legibilidade (TEA = Tradução Extremamente Rígida)
    Regras:
    1. Adicionar artigos definidos apenas quando obrigatório em português
    2. Manter ordem original sempre que possível
    3. Ajustar apenas casos de total incompreensão
    """
    # Por enquanto, retornar literal (ajustes serão feitos manualmente)
    return " ".join(translations)


def main():
    """Traduz Apocalipse (Revelação)"""
    print("=" * 70)
    print("Belem Bible AnC - Tradução de Apocalipse (Revelação)")
    print("Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)")
    print("=" * 70)
    print()
    
    # Carregar arquivo fonte
    source_file = Path(__file__).parent.parent / "sources" / "nt_nestle1904" / "Nestle1904-master" / "morph" / "Nestle1904.csv"
    
    if not source_file.exists():
        print(f"❌ Arquivo não encontrado: {source_file}")
        return
    
    print(f"📖 Carregando: {source_file.name}")
    verses_data = load_nestle_file(str(source_file))
    print(f"✓ {len(verses_data)} versículos carregados")
    print()
    
    # Traduzir capítulo 1 (versículos 1-3 como exemplo)
    output_dir = Path(__file__).parent / "NT"
    output_dir.mkdir(exist_ok=True)
    
    revelation_data = {
        "book": "Revelation",
        "book_pt": "Apocalipse (Revelação)",
        "testament": "NT",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA",
        "source": "Nestle 1904 Greek New Testament",
        "chapters": []
    }
    
    # Processar capítulo 1
    chapter_1 = {
        "chapter": 1,
        "verses": []
    }
    
    for verse_num in range(1, 4):  # Versículos 1-3
        verse_key = 1000 + verse_num
        if verse_key in verses_data:
            words = verses_data[verse_key]
            verse_translation = translate_verse(words)
            chapter_1["verses"].append(verse_translation)
            
            print(f"Apocalipse 1:{verse_num}")
            print(f"Grego: {verse_translation['greek_text']}")
            print(f"Literal: {verse_translation['literal_translation']}")
            print(f"Legível (TEA): {verse_translation['readable_translation']}")
            print()
    
    revelation_data["chapters"].append(chapter_1)
    
    # Salvar JSON
    output_file = output_dir / "Revelation_Chapter_01.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(revelation_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Salvo em: {output_file}")
    print()
    print("=" * 70)
    print("Tradução de Apocalipse 1:1-3 concluída!")
    print("Método Ipísis Iliteris: palavra-por-palavra, ordem original preservada")
    print("=" * 70)


if __name__ == "__main__":
    main()
