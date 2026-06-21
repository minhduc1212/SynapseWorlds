# 📖 Character Relationship Evolving Graph — Full App Plan

> Build a web application that ingests any novel, film, manga, or anime content and generates an interactive, timeline-driven **Character Relationship Graph** with precise relationship labels (mother–daughter, rivals, lovers, mentor–student, etc.) that evolve across the story's arc.

---

## 1. Vision & Core Features

| Feature | Description |
|---|---|
| 📥 Content Ingestion | Upload raw text, PDF, subtitle files (.srt/.ass), paste URLs, or manual synopsis input |
| 🤖 AI Extraction | LLM-powered NLP pipeline to extract characters, events, and relationships per chapter/episode/act |
| 🕸️ Dynamic Graph | Force-directed or hierarchical graph with labeled, directional edges (e.g. "mother → daughter") |
| ⏱️ Timeline Slider | Scrub through timeline — relationships change, characters appear/disappear, edges update live |
| 🔍 Detail Panel | Click any character or edge to see a rich card: scenes/quotes where relationship was established |
| 🎨 Themes | Dark cinematic mode for films/anime, warm parchment mode for novels, ink wash for manga |
| 📤 Export | Export graph as SVG/PNG or relationship data as JSON/CSV |

---

## 2. Tech Stack

### Backend — Python (FastAPI)
```
backend/
├── main.py                  # FastAPI app entrypoint
├── routers/
│   ├── ingest.py            # File upload & URL scrape endpoints
│   ├── extract.py           # Run extraction pipeline
│   └── graph.py             # Serve graph data (nodes/edges/timeline)
├── services/
│   ├── ingestion/
│   │   ├── pdf_reader.py    # PyMuPDF or pdfplumber
│   │   ├── subtitle_parser.py  # pysrt / ass parser
│   │   ├── url_scraper.py   # httpx + BeautifulSoup4
│   │   └── text_chunker.py  # Split into timeline chunks
│   ├── extraction/
│   │   ├── llm_extractor.py     # Call Claude/GPT with structured output
│   │   ├── entity_resolver.py   # Merge alias names (e.g. "Frodo" = "Mr. Baggins")
│   │   ├── relationship_classifier.py  # Map free text → canonical labels
│   │   └── timeline_builder.py  # Assign events to timeline slots
│   └── graph/
│       ├── graph_builder.py     # Build NetworkX graph per snapshot
│       └── diff_engine.py       # Compute diffs between snapshots
├── models/
│   ├── character.py
│   ├── relationship.py
│   └── timeline.py
├── db/
│   ├── database.py          # SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
│   └── migrations/          # Alembic migrations
└── tests/
```

### Frontend — React + TypeScript + Vite
```
frontend/
├── src/
│   ├── components/
│   │   ├── GraphCanvas/
│   │   │   ├── ForceGraph.tsx       # D3-force or react-force-graph
│   │   │   ├── NodeCard.tsx         # Character bubble + portrait
│   │   │   ├── EdgeLabel.tsx        # Relationship label on edges
│   │   │   └── GraphLegend.tsx
│   │   ├── TimelineSlider/
│   │   │   ├── Slider.tsx           # Custom scrubber (chapter/episode)
│   │   │   ├── EventMarkers.tsx     # Key events plotted on timeline
│   │   │   └── PlaybackControls.tsx # Auto-play through time
│   │   ├── DetailPanel/
│   │   │   ├── CharacterSheet.tsx   # Full character profile
│   │   │   ├── RelationshipCard.tsx # Edge detail with quotes/scenes
│   │   │   └── EvidenceQuotes.tsx   # Source passages
│   │   ├── IngestForm/
│   │   │   ├── FileUploader.tsx     # Drag-and-drop
│   │   │   ├── URLInput.tsx
│   │   │   └── MediaTypeSelector.tsx
│   │   └── Layout/
│   │       ├── Sidebar.tsx
│   │       ├── Toolbar.tsx
│   │       └── ThemeSwitcher.tsx
│   ├── hooks/
│   │   ├── useGraphData.ts          # Fetch + cache graph snapshots
│   │   ├── useTimeline.ts           # Timeline state machine
│   │   └── useGraphLayout.ts        # Layout algorithm switcher
│   ├── store/
│   │   └── graphStore.ts            # Zustand store
│   ├── types/
│   │   ├── character.ts
│   │   ├── relationship.ts
│   │   └── timeline.ts
│   └── styles/
│       ├── themes/
│       │   ├── cinematic.css        # Dark film noir palette
│       │   ├── parchment.css        # Warm novel palette
│       │   └── inkwash.css          # Manga monochrome + ink
│       └── global.css
```

