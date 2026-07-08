import customtkinter as ctk


def apply_theme() -> None:
    """Apply the default desktop appearance."""
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

