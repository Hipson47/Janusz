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

        # RAG button - available when RAG system is ready
        rag_button = ttk.Button(ai_buttons_frame, text="🔍 RAG Przeszukiwanie",
                              command=self.rag_search)
        rag_button.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        # Enable RAG button if RAG is available
        if self.rag_available:
            rag_button.config(state="normal")
        else:
            rag_button.config(state="disabled")

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
        """Advanced RAG-powered search interface."""
        if not self.rag_available or not self.rag_system:
            messagebox.showerror("RAG niedostępny",
                               "System RAG nie jest dostępny. Sprawdź konfigurację.")
            return

        # Create advanced RAG search dialog
        rag_window = tk.Toplevel(self.root)
        rag_window.title("🔍 RAG - Inteligentne przeszukiwanie wiedzy")
        rag_window.geometry("900x700")
        rag_window.resizable(True, True)

        # Initialize search history
        if not hasattr(self, 'rag_search_history'):
            self.rag_search_history = []

        # Main container
        main_frame = ttk.Frame(rag_window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        rag_window.columnconfigure(0, weight=1)
        rag_window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="🤖 Inteligentne przeszukiwanie wiedzy",
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 15))

        # Question input section
        self._create_question_section(main_frame, rag_window)

        # Settings section
        self._create_settings_section(main_frame)

        # Results section
        self._create_results_section(main_frame, rag_window)

        # Stats section
        self._create_stats_section(main_frame)

        # Configure final layout
        main_frame.rowconfigure(3, weight=1)  # Results section expands

    def _create_question_section(self, parent, window):
        """Create the question input section."""
        question_frame = ttk.LabelFrame(parent, text="❓ Zadaj pytanie", padding="10")
        question_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        question_frame.columnconfigure(1, weight=1)

        # Question input with history
        ttk.Label(question_frame, text="Pytanie:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))

        # Question entry with dropdown history
        self.question_var = tk.StringVar()
        question_entry = ttk.Entry(question_frame, textvariable=self.question_var, width=50)
        question_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))

        # History dropdown
        if self.rag_search_history:
            history_combo = ttk.Combobox(question_frame, values=self.rag_search_history[-10:],
                                       state="readonly", width=20)
            history_combo.grid(row=0, column=2, padx=(5, 0))
            history_combo.bind('<<ComboboxSelected>>',
                             lambda e: self.question_var.set(history_combo.get()))

        # Control buttons
        button_frame = ttk.Frame(question_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))

        search_button = ttk.Button(button_frame, text="🔍 Szukaj",
                                 command=lambda: self._perform_advanced_rag_search(window))
        search_button.grid(row=0, column=0, padx=(0, 5))

        clear_button = ttk.Button(button_frame, text="🗑️ Wyczyść",
                                command=self._clear_rag_results)
        clear_button.grid(row=0, column=1, padx=(0, 5))

        # Bind Enter key to search
        question_entry.bind('<Return>', lambda e: self._perform_advanced_rag_search(window))

    def _create_settings_section(self, parent):
        """Create the settings section."""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Ustawienia", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Max results setting
        ttk.Label(settings_frame, text="Maks. wyników:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.max_results_var = tk.IntVar(value=5)
        max_results_spin = tk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.max_results_var, width=5)
        max_results_spin.grid(row=0, column=1, padx=(0, 15))

        # AI generation toggle
        self.use_ai_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Generuj odpowiedź AI", variable=self.use_ai_var).grid(
            row=0, column=2, sticky=tk.W, padx=(0, 15))

        # Show sources toggle
        self.show_sources_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, text="Pokaż źródła", variable=self.show_sources_var).grid(
            row=0, column=3, sticky=tk.W)

    def _create_results_section(self, parent, window):
        """Create the results section."""
        results_frame = ttk.LabelFrame(parent, text="📋 Wyniki", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results text area with better formatting
        self.rag_results_text = scrolledtext.ScrolledText(
            results_frame, wrap=tk.WORD, height=15,
            font=("Consolas", 10)  # Monospace for better formatting
        )
        self.rag_results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure text tags for different content types
        self.rag_results_text.tag_configure("title", font=("Consolas", 12, "bold"), foreground="blue")
        self.rag_results_text.tag_configure("answer", font=("Consolas", 10), foreground="black")
        self.rag_results_text.tag_configure("source", font=("Consolas", 9), foreground="green")
        self.rag_results_text.tag_configure("metadata", font=("Consolas", 8), foreground="gray")
        self.rag_results_text.tag_configure("error", font=("Consolas", 10), foreground="red")
        self.rag_results_text.tag_configure("success", font=("Consolas", 10), foreground="green")

    def _create_stats_section(self, parent):
        """Create the statistics section."""
        stats_frame = ttk.LabelFrame(parent, text="📊 Statystyki", padding="5")
        stats_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

        # Stats labels
        self.stats_labels = {}
        stats_items = [
            ("indexed_docs", "Zindeksowane dokumenty:"),
            ("query_count", "Wykonane zapytania:"),
            ("avg_confidence", "Średnia ufność:"),
            ("last_query_time", "Czas ostatniego zapytania:")
        ]

        for i, (key, label) in enumerate(stats_items):
            ttk.Label(stats_frame, text=label).grid(row=0, column=i*2, sticky=tk.W, padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_frame, text="-")
            self.stats_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=(0, 15))

        # Update initial stats
        self._update_rag_stats()

    def _perform_advanced_rag_search(self, window):
        """Perform advanced RAG search with enhanced UI feedback."""
        question = self.question_var.get().strip()

        if not question:
            messagebox.showwarning("Brak pytania", "Wpisz pytanie do wyszukania.")
            return

        # Add to history
        if question not in self.rag_search_history:
            self.rag_search_history.append(question)
            if len(self.rag_search_history) > 20:  # Keep only last 20
                self.rag_search_history = self.rag_search_history[-20:]

        # Clear previous results
        self.rag_results_text.delete(1.0, tk.END)

        # Show searching message
        self.rag_results_text.insert(tk.END, f"🔍 Przeszukuję wiedzę na temat: '{question}'\n\n", "title")
        self.rag_results_text.insert(tk.END, "⏳ Analizuję dostępne dokumenty...\n\n")
        window.update()

        try:
            # Perform RAG query
            response = self.rag_system.query(
                question=question,
                max_results=self.max_results_var.get(),
                generate_answer=self.use_ai_var.get()
            )

            # Update stats
            self._update_rag_stats()

            # Clear and show results
            self.rag_results_text.delete(1.0, tk.END)

            # Question
            self.rag_results_text.insert(tk.END, f"❓ Pytanie: {question}\n\n", "title")

            # Answer
            if response.answer:
                self.rag_results_text.insert(tk.END, "🤖 Odpowiedź:\n", "title")
                self.rag_results_text.insert(tk.END, f"{response.answer}\n\n", "answer")

            # Statistics
            self.rag_results_text.insert(tk.END, "📊 Statystyki zapytania:\n", "title")
            self.rag_results_text.insert(tk.END, ".1f"            self.rag_results_text.insert(tk.END, f"• Czas przetwarzania: {response.processing_time:.2f}s\n")
            self.rag_results_text.insert(tk.END, f"• Liczba źródeł: {len(response.sources)}\n\n")

            # Sources (if enabled)
            if self.show_sources_var.get() and response.sources:
                self.rag_results_text.insert(tk.END, "📚 Źródła:\n", "title")

                for i, source in enumerate(response.sources, 1):
                    self.rag_results_text.insert(tk.END, f"{i}. ", "source")
                    self.rag_results_text.insert(tk.END, f"{source.metadata.get('title', 'Nieznany dokument')} ", "source")
                    self.rag_results_text.insert(tk.END, f"(trafność: {source.score:.2f})\n", "metadata")

                    # Show content preview
                    content_preview = source.content[:300] + "..." if len(source.content) > 300 else source.content
                    self.rag_results_text.insert(tk.END, f"   {content_preview}\n\n", "answer")

                    # Show highlights if available
                    if source.highlights:
                        self.rag_results_text.insert(tk.END, "   🔍 Podświetlenia: ", "metadata")
                        highlights_text = " | ".join(source.highlights[:3])
                        self.rag_results_text.insert(tk.END, f"{highlights_text}\n", "metadata")

            # Success message
            self.rag_results_text.insert(tk.END, "✅ Wyszukiwanie zakończone pomyślnie", "success")

        except Exception as e:
            self.rag_results_text.insert(tk.END, f"❌ Błąd podczas wyszukiwania: {str(e)}", "error")
            logger.error(f"RAG search error: {e}")

    def _clear_rag_results(self):
        """Clear RAG search results."""
        if hasattr(self, 'rag_results_text'):
            self.rag_results_text.delete(1.0, tk.END)
            self.rag_results_text.insert(tk.END, "Wyniki zostały wyczyszczone. Wpisz nowe pytanie i kliknij 'Szukaj'.\n")

    def _update_rag_stats(self):
        """Update RAG statistics display."""
        if not hasattr(self, 'stats_labels') or not self.rag_available or not self.rag_system:
            return

        try:
            stats = self.rag_system.get_statistics()

            self.stats_labels["indexed_docs"].config(text=str(stats.get("indexed_documents", 0)))
            self.stats_labels["query_count"].config(text=str(stats.get("query_count", 0)))

            # Average confidence (placeholder - would need to track this)
            self.stats_labels["avg_confidence"].config(text="N/A")

            # Last query time (placeholder)
            self.stats_labels["last_query_time"].config(text="N/A")

        except Exception as e:
            logger.error(f"Failed to update RAG stats: {e}")

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