### Infrastructure
| Layer | Tool |
|---|---|
| Package manager | `uv` (Python), `pnpm` (JS) |
| API framework | FastAPI + Pydantic v2 |
| Task queue | Celery + Redis (async extraction jobs) |
| Database | SQLite → PostgreSQL (prod) |
| Graph DB (optional) | Neo4j for complex traversal queries |
| Auth (optional) | Clerk or Supabase Auth |
| Deployment | Docker Compose (dev) → Railway / Render / Fly.io (prod) |
| CDN | Cloudflare R2 for uploaded files |

---

## 3. Data Models

### `Character`
```python
class Character(BaseModel):
    id: str                        # UUID
    canonical_name: str            # "Hermione Granger"
    aliases: list[str]             # ["Hermione", "Granger", "The brightest witch"]
    first_appearance: TimelinePoint
    last_appearance: TimelinePoint | None
    description: str               # LLM-generated bio
    portrait_url: str | None       # Auto-fetched or user-provided
    attributes: dict               # {"house": "Gryffindor", "age": "11→17"}
```

### `Relationship`
```python
class Relationship(BaseModel):
    id: str
    source_id: str                 # Character UUID
    target_id: str
    label: str                     # Canonical label (see taxonomy below)
    direction: Literal["one-way", "mutual", "asymmetric"]
    strength: float                # 0.0 → 1.0 (how established)
    valid_from: TimelinePoint
    valid_until: TimelinePoint | None   # None = persists to end
    evidence: list[EvidenceQuote]  # Passages that prove this relationship
    sentiment: Literal["positive", "negative", "neutral", "complex"]
    status_changes: list[RelationshipEvent]  # e.g. "allies → enemies at Ch.40"
```

### `TimelinePoint`
```python
class TimelinePoint(BaseModel):
    type: Literal["chapter", "episode", "act", "page", "timestamp"]
    index: int                     # Chapter 3, Episode 5, Act 2…
    label: str                     # "Chapter 3: The Dark Forest"
    in_story_time: str | None      # "Year 3 at Hogwarts"
```

### Relationship Taxonomy (canonical labels)
```
FAMILY
  parent → child          (father-son, mother-daughter, father-daughter, mother-son)
  siblings                (elder-younger, twin)
  extended_family         (uncle, aunt, cousin, grandparent)
  step / adoptive / foster

ROMANTIC
  lovers                  (current)
  ex_lovers
  unrequited_love         (source → target)
  betrothed / married

SOCIAL
  friends
  best_friends
  rivals
  enemies
  acquaintances
  colleague / allies

POWER
  master → servant
  ruler → subject
  mentor → student / protégé
  employer → employee
  commander → soldier

SPECIAL
  creator → creation      (Frankenstein → Monster)
  nemesis                 (arch-enemy, fated opposition)
  prophesied / destined
  reincarnation
```

---

## 4. AI Extraction Pipeline

### Step 1 — Chunking
```python
# text_chunker.py
def chunk_by_chapter(text: str) -> list[Chunk]:
    # Regex detect "Chapter N" / "Episode N" / "ACT N" headers
    # Fallback: sliding window of ~2000 tokens with 200-token overlap

def assign_timeline(chunks: list[Chunk], media_type: str) -> list[TimelineChunk]:
    # Map each chunk → TimelinePoint(type, index, label)
```

### Step 2 — LLM Extraction (per chunk)
**System prompt:**
```
You are a literary analyst. Given the following text passage from {media_type} titled "{title}",
extract ALL characters and relationships mentioned or implied.

Return ONLY valid JSON matching this schema:
{
  "characters": [
    {"name": str, "aliases": [str], "description": str}
  ],
  "relationships": [
    {
      "source": str,       // character name
      "target": str,
      "label": str,        // from the provided taxonomy
      "direction": "one-way" | "mutual" | "asymmetric",
      "evidence": str,     // verbatim quote proving this relationship (max 150 chars)
      "sentiment": "positive" | "negative" | "neutral" | "complex",
      "is_new": bool,      // newly established in this chunk?
      "is_changed": bool,  // changed from previous state?
      "is_ended": bool     // relationship terminated here?
    }
  ]
}

Taxonomy of allowed labels: [inject full taxonomy list]
Be as SPECIFIC as possible: prefer "mother-daughter" over "family".
```

