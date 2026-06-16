import customtkinter as ctk
from logic import BitConverter

class CalculadoraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RA Bit Flag & Hex Converter")
        self.geometry("650x450")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.updating = False
        self.modo_atual = "8-bit"
        self.num_bits = 8
        self.bits = []
        
        self.dec_var = ctk.StringVar(value="0")
        self.hex_var = ctk.StringVar(value="0x00")
        
        self.construir_interface()
        self.desenhar_bits()

    def construir_interface(self):
        # --- Seletor de Modo ---
        self.frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_topo.pack(pady=15)
        
        ctk.CTkLabel(self.frame_topo, text="Tamanho da Memória:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        self.menu_modo = ctk.CTkOptionMenu(
            self.frame_topo, 
            values=["8-bit", "16-bit", "32-bit", "Float (32-bit)"],
            command=self.mudar_modo
        )
        self.menu_modo.pack(side="left")

        # --- Frame dos Bits ---
        self.frame_bits = ctk.CTkFrame(self)
        self.frame_bits.pack(pady=10, padx=20, fill="x")
        
        self.lbl_bits = ctk.CTkLabel(self.frame_bits, text="Bit Flags", font=("Arial", 14, "bold"))
        self.lbl_bits.pack(pady=5)
        
        self.grid_bits = ctk.CTkFrame(self.frame_bits, fg_color="transparent")
        self.grid_bits.pack(pady=5, padx=15)

        # --- Frame dos Inputs ---
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=15)

        self.lbl_dec = ctk.CTkLabel(self.frame_inputs, text="Valor (Dec):", font=("Arial", 12, "bold"))
        self.lbl_dec.grid(row=0, column=0, padx=10, sticky="e")
        
        entrada_dec = ctk.CTkEntry(self.frame_inputs, textvariable=self.dec_var, width=160)
        entrada_dec.grid(row=0, column=1, pady=5)
        entrada_dec.bind("<KeyRelease>", self.atualizar_pelo_decimal)

        ctk.CTkLabel(self.frame_inputs, text="Hexadecimal:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, sticky="e")
        entrada_hex = ctk.CTkEntry(self.frame_inputs, textvariable=self.hex_var, width=160)
        entrada_hex.grid(row=1, column=1, pady=5)
        entrada_hex.bind("<KeyRelease>", self.atualizar_pelo_hexadecimal)

        self.btn_limpar = ctk.CTkButton(
            self.frame_inputs, 
            text="Limpar Tudo", 
            command=self.limpar_campos,
            fg_color="#A83232", hover_color="#822626", width=160
        )
        self.btn_limpar.grid(row=2, column=0, columnspan=2, pady=15)

    def mudar_modo(self, novo_modo):
        self.modo_atual = novo_modo
        
        if novo_modo == "8-bit": self.num_bits = 8
        elif novo_modo == "16-bit": self.num_bits = 16
        else: self.num_bits = 32
            
        # Atualiza a label do input
        self.lbl_dec.configure(text="Valor (Float):" if novo_modo == "Float (32-bit)" else "Valor (Dec):")
        
        # Lógica para esconder/mostrar as bitflags e redimensionar a janela
        if self.num_bits >= 32:
            self.frame_bits.pack_forget() # Oculta as flags
            self.bits = []
            self.geometry("450x230") # Encolhe a janela para ficar clean
        else:
            # Mostra as flags e recoloca o frame na ordem correta
            self.frame_bits.pack(pady=10, padx=20, fill="x", before=self.frame_inputs)
            self.geometry("650x450") # Retorna ao tamanho original
            self.desenhar_bits()
        
        self.limpar_campos()

    def desenhar_bits(self):
        for widget in self.grid_bits.winfo_children():
            widget.destroy()

        self.bits = [ctk.IntVar() for _ in range(self.num_bits)]
        self.lbl_bits.configure(text=f"Bit Flags ({self.num_bits}-bit)")
        
        for i in range(self.num_bits):
            bit_index = self.num_bits - 1 - i
            linha = i // 8
            coluna = i % 8
            
            cb = ctk.CTkCheckBox(
                self.grid_bits, 
                text=f"b{bit_index:02d}", 
                variable=self.bits[bit_index], 
                command=self.atualizar_pelos_bits,
                width=55, checkbox_height=20, checkbox_width=20
            )
            cb.grid(row=linha, column=coluna, padx=5, pady=8)

    def limpar_campos(self):
        self.updating = True
        for var in self.bits: var.set(0)
        
        self.dec_var.set("0.0" if self.modo_atual == "Float (32-bit)" else "0")
        self.hex_var.set(BitConverter.int_to_hex(0, self.num_bits))
        self.updating = False

    def atualizar_pelos_bits(self):
        # Ignora se estiver num modo de 32 bits (pois as checkboxes nem existem)
        if self.updating or self.num_bits >= 32: return
        self.updating = True
        
        valores_bits = [var.get() for var in self.bits]
        total_int = BitConverter.bits_to_int(valores_bits)
        
        self.dec_var.set(str(total_int))
        self.hex_var.set(BitConverter.int_to_hex(total_int, self.num_bits))
        self.updating = False

    def atualizar_pelo_decimal(self, event=None):
        if self.updating: return
        self.updating = True
        
        try:
            val = self.dec_var.get().strip()
            if not val: val = "0"

            if self.modo_atual == "Float (32-bit)":
                f_val = float(val)
                total_int = BitConverter.float_to_int(f_val)
            else:
                total_int = int(val)
                max_val = (1 << self.num_bits) - 1
                if total_int > max_val: total_int = max_val
            
            self.hex_var.set(BitConverter.int_to_hex(total_int, self.num_bits))
            
            # Só atualiza visualmente os bits se eles estiverem aparecendo
            if self.num_bits < 32:
                self._setar_bits_na_ui(total_int)
        except ValueError:
            pass # Impede que o app crashe se você digitar "100." ou texto inválido
            
        self.updating = False

    def atualizar_pelo_hexadecimal(self, event=None):
        if self.updating: return
        self.updating = True
        
        try:
            val = self.hex_var.get().strip()
            total_int = BitConverter.hex_to_int(val)
            
            max_val = (1 << self.num_bits) - 1
            if total_int > max_val: total_int = max_val
            
            if self.modo_atual == "Float (32-bit)":
                f_val = BitConverter.int_to_float(total_int)
                self.dec_var.set(f"{f_val:.6g}") 
            else:
                self.dec_var.set(str(total_int))
                
            if self.num_bits < 32:
                self._setar_bits_na_ui(total_int)
        except ValueError:
            pass
            
        self.updating = False

    def _setar_bits_na_ui(self, valor_int):
        if self.num_bits >= 32: return
        bits_ativos = BitConverter.int_to_bits(valor_int, self.num_bits)
        for i in range(self.num_bits):
            self.bits[i].set(bits_ativos[i])