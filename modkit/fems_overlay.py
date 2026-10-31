"""F8-triggered Steam-style companion overlay for the supported game build."""
import ctypes
import json
import os
import sys
import tkinter as tk
import webbrowser
from ctypes import wintypes
from io import BytesIO
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

HERE = (Path(sys.executable).resolve().parent if getattr(sys, "frozen", False)
        else Path(__file__).resolve().parent)
sys.path.insert(0, str(HERE))
from fedklib import __version__
from fedklib import manager, mods


USER32 = ctypes.windll.user32
KERNEL32 = ctypes.windll.kernel32
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
VK_F8 = 0x77
GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
HWND_TOPMOST = wintypes.HWND(-1)
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
SWP_FRAMECHANGED = 0x0020
WM_MOUSEACTIVATE = 0x0021
MA_NOACTIVATE = 3
GA_ROOT = 2
_get_window_long = getattr(USER32, "GetWindowLongPtrW", USER32.GetWindowLongW)
_set_window_long = getattr(USER32, "SetWindowLongPtrW", USER32.SetWindowLongW)
_get_window_long.argtypes = (wintypes.HWND, ctypes.c_int)
_get_window_long.restype = ctypes.c_ssize_t
_set_window_long.argtypes = (wintypes.HWND, ctypes.c_int, ctypes.c_ssize_t)
_set_window_long.restype = ctypes.c_ssize_t
USER32.SetWindowPos.argtypes = (wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int,
                                ctypes.c_int, ctypes.c_int, wintypes.UINT)
USER32.SetWindowPos.restype = wintypes.BOOL
USER32.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
USER32.GetAncestor.restype = wintypes.HWND
COMCTL32 = ctypes.WinDLL("comctl32")
SUBCLASS_PROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t, wintypes.HWND, wintypes.UINT,
    ctypes.c_size_t, ctypes.c_ssize_t, ctypes.c_size_t, ctypes.c_size_t,
)
COMCTL32.SetWindowSubclass.argtypes = (wintypes.HWND, SUBCLASS_PROC, ctypes.c_size_t, ctypes.c_size_t)
COMCTL32.SetWindowSubclass.restype = wintypes.BOOL
COMCTL32.DefSubclassProc.argtypes = (wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t)
COMCTL32.DefSubclassProc.restype = ctypes.c_ssize_t
KERNEL32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
KERNEL32.OpenProcess.restype = wintypes.HANDLE
KERNEL32.CloseHandle.argtypes = (wintypes.HANDLE,)
KERNEL32.CloseHandle.restype = wintypes.BOOL
KERNEL32.QueryFullProcessImageNameW.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD))
KERNEL32.QueryFullProcessImageNameW.restype = wintypes.BOOL
USER32.IsWindowVisible.argtypes = (wintypes.HWND,)
USER32.IsWindowVisible.restype = wintypes.BOOL
USER32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
USER32.GetWindowThreadProcessId.restype = wintypes.DWORD
USER32.GetWindowRect.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.RECT))
USER32.GetWindowRect.restype = wintypes.BOOL
USER32.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
USER32.GetWindowTextW.restype = ctypes.c_int
USER32.GetForegroundWindow.restype = wintypes.HWND
USER32.GetAsyncKeyState.argtypes = (ctypes.c_int,)
USER32.GetAsyncKeyState.restype = ctypes.c_short
KERNEL32.GetCurrentProcessId.restype = wintypes.DWORD


def profile_path():
    doc = json.loads((HERE / "fems_supported_build.json").read_text(encoding="utf-8"))
    return (HERE / doc["project"]).resolve()


def _process_image(pid):
    handle = KERNEL32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return ""
    try:
        size = wintypes.DWORD(32768)
        buf = ctypes.create_unicode_buffer(size.value)
        if KERNEL32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return buf.value
    except Exception:
        pass
    finally:
        KERNEL32.CloseHandle(handle)
    return ""


