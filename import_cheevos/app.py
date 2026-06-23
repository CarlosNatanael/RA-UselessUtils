import customtkinter as ctk
from tkinter import messagebox
from io import BytesIO
import requests
from PIL import Image

# Configurações globais de design moderno
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class RetroExporterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RetroAchievements Exporter")
        self.geometry("650x700")
        
        self.username = ""
        self.api_key = ""
        self.game_data = None
        
        # Configuração de grade para a janela principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Instanciação das duas telas
        self.login_frame = ctk.CTkFrame(self)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.build_login_screen()

    def build_login_screen(self):
        """Monta a tela inicial pedindo os dados da API."""
        self.login_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.login_frame, 
            text="RetroAchievements Exporter", 
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(60, 30))
        
        self.entry_user = ctk.CTkEntry(self.login_frame, placeholder_text="Seu Usuário", width=300, height=40)
        self.entry_user.pack(pady=10)
        
        # Oculta a chave de API visualmente por segurança
        self.entry_key = ctk.CTkEntry(self.login_frame, placeholder_text="Web API Key", width=300, height=40, show="*")
        self.entry_key.pack(pady=10)
        
        ctk.CTkButton(
            self.login_frame, 
            text="Acessar", 
            command=self.do_login, 
            width=300, 
            height=40,
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=30)

    def do_login(self):
        """Valida se os campos foram preenchidos e avança."""
        user = self.entry_user.get().strip()
        key = self.entry_key.get().strip()
        
        if not user or not key:
            messagebox.showwarning("Aviso", "Preencha o usuário e a API Key.")
            return
            
        self.username = user
        self.api_key = key
        
        # Oculta o painel de login e exibe o principal
        self.login_frame.grid_forget()
        self.build_main_screen()

    def build_main_screen(self):
        """Monta a interface de busca e exportação."""
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # --- Barra de Busca ---
        frame_search = ctk.CTkFrame(self.main_frame)
        frame_search.pack(fill="x", pady=(0, 15))
        
        self.entry_id = ctk.CTkEntry(frame_search, placeholder_text="ID do Jogo (ex: 286)", width=200)
        self.entry_id.pack(side="left", padx=15, pady=15)
        
        ctk.CTkButton(frame_search, text="Buscar Jogo", command=self.fetch_game).pack(side="left", padx=10, pady=15)
        
        # --- Informações do Jogo ---
        self.frame_info = ctk.CTkFrame(self.main_frame)
        self.frame_info.pack(fill="x", pady=5)
        
        self.label_title = ctk.CTkLabel(
            self.frame_info, 
            text="Nenhum jogo carregado", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.label_title.pack(pady=(15, 5), padx=15, anchor="w")
        
        self.label_icon = ctk.CTkLabel(self.frame_info, text="")
        self.label_icon.pack(pady=(0, 15), padx=15, anchor="w")
        
        # --- Filtros de Exportação ---
        frame_filters = ctk.CTkFrame(self.main_frame)
        frame_filters.pack(fill="x", pady=15)
        
        self.chk_id = ctk.BooleanVar(value=True)
        self.chk_title = ctk.BooleanVar(value=True)
        self.chk_desc = ctk.BooleanVar(value=True)
        self.chk_points = ctk.BooleanVar(value=True)
        
        ctk.CTkCheckBox(frame_filters, text="ID", variable=self.chk_id).pack(side="left", padx=20, pady=15)
        ctk.CTkCheckBox(frame_filters, text="Título", variable=self.chk_title).pack(side="left", padx=20, pady=15)
        ctk.CTkCheckBox(frame_filters, text="Descrição", variable=self.chk_desc).pack(side="left", padx=20, pady=15)
        ctk.CTkCheckBox(frame_filters, text="Pontos", variable=self.chk_points).pack(side="left", padx=20, pady=15)
        
        # --- Geração e Saída ---
        ctk.CTkButton(
            self.main_frame, 
            text="Gerar Lista de Conquistas", 
            command=self.generate_list,
            fg_color="#2b8a3e", # Botão verde para destacar a ação principal
            hover_color="#237032"
        ).pack(pady=5)
        
        self.txt_output = ctk.CTkTextbox(self.main_frame, height=250, font=ctk.CTkFont(family="Consolas", size=13))
        self.txt_output.pack(fill="both", expand=True, pady=15)

    def fetch_game(self):
        """Faz a requisição para a API oficial."""
        game_id = self.entry_id.get().strip()
        if not game_id:
            messagebox.showerror("Erro", "Digite um ID de jogo válido.")
            return
            
        url = f"https://retroachievements.org/API/API_GetGameProgression.php?i={game_id}&y={self.api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "Title" not in data:
                messagebox.showerror("Erro", "Jogo não encontrado ou sua API Key está incorreta.")
                return
                
            self.game_data = data
            self.label_title.configure(text=f"{data.get('Title')} ({data.get('ConsoleName')})")
            
            # Processamento da imagem com CustomTkinter Image
            icon_path = data.get("ImageIcon")
            if icon_path:
                img_url = f"https://retroachievements.org{icon_path}"
                img_res = requests.get(img_url)
                img_data = Image.open(BytesIO(img_res.content))
                
                ctk_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(80, 80))
                self.label_icon.configure(image=ctk_image, text="")
                self.label_icon.image = ctk_image # Mantém a referência da imagem viva
                
        except Exception as e:
            messagebox.showerror("Erro de Conexão", f"Falha ao comunicar com o servidor:\n{e}")

    def generate_list(self):
        """Gera o texto final baseado nas caixas de seleção marcadas."""
        if not self.game_data or "Achievements" not in self.game_data:
            messagebox.showwarning("Aviso", "Busque um jogo válido primeiro.")
            return
            
        self.txt_output.delete("1.0", ctk.END)
        achievements = self.game_data.get("Achievements", [])
        
        for ach in achievements:
            parts = []
            if self.chk_id.get():
                parts.append(str(ach.get("ID", "")))
                
            prefix = " | " if (self.chk_id.get() and (self.chk_title.get() or self.chk_desc.get() or self.chk_points.get())) else ""
            
            content_parts = []
            if self.chk_title.get():
                content_parts.append(ach.get("Title", ""))
                
            if self.chk_desc.get():
                desc = ach.get("Description", "")
                if self.chk_title.get():
                    content_parts[-1] = f"{content_parts[-1]}: {desc}"
                else:
                    content_parts.append(desc)
                    
            if self.chk_points.get():
                pts = f"({ach.get('Points', 0)})"
                content_parts.append(pts)
                
            main_content = " ".join(content_parts).replace(" : ", ": ")
            line = f"{''.join(parts)}{prefix}{main_content}".strip()
            
            if line.startswith("|"):
                line = line.replace("|", "", 1).strip()
                
            self.txt_output.insert(ctk.END, line + "\n")

if __name__ == "__main__":
    app = RetroExporterApp()
    app.mainloop()