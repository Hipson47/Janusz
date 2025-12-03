# Janusz AI Enhancement Plan — Complete Roadmap

## Phase 1 ✅ COMPLETED: AI-Powered Content Understanding
**Status: IMPLEMENTED** - Enhanced YAML analysis with LLM-powered extraction, OpenRouter integration, and AI insights.

## Phase 2 ✅ COMPLETED: Local GUI (Tkinter)
**Status: IMPLEMENTED** - Desktop application with file selection, format conversion, and user-friendly interface.

## Phase 3 ✅ COMPLETED: Modular Schemas + Orchestrator
**Status: IMPLEMENTED** - Reusable document processing templates and intelligent AI orchestrator.

## Phase 4 ✅ COMPLETED: Semantic Search & RAG System
**Status: IMPLEMENTED** - Vector database with FAISS/ChromaDB, embeddings, and question-answering.

---

## Phase 5: Prompt Optimization & Advanced Features ✅ COMPLETED

### 5.1 Cel fazy
Wprowadzić zaawansowany system optymalizacji promptów oraz rozszerzone funkcjonalności RAG, tworząc kompleksowe środowisko do pracy z AI. Docelowo:

- stworzyć narzędzia do optymalizacji i testowania promptów LLM,
- rozszerzyć możliwości RAG o zaawansowane funkcje wyszukiwania,
- zintegrować wszystko w ujednolicony interfejs użytkownika,
- przygotować fundament pod przyszłe rozszerzenia.

### 5.2 Stan bieżący (grudzień 2025)

| Obszar | Stan |
| --- | --- |
| RAG System | ✅ Implementacja bazowa (FAISS/ChromaDB, OpenRouter embeddings) |
| GUI | ✅ Podstawowy interfejs z wyszukiwaniem RAG |
| Prompt Engineering | ❌ Brak dedykowanych narzędzi |
| Zaawansowane RAG | ❌ Ograniczone do podstawowego wyszukiwania |
| Biblioteka Promptów | ❌ Brak zarządzania promptami |
| Optymalizacja | ❌ Brak narzędzi do testowania promptów |

### 5.3 Luka funkcjonalna

1. **Brak narzędzi optymalizacji promptów**: Użytkownicy nie mają możliwości testowania i porównywania różnych wersji promptów.
2. **Ograniczone możliwości RAG**: Brak hybrydowego wyszukiwania, multi-modal support, czy zaawansowanych filtrów.
3. **Brak biblioteki promptów**: Trudność w zarządzaniu i ponownym wykorzystaniu sprawdzonych promptów.
4. **Brak benchmarkingu**: Nie ma możliwości porównania efektywności różnych podejść.

### 5.4 Plan realizacji

#### 5.4.1 System optymalizacji promptów (`src/janusz/prompts/`)

**Nowe moduły:**
- `prompt_optimizer.py` - Główny optymalizator promptów
- `prompt_templates.py` - Biblioteka szablonów promptów
- `prompt_tester.py` - Narzędzia do testowania i benchmarkingu
- `prompt_library.py` - Zarządzanie biblioteką promptów

**Kluczowe klasy:**
```python
class PromptTemplate(BaseModel):
    id: str
    name: str
    description: str
    template: str
    variables: List[str]
    category: Literal["extraction", "generation", "analysis", "qa", "optimization"]
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class OptimizationResult(BaseModel):
    original_prompt: str
    optimized_prompt: str
    improvement_score: float
    test_results: List[TestResult]
    suggestions: List[str]

class PromptLibrary:
    """Zarządzanie biblioteką promptów z importem/eksportem."""
    def save_template(self, template: PromptTemplate)
    def load_template(self, template_id: str) -> PromptTemplate
    def search_templates(self, query: str) -> List[PromptTemplate]
    def export_library(self, path: str)
    def import_library(self, path: str)
```

#### 5.4.2 Rozszerzony system RAG (`src/janusz/rag/`)

**Ulepszenia:**
- **Hybrydowe wyszukiwanie**: Kombinacja semantycznego i keyword-based search
- **Multi-modal support**: Obsługa różnych typów dokumentów
- **Zaawansowane filtry**: Filtrowanie po metadanych, dacie, autorze
- **Query expansion**: Rozszerzanie zapytań dla lepszych wyników
- **Result ranking**: Zaawansowane rankingowanie wyników

