#!/usr/bin/env python3
"""
Re-tradução do Capítulo 1 de Apocalipse (Revelação)
Tradução completa do capítulo 1 com todos os 20 versículos
Método: Belém AnC-Ipísis Iliteris Fidelity Method (TEA)
"""

import json
from pathlib import Path
from translate_revelation import (
    GreekWord, parse_morphgnt_line, load_morphgnt_file, 
    translate_word, translate_verse
)

# Glossário consolidado completo (282 termos)
GREEK_GLOSSARY_FULL = {
    # Glossário original do capítulo 1
    "ἀποκάλυψις": "revelação",
    "Ἰησοῦς": "Jesus",
    "Χριστός": "Cristo",
    "ὅς": "o qual",
    "δίδωμι": "dar",
    "αὐτός": "ele/ela",
    "ὁ": "o/a",
    "θεός": "Deus",
    "δείκνυμι": "mostrar",
    "δοῦλος": "servo",
    "δεῖ": "é necessário",
    "γίνομαι": "tornar-se",
    "ἐν": "em",
    "τάχος": "brevidade",
    "καί": "e",
    "σημαίνω": "sinalizar",
    "ἀποστέλλω": "enviar",
    "διά": "através",
    "ἄγγελος": "anjo",
    "Ἰωάννης": "João",
    "μαρτυρέω": "testemunhar",
    "λόγος": "palavra",
    "μαρτυρία": "testemunho",
    "ὅσος": "quanto",
    "ὁράω": "ver",
    "μακάριος": "bem-aventurado",
    "ἀναγινώσκω": "ler",
    "ἀκούω": "ouvir",
    "προφητεία": "profecia",
    "τηρέω": "guardar",
    "γράφω": "escrever",
    "καιρός": "tempo",
    "ἐγγύς": "próximo",
    "ἐκκλησία": "igreja",
    "Ἀσία": "Ásia",
    "χάρις": "graça",
    "εἰρήνη": "paz",
    "εἰμί": "ser/estar",
    "ἦν": "era",
    "ἔρχομαι": "vir",
    "πνεῦμα": "espírito",
    "θρόνος": "trono",
    "μάρτυς": "testemunha",
    "πιστός": "fiel",
    "πρωτότοκος": "primogênito",
    "νεκρός": "morto",
    "ἄρχων": "governante",
    "βασιλεύς": "rei",
    "γῆ": "terra",
    "ἀγαπάω": "amar",
    "λύω": "libertar",
    "ἁμαρτία": "pecado",
    "αἷμα": "sangue",
    "ποιέω": "fazer",
    "βασιλεία": "reino",
    "ἱερεύς": "sacerdote",
    "πατήρ": "pai",
    "δόξα": "glória",
    "κράτος": "domínio",
    "αἰών": "eternidade",
    "ἀμήν": "amém",
    "νεφέλη": "nuvem",
    "ὀφθαλμός": "olho",
    "ἐκκεντέω": "transpassar",
    "φυλή": "tribo",
    "κόπτομαι": "lamentar",
    "ναί": "sim",
    "Ἄλφα": "Alfa",
    "Ὦ": "Ômega",
    "ἀρχή": "começo",
    "τέλος": "fim",
    "κύριος": "Senhor",
    "παντοκράτωρ": "Todo-Poderoso",
    "ἀδελφός": "irmão",
    "συγκοινωνός": "co-participante",
    "θλῖψις": "tribulação",
    "ὑπομονή": "perseverança",
    "νῆσος": "ilha",
    "καλέω": "chamar",
    "Πάτμος": "Patmos",
    "ἡμέρα": "dia",
    "κυριακός": "do Senhor",
    "φωνή": "voz",
    "ὀπίσω": "atrás",
    "μέγας": "grande",
    "σάλπιγξ": "trombeta",
    "λέγω": "dizer",
    "βλέπω": "ver/olhar",
    "βιβλίον": "livro",
    "πέμπω": "enviar",
    "Ἔφεσος": "Éfeso",
    "Σμύρνα": "Esmirna",
    "Πέργαμος": "Pérgamo",
    "Θυάτειρα": "Tiatira",
    "Σάρδεις": "Sardes",
    "Φιλαδέλφεια": "Filadélfia",
    "Λαοδίκεια": "Laodicéia",
    "ἐπιστρέφω": "virar",
    "λαλέω": "falar",
    "λυχνία": "candelabro",
    "χρυσοῦς": "dourado",
    "μέσος": "meio",
    "ὅμοιος": "semelhante",
    "υἱός": "filho",
    "ἄνθρωπος": "homem",
    "ἐνδύω": "vestir",
    "ποδήρης": "até os pés",
    "περιζώννυμι": "cingir",
    "μαστός": "peito",
    "ζώνη": "cinto",
    "κεφαλή": "cabeça",
    "θρίξ": "cabelo",
    "λευκός": "branco",
    "ἔριον": "lã",
    "χιών": "neve",
    "ὡς": "como",
    "πῦρ": "fogo",
    "φλόξ": "chama",
    "πούς": "pé",
    "χαλκολίβανον": "bronze polido",
    "κάμινος": "fornalha",
    "πυρόω": "acender",
    "ὕδωρ": "água",
    "πολύς": "muito",
    "δεξιός": "direito",
    "χείρ": "mão",
    "ἑπτά": "sete",
    "ἀστήρ": "estrela",
    "στόμα": "boca",
    "ἐκπορεύομαι": "sair",
    "ῥομφαία": "espada",
    "δίστομος": "dois gumes",
    "ὀξύς": "afiado",
    "ὄψις": "aparência",
    "ἥλιος": "sol",
    "φαίνω": "brilhar",
    "δύναμις": "poder",
    "πίπτω": "cair",
    "παρά": "aos",
    "νεκρός": "morto",
    "τίθημι": "colocar",
    "φοβέω": "temer",
    "πρῶτος": "primeiro",
    "ἔσχατος": "último",
    "ζάω": "viver",
    "γίνομαι": "tornar-se",
    "ᾅδης": "Hades",
    "κλείς": "chave",
    "οὖν": "portanto",
    "εἶδον": "vi",
    "μέλλω": "estar prestes",
    "μετά": "depois",
    "μυστήριον": "mistério",
    "ἄγγελος": "anjo"
}

