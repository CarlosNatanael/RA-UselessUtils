import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from dataclasses import dataclass, field
from typing import Optional

import customtkinter as ctk

# Drag & drop opcional
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0f1115",
    "card": "#181b22",
    "card_hover": "#1f232c",
    "border": "#2a2f3a",
    "text": "#e6e8ee",
    "text_dim": "#8b93a7",
    "accent": "#4f8cff",
    "accent_hover": "#3d7aee",
    "success": "#3ddc84",
    "warning": "#ffb020",
    "error": "#ff5c5c",
}

if DND_AVAILABLE:
    class _BaseApp(ctk.CTk, TkinterDnD.Tk):
        """App com suporte a drag & drop."""
        def __init__(self):
            super().__init__()
            # Garante que o tkdnd seja carregado na raiz
            try:
                self.TkdndVersion = TkinterDnD._require(self)
            except Exception:
                pass
else:
    class _BaseApp(ctk.CTk):
        """App sem drag & drop."""
        def __init__(self):
            super().__init__()

@dataclass
class Achievement:
    line_index: int
    id: str
    conditions: str
    titulo: str
    descricao: str
    resto: str

    def rebuild(self, novo_titulo: str, nova_descricao: str) -> str:
        return f'{self.id}:"{self.conditions}":{novo_titulo}:{nova_descricao}:{self.resto}'


@dataclass
class TitleEntry:
    titulo: str
    descricao: str


@dataclass
class UpdateResult:
    total: int = 0
    atualizados: int = 0
    erros: list = field(default_factory=list)
    output_path: str = ""