### Step 3 — Entity Resolution
```python
# entity_resolver.py
# Problem: "Voldemort", "He-Who-Must-Not-Be-Named", "The Dark Lord" → same node
# Approach:
# 1. Collect all names + aliases across all chunks
# 2. Embed with sentence-transformers
# 3. Cosine similarity clustering (threshold 0.82)
# 4. LLM verification pass on ambiguous clusters
# 5. Produce canonical_name → alias_list mapping
```

### Step 4 — Timeline Assembly
```python
# timeline_builder.py
def build_snapshots(chunks: list[ProcessedChunk]) -> list[GraphSnapshot]:
    """
    For each timeline point, compute the FULL graph state:
    - All characters seen so far
    - All active relationships (not yet ended)
    - All changed relationships
    Returns: list of snapshots sorted by timeline index
    """
```

### Step 5 — Diff Engine
```python
# diff_engine.py
def compute_diff(prev: GraphSnapshot, curr: GraphSnapshot) -> GraphDiff:
    return GraphDiff(
        added_nodes=[...],
        removed_nodes=[...],
        added_edges=[...],
        removed_edges=[...],
        changed_edges=[...]   # label or sentiment changed
    )
```

---

## 5. API Endpoints

```
POST   /api/v1/projects                    # Create new project
POST   /api/v1/projects/{id}/ingest        # Upload file or submit URL
GET    /api/v1/projects/{id}/status        # Check extraction job status
GET    /api/v1/projects/{id}/graph         # Full graph (all snapshots)
GET    /api/v1/projects/{id}/graph/snapshot?at={timeline_index}
GET    /api/v1/projects/{id}/characters    # List all characters
GET    /api/v1/projects/{id}/characters/{char_id}
GET    /api/v1/projects/{id}/relationships
GET    /api/v1/projects/{id}/relationships/{rel_id}
GET    /api/v1/projects/{id}/timeline      # Timeline metadata
GET    /api/v1/projects/{id}/diff?from={t1}&to={t2}
POST   /api/v1/projects/{id}/export        # Export graph as JSON/CSV/SVG
```

---

## 6. Graph Visualization

### Library Choice
| Option | When to use |
|---|---|
| **`react-force-graph`** (Three.js/WebGL) | Best for large graphs (100+ nodes), 3D mode |
| **`@antv/g6`** | Rich built-in layouts, enterprise-grade |
| **`cytoscape.js`** | Best algorithm variety (dagre, cola, cose-bilkent) |
| **D3.js custom** | Maximum control, best for animated transitions |

**Recommended: `@antv/g6` for layout richness + `react-force-graph-2d` fallback for very large graphs.**

### Layout Algorithms
- **Family / hierarchy**: Dagre (top-down tree) — best for family trees
- **Social network**: Force-directed (cola/d3-force) — best for complex webs  
- **Timeline-linear**: Custom swimlane layout (characters as rows, time as X-axis)

### Edge Rendering
```typescript
// Relationships rendered as:
// - Solid line: current / active relationship
// - Dashed line: past / ended relationship
// - Animated pulse: newly formed this snapshot
// - Color: sentiment (green=positive, red=negative, grey=neutral, purple=complex)
// - Thickness: strength score
// - Label: always visible for specific labels (e.g. "mother→daughter"),
//           hover-only for weak/acquaintance links
// - Arrow direction: one-way relationships
// - Double-headed arrow: mutual relationships
```

### Timeline Slider UX
```
[●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━○]
 Ch.1                                     Ch.40
  ↑          ↑             ↑
[key event] [key event] [key event]        ← click to jump

▶ Auto-play   ⏸ Pause   Speed: 1× 2× 4×
```
- Debounced API fetch on scrub (300ms)
- Optimistic local diff application for perceived speed
- Key events shown as markers on slider rail

---

## 7. Frontend Graph Interactions

