import tkinter as tk
from tkinter import scrolledtext, messagebox
import tkinter.ttk as ttk

class AchievementConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversor de Achievements")
        self.root.geometry("900x700")
        
        # Cores do tema dark
        self.bg_color = "#1e1e1e"
        self.bg_secondary = "#2d2d2d"
        self.bg_input = "#252525"
        self.text_color = "#e0e0e0"
        self.accent_color = "#007acc"
        self.accent_hover = "#005999"
        self.success_color = "#28a745"
        self.danger_color = "#dc3545"
        self.warning_color = "#ffc107"
        self.border_color = "#404040"
        
        # Configurar tema dark
        self.root.configure(bg=self.bg_color)
        
        # Configurar estilos ttk
        self.setup_styles()
        
        # Container principal
        main_container = tk.Frame(root, bg=self.bg_color, padx=30, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        self.create_header(main_container)
        
        # Frame de entrada
        self.create_input_section(main_container)
        
        # Área de botões
        self.create_button_section(main_container)
        
        # Frame de saída
        self.create_output_section(main_container)
        
        # Barra de status
        self.create_status_bar(main_container)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Título com ícone
        title_label = tk.Label(
            header_frame, 
            text="Achievement Converter",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_label.pack()
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_frame,
            text="Converta suas conquistas para o formato desejado",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="#888888"
        )
        subtitle_label.pack()

    def create_input_section(self, parent):
        # Frame principal de entrada
        input_frame = tk.Frame(parent, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Header do frame
        header = tk.Frame(input_frame, bg=self.bg_secondary)
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(
            header, 
            text="ENTRADA",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_secondary,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        tk.Label(
            header,
            text="Formato: Title: Description",
            font=("Segoe UI", 9),
            bg=self.bg_secondary,
            fg="#888888"
        ).pack(side=tk.RIGHT)
        
        # Área de texto com borda personalizada
        text_container = tk.Frame(input_frame, bg=self.border_color, padx=1, pady=1)
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.input_text = scrolledtext.ScrolledText(
            text_container,
            height=8,
            font=("Consolas", 10),
            bg=self.bg_input,
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            selectforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        self.input_text.insert(1.0, "Cole sua lista aqui...\n\nExemplo:\nSwamp Survivor: Successfully complete all minigames in the Swamp mission")
        self.input_text.bind("<FocusIn>", self.on_input_focus_in)
        self.input_text.bind("<FocusOut>", self.on_input_focus_out)
        self.input_text.configure(fg="#666666")

    def create_button_section(self, parent):
        button_frame = tk.Frame(parent, bg=self.bg_color)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Container centralizado para botões
        buttons_container = tk.Frame(button_frame, bg=self.bg_color)
        buttons_container.pack(expand=True)
        
        # Botão Converter
        self.create_styled_button(
            buttons_container,
            "Converter",
            self.convert_achievements,
            self.accent_color,
            "white",
            "bold"
        ).pack(side=tk.LEFT, padx=5)
        
        # Botão Copiar
        self.create_styled_button(
            buttons_container,
            "📋 Copiar Resultado",
            self.copy_result,
            self.success_color,
            "white",
            "normal"
        ).pack(side=tk.LEFT, padx=5)
        
        # Botão Limpar
        self.create_styled_button(
            buttons_container,
            "Limpar Tudo",
            self.clear_all,
            self.danger_color,
            "white",
            "normal"
        ).pack(side=tk.LEFT, padx=5)

    def create_output_section(self, parent):
        # Frame principal de saída
        output_frame = tk.Frame(parent, bg=self.bg_secondary, relief=tk.FLAT, bd=0)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Header do frame
        header = tk.Frame(output_frame, bg=self.bg_secondary)
        header.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        tk.Label(
            header,
            text="SAÍDA",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_secondary,
            fg=self.success_color
        ).pack(side=tk.LEFT)
        
        self.output_count = tk.Label(
            header,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_secondary,
            fg="#888888"
        )
        self.output_count.pack(side=tk.RIGHT)
        
        # Área de texto com borda personalizada
        text_container = tk.Frame(output_frame, bg=self.border_color, padx=1, pady=1)
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.output_text = scrolledtext.ScrolledText(
            text_container,
            height=8,
            font=("Consolas", 10),
            bg=self.bg_input,
            fg=self.text_color,
            insertbackground=self.text_color,
            selectbackground=self.accent_color,
            selectforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self, parent):
        self.status_frame = tk.Frame(parent, bg=self.bg_secondary, height=30)
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Pronto para converter | Pressione Ctrl+V para colar",
            font=("Segoe UI", 9),
            bg=self.bg_secondary,
            fg="#888888"
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=5)
        
        self.version_label = tk.Label(
            self.status_frame,
            text="v1.0 Dark Mode",
            font=("Segoe UI", 9),
            bg=self.bg_secondary,
            fg="#555555"
        )
        self.version_label.pack(side=tk.RIGHT, padx=15, pady=5)

    def create_styled_button(self, parent, text, command, bg_color, fg_color, weight):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Segoe UI", 10, weight),
            bg=bg_color,
            fg=fg_color,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            activebackground=self.accent_hover,
            activeforeground="white"
        )
        
        # Efeitos hover
        def on_enter(e):
            btn['background'] = self.lighten_color(bg_color)
            
        def on_leave(e):
            btn['background'] = bg_color
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def lighten_color(self, color):
        # Clarear a cor para efeito hover
        if color == self.accent_color:
            return "#0088dd"
        elif color == self.success_color:
            return "#2ecc71"
        elif color == self.danger_color:
            return "#e74c3c"
        return color

    def on_input_focus_in(self, event):
        if self.input_text.get(1.0, tk.END).strip() == "Cole sua lista aqui...\n\nExemplo:\nSwamp Survivor: Successfully complete all minigames in the Swamp mission":
            self.input_text.delete(1.0, tk.END)
            self.input_text.configure(fg=self.text_color)

    def on_input_focus_out(self, event):
        if not self.input_text.get(1.0, tk.END).strip():
            self.input_text.insert(1.0, "Cole sua lista aqui...\n\nExemplo:\nSwamp Survivor: Successfully complete all minigames in the Swamp mission")
            self.input_text.configure(fg="#666666")

    def update_status(self, message, type="info"):
        colors = {
            "info": "#888888",
            "success": self.success_color,
            "error": self.danger_color,
            "warning": self.warning_color
        }
        self.status_label.config(text=message, fg=colors.get(type, "#888888"))

    def convert_achievements(self):
        # Habilitar saída para escrita
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        
        # Pegar texto de entrada
        input_content = self.input_text.get(1.0, tk.END).strip()
        
        # Verificar placeholder
        if input_content == "Cole sua lista aqui...\n\nExemplo:\nSwamp Survivor: Successfully complete all minigames in the Swamp mission":
            messagebox.showwarning("Aviso", "Por favor, cole sua lista de achievements primeiro!")
            self.output_text.config(state=tk.DISABLED)
            return
        
        if not input_content:
            self.update_status("Nenhum texto para converter", "warning")
            self.output_text.config(state=tk.DISABLED)
            return
        
        # Processar cada linha
        lines = input_content.split('\n')
        achievements = []
        
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue
                
            # Separar título e descrição
            parts = line.split(':', 1)
            if len(parts) == 2:
                title = parts[0].strip()
                description = parts[1].strip()
                if title and description:  # Verificar se ambos não estão vazios
                    achievements.append((title, description))
        
        if not achievements:
            self.update_status("Nenhum achievement válido encontrado", "error")
            messagebox.showwarning("Aviso", "Nenhum achievement válido encontrado!\nFormato esperado: Title: Description")
            self.output_text.config(state=tk.DISABLED)
            return
        
        # Gerar IDs incrementais
        result_lines = []
        for i, (title, description) in enumerate(achievements):
            achievement_id = f"111{i+1:06d}"
            formatted_line = f'{achievement_id}:"":{title}:{description}::::Cnat:0:::::00000'
            result_lines.append(formatted_line)
        
        # Mostrar resultado
        result_text = '\n'.join(result_lines)
        self.output_text.insert(1.0, result_text)
        self.output_text.config(state=tk.DISABLED)
        
        # Atualizar contador e status
        self.output_count.config(text=f"{len(achievements)} achievements gerados")
        self.update_status(f"✅ {len(achievements)} achievements convertidos com sucesso!", "success")
        
        # Efeito visual de sucesso
        self.flash_status()

    def flash_status(self):
        original_bg = self.status_frame.cget("bg")
        self.status_frame.configure(bg=self.success_color)
        self.root.after(500, lambda: self.status_frame.configure(bg=original_bg))

    def clear_all(self):
        self.input_text.delete(1.0, tk.END)
        self.input_text.insert(1.0, "Cole sua lista aqui...\n\nExemplo:\nSwamp Survivor: Successfully complete all minigames in the Swamp mission")
        self.input_text.configure(fg="#666666")
        
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
        
        self.output_count.config(text="")
        self.update_status("Campos limpos | Pronto para nova conversão", "info")
        
    def copy_result(self):
        result_content = self.output_text.get(1.0, tk.END).strip()
        if result_content:
            self.root.clipboard_clear()
            self.root.clipboard_append(result_content)
            self.update_status("📋 Resultado copiado para a área de transferência!", "success")
            self.flash_status()
        else:
            self.update_status("Nada para copiar", "warning")
            messagebox.showwarning("Aviso", "Não há resultado para copiar!")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Centralizar janela
    root.update_idletasks()
    width = 900
    height = 700
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    app = AchievementConverter(root)
    root.mainloop()