#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Belem Bible AnC - Translation Tools
Ferramentas para Tradução Ipísis Iliteris (Palavra por Palavra)

Método: Belém AnC-Ipísis Iliteris Fidelity Method
Autor: Anderson Belem Costa (Belem, AnC)
Nível: TEA (Tradução Extremamente Rígida)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
from bs4 import BeautifulSoup

# Opcional: se CLTK estiver disponível
try:
    from cltk.alphabet.processes import Alphabet
    from cltk.tokenize.word import WordTokenizer
    CLTK_AVAILABLE = True
except ImportError:
    CLTK_AVAILABLE = False
    print("⚠️ CLTK não disponível. Funcionalidades limitadas.")


@dataclass
class Word:
    """Representa uma palavra no texto fonte"""
    position: int
    original: str
    strong_number: str = ""
    morphology: str = ""
    gloss: str = ""
    translation: str = ""
    notes: str = ""


@dataclass
class Verse:
    """Representa um versículo com tradução palavra-por-palavra"""
    book: str
    chapter: int
    verse: int
    source_text: str
    words: List[Word]
    literal_translation: str = ""
    readable_translation: str = ""
    notes: str = ""


class BelemBibleTranslator:
    """
    Tradutor principal da Belem Bible AnC
    Implementa o método Ipísis Iliteris (palavra-por-palavra)
    """
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            base_path = Path(__file__).parent
        else:
            base_path = Path(base_path)
        
        self.base_path = base_path
        self.ot_path = base_path / "OT"
        self.nt_path = base_path / "NT"
        self.glossary_path = base_path / "glossary"
        self.metadata_path = base_path / "metadata"
        
        # Carregar glossários
        self.hebrew_glossary = self._load_glossary("hebrew_terms.md")
        self.greek_glossary = self._load_glossary("greek_terms.md")
    
    def _load_glossary(self, filename: str) -> Dict[str, str]:
        """Carrega glossário de termos"""
        glossary = {}
        glossary_file = self.glossary_path / filename
        
        if glossary_file.exists():
            with open(glossary_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Parse markdown table (implementação básica)
                # TODO: Implementar parser robusto
        
        return glossary
    
    def parse_wlc_morphhb(self, xml_content: str) -> List[Verse]:
        """
        Parse Westminster Leningrad Codex com morfologia
        Formato: XML com Strong's numbers e morfologia
        """
        soup = BeautifulSoup(xml_content, 'xml')
        verses = []
        
        # TODO: Implementar parser específico WLC
        # Estrutura esperada: <verse><w strong="H1234" morph="...">בראשית</w></verse>
        
        return verses
    
    def parse_westcott_hort(self, text_content: str) -> List[Verse]:
        """
        Parse Westcott-Hort 1881 Greek NT
        """
        verses = []
        
        # TODO: Implementar parser específico WH1881
        
        return verses
    
    def translate_word(self, word: Word, language: str = "hebrew") -> str:
        """
        Traduz palavra individual usando glossário
        Mantém ordem original (ipísis iliteris)
        """
        glossary = self.hebrew_glossary if language == "hebrew" else self.greek_glossary
        
        # Buscar no glossário
        if word.original in glossary:
            return glossary[word.original]
        
        # Se não houver tradução, retornar transliteração
        return f"[{word.original}]"
    
    def translate_verse(self, verse: Verse, language: str = "hebrew") -> Verse:
        """
        Traduz versículo palavra-por-palavra
        Método Ipísis Iliteris: ordem original preservada
        """
        translations = []
        
        for word in verse.words:
            word.translation = self.translate_word(word, language)
            translations.append(word.translation)
        
        # Tradução literal (ordem original, sem ajustes)
        verse.literal_translation = " ".join(translations)
        
        # Tradução legível (TEA = mínimo ajuste, apenas artigos/preposições necessários)
        verse.readable_translation = self._make_readable(translations, language)
        
        return verse
    
    def _make_readable(self, word_translations: List[str], language: str) -> str:
        """
        Ajustes mínimos para tornar texto português legível
        TEA = Tradução Extremamente Rígida: apenas artigos/preposições obrigatórios
        """
        # TODO: Implementar regras mínimas de legibilidade
        # Exemplos:
        # - Adicionar artigos quando obrigatório em português
        # - Ajustar ordem sujeito-verbo apenas se incompreensível
        # - Manter ordem original sempre que possível
        
        return " ".join(word_translations)
    
    def save_verse_json(self, verse: Verse, book_path: Path):
        """Salva versículo em formato JSON estruturado"""
        chapter_file = book_path / f"chapter_{verse.chapter}.json"
        
        # Carregar capítulo existente ou criar novo
        if chapter_file.exists():
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
        else:
            chapter_data = {
                "book": verse.book,
                "chapter": verse.chapter,
                "verses": []
            }
        
        # Adicionar/atualizar versículo
        verse_data = asdict(verse)
        chapter_data["verses"].append(verse_data)
        
        # Salvar
        with open(chapter_file, 'w', encoding='utf-8') as f:
            json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    def save_verse_markdown(self, verse: Verse, book_path: Path):
        """Salva versículo em formato Markdown legível"""
        md_file = book_path / f"{verse.book}.md"
        
        with open(md_file, 'a', encoding='utf-8') as f:
            f.write(f"\n### {verse.chapter}:{verse.verse}\n\n")
            f.write(f"**Texto Fonte:** {verse.source_text}\n\n")
            f.write(f"**Tradução Literal:** {verse.literal_translation}\n\n")
            f.write(f"**Tradução Legível (TEA):** {verse.readable_translation}\n\n")
            
            if verse.notes:
                f.write(f"**Notas:** {verse.notes}\n\n")
            
            # Tabela palavra-por-palavra
            f.write("| Pos | Original | Strong's | Morfologia | Gloss | Tradução | Notas |\n")
            f.write("|-----|----------|----------|------------|-------|----------|-------|\n")
            for word in verse.words:
                f.write(f"| {word.position} | {word.original} | {word.strong_number} | "
                       f"{word.morphology} | {word.gloss} | {word.translation} | {word.notes} |\n")
            f.write("\n---\n\n")
    
    def update_progress(self, book: str, chapter: int, total_verses: int):
        """Atualiza progresso no metadata/translation_info.json"""
        metadata_file = self.metadata_path / "translation_info.json"
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Atualizar livro específico
        if book not in metadata.get("books_completed", {}):
            metadata["books_completed"][book] = {
                "status": "in_progress",
                "chapters_completed": 0,
                "total_chapters": 0,
                "verses_completed": 0
            }
        
        metadata["books_completed"][book]["chapters_completed"] = chapter
        metadata["books_completed"][book]["verses_completed"] += total_verses
        
        # Recalcular progresso geral
        total_books = 66
        completed_books = len([b for b in metadata["books_completed"].values() 
                               if b["status"] == "completed"])
        metadata["progress"]["books_completed"] = completed_books
        metadata["progress"]["percentage"] = (completed_books / total_books) * 100
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)


def main():
    """Exemplo de uso"""
    translator = BelemBibleTranslator()
    
    print("=" * 60)
    print("Belem Bible AnC - Translation Tools")
    print("Belém AnC-Ipísis Iliteris Fidelity Method")
    print("=" * 60)
    print()
    print("Ferramentas carregadas:")
    print(f"✓ Base path: {translator.base_path}")
    print(f"✓ OT path: {translator.ot_path}")
    print(f"✓ NT path: {translator.nt_path}")
    print(f"✓ CLTK disponível: {'Sim' if CLTK_AVAILABLE else 'Não'}")
    print()
    print("Para começar a traduzir:")
    print("1. Prepare arquivos fonte em formatos XML/JSON")
    print("2. Atualize glossários (hebrew_terms.md, greek_terms.md)")
    print("3. Execute: translator.parse_wlc_morphhb(xml_content)")
    print("4. Execute: translator.translate_verse(verse, 'hebrew')")
    print()


if __name__ == "__main__":
    main()
