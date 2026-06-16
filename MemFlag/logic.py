import struct

class BitConverter:
    @staticmethod
    def bits_to_int(bits):
        """Recebe uma lista de 1s e 0s (do bit 0 até o limite) e retorna o decimal total"""
        return sum(val * (2**i) for i, val in enumerate(bits))

    @staticmethod
    def int_to_hex(valor, num_bits):
        """Converte para string hexadecimal com o padding correto"""
        chars = num_bits // 4
        mascara = (1 << num_bits) - 1
        valor_mascarado = valor & mascara
        return f"0x{valor_mascarado:0{chars}x}"

    @staticmethod
    def hex_to_int(hex_str):
        """Converte string hexadecimal para inteiro"""
        if not hex_str: 
            return 0
        return int(hex_str, 16)

    @staticmethod
    def int_to_bits(valor, num_bits):
        """Converte inteiro para uma lista de bits (0s e 1s)"""
        return [(valor >> i) & 1 for i in range(num_bits)]

    @staticmethod
    def float_to_int(f_val):
        """Converte Float para a sua representação inteira bit a bit (IEEE 754 de 32-bits)"""
        try:
            return struct.unpack('>I', struct.pack('>f', f_val))[0]
        except Exception:
            return 0

    @staticmethod
    def int_to_float(i_val):
        """Converte a representação inteira bit a bit de volta para Float (IEEE 754)"""
        try:
            return struct.unpack('>f', struct.pack('>I', i_val & 0xFFFFFFFF))[0]
        except Exception:
            return 0.0
        
    @staticmethod
    def calc_pointer_target(base_hex, offset_hex):
        """Soma Base + Offset para achar o Alvo"""
        try:
            base = int(base_hex, 16) if base_hex else 0
            offset = int(offset_hex, 16) if offset_hex else 0
            return f"0x{(base + offset):06x}"
        except ValueError:
            return ""
    
    @staticmethod
    def calc_pointer_offset(base_hex, target_hex):
        """Subtrai Alvo - Base para achar o Offset"""
        try:
            base = int(base_hex, 16) if base_hex else 0
            target = int(target_hex, 16) if target_hex else 0
            diff = target - base
            if diff < 0:
                return f"-0x{(diff):x}"
            return f"+0x{diff:x}"
        except ValueError:
            return ""
        
    @staticmethod
    def calc_pointer_base(target_hex, offset_hex):
        """Subtrai Alvo - Offset para achar a Base"""
        try:
            target = int(target_hex, 16) if target_hex else 0
            offset = int(offset_hex, 16) if offset_hex else 0
            base = target - offset
            return f"0x{max(0, base):06x}"
        except ValueError:
            return ""