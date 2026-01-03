-- ============================================================================
-- SCHEMA: Nova Tradução Bíblica Literal Rígida Belem AnC
-- Autor: Belem, Anderson Costa
-- Descrição: Banco de dados para textos bíblicos originais (HE, ARM, GRC)
--            com tradução literal PT-BR e camadas de normalização assistida
-- ============================================================================

-- Extensão para UUID (opcional, para IDs únicos)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABELA: text_sources
-- Fontes de texto (OSHB, BHSA, SBLGNT, LXX, etc.)
-- ============================================================================
CREATE TABLE IF NOT EXISTS text_sources (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    license_name VARCHAR(100),
    website_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inserir fontes padrão
INSERT INTO text_sources (code, name, description, license_name, website_url) VALUES
    ('OSHB', 'Open Scriptures Hebrew Bible', 'Texto hebraico do Antigo Testamento com morfologia', 'CC BY 4.0', 'https://github.com/openscriptures/morphhb'),
    ('BHSA', 'ETCBC Hebrew (BHSA)', 'Biblia Hebraica Stuttgartensia Amstelodamensis', 'CC BY-NC 4.0', 'https://github.com/ETCBC/bhsa'),
    ('BHSA-ARM', 'ETCBC Aramaic (BHSA)', 'Porções aramaicas do AT com morfologia ETCBC', 'CC BY-NC 4.0', 'https://github.com/ETCBC/bhsa'),
    ('SBLGNT', 'SBL Greek New Testament', 'Texto grego do Novo Testamento', 'CC BY 4.0', 'https://github.com/LogosBible/SBLGNT'),
    ('LXX', 'Septuaginta', 'Tradução grega do Antigo Testamento', 'Public Domain', NULL)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- TABELA: books
-- Livros bíblicos com metadados
-- ============================================================================
CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    canon_order SMALLINT NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    name_original VARCHAR(100) NOT NULL,
    name_pt VARCHAR(100) NOT NULL,
    testament VARCHAR(10) NOT NULL CHECK (testament IN ('AT', 'NT', 'LXX')),
    trad_group VARCHAR(20) NOT NULL CHECK (trad_group IN ('HEB_TM', 'ARM_TM', 'GRC_NT', 'GRC_LXX')),
    chapters_count SMALLINT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_books_testament ON books(testament);
CREATE INDEX IF NOT EXISTS idx_books_trad_group ON books(trad_group);

-- ============================================================================
-- TABELA: verses
-- Versículos bíblicos
-- ============================================================================
CREATE TABLE IF NOT EXISTS verses (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    chapter SMALLINT NOT NULL,
    verse SMALLINT NOT NULL,
    canonical_ref VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(book_id, chapter, verse)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses(book_id, chapter);
CREATE INDEX IF NOT EXISTS idx_verses_canonical_ref ON verses(canonical_ref);

-- ============================================================================
-- TABELA: tokens
-- Palavras/tokens do texto original com tradução literal
-- IMPORTANTE: script pode ser 'HE' (Hebraico), 'ARM' (Aramaico), 'GRC' (Grego)
-- ============================================================================
CREATE TABLE IF NOT EXISTS tokens (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL REFERENCES verses(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES text_sources(id) ON DELETE CASCADE,
    position SMALLINT NOT NULL,
    text_utf8 VARCHAR(100) NOT NULL,
    script VARCHAR(10) NOT NULL CHECK (script IN ('HE', 'ARM', 'GRC')),
    normalized VARCHAR(100),
    -- TRADUÇÃO LITERAL RÍGIDA (Camada A)
    pt_literal VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(verse_id, source_id, position)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_tokens_verse ON tokens(verse_id);
CREATE INDEX IF NOT EXISTS idx_tokens_source ON tokens(source_id);
CREATE INDEX IF NOT EXISTS idx_tokens_script ON tokens(script);
CREATE INDEX IF NOT EXISTS idx_tokens_normalized ON tokens(normalized);
CREATE INDEX IF NOT EXISTS idx_tokens_pt_literal ON tokens(pt_literal);

-- ============================================================================
-- TABELA: verse_translations
-- Traduções consolidadas por versículo (camada de leitura)
-- ============================================================================
CREATE TABLE IF NOT EXISTS verse_translations (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL REFERENCES verses(id) ON DELETE CASCADE,
    layer VARCHAR(10) NOT NULL DEFAULT 'N0',
    literal_pt TEXT,
    readable_pt TEXT,
    translator VARCHAR(100),
    method VARCHAR(150),
    rigidity_level VARCHAR(50),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(verse_id, layer)
);

CREATE INDEX IF NOT EXISTS idx_verse_translations_verse ON verse_translations(verse_id);
CREATE INDEX IF NOT EXISTS idx_verse_translations_layer ON verse_translations(layer);

-- ============================================================================
-- TABELA: morphology
-- Análise morfológica detalhada de cada token
-- ============================================================================
CREATE TABLE IF NOT EXISTS morphology (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL REFERENCES tokens(id) ON DELETE CASCADE,
    lemma VARCHAR(100),
    strong_number VARCHAR(20),
    morph_code VARCHAR(50),
    -- Campos decompostos (extraídos do morph_code)
    tense VARCHAR(20),
    voice VARCHAR(20),
    mood VARCHAR(20),
    person VARCHAR(10),
    number VARCHAR(20),
    gender VARCHAR(20),
    case_gram VARCHAR(20),
    state VARCHAR(20),
    -- Extensível via JSONB
    extra_tags JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(token_id)
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_morphology_token ON morphology(token_id);
CREATE INDEX IF NOT EXISTS idx_morphology_lemma ON morphology(lemma);
CREATE INDEX IF NOT EXISTS idx_morphology_strong ON morphology(strong_number);

-- ============================================================================
-- TABELA: glosses
-- Camadas de normalização assistida (Camada B)
-- N1: glossário mínimo
-- N2: marcações morfológicas
-- N3: reordenação de leitura
-- N4: expansão de elipses
-- N5: alternativas lexicais
-- ============================================================================
CREATE TABLE IF NOT EXISTS glosses (
    id SERIAL PRIMARY KEY,
    token_id INTEGER NOT NULL REFERENCES tokens(id) ON DELETE CASCADE,
    layer VARCHAR(10) NOT NULL CHECK (layer IN ('N1', 'N2', 'N3', 'N4', 'N5')),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_glosses_token ON glosses(token_id);
CREATE INDEX IF NOT EXISTS idx_glosses_layer ON glosses(layer);
CREATE INDEX IF NOT EXISTS idx_glosses_token_layer ON glosses(token_id, layer);

-- ============================================================================
-- TABELA: syntax_units
-- Unidades sintáticas (cláusulas, frases)
-- ============================================================================
CREATE TABLE IF NOT EXISTS syntax_units (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL REFERENCES verses(id) ON DELETE CASCADE,
    source_id INTEGER NOT NULL REFERENCES text_sources(id) ON DELETE CASCADE,
    unit_type VARCHAR(20) NOT NULL,
    start_position SMALLINT NOT NULL,
    end_position SMALLINT NOT NULL,
    function VARCHAR(50),
    label VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_syntax_units_verse ON syntax_units(verse_id);

-- ============================================================================
-- TABELA: variants
-- Variantes textuais
-- ============================================================================
CREATE TABLE IF NOT EXISTS variants (
    id SERIAL PRIMARY KEY,
    verse_id INTEGER NOT NULL REFERENCES verses(id) ON DELETE CASCADE,
    position SMALLINT NOT NULL,
    variant_text VARCHAR(200) NOT NULL,
    witnesses TEXT[],
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_variants_verse ON variants(verse_id);

-- ============================================================================
-- TABELA: manuscripts
-- Metadados de manuscritos
-- ============================================================================
CREATE TABLE IF NOT EXISTS manuscripts (
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    date_range VARCHAR(50),
    location VARCHAR(100),
    description TEXT,
    image_provider VARCHAR(100),
    license_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Inserir manuscritos conhecidos
INSERT INTO manuscripts (code, name, date_range, location, description, image_provider) VALUES
    ('SINAITICUS', 'Codex Sinaiticus', 'séc. IV', 'British Library', 'Um dos mais antigos manuscritos completos da Bíblia grega', 'codexsinaiticus.org'),
    ('VATICANUS', 'Codex Vaticanus', 'séc. IV', 'Biblioteca Vaticana', 'Manuscrito grego do século IV', 'Vatican Library'),
    ('ALEXANDRINUS', 'Codex Alexandrinus', 'séc. V', 'British Library', 'Manuscrito grego do século V', 'British Library'),
    ('LENINGRADENSIS', 'Codex Leningradensis', '1008 d.C.', 'Biblioteca Nacional da Rússia', 'Base do texto massorético moderno', 'Tanach.us'),
    ('ALEPPO', 'Codex de Aleppo', 'c. 930 d.C.', 'Israel Museum', 'Manuscrito massorético mais antigo (parcialmente preservado)', 'Aleppo Codex')
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- TABELA: manuscript_images
-- Links para imagens de manuscritos
-- ============================================================================
CREATE TABLE IF NOT EXISTS manuscript_images (
    id SERIAL PRIMARY KEY,
    manuscript_id INTEGER NOT NULL REFERENCES manuscripts(id) ON DELETE CASCADE,
    book_id INTEGER REFERENCES books(id) ON DELETE SET NULL,
    chapter SMALLINT,
    verse SMALLINT,
    image_url VARCHAR(500) NOT NULL,
    viewer_url VARCHAR(500),
    folio VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_manuscript_images_manuscript ON manuscript_images(manuscript_id);
CREATE INDEX IF NOT EXISTS idx_manuscript_images_book ON manuscript_images(book_id);

-- ============================================================================
-- INSERIR LIVROS BÍBLICOS
-- ============================================================================

-- Antigo Testamento (Hebraico)
INSERT INTO books (canon_order, code, name_original, name_pt, testament, trad_group, chapters_count) VALUES
    (1, 'GEN', 'בְּרֵאשִׁית', 'Gênesis', 'AT', 'HEB_TM', 50),
    (2, 'EXO', 'שְׁמוֹת', 'Êxodo', 'AT', 'HEB_TM', 40),
    (3, 'LEV', 'וַיִּקְרָא', 'Levítico', 'AT', 'HEB_TM', 27),
    (4, 'NUM', 'בְּמִדְבַּר', 'Números', 'AT', 'HEB_TM', 36),
    (5, 'DEU', 'דְּבָרִים', 'Deuteronômio', 'AT', 'HEB_TM', 34),
    (6, 'JOS', 'יְהוֹשֻׁעַ', 'Josué', 'AT', 'HEB_TM', 24),
    (7, 'JDG', 'שׁוֹפְטִים', 'Juízes', 'AT', 'HEB_TM', 21),
    (8, 'RUT', 'רוּת', 'Rute', 'AT', 'HEB_TM', 4),
    (9, '1SA', 'שְׁמוּאֵל א', '1 Samuel', 'AT', 'HEB_TM', 31),
    (10, '2SA', 'שְׁמוּאֵל ב', '2 Samuel', 'AT', 'HEB_TM', 24),
    (11, '1KI', 'מְלָכִים א', '1 Reis', 'AT', 'HEB_TM', 22),
    (12, '2KI', 'מְלָכִים ב', '2 Reis', 'AT', 'HEB_TM', 25),
    (13, '1CH', 'דִּבְרֵי הַיָּמִים א', '1 Crônicas', 'AT', 'HEB_TM', 29),
    (14, '2CH', 'דִּבְרֵי הַיָּמִים ב', '2 Crônicas', 'AT', 'HEB_TM', 36),
    (15, 'EZR', 'עֶזְרָא', 'Esdras', 'AT', 'HEB_TM', 10),
    (16, 'NEH', 'נְחֶמְיָה', 'Neemias', 'AT', 'HEB_TM', 13),
    (17, 'EST', 'אֶסְתֵּר', 'Ester', 'AT', 'HEB_TM', 10),
    (18, 'JOB', 'אִיּוֹב', 'Jó', 'AT', 'HEB_TM', 42),
    (19, 'PSA', 'תְּהִלִּים', 'Salmos', 'AT', 'HEB_TM', 150),
    (20, 'PRO', 'מִשְׁלֵי', 'Provérbios', 'AT', 'HEB_TM', 31),
    (21, 'ECC', 'קֹהֶלֶת', 'Eclesiastes', 'AT', 'HEB_TM', 12),
    (22, 'SNG', 'שִׁיר הַשִּׁירִים', 'Cantares', 'AT', 'HEB_TM', 8),
    (23, 'ISA', 'יְשַׁעְיָהוּ', 'Isaías', 'AT', 'HEB_TM', 66),
    (24, 'JER', 'יִרְמְיָהוּ', 'Jeremias', 'AT', 'HEB_TM', 52),
    (25, 'LAM', 'אֵיכָה', 'Lamentações', 'AT', 'HEB_TM', 5),
    (26, 'EZK', 'יְחֶזְקֵאל', 'Ezequiel', 'AT', 'HEB_TM', 48),
    (27, 'DAN', 'דָּנִיֵּאל', 'Daniel', 'AT', 'HEB_TM', 12),
    (28, 'HOS', 'הוֹשֵׁעַ', 'Oséias', 'AT', 'HEB_TM', 14),
    (29, 'JOL', 'יוֹאֵל', 'Joel', 'AT', 'HEB_TM', 3),
    (30, 'AMO', 'עָמוֹס', 'Amós', 'AT', 'HEB_TM', 9),
    (31, 'OBA', 'עֹבַדְיָה', 'Obadias', 'AT', 'HEB_TM', 1),
    (32, 'JON', 'יוֹנָה', 'Jonas', 'AT', 'HEB_TM', 4),
    (33, 'MIC', 'מִיכָה', 'Miquéias', 'AT', 'HEB_TM', 7),
    (34, 'NAM', 'נַחוּם', 'Naum', 'AT', 'HEB_TM', 3),
    (35, 'HAB', 'חֲבַקּוּק', 'Habacuque', 'AT', 'HEB_TM', 3),
    (36, 'ZEP', 'צְפַנְיָה', 'Sofonias', 'AT', 'HEB_TM', 3),
    (37, 'HAG', 'חַגַּי', 'Ageu', 'AT', 'HEB_TM', 2),
    (38, 'ZEC', 'זְכַרְיָה', 'Zacarias', 'AT', 'HEB_TM', 14),
    (39, 'MAL', 'מַלְאָכִי', 'Malaquias', 'AT', 'HEB_TM', 4)
ON CONFLICT (code) DO NOTHING;

-- Novo Testamento (Grego)
INSERT INTO books (canon_order, code, name_original, name_pt, testament, trad_group, chapters_count) VALUES
    (40, 'MAT', 'Κατὰ Μαθθαῖον', 'Mateus', 'NT', 'GRC_NT', 28),
    (41, 'MRK', 'Κατὰ Μᾶρκον', 'Marcos', 'NT', 'GRC_NT', 16),
    (42, 'LUK', 'Κατὰ Λουκᾶν', 'Lucas', 'NT', 'GRC_NT', 24),
    (43, 'JHN', 'Κατὰ Ἰωάννην', 'João', 'NT', 'GRC_NT', 21),
    (44, 'ACT', 'Πράξεις Ἀποστόλων', 'Atos', 'NT', 'GRC_NT', 28),
    (45, 'ROM', 'Πρὸς Ῥωμαίους', 'Romanos', 'NT', 'GRC_NT', 16),
    (46, '1CO', 'Πρὸς Κορινθίους Αʹ', '1 Coríntios', 'NT', 'GRC_NT', 16),
    (47, '2CO', 'Πρὸς Κορινθίους Βʹ', '2 Coríntios', 'NT', 'GRC_NT', 13),
    (48, 'GAL', 'Πρὸς Γαλάτας', 'Gálatas', 'NT', 'GRC_NT', 6),
    (49, 'EPH', 'Πρὸς Ἐφεσίους', 'Efésios', 'NT', 'GRC_NT', 6),
    (50, 'PHP', 'Πρὸς Φιλιππησίους', 'Filipenses', 'NT', 'GRC_NT', 4),
    (51, 'COL', 'Πρὸς Κολοσσαεῖς', 'Colossenses', 'NT', 'GRC_NT', 4),
    (52, '1TH', 'Πρὸς Θεσσαλονικεῖς Αʹ', '1 Tessalonicenses', 'NT', 'GRC_NT', 5),
    (53, '2TH', 'Πρὸς Θεσσαλονικεῖς Βʹ', '2 Tessalonicenses', 'NT', 'GRC_NT', 3),
    (54, '1TI', 'Πρὸς Τιμόθεον Αʹ', '1 Timóteo', 'NT', 'GRC_NT', 6),
    (55, '2TI', 'Πρὸς Τιμόθεον Βʹ', '2 Timóteo', 'NT', 'GRC_NT', 4),
    (56, 'TIT', 'Πρὸς Τίτον', 'Tito', 'NT', 'GRC_NT', 3),
    (57, 'PHM', 'Πρὸς Φιλήμονα', 'Filemom', 'NT', 'GRC_NT', 1),
    (58, 'HEB', 'Πρὸς Ἑβραίους', 'Hebreus', 'NT', 'GRC_NT', 13),
    (59, 'JAS', 'Ἰακώβου', 'Tiago', 'NT', 'GRC_NT', 5),
    (60, '1PE', 'Πέτρου Αʹ', '1 Pedro', 'NT', 'GRC_NT', 5),
    (61, '2PE', 'Πέτρου Βʹ', '2 Pedro', 'NT', 'GRC_NT', 3),
    (62, '1JN', 'Ἰωάννου Αʹ', '1 João', 'NT', 'GRC_NT', 5),
    (63, '2JN', 'Ἰωάννου Βʹ', '2 João', 'NT', 'GRC_NT', 1),
    (64, '3JN', 'Ἰωάννου Γʹ', '3 João', 'NT', 'GRC_NT', 1),
    (65, 'JUD', 'Ἰούδα', 'Judas', 'NT', 'GRC_NT', 1),
    (66, 'REV', 'Ἀποκάλυψις Ἰωάννου', 'Apocalipse', 'NT', 'GRC_NT', 22)
ON CONFLICT (code) DO NOTHING;

-- ============================================================================
-- VIEWS ÚTEIS
-- ============================================================================

-- View: Versículos com texto completo
CREATE OR REPLACE VIEW v_verses_full AS
SELECT
    v.id AS verse_id,
    b.code AS book_code,
    b.name_pt AS book_name,
    v.chapter,
    v.verse,
    v.canonical_ref,
    b.testament,
    b.trad_group
FROM verses v
JOIN books b ON v.book_id = b.id;

-- View: Tokens com morfologia
CREATE OR REPLACE VIEW v_tokens_morphology AS
SELECT
    t.id AS token_id,
    t.verse_id,
    t.position,
    t.text_utf8,
    t.script,
    t.normalized,
    t.pt_literal,
    m.lemma,
    m.strong_number,
    m.morph_code,
    m.tense,
    m.voice,
    m.mood,
    m.person,
    m.number,
    m.gender,
    m.case_gram,
    m.state,
    ts.code AS source_code
FROM tokens t
LEFT JOIN morphology m ON t.id = m.token_id
JOIN text_sources ts ON t.source_id = ts.id;

-- View: Interlinear (texto original + tradução literal)
CREATE OR REPLACE VIEW v_interlinear AS
SELECT
    v.canonical_ref,
    t.position,
    t.text_utf8 AS original,
    t.script,
    t.pt_literal AS literal_pt,
    m.lemma,
    m.strong_number,
    m.morph_code
FROM tokens t
JOIN verses v ON t.verse_id = v.id
LEFT JOIN morphology m ON t.id = m.token_id
ORDER BY v.id, t.position;
