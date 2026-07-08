import asyncio
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from medbis_price_intelligence.config import AppConfig
from medbis_price_intelligence.database.repositories import (
    CompetitorRepository,
    MatchRepository,
    ProductRepository,
    RunRepository,
)
from medbis_price_intelligence.database.session import Database
from medbis_price_intelligence.importer.importer import ProductImporter
from medbis_price_intelligence.reports.excel import ExcelReportGenerator
from medbis_price_intelligence.services.price_search import PriceSearchService
from medbis_price_intelligence.settings import RuntimeSettings, SettingsService
from medbis_price_intelligence.ui.chart import BarChart
from medbis_price_intelligence.ui.theme import apply_theme


class MainWindow(ctk.CTk):
    """Main CustomTkinter desktop shell."""

    def __init__(self, config: AppConfig, database: Database) -> None:
        apply_theme()
        super().__init__()
        self.config = config
        self.database = database

        self.title(config.app_name)
        self.geometry("1180x720")
        self.minsize(980, 620)

        self.status_text = ctk.StringVar(value="Ready")
        self.product_count = ctk.StringVar(value="0")
        self.competitor_count = ctk.StringVar(value="0")
        self.import_count = ctk.StringVar(value="0")
        self.match_count = ctk.StringVar(value="0")
        self.scrape_count = ctk.StringVar(value="0")
        self.search_text = ctk.StringVar(value="")
        self.cache_days = ctk.StringVar(value="14")
        self.scraper_concurrency = ctk.StringVar(value="4")
        self.products_per_run = ctk.StringVar(value="3")

        self._ensure_competitors()
        self._build_layout()
        self.refresh_stats()

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(sidebar, text="MedBIS", font=ctk.CTkFont(size=28, weight="bold")).grid(
            row=0, column=0, padx=22, pady=(28, 2), sticky="w"
        )
        ctk.CTkLabel(sidebar, text="Price Intelligence").grid(
            row=1, column=0, padx=22, pady=(0, 28), sticky="w"
        )

        ctk.CTkButton(sidebar, text="Dashboard", command=self.refresh_stats).grid(
            row=2, column=0, padx=18, pady=8, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Import Products", command=self.import_products).grid(
            row=3, column=0, padx=18, pady=8, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Refresh", command=self.refresh_stats).grid(
            row=4, column=0, padx=18, pady=8, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Run Test Search", command=self.run_test_search).grid(
            row=5, column=0, padx=18, pady=8, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Run All Competitors", command=self.run_all_competitors).grid(
            row=6, column=0, padx=18, pady=8, sticky="ew"
        )
        ctk.CTkButton(sidebar, text="Export Report", command=self.export_report).grid(
            row=7, column=0, padx=18, pady=8, sticky="ew"
        )

        content = ctk.CTkFrame(self, corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure((0, 1, 2), weight=1)
        content.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(content, text="Dashboard", font=ctk.CTkFont(size=26, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=28, pady=(28, 8), sticky="w"
        )

        self._stat_card(content, "Products", self.product_count, 0)
        self._stat_card(content, "Competitors", self.competitor_count, 1)
        self._stat_card(content, "Imports", self.import_count, 2)
        self._stat_card(content, "Matches", self.match_count, 0, row=2)
        self._stat_card(content, "Search Runs", self.scrape_count, 1, row=2)

        toolbar = ctk.CTkFrame(content)
        toolbar.grid(row=3, column=0, columnspan=3, padx=28, pady=18, sticky="ew")
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_box = ctk.CTkEntry(toolbar, placeholder_text="Search and filtering")
        self.search_box.configure(textvariable=self.search_text)
        self.search_box.grid(row=0, column=0, padx=14, pady=14, sticky="ew")
        self.search_box.bind("<KeyRelease>", lambda _event: self.refresh_lists())
        ctk.CTkButton(toolbar, text="Import Excel/CSV", command=self.import_products).grid(
            row=0, column=1, padx=(0, 14), pady=14
        )

        tabs = ctk.CTkTabview(content)
        tabs.grid(row=4, column=0, columnspan=3, padx=28, pady=(0, 18), sticky="nsew")
        self.overview_tab = tabs.add("Overview")
        self.products_tab = tabs.add("Products")
        self.matches_tab = tabs.add("Matches")
        self.history_tab = tabs.add("History")
        self.settings_tab = tabs.add("Settings")
        self.logs_tab = tabs.add("Logs")
        self._build_tabs()

        status = ctk.CTkLabel(content, textvariable=self.status_text, anchor="w")
        status.grid(row=5, column=0, columnspan=3, padx=28, pady=(0, 18), sticky="ew")

    def _build_tabs(self) -> None:
        self.overview_tab.grid_columnconfigure((0, 1), weight=1)
        self.match_chart = BarChart(self.overview_tab, "Match Quality")
        self.match_chart.grid(row=0, column=0, padx=12, pady=12, sticky="new")
        self.run_chart = BarChart(self.overview_tab, "Run Activity")
        self.run_chart.grid(row=0, column=1, padx=12, pady=12, sticky="new")

        self.products_text = self._readonly_textbox(self.products_tab)
        self.matches_text = self._readonly_textbox(self.matches_tab)
        self.history_text = self._readonly_textbox(self.history_tab)
        self.logs_text = self._readonly_textbox(self.logs_tab)
        self._build_settings_tab()
        self.load_settings()
        self.refresh_logs()

    def _build_settings_tab(self) -> None:
        self.settings_tab.grid_columnconfigure(1, weight=1)
        fields = [
            ("Cache age days", self.cache_days),
            ("Scraper concurrency", self.scraper_concurrency),
            ("Products per run", self.products_per_run),
        ]
        for row, (label, variable) in enumerate(fields):
            ctk.CTkLabel(self.settings_tab, text=label).grid(
                row=row,
                column=0,
                padx=18,
                pady=12,
                sticky="w",
            )
            ctk.CTkEntry(self.settings_tab, textvariable=variable).grid(
                row=row,
                column=1,
                padx=18,
                pady=12,
                sticky="ew",
            )
        ctk.CTkButton(self.settings_tab, text="Save Settings", command=self.save_settings).grid(
            row=3,
            column=1,
            padx=18,
            pady=18,
            sticky="e",
        )

    def _readonly_textbox(self, parent: ctk.CTkFrame) -> ctk.CTkTextbox:
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        textbox = ctk.CTkTextbox(parent)
        textbox.grid(row=0, column=0, padx=12, pady=12, sticky="nsew")
        textbox.configure(state="disabled")
        return textbox

    def _stat_card(
        self,
        parent: ctk.CTkFrame,
        label: str,
        value: ctk.StringVar,
        column: int,
        row: int = 1,
    ) -> None:
        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=column, padx=28 if column == 0 else 8, pady=10, sticky="ew")
        ctk.CTkLabel(card, text=label).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        ctk.CTkLabel(card, textvariable=value, font=ctk.CTkFont(size=34, weight="bold")).grid(
            row=1, column=0, padx=18, pady=(0, 16), sticky="w"
        )

    def import_products(self) -> None:
        file_name = filedialog.askopenfilename(
            title="Import MedBIS product list",
            filetypes=[
                ("Excel files", "*.xlsx *.xls"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )
        if not file_name:
            return

        try:
            with self.database.session() as session:
                result = ProductImporter(session).import_file(Path(file_name))
            self.status_text.set(f"Imported {result.products_saved} products from {result.source_file.name}")
            self.refresh_stats()
            self.refresh_lists()
            messagebox.showinfo("Import complete", f"Imported {result.products_saved} products.")
        except Exception as exc:
            self.status_text.set("Import failed")
            messagebox.showerror("Import failed", str(exc))

    def run_test_search(self) -> None:
        """Run the first scraper integration without blocking the desktop UI."""
        self.status_text.set("Running Medisave and Medical World test search...")
        thread = threading.Thread(target=self._run_search_worker, args=(False,), daemon=True)
        thread.start()

    def run_all_competitors(self) -> None:
        """Run all configured competitor scrapers for the first few products."""
        self.status_text.set("Running all competitor scrapers...")
        thread = threading.Thread(target=self._run_search_worker, args=(True,), daemon=True)
        thread.start()

    def _run_search_worker(self, all_competitors: bool) -> None:
        try:
            with self.database.session() as session:
                service = PriceSearchService(session, all_competitors=all_competitors)
                saved = asyncio.run(service.run_first_products())
            self.after(0, lambda: self._test_search_finished(saved))
        except Exception as exc:
            self.after(0, lambda exc=exc: self._test_search_failed(exc))

    def _test_search_finished(self, saved: int) -> None:
        self.status_text.set(f"Test search complete. Saved {saved} matches.")
        self.refresh_stats()
        self.refresh_lists()
        messagebox.showinfo("Search complete", f"Saved {saved} competitor matches.")

    def _test_search_failed(self, exc: Exception) -> None:
        self.status_text.set("Test search failed")
        messagebox.showerror("Search failed", str(exc))

    def export_report(self) -> None:
        file_name = filedialog.asksaveasfilename(
            title="Export price intelligence report",
            defaultextension=".xlsx",
            filetypes=[("Excel workbook", "*.xlsx")],
            initialfile="medbis_price_intelligence_report.xlsx",
        )
        if not file_name:
            return

        try:
            with self.database.session() as session:
                output_path = ExcelReportGenerator(session).generate(Path(file_name))
            self.status_text.set(f"Report exported to {output_path.name}")
            messagebox.showinfo("Report exported", f"Created {output_path.name}")
        except Exception as exc:
            self.status_text.set("Report export failed")
            messagebox.showerror("Report export failed", str(exc))

    def load_settings(self) -> None:
        with self.database.session() as session:
            settings = SettingsService(session).load()
        self.cache_days.set(str(settings.cache_days))
        self.scraper_concurrency.set(str(settings.scraper_concurrency))
        self.products_per_run.set(str(settings.products_per_run))

    def save_settings(self) -> None:
        try:
            settings = RuntimeSettings(
                cache_days=int(self.cache_days.get()),
                scraper_concurrency=int(self.scraper_concurrency.get()),
                products_per_run=int(self.products_per_run.get()),
            )
            with self.database.session() as session:
                SettingsService(session).save(settings)
            self.status_text.set("Settings saved")
            messagebox.showinfo("Settings saved", "Settings saved successfully.")
        except ValueError:
            messagebox.showerror("Invalid settings", "Settings must be whole numbers.")

    def refresh_stats(self) -> None:
        with self.database.session() as session:
            products = ProductRepository(session).count()
            competitors = CompetitorRepository(session).count_enabled()
            run_repo = RunRepository(session)
            imports = run_repo.count_imports()
            scrapes = run_repo.count_scrapes()
            match_repo = MatchRepository(session)
            matches = match_repo.count()
            match_status_counts = match_repo.status_counts()
        self.product_count.set(str(products))
        self.competitor_count.set(str(competitors))
        self.import_count.set(str(imports))
        self.scrape_count.set(str(scrapes))
        self.match_count.set(str(matches))
        self.match_chart.set_data(match_status_counts)
        self.run_chart.set_data({"Imports": imports, "Searches": scrapes})
        self.refresh_lists()

    def refresh_lists(self) -> None:
        term = self.search_text.get().strip()
        with self.database.session() as session:
            products = (
                ProductRepository(session).search(term)
                if term
                else ProductRepository(session).recent()
            )
            matches = MatchRepository(session).recent()
            runs = RunRepository(session).recent()

        self._set_text(
            self.products_text,
            "\n".join(
                f"{product.sku or '-'} | {product.product_name} | {product.brand or '-'} | "
                f"{product.selling_price or '-'}"
                for product in products
            )
            or "No products found.",
        )
        self._set_text(
            self.matches_text,
            "\n".join(
                f"{row['product']} | {row['competitor']} | {row['price'] or '-'} | "
                f"{row['confidence']} | {row['status']}"
                for row in matches
            )
            or "No matches yet.",
        )
        self._set_text(
            self.history_text,
            "\n".join(
                f"{run.started_at} | {run.run_type} | {run.status} | {run.message or ''}"
                for run in runs
            )
            or "No run history yet.",
        )
        self.refresh_logs()

    def refresh_logs(self) -> None:
        if not self.config.log_file.exists():
            self._set_text(self.logs_text, "No log file yet.")
            return
        lines = self.config.log_file.read_text(encoding="utf-8", errors="replace").splitlines()
        self._set_text(self.logs_text, "\n".join(lines[-150:]) or "No log entries yet.")

    @staticmethod
    def _set_text(textbox: ctk.CTkTextbox, text: str) -> None:
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")
        textbox.insert("1.0", text)
        textbox.configure(state="disabled")

    def _ensure_competitors(self) -> None:
        with self.database.session() as session:
            CompetitorRepository(session).ensure_defaults()
