#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AppSweeper v1.0.0
Smart Application Closer for macOS
https://github.com/yourusername/AppSweeper
"""

import subprocess
import threading
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# ─── Config ───────────────────────────────────────────────────────────────────

APP_NAME    = "AppSweeper"
APP_VERSION = "1.0.0"

PROTECTED_APPS = frozenset({
    "Finder", "Dock", "SystemUIServer", "WindowServer", "loginwindow",
    "NotificationCenter", "Spotlight", "Control Center",
    "System Preferences", "System Settings",
    APP_NAME,
    "universalaccessd", "SecurityAgent", "AirPlayUIAgent",
    "UserEventAgent", "coreauthd", "TextInputMenuAgent",
    "CoreServicesUIAgent", "ScreenSaverEngine", "KeyboardAccessAgent",
    "VoiceOver", "Accessibility Inspector", "talagent",
    "com.apple.dock.extra",
})

C = {
    "bg":      "#111111",
    "surface": "#1a1a1a",
    "surface2":"#202020",
    "border":  "#2b2b2b",
    "text":    "#eeeeee",
    "muted":   "#555555",
    "accent":  "#c0392b",
    "accent_h":"#a93226",
    "btn":     "#1e1e1e",
    "btn_h":   "#2a2a2a",
    "font":    "Helvetica Neue",
}

# ─── macOS helpers ────────────────────────────────────────────────────────────

def get_running_apps() -> list:
    script = (
        'tell application "System Events" to '
        'get name of every process whose background only is false'
    )
    try:
        r = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0:
            apps = [a.strip() for a in r.stdout.strip().split(",")]
            return sorted(
                [a for a in apps if a and a not in PROTECTED_APPS],
                key=str.lower
            )
    except Exception as e:
        print(f"[AppSweeper] error: {e}", file=sys.stderr)
    return []


def quit_app(name: str) -> bool:
    try:
        subprocess.run(
            ["osascript", "-e", f'tell application "{name}" to quit'],
            capture_output=True, timeout=8
        )
        return True
    except Exception:
        return False

# ─── UI helpers ───────────────────────────────────────────────────────────────

def lbl_btn(parent, text, cmd, bg, fg="#eeeeee",
            hover=None, pady=10, padx=14, size=12, bold=False):
    """tk.Label styled as a button — works correctly on macOS unlike tk.Button."""
    weight = "bold" if bold else "normal"
    lbl = tk.Label(parent, text=text, bg=bg, fg=fg,
                   font=(C["font"], size, weight),
                   padx=padx, pady=pady, cursor="hand2")
    _hover = hover or bg
    lbl.bind("<Button-1>", lambda e: cmd())
    lbl.bind("<Enter>",    lambda e: lbl.configure(bg=_hover))
    lbl.bind("<Leave>",    lambda e: lbl.configure(bg=bg))
    return lbl

# ─── Main App ─────────────────────────────────────────────────────────────────

class AppSweeper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("455x610")
        self.configure(bg=C["bg"])
        self.resizable(True, True)
        self.minsize(370, 490)
        self.app_vars = {}
        self._setup_ttk()
        self._build()
        self.do_refresh()

    # ── Style ──────────────────────────────────────────────────────────────────

    def _setup_ttk(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Dark.TCheckbutton",
                    background=C["surface"],
                    foreground=C["text"],
                    font=(C["font"], 12))
        s.map("Dark.TCheckbutton",
              background=[("active", C["surface"]), ("!active", C["surface"])],
              foreground=[("active", C["text"])])
        s.configure("Alt.TCheckbutton",
                    background=C["surface2"],
                    foreground=C["text"],
                    font=(C["font"], 12))
        s.map("Alt.TCheckbutton",
              background=[("active", C["surface2"]), ("!active", C["surface2"])],
              foreground=[("active", C["text"])])
        s.configure("Vertical.TScrollbar",
                    background=C["surface"], troughcolor=C["bg"],
                    bordercolor=C["bg"], arrowcolor=C["muted"],
                    lightcolor=C["surface"], darkcolor=C["surface"])
        s.map("Vertical.TScrollbar",
              background=[("active", C["surface2"])])

    # ── Layout ─────────────────────────────────────────────────────────────────

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=C["bg"])
        hdr.pack(fill=tk.X, padx=22, pady=(22, 2))

        tk.Label(hdr, text=APP_NAME,
                 font=(C["font"], 26, "bold"),
                 bg=C["bg"], fg=C["text"]).pack(side=tk.LEFT)
        tk.Label(hdr, text=f" v{APP_VERSION}",
                 font=(C["font"], 12),
                 bg=C["bg"], fg=C["muted"]).pack(side=tk.LEFT, pady=(10, 0))

        tk.Label(self,
                 text="Select apps to close  ·  System processes are always protected",
                 font=(C["font"], 11),
                 bg=C["bg"], fg=C["muted"], anchor=tk.W
                 ).pack(fill=tk.X, padx=22, pady=(2, 14))

        # Panel (bordered card)
        panel_outer = tk.Frame(self, bg=C["border"])
        panel_outer.pack(fill=tk.BOTH, expand=True, padx=22)
        panel = tk.Frame(panel_outer, bg=C["surface"])
        panel.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Panel top bar
        ph = tk.Frame(panel, bg=C["surface"])
        ph.pack(fill=tk.X)

        self.panel_title = tk.Label(
            ph, text="Running Apps",
            font=(C["font"], 12, "bold"),
            bg=C["surface"], fg=C["text"], padx=14, pady=12)
        self.panel_title.pack(side=tk.LEFT)

        lbl_btn(ph, "↺  Refresh", self._refresh_thread,
                bg=C["surface"], fg=C["muted"],
                hover=C["surface2"], pady=10, padx=12, size=11
                ).pack(side=tk.RIGHT, padx=4)

        # Divider
        tk.Frame(panel, bg=C["border"], height=1).pack(fill=tk.X)

        # Scrollable list
        sw = tk.Frame(panel, bg=C["surface"])
        sw.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(sw, bg=C["surface"], bd=0, highlightthickness=0)
        sb = ttk.Scrollbar(sw, orient=tk.VERTICAL,
                           command=self.canvas.yview,
                           style="Vertical.TScrollbar")
        self.list_frame = tk.Frame(self.canvas, bg=C["surface"])
        self.win_id = self.canvas.create_window(
            (0, 0), window=self.list_frame, anchor=tk.NW)

        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_frame.bind("<Configure>", self._on_frame_cfg)
        self.canvas.bind("<Configure>",     self._on_canvas_cfg)
        self.canvas.bind_all("<MouseWheel>", self._on_scroll)

        # Controls
        ctrl = tk.Frame(self, bg=C["bg"])
        ctrl.pack(fill=tk.X, padx=22, pady=14)

        sel_row = tk.Frame(ctrl, bg=C["bg"])
        sel_row.pack(fill=tk.X, pady=(0, 10))

        lbl_btn(sel_row, "Select All", self.sel_all,
                bg=C["bg"], fg=C["muted"], hover=C["btn"],
                pady=6, padx=0, size=11).pack(side=tk.LEFT)
        tk.Label(sel_row, text="   ·   ",
                 bg=C["bg"], fg=C["muted"],
                 font=(C["font"], 11)).pack(side=tk.LEFT)
        lbl_btn(sel_row, "Deselect All", self.sel_none,
                bg=C["bg"], fg=C["muted"], hover=C["btn"],
                pady=6, padx=0, size=11).pack(side=tk.LEFT)

        # Primary CTA
        lbl_btn(ctrl, "  Close Selected Apps  ",
                self.close_selected,
                bg=C["accent"], fg="white", hover=C["accent_h"],
                pady=13, padx=16, size=14, bold=True
                ).pack(fill=tk.X, pady=(0, 8))

        # Secondary CTA
        lbl_btn(ctrl, "Close All Non-System Apps",
                self.close_all,
                bg=C["btn"], fg=C["text"], hover=C["btn_h"],
                pady=10, padx=14, size=12
                ).pack(fill=tk.X)

        # Status bar
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var,
                 font=(C["font"], 10),
                 bg=C["bg"], fg=C["muted"]).pack(pady=(6, 12))

    # ── Scroll ─────────────────────────────────────────────────────────────────

    def _on_frame_cfg(self, _):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_cfg(self, e):
        self.canvas.itemconfig(self.win_id, width=e.width)

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    # ── App list ───────────────────────────────────────────────────────────────

    def do_refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        self.app_vars.clear()

        apps = get_running_apps()

        if not apps:
            tk.Label(self.list_frame,
                     text="No closable apps found.",
                     font=(C["font"], 12),
                     bg=C["surface"], fg=C["muted"], pady=24).pack()
        else:
            for i, app in enumerate(apps):
                var = tk.BooleanVar(value=False)
                self.app_vars[app] = var
                is_alt   = i % 2 != 0
                row_bg   = C["surface2"] if is_alt else C["surface"]
                cb_style = "Alt.TCheckbutton" if is_alt else "Dark.TCheckbutton"

                row = tk.Frame(self.list_frame, bg=row_bg)
                row.pack(fill=tk.X)

                ttk.Checkbutton(
                    row, text=f"  {app}",
                    variable=var, style=cb_style
                ).pack(anchor=tk.W, padx=10, pady=7)

        n = len(apps)
        self.panel_title.configure(text=f"Running Apps  ({n})")
        self.status_var.set(
            f"🛡  {len(PROTECTED_APPS)} system processes protected")

    def _refresh_thread(self):
        self.status_var.set("Refreshing…")
        threading.Thread(target=self.do_refresh, daemon=True).start()

    # ── Selection ──────────────────────────────────────────────────────────────

    def sel_all(self):
        for v in self.app_vars.values(): v.set(True)

    def sel_none(self):
        for v in self.app_vars.values(): v.set(False)

    # ── Close ──────────────────────────────────────────────────────────────────

    def close_selected(self):
        chosen = [a for a, v in self.app_vars.items() if v.get()]
        if not chosen:
            messagebox.showinfo(APP_NAME, "Please select at least one app.")
            return
        names = "\n".join(f"• {a}" for a in chosen)
        if messagebox.askyesno(
            f"Close {len(chosen)} App(s)?",
            f"Quit the following?\n\n{names}",
        ):
            threading.Thread(
                target=self._run_close, args=(chosen,), daemon=True).start()

    def close_all(self):
        apps = list(self.app_vars.keys())
        if not apps:
            messagebox.showinfo(APP_NAME, "No apps to close.")
            return
        if messagebox.askyesno(
            f"Close All {len(apps)} Apps?",
            f"Quit all {len(apps)} non-system app(s)?",
        ):
            threading.Thread(
                target=self._run_close, args=(apps,), daemon=True).start()

    def _run_close(self, apps):
        total = len(apps)
        for i, app in enumerate(apps, 1):
            self.status_var.set(f"Closing {app}…  ({i}/{total})")
            quit_app(app)
        self.status_var.set(f"✓  {total} app(s) closed.")
        self.after(800, self.do_refresh)

# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    AppSweeper().mainloop()
