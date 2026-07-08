import customtkinter as ctk


class BarChart(ctk.CTkFrame):
    """Small dependency-free bar chart for dashboard summary counts."""

    def __init__(self, master: object, title: str) -> None:
        super().__init__(master)
        self.title = title
        self.grid_columnconfigure(0, weight=1)
        self._label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=15, weight="bold"))
        self._label.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")
        self._body = ctk.CTkFrame(self, fg_color="transparent")
        self._body.grid(row=1, column=0, padx=14, pady=(0, 12), sticky="ew")
        self._body.grid_columnconfigure(1, weight=1)

    def set_data(self, values: dict[str, int]) -> None:
        """Render horizontal bars for the provided values."""
        for child in self._body.winfo_children():
            child.destroy()

        if not values:
            ctk.CTkLabel(self._body, text="No data yet").grid(row=0, column=0, sticky="w")
            return

        maximum = max(values.values()) or 1
        for row, (label, value) in enumerate(values.items()):
            ctk.CTkLabel(self._body, text=label, width=110, anchor="w").grid(
                row=row, column=0, pady=4, sticky="w"
            )
            progress = ctk.CTkProgressBar(self._body)
            progress.set(value / maximum)
            progress.grid(row=row, column=1, padx=8, pady=4, sticky="ew")
            ctk.CTkLabel(self._body, text=str(value), width=34).grid(row=row, column=2, sticky="e")

