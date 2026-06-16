class BitConverter:
    @staticmethod
    def bits_to_int(bits):
        """Recebe uma lista de 1s e 0s (do bit 0 ao 7) e retorna o decimal total."""
        return sum(val * (2**i) for i, val in enumerate(bits))

    @staticmethod
    def int_to_hex(valor):
        """Converte inteiro para string hexadecimal com padding de 2 dígitos e '0x'."""
        return f"0x{valor:02x}"

    @staticmethod
    def hex_to_int(hex_str):
        """Converte string hexadecimal para inteiro de forma segura."""
        if not hex_str: 
            return 0
        return int(hex_str, 16)

    @staticmethod
    def int_to_bits(valor, num_bits=8):
        """Converte inteiro para uma lista de bits (0s e 1s) correspondentes."""
        return [(valor >> i) & 1 for i in range(num_bits)]