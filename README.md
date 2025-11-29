# AI Agent Knowledge Base Pipeline

Automatyczne przetwarzanie dokumentów do formatu TOON (Token-Oriented Object Notation) dla efektywnych promptów AI agentów.

## 🎯 Co to robi

Ten projekt konwertuje dokumenty w różnych formatach na zoptymalizowany format TOON, który jest idealny do:
- Prompt engineering dla AI agentów
- Kompaktowego przechowywania wiedzy
- Efektywnego wykorzystania tokenów w modelach LLM

## 📋 Obsługiwane formaty

| Format | Rozszerzenie | Wymagania |
|--------|-------------|-----------|
| PDF | `.pdf` | `pdfplumber` |
| Markdown | `.md` | - |
| Plain Text | `.txt` | - |
| DOCX | `.docx` | `python-docx` (opcjonalne) |
| HTML | `.html` | `html2text` lub `beautifulsoup4` (opcjonalne) |
| RTF | `.rtf` | (zarezerwowane) |
| EPUB | `.epub` | (zarezerwowane) |

## 🚀 Szybki start

### Pełny pipeline jednym poleceniem

```bash
# Uruchom cały proces: Dokumenty → YAML → TOON
./toon.sh
# lub
make toon
```

### Krok po kroku

```bash
# 1. Konwersja dokumentów do YAML
make yaml
# lub
python pdf_yaml_converter.py

# 2. Konwersja YAML do TOON
make yaml-to-toon
# lub
python toon.py
```

### Pojedynczy plik

```bash
# Konwersja konkretnego pliku
python pdf_yaml_converter.py --file "dokument.md"
python toon.py --file "dokument.yaml"
```

## 📁 Struktura projektu

```
📁 Architekt cursor/
├── 📄 *.md              # Pliki źródłowe (dokumenty)
├── 🎯 *.toon            # Pliki docelowe (dla AI agentów)
├── 🛠️ pdf_yaml_converter.py  # Konwerter dokumentów
├── 🛠️ toon.py          # Konwerter YAML → TOON
├── 🛠️ Makefile         # Komendy make
├── 🛠️ toon.sh          # Skrypt bash pipeline
├── 📁 baza wiedzy 28.11/  # Dodatkowa wiedza
└── 📄 README.md         # Ten plik
```

## 🛠️ Wymagania

### Wymagane
```bash
pip install pdfplumber pyyaml
```

### Opcjonalne (dla dodatkowych formatów)
```bash
pip install python-docx html2text beautifulsoup4
```

### Narzędzia TOON
- [TOON CLI](https://github.com/your-toon-repo) - wymagane do konwersji do formatu TOON

## 📖 Szczegółowe komendy

```bash
# Pokaż dostępne komendy
make help

# Konwertuj tylko dokumenty do YAML
make yaml

# Konwertuj tylko YAML do TOON
make yaml-to-toon

# Wyczyść wygenerowane pliki
make clean
```

## 🔧 Jak to działa

1. **Ekstrakcja tekstu** - z dokumentów w różnych formatach
2. **Parsowanie struktury** - identyfikacja sekcji, nagłówków, wzorców
3. **Analiza treści** - ekstrakcja kluczowych koncepcji i przykładów
4. **Konwersja do YAML** - strukturalny format z metadanymi
5. **Optymalizacja do TOON** - kompaktowy format dla AI

## 📊 Przykład struktury wyjściowej

```yaml
metadata:
  title: "Nazwa dokumentu"
  source: "plik.md"
  source_type: "markdown"
  converted_by: "Universal Document to YAML Converter"
  format_version: "2.0"
content:
  sections:
    - title: "# Nagłówek"
      content: ["Treść sekcji"]
      subsections: []
  raw_text: "Pełny tekst dokumentu"
analysis:
  keywords: ["słowa", "kluczowe"]
  best_practices: ["Zalecenia"]
  examples: ["Przykłady"]
```

## 🤝 Przyczynianie się

1. Dodaj obsługę nowych formatów w `pdf_yaml_converter.py`
2. Popraw parsowanie dla istniejących formatów
3. Dodaj testy i walidację
4. Aktualizuj dokumentację

## 📄 Licencja

Projekt otwarty - użyj jak chcesz!

## 🔗 Powiązane projekty

- [TOON Format](https://github.com/toon-format) - Token-Oriented Object Notation
- [Cursor IDE](https://cursor.sh) - IDE z integracją AI

## 📄 Licencja

Ten projekt jest dostępny na licencji MIT - zobacz plik [LICENSE](LICENSE) po szczegóły.

Licencja MIT pozwala na:
- ✅ Używanie komercyjne
- ✅ Modyfikację
- ✅ Dystrybucję
- ✅ Używanie prywatne

Z obowiązkiem zachowania informacji o autorze i licencji.
