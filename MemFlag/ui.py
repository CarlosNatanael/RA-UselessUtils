import customtkinter as ctk
from logic import BitConverter

class CalculadoraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RA Bit Flag & Hex Converter")
        self.geometry("510x340")  # Aumentado levemente a altura para acomodar o botão
        self.resizable(False, False)
        
        # Configuração do Tema Dark Nativo
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.updating = False
        
        # Variáveis de Estado
        self.bits = [ctk.IntVar() for _ in range(8)]
        self.dec_var = ctk.StringVar(value="0")
        self.hex_var = ctk.StringVar(value="0x00")
        
        self.construir_interface()

    def construir_interface(self):
        # --- Frame dos Bits ---
        self.frame_bits = ctk.CTkFrame(self)
        self.frame_bits.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(self.frame_bits, text="Bit Flags (8-bit)", font=("Arial", 14, "bold")).pack(pady=5)
        
        grid_bits = ctk.CTkFrame(self.frame_bits, fg_color="transparent")
        grid_bits.pack(pady=10)
        
        valores_decimais = [128, 64, 32, 16, 8, 4, 2, 1]
        
        for i in range(8):
            bit_index = 7 - i
            
            lbl_valor = ctk.CTkLabel(grid_bits, text=str(valores_decimais[i]), text_color="gray")
            lbl_valor.grid(row=0, column=i, padx=8)
            
            cb = ctk.CTkCheckBox(
                grid_bits, 
                text=f"Bit{bit_index}", 
                variable=self.bits[bit_index], 
                command=self.atualizar_pelos_bits,
                width=45,
                checkbox_height=20,
                checkbox_width=20
            )
            cb.grid(row=1, column=i, padx=5)

        # --- Frame dos Inputs ---
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        ctk.CTkLabel(self.frame_inputs, text="Decimal:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, sticky="e")
        entrada_dec = ctk.CTkEntry(self.frame_inputs, textvariable=self.dec_var, width=140)
        entrada_dec.grid(row=0, column=1, pady=5)
        entrada_dec.bind("<KeyRelease>", self.atualizar_pelo_decimal)

        ctk.CTkLabel(self.frame_inputs, text="Hexadecimal:", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, sticky="e")
        entrada_hex = ctk.CTkEntry(self.frame_inputs, textvariable=self.hex_var, width=140)
        entrada_hex.grid(row=1, column=1, pady=5)
        entrada_hex.bind("<KeyRelease>", self.atualizar_pelo_hexadecimal)

        self.btn_limpar = ctk.CTkButton(
            self.frame_inputs, 
            text="Limpar Tudo", 
            command=self.limpar_campos,
            fg_color="#A83232",
            hover_color="#822626",
            width=140
        )
        self.btn_limpar.grid(row=2, column=0, columnspan=2, pady=15)

    def limpar_campos(self):
        """Zera todos os bits na interface e força a atualização dos textos para 0 e 0x00."""
        for var in self.bits:
            var.set(0)
        self.atualizar_pelos_bits()

    def atualizar_pelos_bits(self):
        if self.updating: return
        self.updating = True
        
        valores_bits = [var.get() for var in self.bits]
        total = BitConverter.bits_to_int(valores_bits)
        
        self.dec_var.set(str(total))
        self.hex_var.set(BitConverter.int_to_hex(total))
        
        self.updating = False

    def atualizar_pelo_decimal(self, event=None):
        if self.updating: return
        self.updating = True
        
        try:
            val = self.dec_var.get().strip()
            total = int(val) if val else 0
            
            if 0 <= total <= 255:
                self.hex_var.set(BitConverter.int_to_hex(total))
                self._setar_bits_na_ui(total)
        except ValueError:
            pass
            
        self.updating = False

    def atualizar_pelo_hexadecimal(self, event=None):
        if self.updating: return
        self.updating = True
        
        try:
            val = self.hex_var.get().strip()
            total = BitConverter.hex_to_int(val)
            
            if 0 <= total <= 255:
                self.dec_var.set(str(total))
                self._setar_bits_na_ui(total)
        except ValueError:
            pass
            
        self.updating = False

    def _setar_bits_na_ui(self, valor):
        bits_ativos = BitConverter.int_to_bits(valor)
        for i in range(8):
            self.bits[i].set(bits_ativos[i])