| Interaction | Behavior |
|---|---|
| Click character node | Open character sheet sidebar |
| Click relationship edge | Open relationship detail card with evidence quotes |
| Hover node | Highlight all direct connections, dim others |
| Hover edge | Tooltip: label + sentiment + when established |
| Double-click node | Focus subgraph (1-hop neighborhood) |
| Right-click | Context menu: "Find path between…", "Show all relationships" |
| Drag | Reposition nodes (persisted per session) |
| Scroll/pinch | Zoom in/out |
| Search bar | Highlight character, filter graph to show only their connections |
| Filter panel | Filter by relationship type, sentiment, time range |

---

## 8. Supported Input Formats

| Format | Parser | Notes |
|---|---|---|
| `.txt` | Built-in Python | Raw novel text |
| `.pdf` | `pdfplumber` / `PyMuPDF` | Novel scans, manga scripts |
| `.epub` | `ebooklib` | E-book novels |
| `.srt` / `.vtt` | `pysrt` | Film/anime subtitles |
| `.ass` / `.ssa` | Custom regex | Styled anime subtitles |
| `.docx` | `python-docx` | Script / screenplay format |
| URL | `httpx` + `trafilatura` | Web novel pages, wikis, fan wikis |
| Manual text paste | Direct | Any medium |
| Wikipedia page | `wikipedia-api` | Auto-populate character list |

---

## 9. Project Structure (Monorepo)

```
charGraph/
├── backend/                  # Python FastAPI
│   ├── pyproject.toml        # uv / poetry
│   ├── .env.example
│   └── ... (see Section 2)
├── frontend/                 # React + TypeScript + Vite
│   ├── package.json
│   ├── vite.config.ts
│   └── ... (see Section 2)
├── worker/                   # Celery worker (can share backend code)
│   └── tasks.py
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── scripts/
│   ├── seed_demo.py          # Seed with Harry Potter / One Piece demo
│   └── eval_extraction.py    # Accuracy evaluation vs ground truth
├── docs/
│   ├── architecture.md
│   ├── relationship_taxonomy.md
│   └── api_reference.md
└── README.md
```

---

## 10. Implementation Phases

### Phase 1 — Foundation (Week 1–2)
- [ ] FastAPI skeleton + health check
- [ ] Database models (SQLAlchemy)
- [ ] File upload endpoint (text + PDF)
- [ ] Text chunker with chapter detection
- [ ] Basic LLM extraction (single chunk, Claude claude-sonnet-4-20250514)
- [ ] React app scaffold (Vite + TypeScript)
- [ ] Static graph display with hardcoded demo data
- [ ] Force-directed graph canvas with D3

### Phase 2 — Core Pipeline (Week 3–4)
- [ ] Full extraction pipeline (all chunks)
- [ ] Entity resolution (embedding-based)
- [ ] Timeline snapshot builder
- [ ] Diff engine
- [ ] Graph API endpoints
- [ ] Timeline slider component
- [ ] Live graph updates on slider scrub
- [ ] Edge labels + color coding
- [ ] Character detail panel

### Phase 3 — Input Richness (Week 5)
- [ ] Subtitle parser (.srt, .ass)
- [ ] EPUB reader
- [ ] URL scraper (trafilatura)
- [ ] Celery async job queue
- [ ] Job status polling UI

### Phase 4 — UX Polish (Week 6)
- [ ] Three visual themes (cinematic / parchment / ink wash)
- [ ] Advanced graph interactions (focus, path finding)
- [ ] Filter panel (by type, sentiment, character)
- [ ] Export (SVG, JSON, CSV)
- [ ] Demo dataset: Harry Potter, One Piece, or Attack on Titan
- [ ] Responsive layout (tablet support)

### Phase 5 — Production (Week 7–8)
- [ ] PostgreSQL migration
- [ ] Docker Compose full stack
- [ ] Auth (Clerk / Supabase)
- [ ] Rate limiting + cost guardrails on LLM calls
- [ ] Deploy to Railway / Fly.io
- [ ] SEO landing page

---

## 11. Key Libraries (Full List)

