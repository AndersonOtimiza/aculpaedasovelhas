"""
Belem Bible AnC - Consolidador de Apocalipse
Consolida todos os 22 capítulos em um único arquivo JSON master
"""

import json
from pathlib import Path

def consolidate_revelation():
    """Consolida todos os capítulos de Apocalipse em um único JSON"""
    
    print("=" * 80)
    print("Belem Bible AnC - Consolidação de Apocalipse")
    print("=" * 80)
    
    base_path = Path(__file__).parent / "NT"
    
    # Estrutura do livro completo
    revelation_complete = {
        "book": "Revelation",
        "book_pt": "Apocalipse (Revelação)",
        "book_greek": "Ἀποκάλυψις",
        "testament": "NT",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA (Tradução Extremamente Rígida)",
        "description": "Palavra-por-palavra, ordem original preservada",
        "source": "SBL Greek New Testament (MorphGNT)",
        "date_translated": "6 de dezembro de 2025",
        "total_chapters": 22,
        "total_verses": 405,
        "glossary_terms": 282,
        "chapters": []
    }
    
    print(f"\n📚 Consolidando 22 capítulos...")
    
    total_verses = 0
    
    for chapter_num in range(1, 23):  # 1 até 22
        json_file = base_path / f"Revelation_Chapter_{chapter_num:02d}.json"
        
        if json_file.exists():
            print(f"  📜 Capítulo {chapter_num:2d}...", end=" ")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                chapter_data = json.load(f)
            
            # Capítulo 1 tem estrutura diferente (array chapters dentro)
            if chapter_num == 1 and "chapters" in chapter_data:
                if len(chapter_data["chapters"]) > 0:
                    verses = chapter_data["chapters"][0].get("verses", [])
                    chapter_data = {
                        "chapter": 1,
                        "verses": verses
                    }
            
            verse_count = len(chapter_data.get("verses", []))
            total_verses += verse_count
            
            # Adiciona título descritivo para cada capítulo
            chapter_titles = {
                1: "Visão Inaugural e Mensagem às Sete Igrejas",
                2: "Cartas a Éfeso, Esmirna, Pérgamo e Tiatira",
                3: "Cartas a Sardes, Filadélfia e Laodiceia",
                4: "O Trono no Céu",
                5: "O Cordeiro e o Livro Selado",
                6: "Os Seis Primeiros Selos",
                7: "Os 144.000 Selados e a Grande Multidão",
                8: "O Sétimo Selo e as Quatro Primeiras Trombetas",
                9: "A Quinta e Sexta Trombetas",
                10: "O Anjo e o Livrinho",
                11: "As Duas Testemunhas e a Sétima Trombeta",
                12: "A Mulher e o Dragão",
                13: "A Besta do Mar e a Besta da Terra",
                14: "O Cordeiro no Monte Sião e os Anjos",
                15: "O Cântico de Moisés e do Cordeiro",
                16: "As Sete Taças da Ira de Deus",
                17: "A Grande Prostituta e a Besta",
                18: "A Queda da Babilônia",
                19: "Aleluia! As Bodas do Cordeiro",
                20: "O Milênio e o Julgamento Final",
                21: "O Novo Céu e a Nova Terra",
                22: "O Rio da Vida e o Epílogo"
            }
            
            chapter_data["title"] = chapter_titles.get(chapter_num, f"Capítulo {chapter_num}")
            revelation_complete["chapters"].append(chapter_data)
            
            print(f"✓ {verse_count} versículos")
        else:
            print(f"  ❌ Capítulo {chapter_num:2d} não encontrado: {json_file}")
    
    # Salvar arquivo consolidado
    output_path = base_path / "Revelation_Complete.json"
    
    print(f"\n💾 Salvando arquivo consolidado...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(revelation_complete, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print("\n" + "=" * 80)
    print("✅ CONSOLIDAÇÃO CONCLUÍDA!")
    print("=" * 80)
    print(f"📊 Estatísticas:")
    print(f"   • Capítulos consolidados: {len(revelation_complete['chapters'])}/22")
    print(f"   • Total de versículos: {total_verses}")
    print(f"   • Termos no glossário: {revelation_complete['glossary_terms']}")
    print(f"   • Tamanho do arquivo: {file_size_mb:.2f} MB")
    print(f"\n📁 Arquivo salvo em:")
    print(f"   {output_path}")
    print("=" * 80)
    
    # Criar também um índice compacto
    create_index(revelation_complete, base_path)

def create_index(revelation_data, base_path):
    """Cria um índice compacto com referências rápidas"""
    
    print(f"\n📑 Criando índice de referências...")
    
    index = {
        "book": "Apocalipse (Ἀποκάλυψις)",
        "total_chapters": revelation_data["total_chapters"],
        "total_verses": revelation_data["total_verses"],
        "chapters_index": []
    }
    
    for chapter in revelation_data["chapters"]:
        chapter_num = chapter.get("chapter", 0)
        verses = chapter.get("verses", [])
        
        chapter_index = {
            "chapter": chapter_num,
            "title": chapter.get("title", ""),
            "verse_count": len(verses),
            "first_verse": verses[0]["greek_text"][:50] + "..." if verses else "",
            "verse_range": f"{chapter_num}:1-{len(verses)}" if verses else f"{chapter_num}:0"
        }
        index["chapters_index"].append(chapter_index)
    
    # Salvar índice
    index_path = base_path / "Revelation_Index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Índice salvo em: {index_path}")

if __name__ == "__main__":
    consolidate_revelation()
