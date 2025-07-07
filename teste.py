# -*- coding: utf-8 -*-
import time
from rpi_ws281x import *

# --- Configurações da Fita de LED (ajuste conforme sua fita) ---
LED_COUNT      = 60      # Número de LEDs na sua fita.
LED_PIN        = 18      # GPIO 18. NÃO MUDE.
LED_FREQ_HZ    = 800000  # Frequência do sinal (geralmente 800khz).
LED_DMA        = 10      # Canal DMA.
LED_BRIGHTNESS = 75      # Brilho de 0 a 255. Cuidado com fontes fracas!
LED_INVERT     = False   # Mude para True se o sinal precisar ser invertido.
LED_CHANNEL    = 0       # Mude para '1' para GPIOs 13, 19, 41, 45 ou 53.


def wheel(pos):
    """Gera cores do arco-íris a partir de uma posição na roda de cores (0-255)."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=5):
    """Desenha um ciclo de arco-íris que se move pela fita."""
    print("Iniciando Ciclo Arco-Íris...")
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            # A mágica do arco-íris acontece aqui!
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Acende os LEDs em estilo de perseguição de marquise de cinema."""
    print("Iniciando Perseguição Teatral...")
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                # Liga um a cada três LEDs
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                # Apaga os LEDs para o próximo passo da "perseguição"
                strip.setPixelColor(i + q, 0)

def limpar_fita(strip):
    """Apaga TODOS os LEDs da fita."""
    print("\nLimpando a fita...")
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    time.sleep(1) # Pequena pausa para garantir que o comando foi enviado

# --- Programa Principal ---
if __name__ == '__main__':
    # Cria e inicializa o objeto da fita de LED.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()

    print('Show de luzes iniciado! Pressione Ctrl-C para sair.')
    
    try:
        # Executa a sequência de padrões
        theaterChase(strip, Color(127, 0, 0))  # Perseguição Vermelha
        theaterChase(strip, Color(0, 0, 127))  # Perseguição Azul
        rainbow(strip) # Arco-íris

    except KeyboardInterrupt:
        # Se o usuário pressionar Ctrl-C, o bloco 'finally' cuidará da limpeza.
        pass
    
    finally:
        # Garante que os LEDs sejam sempre apagados ao final do script.
        limpar_fita(strip)