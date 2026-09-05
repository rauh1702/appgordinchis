# generar_simon_sounds.py
from pydub import AudioSegment
from pydub.generators import Sine
import os

# Crear carpeta 'sounds' si no existe
os.makedirs("sounds", exist_ok=True)

# Definir sonidos: nombre y frecuencia (Hz)
sounds = {
    "red.wav": 440,      # La
    "green.wav": 554,    # Do#
    "blue.wav": 659,     # Mi
    "yellow.wav": 784    # Sol
}

duration_ms = 300  # Duración de cada tono (ms)

for name, freq in sounds.items():
    sine_wave = Sine(freq).to_audio_segment(duration=duration_ms)
    file_path = os.path.join("sounds", name)
    sine_wave.export(file_path, format="wav")
    print(f"Generado {file_path}")

print("¡Todos los sonidos de Simon Dice se han generado en la carpeta 'sounds'!")