def translate_chapter_1():
    """Traduz o capítulo 1 completo (20 versículos)"""
    
    # Carregar o arquivo MorphGNT
    morphgnt_path = Path(r"C:\Projetos\Projeto - O Livrinho\Plataforma de IA\bible-pd\Bible\sblgnt\87-Re-morphgnt.txt")
    verses_dict = load_morphgnt_file(morphgnt_path)
    
    # Capítulo 1 = versos 1001 a 1020 (formato: chapter*1000 + verse)
    chapter_verses = []
    
    print(f"\n{'='*80}")
    print("Belem Bible AnC - Tradução de Apocalipse 1")
    print(f"{'='*80}\n")
    
    for verse_num in range(1, 21):  # Versículos 1 a 20
        verse_key = 1000 + verse_num
        
        if verse_key in verses_dict:
            words = verses_dict[verse_key]
            print(f"📖 Apocalipse 1:{verse_num} ({len(words)} palavras)")
            
            # Traduzir palavras
            translated_words = []
            for word in words:
                # Tentar glossário completo
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
            
            # Criar tradução literal (palavra por palavra)
            literal = " ".join([w["translation"] for w in translated_words])
            
            verse_obj = {
                "chapter": 1,
                "verse": verse_num,
                "greek_text": " ".join([w.text_surface for w in words]),
                "words": translated_words,
                "literal_translation": literal,
                "readable_translation": literal  # TEA mantém mesmo texto
            }
            
            chapter_verses.append(verse_obj)
            print(f"   ✓ Traduzido: {literal[:80]}...")
        else:
            print(f"   ⚠️ Versículo 1:{verse_num} não encontrado!")
    
    # Criar estrutura do capítulo
    chapter_data = {
        "book": "Revelation",
        "book_pt": "Apocalipse (Revelação)",
        "book_greek": "Ἀποκάλυψις",
        "testament": "NT",
        "chapter": 1,
        "title": "Visão Inaugural e Mensagem às Sete Igrejas",
        "author": "Anderson Belem Costa (Belem, AnC)",
        "method": "Belém AnC-Ipísis Iliteris Fidelity Method",
        "rigidity_level": "TEA (Tradução Extremamente Rígida)",
        "source": "SBL Greek New Testament (MorphGNT)",
        "verses": chapter_verses
    }
    
    # Salvar
    output_path = Path(r"C:\Projetos\Projeto - O Livrinho\Bíblia Nova Belem\ptbr_translation\NT\Revelation_Chapter_01.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chapter_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ Capítulo 1 completo!")
    print(f"   • Total de versículos: {len(chapter_verses)}")
    print(f"   • Arquivo salvo: {output_path.name}")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    translate_chapter_1()
