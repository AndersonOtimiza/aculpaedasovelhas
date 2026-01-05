#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Belem Bible AnC - Tradução de Apocalipse Capítulo 2
Cartas às Sete Igrejas (Éfeso, Esmirna, Pérgamo, Tiatira)
"""

import json
import sys
from pathlib import Path

# Importar do script principal
sys.path.append(str(Path(__file__).parent))
from translate_revelation import (
    load_nestle_file, translate_verse, GreekWord, GREEK_GLOSSARY
)


def main():
    """Traduz Apocalipse Capítulo 2"""
    print("=" * 70)
    print("Belem Bible AnC - Tradução de Apocalipse Capítulo 2")
    print("Cartas às Igrejas: Éfeso, Esmirna, Pérgamo, Tiatira")
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
    
    # Processar capítulo 2 (29 versículos)
    chapter_2 = {
        "chapter": 2,
        "title": "Cartas às Igrejas de Éfeso, Esmirna, Pérgamo e Tiatira",
        "verses": []
    }
    
    print("Traduzindo Apocalipse 2 (29 versículos)...")
    print()
    
    for verse_num in range(1, 30):  # Versículos 1-29
        verse_key = 2000 + verse_num
        if verse_key in verses_data:
            words = verses_data[verse_key]
            verse_translation = translate_verse(words)
            chapter_2["verses"].append(verse_translation)
            
            # Exibir apenas os 3 primeiros e 3 últimos para não poluir
            if verse_num <= 3 or verse_num >= 27:
                print(f"✓ Apocalipse 2:{verse_num}")
                print(f"  Grego: {verse_translation['greek_text'][:80]}...")
                print(f"  Português: {verse_translation['literal_translation'][:80]}...")
                print()
        else:
            print(f"⚠️ Versículo 2:{verse_num} não encontrado")
    
    # Salvar JSON
    output_dir = Path(__file__).parent / "NT"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "Revelation_Chapter_02.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chapter_2, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"✓ Salvo em: {output_file}")
    print()
    print("=" * 70)
    print(f"Tradução de Apocalipse 2 concluída! ({len(chapter_2['verses'])} versículos)")
    print("Método Ipísis Iliteris: palavra-por-palavra, ordem original preservada")
    print("=" * 70)


if __name__ == "__main__":
    main()
