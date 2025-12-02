#!/usr/bin/env python3
"""
Janusz GUI Main Application

A desktop application for intelligent document processing with AI-powered analysis.
Provides an intuitive interface for converting documents to various formats with
advanced AI features.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import threading
import queue
import logging

# Check for tkinter availability
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    print("❌ tkinter not available. GUI requires tkinter.")
    print("Install on Ubuntu/Debian: sudo apt-get install python3-tk")
    print("Install on CentOS/RHEL: sudo yum install tkinter")
    print("Install on macOS: tkinter is included with Python from python.org")
    sys.exit(1)

# Add src to path for imports
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from janusz.converter import UniversalToYAMLConverter, process_directory
from janusz.models import DocumentStructure
from janusz.rag.rag_system import RAGSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JanuszGUI:
    """
    Main GUI application for Janusz document processing.

    Features:
    - File selection from knowledge base
    - Multiple output format support (YAML/JSON/TOON)
    - AI-powered analysis options
    - Real-time progress tracking
    - Modular schema generation
    - RAG integration
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧠 Janusz AI - Inteligentne przetwarzanie dokumentów")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        # Initialize variables
        self.selected_files: List[str] = []
        self.output_format = tk.StringVar(value="YAML")
        self.use_ai = tk.BooleanVar(value=False)
        self.ai_model = tk.StringVar(value="anthropic/claude-3-haiku")
        self.processing_queue = queue.Queue()
        self.is_processing = False

        # Initialize RAG system
        try:
            self.rag_system = RAGSystem()
            self.rag_available = True
        except Exception as e:
            logger.warning(f"RAG system not available: {e}")
            self.rag_system = None
            self.rag_available = False

        # Knowledge base directories
        self.knowledge_base_dirs = [
            "new",           # Current working directory
            "baza wiedzy 28.11"  # Knowledge base
        ]

        self.setup_ui()
        self.load_available_files()

    def setup_ui(self):
        """Setup the main user interface."""
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🧠 Janusz AI Document Processor",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # File selection section
        self.setup_file_selection(main_frame)

        # Output options section
        self.setup_output_options(main_frame)

        # AI features section
        self.setup_ai_features(main_frame)

        # Control buttons
        self.setup_control_buttons(main_frame)

        # Progress and log section
        self.setup_progress_section(main_frame)

    def setup_file_selection(self, parent):
        """Setup file selection interface."""
        # File selection frame
        file_frame = ttk.LabelFrame(parent, text="📁 Wybór plików", padding="10")
        file_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        # Directory selection
        ttk.Label(file_frame, text="Katalog:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.dir_var = tk.StringVar(value=self.knowledge_base_dirs[0])
        dir_combo = ttk.Combobox(file_frame, textvariable=self.dir_var,
                                values=self.knowledge_base_dirs, state="readonly", width=30)
        dir_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        dir_combo.bind('<<ComboboxSelected>>', self.on_directory_change)

        # Refresh button
        ttk.Button(file_frame, text="🔄 Odśwież", command=self.load_available_files).grid(row=0, column=2)

        # File list with checkboxes
        ttk.Label(file_frame, text="Dostępne pliki:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        # Scrollable frame for files
        file_list_frame = ttk.Frame(file_frame)
        file_list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))

        # Canvas and scrollbar for file list
        self.canvas = tk.Canvas(file_list_frame, height=200)
        scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store checkbox variables
        self.file_checkboxes: Dict[str, tk.BooleanVar] = {}

    def setup_output_options(self, parent):
        """Setup output format options."""
        output_frame = ttk.LabelFrame(parent, text="🎯 Format wyjściowy", padding="10")
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))

        formats = ["YAML", "JSON", "TOON"]
        for i, fmt in enumerate(formats):
            ttk.Radiobutton(output_frame, text=fmt, variable=self.output_format,
                           value=fmt).grid(row=i//2, column=i%2, sticky=tk.W, padx=(0, 20))

    def setup_ai_features(self, parent):
        """Setup AI features interface."""
        ai_frame = ttk.LabelFrame(parent, text="🤖 Funkcje AI", padding="10")
        ai_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # AI toggle
        ttk.Checkbutton(ai_frame, text="Włącz analizę AI", variable=self.use_ai,
                        command=self.toggle_ai_options).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # AI model selection (disabled by default)
        ttk.Label(ai_frame, text="Model AI:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.ai_model_combo = ttk.Combobox(ai_frame, textvariable=self.ai_model,
                                         values=["anthropic/claude-3-haiku", "openai/gpt-4", "meta-llama/llama-2-70b"],
                                         state="disabled", width=25)
        self.ai_model_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))

        # AI features buttons
        ai_buttons_frame = ttk.Frame(ai_frame)
        ai_buttons_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))

        ttk.Button(ai_buttons_frame, text="🎯 Optymalizuj prompty",
                  command=self.optimize_prompts, state="disabled").grid(row=0, column=0, padx=(0, 5))
        ttk.Button(ai_buttons_frame, text="📋 Generuj schematy",
                  command=self.generate_schemas, state="disabled").grid(row=0, column=1, padx=(5, 0))
        ttk.Button(ai_buttons_frame, text="🔍 RAG Przeszukiwanie",
                  command=self.rag_search, state="disabled").grid(row=1, column=0, columnspan=2, pady=(5, 0))

        self.ai_buttons = [child for child in ai_buttons_frame.winfo_children() if isinstance(child, ttk.Button)]

    def setup_control_buttons(self, parent):
        """Setup control buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(0, 10))

        self.convert_button = ttk.Button(button_frame, text="🚀 Konwertuj wybrane pliki",
                                       command=self.start_conversion)
        self.convert_button.grid(row=0, column=0, padx=(0, 10))

        ttk.Button(button_frame, text="🧠 Indeksuj do RAG",
                  command=self.index_to_rag).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(button_frame, text="📂 Wybierz katalog wyjściowy",
                  command=self.select_output_directory).grid(row=0, column=2, padx=(0, 10))

        ttk.Button(button_frame, text="⚙️ Ustawienia", command=self.show_settings).grid(row=0, column=3)

    def setup_progress_section(self, parent):
        """Setup progress tracking and logging."""
        progress_frame = ttk.LabelFrame(parent, text="📊 Postęp i logi", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.S), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        progress_frame.rowconfigure(0, weight=1)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(progress_frame, text="Gotowy do pracy")
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        # Log text area
        self.log_text = scrolledtext.ScrolledText(progress_frame, height=8, wrap=tk.WORD)
        self.log_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure text tags for different log levels
        self.log_text.tag_configure("INFO", foreground="black")
        self.log_text.tag_configure("SUCCESS", foreground="green")
        self.log_text.tag_configure("WARNING", foreground="orange")
        self.log_text.tag_configure("ERROR", foreground="red")

    def load_available_files(self):
        """Load and display available files from selected directory."""
        # Clear existing checkboxes
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.file_checkboxes.clear()

        directory = self.dir_var.get()
        if not os.path.exists(directory):
            self.log_message("WARNING", f"Katalog {directory} nie istnieje")
            return

        # Find all supported files
        supported_extensions = {".pdf", ".md", ".txt", ".docx", ".html"}
        available_files = []

        for ext in supported_extensions:
            pattern = f"**/*{ext}"
            try:
                files = list(Path(directory).glob(pattern))
                available_files.extend([str(f) for f in files])
            except Exception as e:
                self.log_message("WARNING", f"Błąd podczas przeszukiwania: {e}")

        if not available_files:
            ttk.Label(self.scrollable_frame, text="Brak plików do przetworzenia").grid(row=0, column=0)
            return

        # Create checkboxes for each file
        for i, file_path in enumerate(sorted(available_files)):
            var = tk.BooleanVar()
            self.file_checkboxes[file_path] = var

            cb = ttk.Checkbutton(self.scrollable_frame, text=os.path.basename(file_path),
                               variable=var)
            cb.grid(row=i, column=0, sticky=tk.W, padx=(0, 10))

            # File info label
            try:
                size = os.path.getsize(file_path)
                size_str = f"{size} bytes" if size < 1024 else f"{size//1024} KB"
                ttk.Label(self.scrollable_frame, text=size_str, foreground="gray").grid(row=i, column=1, sticky=tk.W)
            except:
                pass

        self.log_message("INFO", f"Znaleziono {len(available_files)} plików")

    def on_directory_change(self, event):
        """Handle directory selection change."""
        self.load_available_files()

    def toggle_ai_options(self):
        """Toggle AI-related UI elements."""
        state = "normal" if self.use_ai.get() else "disabled"

        self.ai_model_combo.config(state=state)
        for button in self.ai_buttons:
            button.config(state=state)

    def start_conversion(self):
        """Start the conversion process."""
        selected_files = [path for path, var in self.file_checkboxes.items() if var.get()]

        if not selected_files:
            messagebox.showwarning("Brak plików", "Wybierz przynajmniej jeden plik do konwersji.")
            return

        # Check if AI is enabled but no API key
        if self.use_ai.get():
            api_key = os.getenv("JANUSZ_OPENROUTER_API_KEY")
            if not api_key:
                result = messagebox.askyesno(
                    "Brak klucza API",
                    "AI jest włączone, ale nie znaleziono JANUSZ_OPENROUTER_API_KEY.\n"
                    "Czy chcesz kontynuować bez AI (tylko tradycyjna analiza)?"
                )
                if not result:
                    return
                self.use_ai.set(False)

        # Disable UI during processing
        self.convert_button.config(state="disabled", text="⏳ Przetwarzanie...")
        self.is_processing = True

        # Start processing in background thread
        processing_thread = threading.Thread(target=self.process_files, args=(selected_files,))
        processing_thread.daemon = True
        processing_thread.start()

        # Start progress monitoring
        self.root.after(100, self.check_processing_status)

    def process_files(self, file_paths: List[str]):
        """Process selected files in background thread."""
        try:
            total_files = len(file_paths)
            processed = 0

            self.processing_queue.put(("status", "Rozpoczynam przetwarzanie..."))

            for file_path in file_paths:
                if not self.is_processing:  # Allow cancellation
                    break

                self.processing_queue.put(("status", f"Przetwarzanie: {os.path.basename(file_path)}"))

                try:
                    # Create converter with AI settings
                    converter = UniversalToYAMLConverter(
                        file_path,
                        use_ai=self.use_ai.get(),
                        ai_model=self.ai_model.get()
                    )

                    # Convert to YAML first
                    success = converter.convert_to_yaml()

                    if success:
                        yaml_path = Path(file_path).with_suffix(".yaml")

                        # Convert to final format if needed
                        if self.output_format.get() == "JSON":
                            self.convert_yaml_to_json(yaml_path)
                        elif self.output_format.get() == "TOON":
                            self.convert_yaml_to_toon(yaml_path)

                        self.processing_queue.put(("log", f"✅ {os.path.basename(file_path)} - sukces"))
                    else:
                        self.processing_queue.put(("log", f"❌ {os.path.basename(file_path)} - błąd"))

                except Exception as e:
                    self.processing_queue.put(("log", f"❌ {os.path.basename(file_path)} - {str(e)}"))

                processed += 1
                progress = (processed / total_files) * 100
                self.processing_queue.put(("progress", progress))

            self.processing_queue.put(("status", "Przetwarzanie zakończone"))
            self.processing_queue.put(("done", True))

        except Exception as e:
            self.processing_queue.put(("error", str(e)))
            self.processing_queue.put(("done", True))

    def convert_yaml_to_json(self, yaml_path: Path):
        """Convert YAML to JSON format."""
        try:
            import yaml
            import json

            with open(yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            json_path = yaml_path.with_suffix(".json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.processing_queue.put(("log", f"Błąd konwersji do JSON: {e}"))

    def convert_yaml_to_toon(self, yaml_path: Path):
        """Convert YAML to TOON format."""
        try:
            from janusz.toon_adapter import YAMLToTOONConverter
            converter = YAMLToTOONConverter(str(yaml_path))
            converter.convert()
        except Exception as e:
            self.processing_queue.put(("log", f"Błąd konwersji do TOON: {e}"))

    def check_processing_status(self):
        """Check for processing updates from background thread."""
        try:
            while True:
                message = self.processing_queue.get_nowait()

                if message[0] == "progress":
                    self.progress_var.set(message[1])
                elif message[0] == "status":
                    self.status_label.config(text=message[1])
                elif message[0] == "log":
                    self.log_message("INFO", message[1])
                elif message[0] == "error":
                    self.log_message("ERROR", f"Błąd: {message[1]}")
                    messagebox.showerror("Błąd przetwarzania", message[1])
                elif message[0] == "done":
                    self.convert_button.config(state="normal", text="🚀 Konwertuj wybrane pliki")
                    self.is_processing = False
                    self.progress_var.set(100)
                    return

        except queue.Empty:
            pass

        if self.is_processing:
            self.root.after(100, self.check_processing_status)

    def optimize_prompts(self):
        """AI-powered prompt optimization (placeholder for future implementation)."""
        messagebox.showinfo("Funkcja w przygotowaniu",
                          "Optymalizacja promptów będzie dostępna w następnej wersji.")

    def generate_schemas(self):
        """Generate modular schemas (placeholder for future implementation)."""
        messagebox.showinfo("Funkcja w przygotowaniu",
                          "Generowanie schematów będzie dostępne w następnej wersji.")

    def rag_search(self):
        """RAG-powered search interface."""
        if not self.rag_available or not self.rag_system:
            messagebox.showerror("RAG niedostępny",
                               "System RAG nie jest dostępny. Sprawdź konfigurację.")
            return

        # Create RAG search dialog
        rag_window = tk.Toplevel(self.root)
        rag_window.title("🔍 RAG - Przeszukiwanie wiedzy")
        rag_window.geometry("700x500")

        # Question input
        ttk.Label(rag_window, text="Zadaj pytanie:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

        question_var = tk.StringVar()
        question_entry = ttk.Entry(rag_window, textvariable=question_var, width=60)
        question_entry.grid(row=0, column=1, padx=10, pady=5)

        # Search button
        search_button = ttk.Button(rag_window, text="Szukaj",
                                 command=lambda: self._perform_rag_search(question_var.get(), rag_window))
        search_button.grid(row=0, column=2, padx=10, pady=5)

        # Results area
        results_frame = ttk.Frame(rag_window)
        results_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=5)

        self.rag_results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=20)
        self.rag_results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        rag_window.columnconfigure(1, weight=1)
        rag_window.rowconfigure(1, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Initial status
        self.rag_results_text.insert(tk.END, f"System RAG gotowy. Zindeksowane dokumenty: {self.rag_system.get_statistics()['indexed_documents']}\n")
        self.rag_results_text.insert(tk.END, "Wpisz pytanie i kliknij 'Szukaj'...\n")

    def _perform_rag_search(self, question: str, window: tk.Toplevel):
        """Perform RAG search and display results."""
        if not question.strip():
            messagebox.showwarning("Puste pytanie", "Wpisz pytanie do wyszukania.")
            return

        # Clear previous results
        self.rag_results_text.delete(1.0, tk.END)
        self.rag_results_text.insert(tk.END, f"Szukam odpowiedzi na: '{question}'\n\n")
        window.update()

        try:
            # Perform RAG query
            response = self.rag_system.query(question, generate_answer=True)

            # Display results
            self.rag_results_text.insert(tk.END, "🤖 Odpowiedź:\n", "bold")
            self.rag_results_text.insert(tk.END, f"{response.answer}\n\n")

            self.rag_results_text.insert(tk.END, f"📊 Statystyki:\n")
            self.rag_results_text.insert(tk.END, f"• Poziom ufności: {response.confidence_score:.1%}\n")
            self.rag_results_text.insert(tk.END, f"• Czas przetwarzania: {response.processing_time:.2f}s\n")
            self.rag_results_text.insert(tk.END, f"• Liczba źródeł: {len(response.sources)}\n\n")

            if response.sources:
                self.rag_results_text.insert(tk.END, "📚 Źródła:\n", "bold")
                for i, source in enumerate(response.sources, 1):
                    self.rag_results_text.insert(tk.END, f"{i}. {source.metadata.get('title', 'Nieznany dokument')} ")
                    self.rag_results_text.insert(tk.END, f"(trafność: {source.score:.2f})\n")
                    self.rag_results_text.insert(tk.END, f"   {source.content[:200]}...\n\n")

        except Exception as e:
            self.rag_results_text.insert(tk.END, f"❌ Błąd podczas wyszukiwania: {str(e)}\n")

        # Configure text tags
        self.rag_results_text.tag_configure("bold", font=("TkDefaultFont", 10, "bold"))

    def index_to_rag(self):
        """Index selected documents to RAG system."""
        selected_files = [path for path, var in self.file_checkboxes.items() if var.get()]

        if not selected_files:
            messagebox.showwarning("Brak plików", "Wybierz przynajmniej jeden plik do indeksowania.")
            return

        if not self.rag_available or not self.rag_system:
            messagebox.showerror("RAG niedostępny",
                               "System RAG nie jest dostępny. Sprawdź konfigurację.")
            return

        # Disable UI during indexing
        self.convert_button.config(state="disabled")
        self.root.config(cursor="wait")

        try:
            indexed_count = 0

            for file_path in selected_files:
                try:
                    # Convert file to document structure first
                    converter = UniversalToYAMLConverter(file_path)
                    doc_structure = converter.parse_text_structure(converter.extract_text_from_file())

                    # Index to RAG
                    doc_id = self.rag_system.add_document(doc_structure)
                    indexed_count += 1

                    self.log_message("INFO", f"✅ Zindeksowano: {os.path.basename(file_path)} (ID: {doc_id})")

                except Exception as e:
                    self.log_message("ERROR", f"❌ Błąd indeksowania {os.path.basename(file_path)}: {str(e)}")

            messagebox.showinfo("Indeksowanie zakończone",
                              f"Pomyślnie zindeksowano {indexed_count} z {len(selected_files)} plików.")

        except Exception as e:
            messagebox.showerror("Błąd indeksowania", f"Wystąpił błąd podczas indeksowania: {str(e)}")

        finally:
            # Re-enable UI
            self.convert_button.config(state="normal")
            self.root.config(cursor="")

    def select_output_directory(self):
        """Select output directory."""
        directory = filedialog.askdirectory(title="Wybierz katalog wyjściowy")
        if directory:
            os.chdir(directory)
            self.log_message("INFO", f"Katalog wyjściowy zmieniony na: {directory}")

    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Ustawienia")
        settings_window.geometry("400x300")

        # API Key setting
        ttk.Label(settings_window, text="OpenRouter API Key:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        api_key_var = tk.StringVar(value=os.getenv("JANUSZ_OPENROUTER_API_KEY", ""))
        api_key_entry = ttk.Entry(settings_window, textvariable=api_key_var, width=40, show="*")
        api_key_entry.grid(row=0, column=1, padx=10, pady=5)

        def save_settings():
            api_key = api_key_var.get()
            if api_key:
                os.environ["JANUSZ_OPENROUTER_API_KEY"] = api_key
                messagebox.showinfo("Ustawienia", "Klucz API zapisany dla tej sesji.")
            settings_window.destroy()

        ttk.Button(settings_window, text="Zapisz", command=save_settings).grid(row=1, column=0, columnspan=2, pady=20)

    def log_message(self, level: str, message: str):
        """Add message to log with appropriate formatting."""
        self.log_text.insert(tk.END, f"[{level}] {message}\n", level)
        self.log_text.see(tk.END)
        logger.info(f"{level}: {message}")


def main():
    """Main entry point for the GUI application."""
    root = tk.Tk()
    app = JanuszGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