def find_game_window():
    found = []
    enum_cb = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    USER32.EnumWindows.argtypes = (enum_cb, wintypes.LPARAM)
    USER32.EnumWindows.restype = wintypes.BOOL

    def visit(hwnd, _):
        if not USER32.IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        image = _process_image(pid.value)
        if image and Path(image).name.casefold() == "false echo.exe":
            rect = wintypes.RECT()
            if USER32.GetWindowRect(hwnd, ctypes.byref(rect)):
                title = ctypes.create_unicode_buffer(512)
                USER32.GetWindowTextW(hwnd, title, len(title))
                found.append((hwnd, pid.value, (rect.left, rect.top, rect.right, rect.bottom), title.value))
        return True

    USER32.EnumWindows(enum_cb(visit), 0)
    return found[0] if found else None


class FemsOverlay:
    def __init__(self):
        self.profile = profile_path()
        self.root = tk.Tk()
        self.root.withdraw()
        self.root.title("FEMS Overlay")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.90)
        self.root.configure(bg="#0b1118")
        self.dimmer = tk.Toplevel(self.root)
        self.dimmer.withdraw()
        self.dimmer.overrideredirect(True)
        self.dimmer.attributes("-topmost", True)
        self.dimmer.attributes("-alpha", 0.18)
        self.dimmer.configure(bg="#020406")
        self.visible = False
        self.f8_was_down = False
        self.ever_seen_game = False
        self.rows = {}
        self.selected_file = None
        self.preview_image = None
        self._mouse_activate_proc = SUBCLASS_PROC(self._subclass_window_proc)
        self._build_ui()
        self.root.after(35, self._poll)

    def _build_ui(self):
        bg, panel, panel_hi = "#111b26", "#1a2a38", "#213545"
        text, muted, accent, border = "#f0f5f9", "#afbfcb", "#a7cfe7", "#587184"
        # Tk font descriptions need braces around family names containing spaces.
        self.root.option_add("*Font", "{Segoe UI} 10")
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("FEMS.Treeview", background=panel, fieldbackground=panel, foreground=text,
                        rowheight=36, borderwidth=0, font=("Segoe UI", 10))
        style.map("FEMS.Treeview", background=[("selected", "#214c68")], foreground=[("selected", "#ffffff")])
        style.configure("FEMS.Treeview.Heading", background=panel_hi, foreground=muted,
                        relief="flat", font=("Segoe UI", 8, "bold"))

        self.status = tk.Label(self.root, text="", anchor="w", padx=18, pady=6,
                               fg="#f1d9aa", bg="#51452f", font=("Segoe UI", 9, "bold"))
        # The restart notice appears only when there is a queued change.

        workspace = tk.Frame(self.root, bg=bg, padx=24, pady=24)
        self.workspace = workspace
        workspace.pack(fill="both", expand=True)
        workspace.grid_columnconfigure(0, minsize=280, weight=0)
        workspace.grid_columnconfigure(1, minsize=420, weight=1)
        workspace.grid_columnconfigure(2, minsize=240, weight=0)
        workspace.grid_rowconfigure(0, weight=1)

        library = tk.Frame(workspace, bg=panel, padx=16, pady=15,
                           highlightthickness=1, highlightbackground=border)
        library.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        lib_head = tk.Frame(library, bg=panel)
        lib_head.pack(fill="x", pady=(0, 12))
        tk.Label(lib_head, text="INSTALLED MODS", font=("Segoe UI", 9, "bold"), fg=text,
                 bg=panel).pack(side="left")
        self.mod_count = tk.Label(lib_head, text="0", font=("Segoe UI", 8, "bold"), fg=muted,
                                  bg=panel_hi, padx=7, pady=3)
        self.mod_count.pack(side="right")
        self.mod_list = ttk.Treeview(library, style="FEMS.Treeview", columns=("state", "version"),
                                     show="tree headings", selectmode="browse")
        self.mod_list.heading("#0", text="MOD")
        self.mod_list.heading("state", text="STATUS")
        self.mod_list.heading("version", text="VERSION")
        self.mod_list.column("#0", width=145, anchor="w", stretch=True)
        self.mod_list.column("state", width=55, anchor="center", stretch=False)
        self.mod_list.column("version", width=58, anchor="center", stretch=False)
        self.mod_list.pack(fill="both", expand=True)
        self.mod_list.bind("<<TreeviewSelect>>", self._select_row)
        self.mod_list.bind("<ButtonRelease-1>", self._select_clicked_row)
        self.mod_list.bind("<Double-1>", self._toggle_row)
        self._button(library, "＋   ADD MOD", self._add_package).pack(fill="x", pady=(12, 0))

        details = tk.Frame(workspace, bg=panel, padx=22, pady=19,
                           highlightthickness=1, highlightbackground=border)
        details.grid(row=0, column=1, sticky="nsew", padx=6)
        tk.Label(details, text="MOD DETAILS", font=("Segoe UI", 9, "bold"), fg=muted,
                 bg=panel).pack(anchor="w", pady=(0, 12))
        hero = tk.Frame(details, bg=panel)
        hero.pack(fill="x")
        self.cover = tk.Label(hero, text="NO COVER", width=24, height=8, bg=panel_hi,
                              fg=muted, relief="flat", font=("Segoe UI", 8, "bold"))
        self.cover.pack(side="left", padx=(0, 16), anchor="n")
        info = tk.Frame(hero, bg=panel)
        info.pack(side="left", fill="both", expand=True)
        self.name = tk.Label(info, text="", justify="left", anchor="nw",
                             wraplength=290, font=("Segoe UI", 19, "bold"), fg=text, bg=panel)
        self.name.pack(fill="x")
        self.byline = tk.Label(info, text="", anchor="w", fg=muted, bg=panel,
                               font=("Segoe UI", 9))
        self.byline.pack(fill="x", pady=(7, 13))
        self.link = tk.Label(info, text="", anchor="w", cursor="hand2", fg=accent, bg=panel,
                             font=("Segoe UI", 9, "underline"))
        self.link.pack(fill="x")
        tk.Label(details, text="DESCRIPTION", anchor="w", font=("Segoe UI", 8, "bold"),
                 fg=muted, bg=panel).pack(fill="x", pady=(21, 7))
        self.description = tk.Message(details,
            text="",
            width=500, justify="left", fg=text, bg=panel, font=("Segoe UI", 10))
        self.description.pack(fill="x")
        self.file_count = tk.Label(details, text="", anchor="w", fg=muted, bg=panel,
                                   font=("Segoe UI", 9))
        self.file_count.pack(fill="x", pady=(14, 0))
        self.toggle_button = self._button(details, "ENABLE MOD", self._toggle_selected, primary=True)
        self.toggle_button.pack(side="bottom", anchor="e", pady=(15, 0))

        rail = tk.Frame(workspace, bg=panel, padx=16, pady=15,
                        highlightthickness=1, highlightbackground=border)
        rail.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        tk.Label(rail, text="ENABLED", font=("Segoe UI", 9, "bold"), fg=text,
                 bg=panel).pack(anchor="w")
        self.active_list = tk.Frame(rail, bg=panel)
        self.active_list.pack(fill="x")
        tk.Frame(rail, height=1, bg=border).pack(fill="x", pady=15)
        self.session_label = tk.Label(rail, text="Ready", font=("Segoe UI", 10, "bold"),
                                      fg=text, bg=panel, anchor="w", justify="left", wraplength=190)
        self.session_label.pack(anchor="w", pady=(10, 4))
        self._button(rail, "OPEN MOD FOLDER", self._open_folder).pack(fill="x", side="bottom")

        footer = tk.Frame(self.root, bg="#111b26", padx=20, pady=9)
        footer.pack(fill="x", side="bottom")
        tk.Label(footer, text=f"FEMS v{__version__}", font=("Segoe UI", 8),
                 fg=muted, bg="#111b26").pack(side="right")
        self.root.geometry("1920x1080")
        self.refresh()

    def _button(self, parent, label, command, primary=False):
        return tk.Button(
            parent, text=label, command=command, padx=10, pady=7,
            bg="#315b73" if primary else "#2a3b49", fg="#f4f8fb",
            activebackground="#477c9a", activeforeground="#ffffff", relief="flat",
            borderwidth=0, font=("Segoe UI", 9, "bold"), cursor="hand2",
        )

    def refresh(self):
        state = manager.load_state(self.profile)
        self.mod_list.delete(*self.mod_list.get_children())
        self.rows.clear()
        packages = manager.package_list(self.profile)
        requested = set(state["requested"])
        self.mod_count.configure(text=str(len(packages)))
        for item in packages:
            filename = item["path"].name
            doc = item["doc"]
            enabled = filename in requested and not item["error"]
            label = doc.get("name", doc.get("id", item["path"].stem))
            if item["error"]:
                label += "  [INVALID]"
            self.mod_list.insert("", "end", iid=filename, text=label,
                                 values=("ON" if enabled else "OFF", doc.get("version", "—")))
            self.rows[filename] = item
        pending = state["requested"] != state["applied"]
        self.status.configure(text="RESTART REQUIRED" if pending else "")
        if pending and not self.status.winfo_manager():
            self.status.pack(fill="x", before=self.workspace)
        elif not pending and self.status.winfo_manager():
            self.status.pack_forget()
        self.session_label.configure(text="RESTART REQUIRED" if pending else f"{len(state['applied'])} mod(s) active",
                                      fg="#f1d9aa" if pending else "#edf2f7")
        self._render_loadout(state, packages)
        if self.selected_file not in self.rows or self.rows[self.selected_file]["error"]:
            self.selected_file = next(
                (item["path"].name for item in packages if not item["error"]), None
            )
        if self.selected_file:
            self.mod_list.selection_set(self.selected_file)
            self.mod_list.focus(self.selected_file)
            self._show_mod(self.selected_file)
        self._update_toggle_label()
        if not packages:
            self.selected_file = None
            self.name.configure(text="No mods installed")
            self.byline.configure(text="")
            self.description.configure(text="")
            self.file_count.configure(text="")
            self.link.configure(text="")
            self._show_preview(None)
            self._update_toggle_label()

    def _render_loadout(self, state, packages):
        for child in self.active_list.winfo_children():
            child.destroy()
        by_filename = {item["path"].name: item for item in packages}
        if not state["requested"]:
            tk.Label(self.active_list, text="None", font=("Segoe UI", 9),
                     fg="#8f9eac", bg="#111a24", anchor="w").pack(fill="x", pady=4)
            return
        for filename in state["requested"]:
            item = by_filename.get(filename)
            title = item["doc"].get("name", filename) if item else filename
            line = tk.Frame(self.active_list, bg="#111a24")
            line.pack(fill="x", pady=3)
            tk.Label(line, text="●", fg="#7bb8df", bg="#111a24", font=("Segoe UI", 8)).pack(side="left", padx=(0, 7))
            tk.Label(line, text=title, font=("Segoe UI", 9), fg="#edf2f7", bg="#111a24",
                     anchor="w", justify="left", wraplength=165).pack(side="left", fill="x")

    def _update_toggle_label(self):
        if not self.selected_file or self.selected_file not in self.rows:
            self.toggle_button.configure(text="ENABLE MOD", state="disabled")
            return
        state = manager.load_state(self.profile)
        if self.rows[self.selected_file]["error"]:
            self.toggle_button.configure(text="INVALID PACKAGE", state="disabled")
        elif self.selected_file in state["requested"]:
            self.toggle_button.configure(text="DISABLE MOD", state="normal")
        else:
            self.toggle_button.configure(text="ENABLE MOD", state="normal")

    def _select_row(self, _event=None):
        selection = self.mod_list.selection()
        if not selection:
            return
        self._show_mod(selection[0])

    def _select_clicked_row(self, event):
        filename = self.mod_list.identify_row(event.y)
        if filename and filename in self.rows:
            self.mod_list.selection_set(filename)
            self._show_mod(filename)

    def _show_mod(self, filename):
        item = self.rows.get(filename)
        if not item:
            return
        self.selected_file = filename
        doc = item["doc"]
        self.name.configure(text=doc.get("name", doc.get("id", filename)))
        self.byline.configure(text=f"{doc.get('author') or 'Unknown author'}  •  v{doc.get('version', '?')}")
        self.description.configure(text=doc.get("description") or "No description provided.")
        self.file_count.configure(text=f"{item['files']} data file(s)" + (f"  •  {item['error']}" if item["error"] else ""))
        homepage = doc.get("homepage", "")
        self.link.configure(text=homepage if homepage else "")
        self.link.bind("<Button-1>", lambda _e, url=homepage: self._open_link(url))
        self._show_preview(item["path"])
        self._update_toggle_label()

    def _show_preview(self, package):
        try:
            image_data = mods.read_preview(package)
            if not image_data:
                raise ValueError("no image")
            from PIL import Image, ImageTk
            image = Image.open(BytesIO(image_data)).convert("RGBA")
            image.thumbnail((190, 118))
            self.preview_image = ImageTk.PhotoImage(image)
            self.cover.configure(image=self.preview_image, text="", width=0, height=0)
        except Exception:
            self.preview_image = None
            self.cover.configure(image="", text="NO COVER", width=24, height=8)

    def _open_link(self, url):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme in ("https", "http") and parsed.netloc:
            webbrowser.open(url)

    def _toggle_row(self, _event=None):
        self._toggle_selected()

    def _toggle_selected(self):
        if not self.selected_file:
            return
        state = manager.load_state(self.profile)
        selected = set(state["requested"])
        if self.selected_file in selected:
            selected.remove(self.selected_file)
        elif self.selected_file in self.rows and not self.rows[self.selected_file]["error"]:
            selected.add(self.selected_file)
        try:
            manager.set_requested(self.profile, sorted(selected, key=str.casefold))
        except Exception as exc:
            messagebox.showerror("Mod selection", str(exc), parent=self.root)
            return
        self.refresh()
        if self.selected_file in self.rows:
            self.mod_list.selection_set(self.selected_file)
            self._select_row()

    def _save_selection(self):
        state = manager.load_state(self.profile)
        if state["requested"] != state["applied"]:
            messagebox.showinfo(
                "FEMS — restart required",
                "Your selection is queued. Close False Echo, then start it with fems_play.cmd to install the selected mods and restart.",
                parent=self.root,
            )
        else:
            messagebox.showinfo("FEMS", "Mod selection is up to date.", parent=self.root)
        self.hide()

    def _add_package(self):
        file = filedialog.askopenfilename(
            parent=self.root,
            title="Add FEMS mod package",
            filetypes=(("FEMS mod packages", "*.femod"), ("All files", "*.*")),
        )
        if not file:
            return
        try:
            dest = manager.add_package(self.profile, file)
            messagebox.showinfo("FEMS", f"Added {dest.name}", parent=self.root)
            self.refresh()
        except Exception as exc:
            messagebox.showerror("Could not add mod", str(exc), parent=self.root)

    def _open_folder(self):
        folder = manager.library_dir(self.profile)
        try:
            os.startfile(folder)
        except OSError as exc:
            messagebox.showerror("FEMS", str(exc), parent=self.root)

    def _poll(self):
        game = find_game_window()
        if game:
            self.ever_seen_game = True
        elif self.ever_seen_game:
            self.hide()
            self.root.destroy()
            return
        foreground = USER32.GetForegroundWindow()
        foreground_pid = wintypes.DWORD()
        if foreground:
            USER32.GetWindowThreadProcessId(foreground, ctypes.byref(foreground_pid))
        game_focused = bool(game and foreground_pid.value == game[1])
        # Use the high-order key-down bit and edge-detect it. Windows documents
        # the low-order "pressed since last call" bit as unreliable.
        f8_down = bool(USER32.GetAsyncKeyState(VK_F8) & 0x8000)
        if f8_down and not self.f8_was_down:
            if self.visible:
                self.hide()
            elif game_focused:
                self.show(game)
        self.f8_was_down = f8_down
        if self.visible:
            if not game:
                self.hide()
            else:
                self._position(game)
        self.root.after(35, self._poll)

    def _position(self, game):
        _, _, (left, top, right, bottom), _ = game
        game_width, game_height = right - left, bottom - top
        self.dimmer.geometry(f"{game_width}x{game_height}+{left}+{top}")
        self.root.geometry(f"{game_width}x{game_height}+{left}+{top}")

    def _prepare_window(self, window):
        """Keep clicks on the overlay from activating/minimizing the game."""
        child_hwnd = wintypes.HWND(window.winfo_id())
        hwnd = USER32.GetAncestor(child_hwnd, GA_ROOT) or child_hwnd
        try:
            style = _get_window_long(hwnd, GWL_EXSTYLE)
            _set_window_long(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE)
            if not COMCTL32.SetWindowSubclass(hwnd, self._mouse_activate_proc, 1, 0):
                raise ctypes.WinError(ctypes.get_last_error())
            USER32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE |
                                SWP_FRAMECHANGED)
        except (AttributeError, OSError, TypeError, ctypes.ArgumentError, tk.TclError):
            pass

    def _subclass_window_proc(self, hwnd, message, wparam, lparam, _subclass_id, _ref_data):
        # MA_NOACTIVATE preserves delivery of the mouse click to Tk while
        # keeping the fullscreen game as the active/foreground application.
        if message == WM_MOUSEACTIVATE:
            return MA_NOACTIVATE
        return COMCTL32.DefSubclassProc(hwnd, message, wparam, lparam)

    def _apply_glass(self):
        """Ask Windows 11 DWM for its desktop-acrylic transient backdrop."""
        try:
            dwm = ctypes.WinDLL("dwmapi")
            set_attribute = dwm.DwmSetWindowAttribute
            set_attribute.argtypes = (wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD)
            set_attribute.restype = ctypes.c_long
            value = wintypes.DWORD(3)  # DWMSBT_TRANSIENTWINDOW (Desktop Acrylic)
            hwnd = USER32.GetAncestor(wintypes.HWND(self.root.winfo_id()), GA_ROOT)
            result = set_attribute(hwnd, 38, ctypes.byref(value), ctypes.sizeof(value))
            dark_mode = wintypes.DWORD(1)
            set_attribute(hwnd, 20, ctypes.byref(dark_mode), ctypes.sizeof(dark_mode))
            self.glass_applied = (result == 0)
        except (AttributeError, OSError, TypeError, ctypes.ArgumentError, tk.TclError):
            self.glass_applied = False

    def show(self, game):
        self.visible = True
        self._position(game)
        # Set NOACTIVATE before mapping either top-level window. Showing an
        # activating window over exclusive fullscreen can minimize the game.
        self._prepare_window(self.dimmer)
        self._prepare_window(self.root)
        self.dimmer.deiconify()
        self.dimmer.lift()
        self.root.deiconify()
        self.root.lift()
        self._apply_glass()
        self.refresh()

    def hide(self):
        self.visible = False
        self.root.withdraw()
        self.dimmer.withdraw()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        FemsOverlay().run()
    except Exception as exc:
        print(f"FEMS overlay could not start: {exc}", file=sys.stderr)
        raise SystemExit(1)
