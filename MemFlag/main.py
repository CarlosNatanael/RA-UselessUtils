import tkinter as tk

class CalculadoraBitFlags(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MemFlag")
        self.geometry("550x250")
        
        # Trava para evitar loops infinitos de atualização
        self.updating = False

        # Variáveis do Tkinter
        self.bits = [tk.IntVar() for _ in range(8)]
        self.dec_var = tk.StringVar(value="0")
        self.hex_var = tk.StringVar(value="0x00")

        self.construir_interface()

    def construir_interface(self):
        # --- Frame dos Bits ---
        frame_bits = tk.LabelFrame(self, text="Bit Flags (8-bit)", padx=10, pady=10)
        frame_bits.pack(pady=15, padx=20, fill="x")

        valores_decimais = [128, 64, 32, 16, 8, 4, 2, 1]
        
        for i in range(8):
            bit_index = 7 - i
            
            lbl_valor = tk.Label(frame_bits, text=str(valores_decimais[i]), fg="gray")
            lbl_valor.grid(row=0, column=i, padx=5)
            
            cb = tk.Checkbutton(
                frame_bits, 
                text=f"Bit{bit_index}", 
                variable=self.bits[bit_index], 
                command=self.atualizar_pelos_bits
            )
            cb.grid(row=1, column=i, padx=5)

        # --- Frame dos Conversores ---
        frame_inputs = tk.Frame(self)
        frame_inputs.pack(pady=10)

        # Entrada Decimal
        tk.Label(frame_inputs, text="Decimal:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="e")
        entrada_dec = tk.Entry(frame_inputs, textvariable=self.dec_var, width=15)
        entrada_dec.grid(row=0, column=1, pady=5)
        entrada_dec.bind("<KeyRelease>", self.atualizar_pelo_decimal)

        # Entrada Hexadecimal
        tk.Label(frame_inputs, text="Hexadecimal:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, sticky="e")
        entrada_hex = tk.Entry(frame_inputs, textvariable=self.hex_var, width=15)
        entrada_hex.grid(row=1, column=1, pady=5)
        entrada_hex.bind("<KeyRelease>", self.atualizar_pelo_hexadecimal)

    def atualizar_pelos_bits(self):
        """Calcula o valor total somando os bits ativos e atualiza Dec e Hex."""
        if self.updating: return
        self.updating = True
        
        total = sum(var.get() * (2**i) for i, var in enumerate(self.bits))
        
        self.dec_var.set(str(total))
        self.hex_var.set(f"0x{total:02x}")  # Formata com '0x' e padding de 2 dígitos
        
        self.updating = False

    def atualizar_pelo_decimal(self, event=None):
        """Lê o valor decimal digitado e liga/desliga os bits correspondentes."""
        if self.updating: return
        self.updating = True
        
        try:
            val = self.dec_var.get().strip()
            total = int(val) if val else 0
            
            if 0 <= total <= 255:
                self.hex_var.set(f"0x{total:02x}")
                self.setar_bits(total)
        except ValueError:
            pass
            
        self.updating = False

    def atualizar_pelo_hexadecimal(self, event=None):
        """Lê o valor hexadecimal digitado e ajusta Decimal e Bits."""
        if self.updating: return
        self.updating = True
        
        try:
            val = self.hex_var.get().strip()
            if not val: val = "0"
            
            # Converte de Hex para Int (aceita com ou sem o '0x')
            total = int(val, 16)
            
            if 0 <= total <= 255:
                self.dec_var.set(str(total))
                self.setar_bits(total)
        except ValueError:
            pass
            
        self.updating = False

    def setar_bits(self, valor):
        """Liga ou desliga os Checkbuttons de acordo com o valor inteiro passado."""
        for i in range(8):
            bit_ativo = (valor >> i) & 1
            self.bits[i].set(bit_ativo)

if __name__ == "__main__":
    app = CalculadoraBitFlags()
    app.mainloop()