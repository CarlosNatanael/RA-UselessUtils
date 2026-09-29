import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Configuração inicial do tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def obter_caminho_recurso(relative_path):
    try:
        # O PyInstaller cria uma pasta temporária em sys._MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class PyHasherApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PyHasher")
        self.geometry("600x400")
        self.minsize(550, 350)

        # Configuração do Grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Seleção do Jogo / Arquivo
        self.frame_file = ctk.CTkFrame(self)
        self.frame_file.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.frame_file.grid_columnconfigure(1, weight=1)

        self.lbl_file = ctk.CTkLabel(self.frame_file, text="Arquivo ROM:")
        self.lbl_file.grid(row=0, column=0, padx=10, pady=10)

        self.entry_file = ctk.CTkEntry(
            self.frame_file, placeholder_text="Selecione a ROM..."
        )
        self.entry_file.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.btn_browse_file = ctk.CTkButton(
            self.frame_file, text="Procurar", width=90, command=self.browse_rom
        )
        self.btn_browse_file.grid(row=0, column=2, padx=10, pady=10)

        # 2. Configurações (System ID e Verbose)
        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_config.grid_columnconfigure(3, weight=1)

        self.lbl_system = ctk.CTkLabel(self.frame_config, text="System ID:")
        self.lbl_system.grid(row=0, column=0, padx=10, pady=10)

        self.system_options = [
            "21 - Famicom / NES",
            "2 - Mega Drive",
            "3 - SNES",
            "4 - Game Boy",
            "5 - Game Boy Advance",
            "6 - PlayStation",
        ]
        self.combo_system = ctk.CTkComboBox(
            self.frame_config, values=self.system_options, width=200
        )
        self.combo_system.grid(row=0, column=1, padx=10, pady=10)
        self.combo_system.set(self.system_options[0])

        self.check_verbose = ctk.CTkCheckBox(
            self.frame_config, text="Modo Verbose (-v)"
        )
        self.check_verbose.grid(row=0, column=2, padx=20, pady=10)

        self.btn_run = ctk.CTkButton(
            self.frame_config,
            text="Gerar Hash",
            fg_color="green",
            hover_color="darkgreen",
            command=self.run_rahasher,
        )
        self.btn_run.grid(row=0, column=3, padx=10, pady=10, sticky="e")

        # 3. Caixa de Saída (Output)
        self.frame_output = ctk.CTkFrame(self)
        self.frame_output.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.frame_output.grid_columnconfigure(0, weight=1)
        self.frame_output.grid_rowconfigure(1, weight=1)

        self.lbl_output = ctk.CTkLabel(
            self.frame_output, text="Resultado / Logs:", anchor="w"
        )
        self.lbl_output.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.txt_output = ctk.CTkTextbox(self.frame_output, width=540, height=150)
        self.txt_output.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def browse_rom(self):
        filename = filedialog.askopenfilename(
            title="Selecione a ROM", filetypes=[("All files", "*.*")]
        )
        if filename:
            self.entry_file.delete(0, tk.END)
            self.entry_file.insert(0, filename)

    def run_rahasher(self):
        # Aqui ele procura o executável embutido ou na mesma pasta durante o desenvolvimento
        exe_path = obter_caminho_recurso("RAHasher.exe")
        rom_path = self.entry_file.get().strip()
        selected_system = self.combo_system.get()

        system_id = selected_system.split(" - ")[0]

        if not os.path.exists(exe_path):
            self.txt_output.delete("0.0", tk.END)
            self.txt_output.insert(
                "0.0", f"Erro: RAHasher.exe oculto não encontrado em:\n{exe_path}"
            )
            return

        if not os.path.exists(rom_path):
            self.txt_output.delete("0.0", tk.END)
            self.txt_output.insert(
                "0.0", f"Erro: O ficheiro de ROM não foi encontrado em:\n{rom_path}"
            )
            return

        cmd = [exe_path]

        if self.check_verbose.get() == 1:
            cmd.append("-v")

        cmd.append(system_id)
        cmd.append(rom_path)

        try:
            # CREATE_NO_WINDOW (0x08000000) impede que a janela do terminal pisque no Windows
            creationflags = 0
            if os.name == 'nt':
                creationflags = 0x08000000 

            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="ignore",
                creationflags=creationflags
            )

            self.txt_output.delete("0.0", tk.END)

            output_text = ""
            if result.stdout:
                output_text += f"[Saída]:\n{result.stdout}\n"
            if result.stderr:
                output_text += f"[Erros/Logs]:\n{result.stderr}\n"

            if not output_text:
                output_text = "Executado, mas nenhuma saída foi retornada."

            self.txt_output.insert("0.0", output_text)

        except Exception as e:
            self.txt_output.delete("0.0", tk.END)
            self.txt_output.insert(
                "0.0", f"Ocorreu um erro ao executar o processo:\n{str(e)}"
            )

if __name__ == "__main__":
    app = PyHasherApp()
    app.mainloop()