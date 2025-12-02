# Janusz AI Enhancement Plan — Phase 1 Validation

## 1. Cel fazy
Wdrożyć „AI-Powered Content Understanding” jako rozszerzenie aktualnego pipeline’u (konwersja dokumentów → YAML → TOON) bez naruszania istniejących funkcji CLI (`janusz convert`, `janusz toon`, `janusz json`). Docelowo:

- wzbogacić `analysis` w strukturze YAML o dane generowane przez LLM,
- umożliwić wybór źródła ekstrakcji (regex + heurystyki **lub** AI),
- przygotować fundament pod GUI/RAG w kolejnych fazach.

## 2. Stan bieżący (grudzień 2025)

| Obszar | Stan |
| --- | --- |
| Konwersja źródeł | `src/janusz/converter.py`, obsługa PDF/MD/TXT/DOCX/HTML |
| Struktura danych | `src/janusz/models.py`, Pydantic 2.x, brak AI pól |
| Ekstrakcja heurystyczna | `src/janusz/extraction_patterns.py`, regexy na best practices / examples |
| CLI | `src/janusz/cli.py` – komendy `convert`, `toon`, `json`, `test` |
| Zależności | `pyproject.toml` – brak klienta OpenRouter/LLM |
| GUI / RAG | Brak |

Wniosek: mamy solidny pipeline, ale potrzeba nowej warstwy AI + konfiguracji.

## 3. Luka funkcjonalna

1. Analiza treści opiera się wyłącznie na regexach (`extract_best_practices_and_examples`), przez co:
   - brak kontekstu, hierarchii i jakości ocen,
   - brak powiązań semantycznych między sekcjami,
   - brak insightów/sugestii dla użytkownika.
2. Modele danych (`Analysis`) nie przechowują informacji AI (confidence score, reasoning, summary).
3. Brak integracji z usługą LLM (preferowany OpenRouter).
4. CLI nie posiada przełącznika pozwalającego włączyć/wyłączyć AI.

## 4. Plan realizacji (w zgodzie z obecną bazą)

### 4.1 Zmiany w modelach (`src/janusz/models.py`)
- Dodać klasy:
  ```python
  class AIInsight(BaseModel):
      text: str
      insight_type: Literal["summary", "improvement", "warning", "enhancement"]
      confidence_score: float = Field(ge=0.0, le=1.0)
      reasoning: Optional[str] = None
      tags: List[str] = Field(default_factory=list)

  class AIExtractionResult(BaseModel):
      best_practices: List[ExtractionItem] = Field(default_factory=list)
      examples: List[ExtractionItem] = Field(default_factory=list)
      insights: List[AIInsight] = Field(default_factory=list)
      summary: Optional[str] = None
      quality_score: float = Field(ge=0.0, le=1.0, default=0.5)
  ```
- Rozszerzyć `Analysis` o opcjonalne pole `ai: Optional[AIExtractionResult]`.

### 4.2 Warstwa AI (`src/janusz/ai/ai_content_analyzer.py`)
- Nowy moduł z klasą `AIContentAnalyzer`, która:
  - korzysta z OpenRouter API (np. REST via `httpx`),
  - przyjmuje surowy tekst / sekcje,
  - zwraca `AIExtractionResult`.
- Obsłużyć fallback (gdy brak klucza API → ostrzeżenie i powrót do heurystyk).
- Konfiguracja modelu (np. `openrouter_model` w `.env` / ustawieniach CLI).

### 4.3 Integracja w pipeline (`src/janusz/converter.py`)
- Dodać flagi `use_ai: bool` w konstruktorze `UniversalToYAMLConverter`.
- W `convert_to_yaml()`:
  - wykonać dotychczasowy flow,
  - **jeśli** `use_ai` → pobrać `AIExtractionResult` i wstrzyknąć do `structure["analysis"]["ai"]`.
- Upewnić się, że zapis YAML/JSON wciąż działa (PyYAML obsłuży nowe pola).

### 4.4 CLI i konfiguracja (`src/janusz/cli.py`)
- Dodać opcję globalną `--use-ai` (domyślnie `False`).
- Dodać obsługę zmiennej środowiskowej `JANUSZ_OPENROUTER_KEY` lub pliku konfiguracyjnego.
- Przekazać flagę do `UniversalToYAMLConverter`.

### 4.5 Zależności i bezpieczeństwo
- `pyproject.toml`: dodać klienta HTTP (np. `httpx>=0.27`) i ewentualnie SDK (jeśli użyjemy openrouter-official).
- Rozszerzyć `pyproject.toml` o sekcję `[tool.janusz.ai]` (opcjonalnie) z domyślnym modelem i parametrami.
- Dodać do dokumentacji instrukcję konfiguracji klucza OpenRouter.

### 4.6 Testy i walidacja
- Testy jednostkowe: mock OpenRouter → `tests/test_ai_content_analyzer.py`.
- Testy integracyjne: `janusz convert --use-ai` na przykładowych plikach (z mockiem).
- Walidacja YAML/JSON → `YAMLToTOONConverter` musi tolerować nowe pola.

## 5. Ryzyka i mitigacje

| Ryzyko | Mitigacja |
| --- | --- |
| Brak klucza OpenRouter | Fallback do heurystyk + czytelny komunikat |
| Koszt tokenów | Limit długości tekstu (chunking sekcji) + konfiguracja modelu |
| Opóźnienia API | Kolejkowanie żądań / caching wyników |
| Niespójne dane AI | Walidacja Pydantic + sanity checks (confidence thresholds) |

## 6. Następne kroki (priorytetyzowane)
1. **Model layer** (4.1) — wymagane, by móc przechowywać wyniki AI.
2. **AIContentAnalyzer + config** (4.2, 4.5).
3. **Integracja z converter + CLI flagi** (4.3, 4.4).
4. **Testy + dokumentacja** (4.6, README/AI_ENHANCEMENT_PLAN aktualizacja).

Plan jest w pełni zgodny z aktualnym stanem repozytorium i może być realizowany iteracyjnie bez blokowania pozostałych prac (GUI, RAG itp.).