class AchievementParser:
    LINE_RE = re.compile(r'^(\d+):"(.*?)":(.*?):(.*?):(.*)$')
    ACHIEVEMENT_RE = re.compile(r"^\d+:")

    @staticmethod
    def parse_achievement(line: str, line_index: int) -> Optional[Achievement]:
        m = AchievementParser.LINE_RE.match(line)
        if not m:
            return None
        return Achievement(
            line_index=line_index,
            id=m.group(1),
            conditions=m.group(2),
            titulo=m.group(3),
            descricao=m.group(4),
            resto=m.group(5),
        )

    @staticmethod
    def parse_titles(path: str) -> list:
        entries = []
        with open(path, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.rstrip("\r\n")
                if not line.strip():
                    continue
                if ":" in line:
                    t, d = line.split(":", 1)
                    entries.append(TitleEntry(t.strip(), d.strip()))
                else:
                    entries.append(TitleEntry(line.strip(), ""))
        return entries

class AchievementService:
    @staticmethod
    def load_achievements(path: str):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        achievements = []
        for i, line in enumerate(lines):
            if AchievementParser.ACHIEVEMENT_RE.match(line.strip()):
                ach = AchievementParser.parse_achievement(line.rstrip("\r\n"), i)
                if ach:
                    achievements.append(ach)
        return lines, achievements

    @staticmethod
    def update(original_path: str, titles_path: str, output_path: str) -> UpdateResult:
        result = UpdateResult(output_path=output_path)

        lines, achievements = AchievementService.load_achievements(original_path)
        titles = AchievementParser.parse_titles(titles_path)

        result.total = len(achievements)

        for ach, entry in zip(achievements, titles):
            nova_linha = ach.rebuild(entry.titulo, entry.descricao)
            lines[ach.line_index] = nova_linha + "\n"
            result.atualizados += 1

        with open(output_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        return result

class FilePicker(ctk.CTkFrame):
    """Card moderno para seleção de arquivo."""

    def __init__(self, master, title: str, subtitle: str, on_pick, **kwargs):
        super().__init__(
            master,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            **kwargs,
        )
        self.on_pick = on_pick
        self.path_var = tk.StringVar()

        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        # Path + Button
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        row.grid_columnconfigure(0, weight=1)

        self.path_entry = ctk.CTkEntry(
            row,
            textvariable=self.path_var,
            placeholder_text="Nenhum arquivo selecionado...",
            height=36,
            corner_radius=8,
            fg_color=COLORS["bg"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
        )
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            row,
            text="Selecionar",
            width=100,
            height=36,
            corner_radius=8,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self._pick,
        ).grid(row=0, column=1)

        # Drag & drop (só se disponível E se o tkdnd foi carregado)
        if DND_AVAILABLE:
            try:
                self.path_entry.drop_target_register(DND_FILES)
                self.path_entry.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass  # se falhar, ignora silenciosamente

    def _pick(self):
        path = self.on_pick()
        if path:
            self.path_var.set(path)

    def _on_drop(self, event):
        try:
            files = self.tk.splitlist(event.data)
            if files:
                self.path_var.set(files[0])
        except Exception:
            pass

    def get(self) -> str:
        return self.path_var.get().strip()

    def set(self, value: str):
        self.path_var.set(value)

class AchievementUpdaterApp(_BaseApp):
    def __init__(self):
        super().__init__()

        self.title("Achievement Updater · Shining Force Gaiden")
        self.geometry("980x720")
        self.minsize(860, 640)
        self.configure(fg_color=COLORS["bg"])

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 8))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Achievement Updater",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Atualize títulos e descrições mantendo IDs e condições",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=2, column=0, sticky="nsew", padx=24, pady=8)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(3, weight=1)

        # Pickers
        self.original_picker = FilePicker(
            body,
            "1 · Arquivo original",
            "Arquivo .txt no formato RetroAchievements (ex: 1.4.2.0.txt)",
            on_pick=self._pick_original,
        )
        self.original_picker.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        self.titles_picker = FilePicker(
            body,
            "2 · Arquivo com novos títulos",
            "Uma linha por achievement no formato  Título:Descrição",
            on_pick=self._pick_titles,
        )
        self.titles_picker.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.output_picker = FilePicker(
            body,
            "3 · Arquivo de saída  (opcional)",
            "Se vazio, sobrescreve o arquivo original",
            on_pick=self._pick_output,
        )
        self.output_picker.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Preview / Log (tabs)
        self.tabs = ctk.CTkTabview(
            body,
            fg_color=COLORS["card"],
            segmented_button_fg_color=COLORS["bg"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg"],
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["border"],
            corner_radius=12,
        )
        self.tabs.grid(row=3, column=0, sticky="nsew")

        self.tab_preview = self.tabs.add("Pré-visualização")
        self.tab_log = self.tabs.add("Log")

        # Preview
        self.preview_box = ctk.CTkTextbox(
            self.tab_preview,
            fg_color=COLORS["bg"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.preview_box.pack(fill="both", expand=True, padx=8, pady=8)

        # Log
        self.log_box = ctk.CTkTextbox(
            self.tab_log,
            fg_color=COLORS["bg"],
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=1,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.log_box.pack(fill="both", expand=True, padx=8, pady=8)

        self._setup_text_tags()

    def _setup_text_tags(self):
        for box in (self.preview_box, self.log_box):
            box.tag_config("before", foreground=COLORS["text_dim"])
            box.tag_config("after", foreground=COLORS["success"])
            box.tag_config("id", foreground=COLORS["accent"])
            box.tag_config("error", foreground=COLORS["error"])
            box.tag_config("warn", foreground=COLORS["warning"])
            box.tag_config("ok", foreground=COLORS["success"])
            box.tag_config("sep", foreground=COLORS["border"])

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=24, pady=(4, 20))
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer,
            text="Pronto.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_dim"],
            anchor="w",
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        self.progress = ctk.CTkProgressBar(
            footer,
            width=200,
            height=6,
            corner_radius=3,
            fg_color=COLORS["card"],
            progress_color=COLORS["accent"],
        )
        self.progress.grid(row=0, column=1, padx=(0, 16))
        self.progress.set(0)

        ctk.CTkButton(
            footer,
            text="Pré-visualizar",
            width=140,
            height=40,
            corner_radius=10,
            fg_color=COLORS["card"],
            hover_color=COLORS["card_hover"],
            border_width=1,
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            command=self._on_preview,
        ).grid(row=0, column=2, padx=(0, 8))

        ctk.CTkButton(
            footer,
            text="Atualizar Arquivo",
            width=160,
            height=40,
            corner_radius=10,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_update,
        ).grid(row=0, column=3)

    def _pick_original(self):
        return filedialog.askopenfilename(
            title="Selecione o arquivo original",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

    def _pick_titles(self):
        return filedialog.askopenfilename(
            title="Selecione o arquivo com novos títulos",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

    def _pick_output(self):
        return filedialog.asksaveasfilename(
            title="Salvar arquivo atualizado como...",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )

    def _log(self, msg: str, tag: str = ""):
        self.log_box.insert("end", msg + "\n", tag)
        self.log_box.see("end")

    def _set_status(self, msg: str, color: str = COLORS["text_dim"]):
        self.status_label.configure(text=msg, text_color=color)

    def _validate_inputs(self) -> Optional[tuple]:
        original = self.original_picker.get()
        titles = self.titles_picker.get()
        output = self.output_picker.get()

        if not original or not os.path.isfile(original):
            messagebox.showerror("Erro", "Selecione um arquivo original válido.")
            return None
        if not titles or not os.path.isfile(titles):
            messagebox.showerror("Erro", "Selecione um arquivo de títulos válido.")
            return None

        return original, titles, output or original

    def _clear_box(self, box):
        box.configure(state="normal")
        box.delete("1.0", "end")

    def _on_preview(self):
        inputs = self._validate_inputs()
        if not inputs:
            return

        original, titles, _ = inputs
        self._clear_box(self.preview_box)
        self.tabs.set("Pré-visualização")

        try:
            lines, achievements = AchievementService.load_achievements(original)
            entries = AchievementParser.parse_titles(titles)

            self._log("=" * 60, "sep")
            self._log(f"Pré-visualização · {len(achievements)} achievements", "ok")
            self._log("=" * 60, "sep")

            total = min(len(achievements), len(entries))
            for i in range(total):
                ach = achievements[i]
                entry = entries[i]

                self.preview_box.insert("end", f"[{ach.id}] ", "id")
                self.preview_box.insert("end", f"{ach.titulo} | {ach.descricao}\n", "before")
                self.preview_box.insert("end", "     → ", "sep")
                self.preview_box.insert("end", f"{entry.titulo} | {entry.descricao}\n", "after")
                self.preview_box.insert("end", "\n")

            if len(achievements) != len(entries):
                msg = f"⚠ Aviso: {len(achievements)} achievements vs {len(entries)} títulos."
                self.preview_box.insert("end", msg + "\n", "warn")
                self._log(msg, "warn")

            self._set_status(f"Preview gerado: {total} entradas.", COLORS["accent"])
            self.preview_box.see("1.0")

        except Exception as e:
            self._log(f"❌ Erro no preview: {e}", "error")
            self._set_status("Erro no preview.", COLORS["error"])

    def _on_update(self):
        inputs = self._validate_inputs()
        if not inputs:
            return

        original, titles, output = inputs

        if output == original:
            ok = messagebox.askyesno(
                "Confirmar",
                "Nenhum arquivo de saída selecionado.\n\n"
                "Isso vai SOBRESCREVER o arquivo original.\n\n"
                "Deseja continuar?",
            )
            if not ok:
                return

        try:
            _, achievements = AchievementService.load_achievements(original)
            entries = AchievementParser.parse_titles(titles)
            if len(achievements) != len(entries):
                ok = messagebox.askyesno(
                    "Aviso",
                    f"Contagens diferentes:\n"
                    f"  • Achievements: {len(achievements)}\n"
                    f"  • Títulos:      {len(entries)}\n\n"
                    f"Continuar mesmo assim?",
                )
                if not ok:
                    return
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler arquivos:\n{e}")
            return

        self.progress.set(0)
        self._set_status("Processando...", COLORS["accent"])
        self.tabs.set("Log")

        threading.Thread(
            target=self._run_update,
            args=(original, titles, output),
            daemon=True,
        ).start()

    def _run_update(self, original: str, titles: str, output: str):
        try:
            self._log("=" * 60, "sep")
            self._log("Iniciando atualização...", "ok")

            result = AchievementService.update(original, titles, output)

            self.after(0, lambda: self.progress.set(1.0))
            self._log(f"✔ {result.atualizados} achievements atualizados.", "ok")
            self._log(f"💾 Salvo em: {result.output_path}", "ok")
            self._log("=" * 60, "sep")

            self.after(0, lambda: self._set_status(
                f"Concluído · {result.atualizados} atualizados.",
                COLORS["success"],
            ))
            self.after(0, lambda: messagebox.showinfo(
                "Sucesso",
                f"Arquivo atualizado com sucesso!\n\n"
                f"Achievements: {result.atualizados}\n"
                f"Salvo em:\n{result.output_path}",
            ))

        except Exception as e:
            self._log(f"❌ Erro: {e}", "error")
            self.after(0, lambda: self._set_status("Erro.", COLORS["error"]))
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))

def main():
    app = AchievementUpdaterApp()
    app.mainloop()


if __name__ == "__main__":
    main()