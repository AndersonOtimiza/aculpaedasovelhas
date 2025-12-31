#!/usr/bin/env python3
"""
Re-tradução do Capítulo 12 de Apocalipse
Corrigindo contagem: deve ter 18 versículos, não 17
"""

import json
from pathlib import Path
from translate_revelation import load_morphgnt_file, GreekWord

# Glossário completo
from translate_all_revelation import GREEK_GLOSSARY_FULL

def translate_chapter_12():
    """Re-traduz capítulo 12 com todos os 18 versículos"""
    
    morphgnt_path = Path(r"C:\Projetos\Projeto - O Livrinho\Plataforma de IA\bible-pd\Bible\sblgnt\87-Re-morphgnt.txt")
    verses_dict = load_morphgnt_file(morphgnt_path)
    
    chapter_verses = []
    
    print(f"\n{'='*80}")
    print("Re-traduzindo Apocalipse 12 (18 versículos)")
    print(f"{'='*80}\n")
    
    for verse_num in range(1, 19):  # 1 a 18
        verse_key = 12000 + verse_num
        
        if verse_key in verses_dict:
            words = verses_dict[verse_key]
            print(f"📖 Apocalipse 12:{verse_num} ({len(words)} palavras)")
            
            # Traduzir palavras
            translated_words = []
            for word in words:
                translation = None
                if word.text_lemma in GREEK_GLOSSARY_FULL:
                    translation = GREEK_GLOSSARY_FULL[word.text_lemma]
                elif word.lemma in GREEK_GLOSSARY_FULL:
                    translation = GREEK_GLOSSARY_FULL[word.lemma]
                else:
                    translation = f"[{word.text_surface}]"
                
                translated_words.append({
                    "original": word.text_normalized,
                    "lemma": word.text_lemma,
                    "morphology": word.parse,
                    "translation": translation
                })
            
            # Tradução literal
            literal = " ".join([w["translation"] for w in translated_words])
            
            verse_obj = {
                "chapter": 12,
                "verse": verse_num,
                "greek_text": " ".join([w.text_surface for w in words]),
                "words": translated_words,
                "literal_translation": literal,
                "readable_translation": literal
            }
            
            chapter_verses.append(verse_obj)
            print(f"   ✓ {literal[:60]}...")
    
    # Estrutura do capítulo
    chapter_data = {
        "book": "Revelation",
        "book_pt": "Apocalipse (Revelação)",
        "book_greek": "Ἀποκάλυψις",
        "testament": "NT",
        "chapter": 12,
        "title": "A Mulher e o Dragão",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA (Tradução Extremamente Rígida)",
        "source": "SBL Greek New Testament (MorphGNT)",
        "verses": chapter_verses
    }
    
    # Salvar
    output_path = Path(r"C:\Projetos\Projeto - O Livrinho\Bíblia Nova Belem\ptbr_translation\NT\Revelation_Chapter_12.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ Capítulo 12 re-traduzido!")
    print(f"   • Total de versículos: {len(chapter_verses)}")
    print(f"   • Arquivo: {output_path.name}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    translate_chapter_12()
