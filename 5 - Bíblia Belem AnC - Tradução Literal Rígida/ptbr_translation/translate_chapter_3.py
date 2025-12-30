"""
Belem Bible AnC - Tradução de Apocalipse Capítulo 3
Cartas às Igrejas: Sardes, Filadélfia, Laodiceia
Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar translate_revelation
sys.path.insert(0, str(Path(__file__).parent))

from translate_revelation import (
    load_nestle_file,
    translate_verse,
    GreekWord,
    GREEK_GLOSSARY
)


def main():
    print("=" * 70)
    print("Belem Bible AnC - Tradução de Apocalipse Capítulo 3")
    print("Cartas às Igrejas: Sardes, Filadélfia, Laodiceia")
    print("=" * 70)
    
    # Caminho para o arquivo Nestle1904
    nestle_path = Path(__file__).parent.parent / "sources" / "nt_nestle1904" / "Nestle1904-master" / "morph" / "Nestle1904.csv"
    
    print(f"📖 Carregando: {nestle_path.name}")
    verses_dict = load_nestle_file(str(nestle_path))
    print(f"✓ {len(verses_dict)} versículos carregados")
    
    # Traduzir capítulo 3 (22 versículos: 3:1-22)
    chapter = 3
    total_verses = 22
    chapter_data = {
        "chapter": chapter,
        "title": "Cartas às Igrejas de Sardes, Filadélfia e Laodiceia",
        "verses": []
    }
    
    print(f"\nTraduzindo Apocalipse {chapter} ({total_verses} versículos)...")
    
    for verse_num in range(1, total_verses + 1):
        verse_key = chapter * 1000 + verse_num
        
        if verse_key in verses_dict:
            words = verses_dict[verse_key]
            
            # Usar função padronizada de tradução
            verse_translation = translate_verse(words)
            
            chapter_data["verses"].append(verse_translation)
            
            # Mostrar apenas primeiros 3 e últimos 3 para não poluir
            if verse_num <= 3 or verse_num >= total_verses - 2:
                print(f"✓ Apocalipse {chapter}:{verse_num}")
                print(f"  Grego: {verse_translation["greek_text"][:80]}...")
                print(f"  Português: {verse_translation["literal_translation"][:80]}...")
    
    # Salvar JSON
    import json
    output_path = Path(__file__).parent / "NT" / f"Revelation_Chapter_{chapter:02d}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Salvo em: {output_path}")
    print(f"\nTradução de Apocalipse {chapter} concluída! ({total_verses} versículos)")
    print("Método Ipísis Iliteris: palavra-por-palavra, ordem original preservada")

if __name__ == "__main__":
    main()

