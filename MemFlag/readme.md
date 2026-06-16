Uma ferramenta de engenharia reversa e mapeamento de memória desenvolvida em Python (CustomTkinter) para auxiliar desenvolvedores do [RetroAchievements](https://retroachievements.org/). 

Esta aplicação elimina a necessidade de fazer cálculos manuais repetitivos durante a criação de conquistas, oferecendo conversores em tempo real para Bit Flags, Hexadecimal, Decimal, Floats e resolução de ponteiros.

## Funcionalidades

* **Conversor Dinâmico:** Conversão em tempo real entre Decimal e Hexadecimal.
* **Calculadora de Bit Flags:** Interface interativa para ativar/desativar bits individuais, calculando automaticamente os valores (suporta 8-bit, 16-bit e 32-bit).
* **Suporte a Float (IEEE 754):** Conversão precisa de valores de ponto flutuante de 32-bits para Hexadecimal.
* **Smart Pointer Solver:** Calculadora inteligente de offsets. Preencha dois campos (Base, Offset ou Alvo) e a ferramenta calcula o terceiro automaticamente.
* **Modo Escuro Nativo:** Interface limpa e moderna construída com `customtkinter`.