### Python Backend
```toml
[dependencies]
fastapi = ">=0.115"
uvicorn = {extras = ["standard"]}
pydantic = ">=2.0"
sqlalchemy = ">=2.0"
alembic = "*"
celery = {extras = ["redis"]}
redis = "*"
httpx = "*"
pdfplumber = "*"         # PDF extraction
PyMuPDF = "*"            # fitz — fast PDF/image
ebooklib = "*"           # EPUB
python-docx = "*"        # DOCX
pysrt = "*"              # SRT subtitles
trafilatura = "*"        # Web scraping
sentence-transformers = "*"  # Embedding for entity resolution
anthropic = ">=0.40"     # Claude API
openai = "*"             # Fallback GPT-4o
networkx = "*"           # Graph algorithms
python-multipart = "*"   # File upload
boto3 = "*"              # S3/R2 uploads
python-jose = "*"        # JWT auth
```

### JavaScript Frontend
```json
{
  "dependencies": {
    "react": "^19",
    "react-dom": "^19",
    "@antv/g6": "^5",
    "d3": "^7",
    "zustand": "^5",
    "react-query": "^5",
    "@radix-ui/react-*": "latest",
    "framer-motion": "^12",
    "tailwindcss": "^4",
    "react-dropzone": "^14",
    "react-slider": "^2",
    "lucide-react": "latest",
    "date-fns": "^4"
  }
}
```

---

## 12. LLM Cost Estimate

| Input Type | Avg tokens/chunk | Chunks | Total tokens | Est. cost (claude-sonnet) |
|---|---|---|---|---|
| Short novel (80k words) | 1,500 | ~55 | ~82k | ~$0.25 |
| Full novel (250k words) | 1,500 | ~167 | ~250k | ~$0.75 |
| Anime series (26 eps) | 800 (subs) | 26 | ~21k | ~$0.06 |
| Manga (100 chapters) | 600 | 100 | ~60k | ~$0.18 |

> Use `claude-haiku-4-5` for initial pass, `claude-sonnet-4-20250514` for final relationship verification pass to balance cost/accuracy.

---

## 13. Accuracy Improvement Strategies

1. **Two-pass extraction**: Fast Haiku pass → Sonnet verification pass on complex relationships
2. **Few-shot examples**: Include 2–3 perfect extraction examples in system prompt per media type
3. **Structured output enforcement**: Use Pydantic models + `response_format: json_schema` to prevent hallucinated fields
4. **Confidence scores**: Ask LLM to rate each relationship 0–1; filter out low-confidence edges
5. **Contradiction detection**: If LLM says A is B's mother in Ch.1 but sister in Ch.5, flag for review
6. **User correction UI**: Allow users to add/edit/delete nodes and edges, feeding corrections back as fine-tuning signal
7. **Alias disambiguation prompt**: Separate dedicated prompt just for "are these the same person?"
8. **Cross-chunk context window**: Include summary of previous chunk when extracting next chunk

---

## 14. Example Output (Harry Potter, Ch.1–3)

```json
{
  "snapshot": { "type": "chapter", "index": 3, "label": "Chapter 3: The Letters from No One" },
  "nodes": [
    { "id": "hp", "name": "Harry Potter", "first_seen": 1 },
    { "id": "vv", "name": "Vernon Dursley", "first_seen": 1 },
    { "id": "pv", "name": "Petunia Dursley", "first_seen": 1 },
    { "id": "dv", "name": "Dudley Dursley", "first_seen": 1 }
  ],
  "edges": [
    { "source": "pv", "target": "hp", "label": "aunt→nephew", "sentiment": "negative", "strength": 0.9 },
    { "source": "vv", "target": "hp", "label": "guardian→ward", "sentiment": "negative", "strength": 0.9 },
    { "source": "pv", "target": "vv", "label": "married", "sentiment": "positive", "strength": 1.0 },
    { "source": "dv", "target": "hp", "label": "cousin (bully)", "sentiment": "negative", "strength": 0.8 }
  ]
}
```

---

## 15. Stretch Goals

- 🌐 **Multi-language support**: Japanese manga/anime, Korean manhwa (auto-translate before extraction)
- 🎭 **Character arc heatmap**: Show each character's emotional journey as a color-coded timeline strip
- 🔗 **Cross-work comparison**: Compare relationship patterns between two works (e.g., HP vs LOTR)
- 🤝 **Collaborative editing**: Multiple users annotating the same graph
- 📱 **Mobile app**: React Native port with touch-optimized graph navigation
- 🎬 **Video input**: Transcribe film audio with Whisper, then extract from transcript
- 🏷️ **Auto-wiki enrichment**: Fetch character portraits and extra info from Fandom wikis automatically