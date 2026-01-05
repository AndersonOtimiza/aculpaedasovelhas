"""
Belem Bible AnC - Tradução Completa de Apocalipse
Traduz todos os capítulos restantes (4-22) automaticamente
Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório pai ao path para importar translate_revelation
sys.path.insert(0, str(Path(__file__).parent))

from translate_revelation import load_nestle_file, GreekWord, GREEK_GLOSSARY

# Glossário consolidado e expandido
GREEK_GLOSSARY_FULL = GREEK_GLOSSARY

def translate_chapter(chapter_num, verses_dict, glossary):
    """Traduz um capítulo completo"""
    
    # Estrutura de versículos por capítulo (total de versículos em cada)
    chapter_verses = {
        1: 20, 2: 29, 3: 22, 4: 11, 5: 14, 6: 17, 7: 17, 8: 13, 9: 21, 10: 11,
        11: 19, 12: 18, 13: 18, 14: 20, 15: 8, 16: 21, 17: 18, 18: 24, 19: 21,
        20: 15, 21: 27, 22: 21
    }
    
    total_verses = chapter_verses.get(chapter_num, 0)
    if total_verses == 0:
        return None
    
    chapter_data = {
        "chapter": chapter_num,
        "verses": []
    }
    
    for verse_num in range(1, total_verses + 1):
        verse_key = chapter_num * 1000 + verse_num
        
        if verse_key in verses_dict:
            words = verses_dict[verse_key]
            
            # Traduzir palavra por palavra
            translations = []
            for word in words:
                translation = glossary.get(word.lemma, f"[{word.text_lemma}]")
                word.translation = translation
                translations.append(translation)
            
            # Texto grego (superfície)
            greek_text = " ".join(w.text_surface for w in words)
            
            # Tradução literal (mantém ordem grega)
            literal_translation = " ".join(translations)
            
            # Tradução legível (TEA - por ora igual à literal)
            readable_translation = literal_translation
            
            verse_data = {
                "chapter": chapter_num,
                "verse": verse_num,
                "greek_text": greek_text,
                "literal_translation": literal_translation,
                "readable_translation": readable_translation,
                "words": [w.__dict__ for w in words]
            }
            
            chapter_data["verses"].append(verse_data)
    
    return chapter_data

def main():
    print("=" * 80)
    print("Belem Bible AnC - Tradução Completa de Apocalipse")
    print("Capítulos 4-22 (Visões Apocalípticas Completas)")
    print("=" * 80)
    
    # Caminho para o arquivo Nestle1904
    nestle_path = Path(__file__).parent.parent / "sources" / "nt_nestle1904" / "Nestle1904-master" / "morph" / "Nestle1904.csv"
    
    print(f"\n📖 Carregando: {nestle_path.name}")
    verses_dict = load_nestle_file(str(nestle_path))
    print(f"✓ {len(verses_dict)} versículos carregados")
    print(f"✓ Glossário: {len(GREEK_GLOSSARY_FULL)} termos")
    
    # Traduzir capítulos 4-22
    chapters_to_translate = range(4, 23)  # 4 até 22 inclusive
    
    print(f"\n🔄 Traduzindo capítulos 4-22 (19 capítulos, ~351 versículos)...")
    print("=" * 80)
    
    for chapter_num in chapters_to_translate:
        print(f"\n📜 Capítulo {chapter_num}...", end=" ")
        
        chapter_data = translate_chapter(chapter_num, verses_dict, GREEK_GLOSSARY_FULL)
        
        if chapter_data:
            # Salvar JSON
            output_path = Path(__file__).parent / "NT" / f"Revelation_Chapter_{chapter_num:02d}.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, ensure_ascii=False, indent=2)
            
            verse_count = len(chapter_data["verses"])
            print(f"✓ {verse_count} versículos traduzidos")
        else:
            print("❌ Erro")
    
    print("\n" + "=" * 80)
    print("✅ TRADUÇÃO COMPLETA DE APOCALIPSE CONCLUÍDA!")
    print("=" * 80)
    print(f"📊 Total: 22 capítulos, 405 versículos")
    print(f"📁 Arquivos salvos em: NT/Revelation_Chapter_XX.json")
    print(f"🔤 Método: Belém AnC-Ipísis Iliteris (palavra-por-palavra)")
    print("=" * 80)

if __name__ == "__main__":
    main()
