"""Shared fonts, colours and output folder for the profile SVGs."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"
SANS = "'Segoe UI', Inter, -apple-system, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'Cascadia Mono', Consolas, 'SF Mono', Menlo, monospace"

THEMES = {
    "light": dict(bg="#ffffff", ink="#0f172a", soft="#5b6475", faint="#8a93a6", dot="#dfe4ee",
                  accent="#2450e0", accentbg="#e8eeff", panel="#f6f8fc", border="#dfe4ee",
                  hl="#ffd84d", hlink="#0f172a"),
    "dark": dict(bg="#0d1117", ink="#e6edf3", soft="#a3acb9", faint="#7d8590", dot="#1f2632",
                 accent="#7b9bff", accentbg="#16224a", panel="#141a23", border="#262f3d",
                 hl="#ffd84d", hlink="#0f172a"),
}
