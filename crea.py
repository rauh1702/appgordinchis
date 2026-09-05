import os
from PIL import Image, ImageDraw
import wave
import math
import struct

# ---------------------------
# Crear carpetas si no existen
# ---------------------------
folders = ["drawings", "stickers", "videos", "sounds", "saved"]
for f in folders:
    if not os.path.exists(f):
        os.makedirs(f)

# ---------------------------
# Función para crear PNG simple
# ---------------------------
def create_png(path, shape="circle", color=(255,0,0,255), size=(80,80)):
    img = Image.new("RGBA", size, (255,255,255,0))
    draw = ImageDraw.Draw(img)
    if shape == "circle":
        draw.ellipse([0,0,size[0],size[1]], fill=color)
    elif shape == "square":
        draw.rectangle([0,0,size[0],size[1]], fill=color)
    elif shape == "star":
        w, h = size
        points = [
            (w*0.5,0),(w*0.6,h*0.35),(w,h*0.4),(w*0.65,h*0.65),
            (w*0.75,h),(w*0.5,h*0.8),(w*0.25,h),(w*0.35,h*0.65),
            (0,h*0.4),(w*0.4,h*0.35)
        ]
        draw.polygon(points, fill=color)
    img.save(path)

# ---------------------------
# Crear dibujos para colorear
# ---------------------------
create_png("drawings/dog.png", "circle", (200,100,50))
create_png("drawings/cat.png", "square", (100,200,50))
create_png("drawings/star.png", "star", (255,255,0))

# ---------------------------
# Crear stickers para el juego
# ---------------------------
create_png("stickers/dog.png", "circle", (200,100,50))
create_png("stickers/cat.png", "square", (100,200,50))
create_png("stickers/star.png", "star", (255,255,0))
create_png("stickers/ball.png", "circle", (50,150,255))

# ---------------------------
# Crear sonido WAV simple
# ---------------------------
def create_wav(path, duration=0.2, freq=440):
    framerate = 44100
    amplitude = 16000
    nframes = int(duration * framerate)
    
    wav_file = wave.open(path, 'w')
    wav_file.setparams((1, 2, framerate, nframes, 'NONE', 'not compressed'))

    for i in range(nframes):
        t = i / framerate
        value = int(amplitude * math.sin(2 * math.pi * freq * t))
        data = struct.pack('<h', value)
        wav_file.writeframesraw(data)
    
    wav_file.close()

create_wav("sounds/correct.wav")

# ---------------------------
# Mensaje final
# ---------------------------
print("Mini-pack de recursos generado correctamente.")
print("Carpetas y archivos creados:")
for f in folders:
    print(f"- {f}/")
print("\nRecuerda agregar un video MP4 corto en la carpeta videos/ para probar Dibujos Animados.")

