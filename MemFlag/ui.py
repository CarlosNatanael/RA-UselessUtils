import customtkinter as ctk
from logic import BitConverter
import os
import sys

class CalculadoraApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("RA Tool - Cheevos Engineer")
        if hasattr(sys, '_MEIPASS'):
            caminho_icone = os.path.join(sys._MEIPASS, "icon.ico")
        else:
            caminho_icone = os.path.join(os.path.dirname(__file__), "icon.ico")
            
        try:
            self.iconbitmap(caminho_icone)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar o ícone. {e}")
        self.geometry("650x520")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.updating = False
        
        # Variáveis - Aba 1 (Conversor)
        self.modo_atual = "8-bit"
        self.num_bits = 8
        self.bits = []
        self.dec_var = ctk.StringVar(value="0")
        self.hex_var = ctk.StringVar(value="0x00")
        
        # Variáveis - Aba 2 (Ponteiros)
        self.pointer_base = ctk.StringVar(value="")
        self.pointer_offset = ctk.StringVar(value="")
        self.pointer_target = ctk.StringVar(value="")
        self.updating_pointer = False

        self.construir_interface()

    def construir_interface(self):
        # --- Sistema de Abas ---
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_conv = self.tabview.add("Conversor & Flags")
        self.tab_ptr = self.tabview.add("Ponteiros & Offsets")
        
        self.construir_aba_conversor()
        self.construir_aba_ponteiros()

    # ABA 1: CONVERSOR E FLAGS
    def construir_aba_conversor(self):
        self.frame_topo = ctk.CTkFrame(self.tab_conv, fg_color="transparent")
        self.frame_topo.pack(pady=10)
        
        ctk.CTkLabel(self.frame_topo, text="Tamanho da Memória:", font=("Arial", 14, "bold")).pack(side="left", padx=10)
        self.menu_modo = ctk.CTkOptionMenu(
            self.frame_topo, 
            values=["8-bit", "16-bit", "32-bit", "Float (32-bit)"],
            command=self.mudar_modo
        )
        self.menu_modo.pack(side="left")

        self.frame_bits = ctk.CTkFrame(self.tab_conv)
        self.frame_bits.pack(pady=5, padx=20, fill="x")
        
        self.lbl_bits = ctk.CTkLabel(self.frame_bits, text="Bit Flags", font=("Arial", 14, "bold"))
        self.lbl_bits.pack(pady=5)
        
        self.grid_bits = ctk.CTkFrame(self.frame_bits, fg_color="transparent")
        self.grid_bits.pack(pady=5, padx=15)

        self.frame_inputs = ctk.CTkFrame(self.tab_conv, fg_color="transparent")
        self.frame_inputs.pack(pady=10)

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
            self.frame_inputs, text="Limpar Tudo", command=self.limpar_campos,
            fg_color="#A83232", hover_color="#822626", width=160
        )
        self.btn_limpar.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.desenhar_bits()

    # Métodos da Aba 1 (Mesma lógica de antes)
    def mudar_modo(self, novo_modo):
        self.modo_atual = novo_modo
        if novo_modo == "8-bit": self.num_bits = 8
        elif novo_modo == "16-bit": self.num_bits = 16
        else: self.num_bits = 32
            
        self.lbl_dec.configure(text="Valor (Float):" if novo_modo == "Float (32-bit)" else "Valor (Dec):")
        
        if self.num_bits >= 32:
            self.frame_bits.pack_forget()
            self.bits = []
        else:
            self.frame_bits.pack(pady=5, padx=20, fill="x", before=self.frame_inputs)
            self.desenhar_bits()
        self.limpar_campos()

    def desenhar_bits(self):
        for widget in self.grid_bits.winfo_children(): widget.destroy()
        self.bits = [ctk.IntVar() for _ in range(self.num_bits)]
        self.lbl_bits.configure(text=f"Bit Flags ({self.num_bits}-bit)")
        
        for i in range(self.num_bits):
            bit_index = self.num_bits - 1 - i
            linha = i // 8
            coluna = i % 8
            cb = ctk.CTkCheckBox(
                self.grid_bits, text=f"b{bit_index:02d}", variable=self.bits[bit_index], 
                command=self.atualizar_pelos_bits, width=55, checkbox_height=20, checkbox_width=20
            )
            cb.grid(row=linha, column=coluna, padx=5, pady=8)

    def limpar_campos(self):
        self.updating = True
        for var in self.bits: var.set(0)
        self.dec_var.set("0.0" if self.modo_atual == "Float (32-bit)" else "0")
        self.hex_var.set(BitConverter.int_to_hex(0, self.num_bits))
        self.updating = False

    def atualizar_pelos_bits(self):
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
            val = self.dec_var.get().strip() or "0"
            if self.modo_atual == "Float (32-bit)":
                total_int = BitConverter.float_to_int(float(val))
            else:
                total_int = min(int(val), (1 << self.num_bits) - 1)
            self.hex_var.set(BitConverter.int_to_hex(total_int, self.num_bits))
            if self.num_bits < 32: self._setar_bits_na_ui(total_int)
        except ValueError: pass
        self.updating = False

    def atualizar_pelo_hexadecimal(self, event=None):
        if self.updating: return
        self.updating = True
        try:
            val = self.hex_var.get().strip()
            total_int = min(BitConverter.hex_to_int(val), (1 << self.num_bits) - 1)
            if self.modo_atual == "Float (32-bit)":
                self.dec_var.set(f"{BitConverter.int_to_float(total_int):.6g}") 
            else:
                self.dec_var.set(str(total_int))
            if self.num_bits < 32: self._setar_bits_na_ui(total_int)
        except ValueError: pass
        self.updating = False

    def _setar_bits_na_ui(self, valor_int):
        if self.num_bits >= 32: return
        bits_ativos = BitConverter.int_to_bits(valor_int, self.num_bits)
        for i in range(self.num_bits): self.bits[i].set(bits_ativos[i])


    # ABA 2: PONTEIROS E OFFSETS
    def construir_aba_ponteiros(self):
        frame_ptr = ctk.CTkFrame(self.tab_ptr, fg_color="transparent")
        frame_ptr.pack(pady=30)
        
        ctk.CTkLabel(frame_ptr, text="Preencha 2 campos para calcular o terceiro", text_color="gray", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=(0,20))

        ctk.CTkLabel(frame_ptr, text="Endereço Base (Hex):", font=("Arial", 12, "bold")).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        entry_base = ctk.CTkEntry(frame_ptr, textvariable=self.pointer_base, width=160, placeholder_text="Ex: 0x0856900")
        entry_base.grid(row=1, column=1, pady=5)
        entry_base.bind("<KeyRelease>", self.calcular_ponteiros)

        ctk.CTkLabel(frame_ptr, text="Offset (Hex):", font=("Arial", 12, "bold")).grid(row=2, column=0, padx=10, pady=5, sticky="e")
        entry_offset = ctk.CTkEntry(frame_ptr, textvariable=self.pointer_offset, width=160, placeholder_text="Ex: +0x78")
        entry_offset.grid(row=2, column=1, pady=5)
        entry_offset.bind("<KeyRelease>", self.calcular_ponteiros)

        ctk.CTkLabel(frame_ptr, text="="*40, text_color="gray").grid(row=3, column=0, columnspan=2, pady=5)

        ctk.CTkLabel(frame_ptr, text="Endereço Alvo (Hex):", font=("Arial", 12, "bold")).grid(row=4, column=0, padx=10, pady=5, sticky="e")
        entry_target = ctk.CTkEntry(frame_ptr, textvariable=self.pointer_target, width=160, placeholder_text="Ex: 0x0856978")
        entry_target.grid(row=4, column=1, pady=5)
        entry_target.bind("<KeyRelease>", self.calcular_ponteiros)
        
        btn_limpar_ptr = ctk.CTkButton(
            frame_ptr, text="Limpar", command=self.limpar_ponteiros,
            fg_color="#A83232", hover_color="#822626", width=160
        )
        btn_limpar_ptr.grid(row=5, column=0, columnspan=2, pady=25)

    def calcular_ponteiros(self, event=None):
        if self.updating_pointer: return
        self.updating_pointer = True
        
        base = self.pointer_base.get().strip().replace("+", "")
        offset = self.pointer_offset.get().strip().replace("+", "")
        target = self.pointer_target.get().strip().replace("+", "")

        widget_focado = self.focus_get()

        if base and offset and str(widget_focado.cget("textvariable")) != str(self.pointer_target):
            self.pointer_target.set(BitConverter.calc_pointer_target(base, offset))

        elif base and target and str(widget_focado.cget("textvariable")) != str(self.pointer_offset):
            self.pointer_offset.set(BitConverter.calc_pointer_offset(base, target))

        elif target and offset and str(widget_focado.cget("textvariable")) != str(self.pointer_base):
            self.pointer_base.set(BitConverter.calc_pointer_base(target, offset))

        self.updating_pointer = False

    def limpar_ponteiros(self):
        self.pointer_base.set("")
        self.pointer_offset.set("")
        self.pointer_target.set("")