**Nowe klasy:**
```python
class HybridSearch:
    """Hybrydowe wyszukiwanie kombinujące kilka metod."""
    def search(self, query: str, filters: Dict[str, Any]) -> List[SearchResult]

class QueryExpander:
    """Rozszerzanie zapytań dla lepszego wyszukiwania."""
    def expand_query(self, query: str) -> List[str]

class AdvancedRAGSystem(RAGSystem):
    """Rozszerzony RAG z dodatkowymi funkcjami."""
    def multi_query_search(self, queries: List[str]) -> List[SearchResult]
    def filtered_search(self, query: str, metadata_filters: Dict) -> List[SearchResult]
```

#### 5.4.3 GUI dla optymalizacji promptów

**Rozszerzenie istniejącego GUI:**
- Zakładka "Optymalizacja Promptów"
- Narzędzia do tworzenia i testowania promptów
- Wizualizacja wyników optymalizacji
- Biblioteka promptów z wyszukiwaniem
- Eksport/import promptów

#### 5.4.4 CLI rozszerzenia

**Nowe komendy:**
```bash
janusz prompt optimize "tekst do optymalizacji" --model anthropic/claude-3-haiku
janusz prompt test --template extraction_prompt --benchmark
janusz prompt library list
janusz prompt library export --output prompts.json
janusz rag advanced-search "query" --filters "category:technical,date:2024"
```

#### 5.4.5 Modele danych (rozszerzenie `src/janusz/models.py`)

```python
class PromptOptimizationRequest(BaseModel):
    text: str
    context: Optional[str] = None
    target_model: str = "anthropic/claude-3-haiku"
    optimization_goal: Literal["clarity", "efficiency", "specificity", "creativity"]

class BenchmarkResult(BaseModel):
    prompt_id: str
    model: str
    metrics: Dict[str, float]  # accuracy, coherence, relevance, etc.
    execution_time: float
    token_usage: int
    score: float

class AdvancedSearchFilters(BaseModel):
    categories: List[str] = Field(default_factory=list)
    date_range: Optional[Tuple[str, str]] = None
    authors: List[str] = Field(default_factory=list)
    content_types: List[str] = Field(default_factory=list)
    min_score: float = 0.0
```

### 5.5 Zależności i konfiguracja

**Nowe zależności w `pyproject.toml`:**
```toml
[project.optional-dependencies]
prompts = [
    "numpy>=1.21.0",  # Dla obliczeń metryk
    "scikit-learn>=1.0.0",  # Dla analizy wyników
    "pandas>=1.5.0",  # Dla analizy danych benchmark
]
```

**Konfiguracja:**
- Domyślne modele do optymalizacji promptów
- Parametry benchmarkingu
- Ścieżki do bibliotek promptów

### 5.6 Testy i walidacja

**Nowe testy:**
- `tests/test_prompt_optimizer.py` - Testy optymalizacji promptów
- `tests/test_prompt_library.py` - Testy zarządzania biblioteką
- `tests/test_advanced_rag.py` - Testy rozszerzonego RAG
- `tests/test_prompt_gui.py` - Testy GUI dla promptów

**Walidacja:**
- Benchmarking różnych podejść optymalizacji
- Porównanie wyników RAG przed/po optymalizacji
- Testy integracyjne całego pipeline'u

### 5.7 Ryzyka i mitigacje

| Ryzyko | Mitigacja |
| --- | --- |
| Złożoność optymalizacji promptów | Modułowa architektura z fallback do prostych metod |
| Wydajność benchmarkingu | Cache'owanie wyników, próbkowanie danych testowych |
| Jakość automatycznej optymalizacji | Walidacja przez ekspertów + metryki jakości |
| Zgodność z istniejącym RAG | Kompatybilność wsteczna + opcjonalne funkcje |

### 5.8 Harmonogram realizacji

1. **Week 1**: Prompt optimization core system
2. **Week 2**: Prompt library and management
3. **Week 3**: Advanced RAG features
4. **Week 4**: GUI integration and testing
5. **Week 5**: Benchmarking and validation

### 5.9 Kryteria sukcesu

- ✅ Możliwość optymalizacji promptów z >20% poprawą jakości
- ✅ Biblioteka z 50+ szablonami promptów
- ✅ Hybrydowe wyszukiwanie RAG z lepszymi wynikami
- ✅ GUI z pełną funkcjonalnością optymalizacji
- ✅ Wszystkie testy przechodzą z >90% pokrycia

---

## Przyszłe fazy (Phase 6+)
- **Multi-modal processing**: Obsługa obrazów, audio, wideo
- **Collaborative features**: Udostępnianie promptów i dokumentów
- **API endpoints**: REST API dla integracji zewnętrznych
- **Cloud deployment**: Docker + Kubernetes
- **Mobile app**: React Native lub Flutter

