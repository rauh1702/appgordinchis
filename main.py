from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, RoundedRectangle, Rectangle
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
import numpy as np
import os
import random
from kivy.core.audio import SoundLoader
from functools import partial
from numba import njit
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
import os
import webview
os.environ["KIVY_METRICS_DENSITY"] = "1"
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

# ---------------------------
# Botón imagen personalizado
# ---------------------------
class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Puedes pasar 'source' como la imagen que quieras mostrar
        # y 'on_release_callback' como función a ejecutar al tocar
        self.on_release_callback = kwargs.get('on_release_callback', None)

    def on_release(self):
        if self.on_release_callback:
            self.on_release_callback()


def open_youtube_kids():
    url = "https://www.youtubekids.com/"
    # Crear ventana de webview con la URL
    webview.create_window("YouTube Kids", url)
    webview.start()
# ---------------------------
# Botón redondo personalizado
# ---------------------------
class RoundButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = kwargs.get('background_color', (1,1,1,1))
        with self.canvas.before:
            Color(*self.background_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[50])
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_color(self, color):
        self.background_color = color
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[50])

# ---------------------------
# Flood fill animado
# ---------------------------
@njit
def flood_fill_numba(pixels, x, y, target, new_color):
    stack = [(x, y)]
    h, w = pixels.shape[:2]
    while stack:
        px, py = stack.pop()
        if 0 <= px < w and 0 <= py < h:
            if np.all(pixels[py, px] == target):
                pixels[py, px] = new_color
                stack.append((px+1, py))
                stack.append((px-1, py))
                stack.append((px, py+1))
                stack.append((px, py-1))

def flood_fill_animated(pixels, x, y, target, new_color, callback, batch=2000):
    stack = [(x, y)]
    h, w = pixels.shape[:2]

    def step(dt):
        nonlocal stack
        count = 0
        while stack and count < batch:
            px, py = stack.pop()
            if 0 <= px < w and 0 <= py < h:
                if np.all(pixels[py, px] == target):
                    pixels[py, px] = new_color
                    stack.append((px+1, py))
                    stack.append((px-1, py))
                    stack.append((px, py+1))
                    stack.append((px, py-1))
            count += 1
        callback()
        return bool(stack)

    def animate(dt):
        if step(dt):
            Clock.schedule_once(animate, 0.01)
    Clock.schedule_once(animate, 0.01)

# ---------------------------
# Widget de dibujo
# ---------------------------
class PaintWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (1,0,0,1)
        self.pixels = None
        self.texture = None
        self.rect = None
        self.flood_fill_active = False

    def set_color(self, rgba):
        self.color = rgba

    def load_image(self, path):
        if os.path.exists(path):
            img = CoreImage(path)
            tex = img.texture
            self.pixels = np.frombuffer(tex.pixels, dtype=np.uint8).reshape(tex.height, tex.width, 4).copy()
            self.pixels = np.flipud(self.pixels)
            self.texture = Texture.create(size=(tex.width, tex.height))
            self.texture.blit_buffer(self.pixels.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        else:
            self.pixels = np.full((400,400,4), 255, dtype=np.uint8)
            self.texture = Texture.create(size=(400,400))
            self.texture.blit_buffer(self.pixels.flatten(), colorfmt='rgba', bufferfmt='ubyte')

        self.canvas.clear()
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        if self.rect:
            self.rect.pos = self.pos
            self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            x = int((touch.x - self.pos[0]) / self.size[0] * self.texture.width)
            y = int((touch.y - self.pos[1]) / self.size[1] * self.texture.height)
            if self.flood_fill_active and self.pixels is not None:
                self.flood_fill(x, y, self.color)
            with self.canvas:
                Color(*self.color)
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=5)

    def on_touch_move(self, touch):
        if 'line' in touch.ud:
            touch.ud['line'].points += [touch.x, touch.y]

    def clear_canvas(self):
        if self.pixels is not None and self.texture is not None:
            self.texture.blit_buffer(self.pixels.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        self.canvas.clear()
        with self.canvas:
            if self.texture:
                self.rect = Rectangle(texture=self.texture, pos=self.pos, size=self.size)

    def flood_fill(self, x, y, rgba):
        if self.pixels is None:
            return
        target_color = self.pixels[y, x].copy()
        new_color = (np.array(rgba)*255).astype(np.uint8)
        if np.array_equal(target_color, new_color):
            return
        flood_fill_animated(self.pixels, x, y, target_color, new_color, callback=self.update_texture)

    def update_texture(self):
        if self.texture:
            self.texture.blit_buffer(self.pixels.flatten(), colorfmt='rgba', bufferfmt='ubyte')
            if self.rect:
                self.rect.texture = self.texture

# ---------------------------
# Pantalla principal con música continua
# ---------------------------
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image

# ---------------------------
# Botón de imagen
# ---------------------------
class ImageButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_release_callback = kwargs.get('on_release_callback', None)

    def on_release(self):
        if self.on_release_callback:
            self.on_release_callback()


# ---------------------------
# Pantalla principal con botones-imagen
# ---------------------------
class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Cargar música de fondo
        music_path = os.path.join('sounds', 'menu_music.mp3')
        if os.path.exists(music_path):
            self.bg_music = SoundLoader.load(music_path)
            if self.bg_music:
                self.bg_music.loop = True
                self.bg_music.play()
        else:
            print("No se encontró menu_music.mp3")

        # Fondo
        if os.path.exists('fondo.png'):
            layout.add_widget(Image(source='fondo.png', allow_stretch=True, keep_ratio=False))

        # Botón Pinta y Colorea (izquierda)
        btn_paint = ImageButton(
            source='boton/paint_ico.png',
            size_hint=(0.25, 0.25),
            pos_hint={"center_x": 0.25, "center_y": 0.5},
            on_release_callback=lambda: self.goto_screen('paint')
        )
        layout.add_widget(btn_paint)

        # Botón Juegos (centro)
        btn_games = ImageButton(
            source='boton/games_icon.png',
            size_hint=(0.25, 0.25),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            on_release_callback=lambda: self.goto_screen('games', stop_music=True)
        )
        layout.add_widget(btn_games)

        # Botón Dibujos Animados (derecha)
        btn_videos = ImageButton(
            source='boton/videos_icon.png',
            size_hint=(0.25, 0.25),
            pos_hint={"center_x": 0.75, "center_y": 0.5},
            on_release_callback=lambda: self.goto_screen('videos')
        )
        layout.add_widget(btn_videos)

        self.add_widget(layout)

    def on_enter(self):
        # Reproducir música cuando se vuelve a la pantalla
        if hasattr(self, 'bg_music') and self.bg_music:
            if self.bg_music.state != 'play':
                self.bg_music.play()

    def goto_screen(self, screen_name, stop_music=False):
        # Detener música solo si se entra a un juego
        if stop_music and hasattr(self, 'bg_music') and self.bg_music:
            self.bg_music.stop()
        self.manager.current = screen_name






# ---------------------------
# Pantalla Pintura
# ---------------------------
class PaintScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.paint_widget = PaintWidget(size_hint=(1,0.75), pos_hint={"x":0, "y":0.15})
        layout.add_widget(self.paint_widget)

        colors = [(1,0,0,1),(0,1,0,1),(0,0,1,1),(1,1,0,1),(1,0.5,0,1),(0,1,1,1),
                  (1,0,1,1),(0.5,0.5,0.5,1),(0.3,0.2,0.1,1),(1,1,1,1),(0,0,0,1),(0.5,0,0.5,1)]
        box_top = BoxLayout(size_hint=(1,0.05), pos_hint={"y":0.9})
        box_bottom = BoxLayout(size_hint=(1,0.05), pos_hint={"y":0.85})
        for i, c in enumerate(colors):
            btn = RoundButton(background_color=c)
            btn.bind(on_release=lambda x, col=c: self.paint_widget.set_color(col))
            (box_top if i<6 else box_bottom).add_widget(btn)
        layout.add_widget(box_top)
        layout.add_widget(box_bottom)

        images_folder = 'images'
        img_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png','.jpg','.jpeg'))]
        box_images = BoxLayout(size_hint=(1,0.1), pos_hint={"y":0.95})
        for img_file in img_files:
            btn_img = RoundButton(background_normal=os.path.join(images_folder,img_file),
                                  background_down=os.path.join(images_folder,img_file))
            btn_img.bind(on_release=lambda b, f=os.path.join(images_folder,img_file): self.load_image(f))
            box_images.add_widget(btn_img)
        layout.add_widget(box_images)

        btn_new = RoundButton(text="Nuevo Dibujo", size_hint=(0.3,0.08), pos_hint={"x":0.05, "y":0.05}, background_color=(0,1,1,1))
        btn_new.bind(on_release=lambda x: self.new_canvas())
        layout.add_widget(btn_new)
        btn_clear = RoundButton(text="Borrar", size_hint=(0.3,0.08), pos_hint={"x":0.4, "y":0.05}, background_color=(1,0,0,1))
        btn_clear.bind(on_release=lambda x: self.paint_widget.clear_canvas())
        layout.add_widget(btn_clear)
        btn_back = RoundButton(text="Volver al menú", size_hint=(0.3,0.08), pos_hint={"x":0.75, "y":0.05}, background_color=(0.2,0.2,0.2,1))
        btn_back.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        layout.add_widget(btn_back)

        self.add_widget(layout)
        if img_files:
            self.load_image(os.path.join(images_folder,img_files[0]))

    def new_canvas(self):
        self.paint_widget.pixels = np.full((400,400,4), 255, dtype=np.uint8)
        self.paint_widget.texture = Texture.create(size=(400,400))
        self.paint_widget.texture.blit_buffer(self.paint_widget.pixels.flatten(), colorfmt='rgba', bufferfmt='ubyte')
        self.paint_widget.canvas.clear()
        with self.paint_widget.canvas:
            self.paint_widget.rect = Rectangle(texture=self.paint_widget.texture, pos=self.paint_widget.pos, size=self.paint_widget.size)
        self.paint_widget.flood_fill_active = False

    def load_image(self, path):
        self.paint_widget.load_image(path)
        self.paint_widget.flood_fill_active = True

# ---------------------------
# Pantalla Juegos Simon Dice con sonido
# ---------------------------
class GamesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.show_main_buttons()

        # Cargar sonidos de los botones (asegúrate de tener estos archivos .wav)
        self.sounds = [
            SoundLoader.load('sounds/red.wav'),
            SoundLoader.load('sounds/green.wav'),
            SoundLoader.load('sounds/blue.wav'),
            SoundLoader.load('sounds/yellow.wav')
        ]

    def show_main_buttons(self):
        self.layout.clear_widgets()

        btn_back = RoundButton(
            text="Volver al menú",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5,"y":0.05},
            background_color=(0.7,0.2,0.2,1)  # rojo oscuro
        )
        btn_back.bind(on_release=lambda x: setattr(self.manager,'current','main'))
        self.layout.add_widget(btn_back)

        btn_simon = RoundButton(
            text="Simon Dice",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5,"y":0.7},
            background_color=(0.2,0.5,1,1)  # azul
        )
        btn_simon.bind(on_release=lambda x: self.start_simon())
        self.layout.add_widget(btn_simon)

        btn_whack = RoundButton(
            text="Golpea al zombie",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5,"y":0.55},
            background_color=(0.8,0.5,0,1)
        )
        btn_whack.bind(on_release=lambda x: setattr(self.manager,'current','whack'))
        self.layout.add_widget(btn_whack)

        btn_audio_paint = RoundButton(
            text="Pinta por Audio",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5,"y":0.4},
            background_color=(1,0.5,0,1)
        )
        btn_audio_paint.bind(on_release=lambda x: setattr(self.manager,'current','paint_audio'))
        self.layout.add_widget(btn_audio_paint)


    def start_simon(self):
        self.layout.clear_widgets()
        self.sequence = []
        self.user_sequence = []
        self.level = 1
        self.colors = [(1,0,0,1),(0,1,0,1),(0,0,1,1),(1,1,0,1)]
        self.buttons = []

        positions = [{"center_x":0.25,"center_y":0.6},
                     {"center_x":0.75,"center_y":0.6},
                     {"center_x":0.25,"center_y":0.3},
                     {"center_x":0.75,"center_y":0.3}]
        for i, col in enumerate(self.colors):
            btn = RoundButton(size_hint=(0.3,0.3), pos_hint=positions[i])
            btn.set_color(col)
            btn.bind(on_release=partial(self.press_color, i))
            self.layout.add_widget(btn)
            self.buttons.append(btn)

        # Botón volver
        btn_back = RoundButton(text="Volver", size_hint=(0.3,0.08), pos_hint={"center_x":0.5,"y":0.05})
        btn_back.bind(on_release=lambda x: self.show_main_buttons())
        self.layout.add_widget(btn_back)

        Clock.schedule_once(lambda dt: self.next_round(), 1)

    def next_round(self):
        self.user_sequence = []
        self.sequence.append(random.randint(0,3))
        self.flash_sequence(0)

    def flash_sequence(self, idx):
        if idx >= len(self.sequence):
            return
        btn_idx = self.sequence[idx]
        btn = self.buttons[btn_idx]
        original_color = btn.background_color

        # Cambiar color a blanco
        btn.set_color((1,1,1,1))

        # Reproducir sonido del botón
        if self.sounds[btn_idx]:
            self.sounds[btn_idx].play()

        Clock.schedule_once(lambda dt: self.restore_color(btn, original_color, idx), 0.5)

    def restore_color(self, btn, color, idx):
        btn.set_color(color)
        Clock.schedule_once(lambda dt: self.flash_sequence(idx+1), 0.3)

    def press_color(self, idx, instance):
        if len(self.user_sequence) >= len(self.sequence):
            return
        self.user_sequence.append(idx)
        if self.user_sequence[-1] != self.sequence[len(self.user_sequence)-1]:
            self.layout.clear_widgets()
            self.layout.add_widget(Label(text=f"Fallaste en el nivel {self.level}", font_size=32, pos_hint={"center_x":0.5,"center_y":0.5}))
            btn_back = RoundButton(text="Volver", size_hint=(0.3,0.08), pos_hint={"center_x":0.5,"y":0.05})
            btn_back.bind(on_release=lambda x: self.show_main_buttons())
            self.layout.add_widget(btn_back)
            return
        if len(self.user_sequence) == len(self.sequence):
            self.level += 1
            Clock.schedule_once(lambda dt: self.next_round(), 1)

# ---------------------------
# Pantalla Golpea al Zombie con niveles infinitos y ovación
# ---------------------------
class WhackAMoleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Variables del juego
        self.grid_size = 3
        self.buttons = []
        self.active_mole = None
        self.current_level = 0
        self.score = 0

        # Cargar sonido de golpe
        sound_path = os.path.join('sounds', 'whack.wav')
        if os.path.exists(sound_path):
            self.mole_sound = SoundLoader.load(sound_path)
        else:
            print("No se encontró whack.wav")
            self.mole_sound = None

        # Cargar sonido de ovación
        applause_path = os.path.join('sounds', 'applause.wav')
        if os.path.exists(applause_path):
            self.applause_sound = SoundLoader.load(applause_path)
        else:
            print("No se encontró applause.wav")
            self.applause_sound = None

        # Botón volver
        btn_back = RoundButton(
            text="Volver al menú",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5,"y":0.05},
            background_color=(0.7,0.2,0.2,1)
        )
        btn_back.bind(on_release=lambda x: self.back_to_menu())
        self.layout.add_widget(btn_back)

        # Label de puntuación
        self.score_label = Label(
            text=f"Puntuación: {self.score}", 
            font_size=32, 
            pos_hint={"center_x":0.5,"y":0.9}
        )
        self.layout.add_widget(self.score_label)

        # Crear rejilla de botones
        spacing_x = 0.05
        spacing_y = 0.15
        size_hint = 0.25
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                btn = Widget(
                    size_hint=(size_hint, size_hint),
                    pos_hint={"x": col*(size_hint+spacing_x)+0.1,
                              "y": row*(size_hint+spacing_y)+0.3}
                )
                self.layout.add_widget(btn)
                self.buttons.append(btn)

        # Widget del zombie
        zombie_path = os.path.join('images', 'zombie.png')
        if os.path.exists(zombie_path):
            self.zombie_texture = CoreImage(zombie_path).texture
        else:
            print("No se encontró zombie.png")
            self.zombie_texture = None

        self.zombie_widget = Widget(size_hint=(size_hint, size_hint), pos=(0,0))
        with self.zombie_widget.canvas:
            if self.zombie_texture:
                self.zombie_rect = Rectangle(
                    texture=self.zombie_texture,
                    pos=self.zombie_widget.pos,
                    size=self.zombie_widget.size
                )
            else:
                from kivy.graphics import Color
                Color(1,0,0,1)
                self.zombie_rect = Rectangle(
                    pos=self.zombie_widget.pos,
                    size=self.zombie_widget.size
                )

        self.zombie_widget.bind(pos=self.update_zombie_rect, size=self.update_zombie_rect)
        self.layout.add_widget(self.zombie_widget)
        self.zombie_widget.opacity = 0

        # Variables de nivel dinámico
        self.levels_dynamic = {"time":1.0, "score_to_pass":5}

        # Iniciar aparición de zombies
        self.mole_event = Clock.schedule_interval(self.show_mole_dynamic, self.levels_dynamic["time"])

    def update_zombie_rect(self, *args):
        self.zombie_rect.pos = self.zombie_widget.pos
        self.zombie_rect.size = self.zombie_widget.size

    def show_mole_dynamic(self, dt):
        # Ocultar zombie anterior
        if self.active_mole:
            self.zombie_widget.opacity = 0
        # Elegir botón aleatorio
        target_widget = random.choice(self.buttons)
        self.active_mole = target_widget
        # Mover zombie
        self.zombie_widget.pos = target_widget.pos
        self.zombie_widget.opacity = 1
        self.update_zombie_rect()

    def on_touch_down(self, touch):
        if self.active_mole and self.zombie_widget.opacity == 1:
            if self.zombie_widget.collide_point(*touch.pos):
                self.score += 1
                self.score_label.text = f"Puntuación: {self.score}"
                if self.mole_sound:
                    self.mole_sound.play()
                self.zombie_widget.opacity = 0
                self.active_mole = None

                # Verificar si pasó el nivel
                if self.score >= self.levels_dynamic["score_to_pass"]:
                    self.next_level()
                return True
        return super().on_touch_down(touch)

    def next_level(self):
        # Mostrar imagen de recompensa cíclica
        reward_index = (self.current_level % 3) + 1
        reward_path = f"images/reward{reward_index}.png"
        if os.path.exists(reward_path):
            self.reward_widget = Widget(size_hint=(0.5,0.5), pos_hint={"center_x":0.5,"center_y":0.5})
            with self.reward_widget.canvas:
                reward_texture = CoreImage(reward_path).texture
                self.reward_rect = Rectangle(texture=reward_texture,
                                             pos=self.reward_widget.pos,
                                             size=self.reward_widget.size)
            self.reward_widget.bind(pos=self.update_reward_rect, size=self.update_reward_rect)
            self.layout.add_widget(self.reward_widget)
            
            # Reproducir sonido de ovación
            if self.applause_sound:
                self.applause_sound.play()
            
            Clock.schedule_once(lambda dt: self.layout.remove_widget(self.reward_widget), 2.0)

        # Incrementar nivel
        self.current_level += 1
        self.score = 0
        self.score_label.text = f"Puntuación: {self.score}"

        # Aumentar dificultad
        new_time = max(0.3, 1.0 - self.current_level * 0.05)  # nunca menor a 0.3s
        new_score_to_pass = 5 + self.current_level
        self.levels_dynamic = {"time": new_time, "score_to_pass": new_score_to_pass}

        # Reiniciar aparición de zombies
        Clock.unschedule(self.mole_event)
        self.mole_event = Clock.schedule_interval(self.show_mole_dynamic, self.levels_dynamic["time"])

    def update_reward_rect(self, *args):
        if hasattr(self, 'reward_rect') and self.reward_rect:
            self.reward_rect.pos = self.reward_widget.pos
            self.reward_rect.size = self.reward_widget.size

    def back_to_menu(self):
        # Reiniciar variables
        self.current_level = 0
        self.score = 0
        self.score_label.text = f"Puntuación: {self.score}"
        self.active_mole = None
        Clock.unschedule(self.mole_event)
        self.levels_dynamic = {"time":1.0, "score_to_pass":5}
        self.mole_event = Clock.schedule_interval(self.show_mole_dynamic, self.levels_dynamic["time"])
        
        # Volver al menú
        self.manager.current = 'main'

# ---------------------------
# Pantalla Pinta por Audio robusta
# ---------------------------
class PaintByAudioScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)

        # Widget de pintura
        self.paint_widget = PaintWidget(size_hint=(1, 0.85), pos_hint={"x":0, "y":0.15})
        self.layout.add_widget(self.paint_widget)

        # Botón limpiar
        btn_clear = RoundButton(
            text="Borrar",
            size_hint=(0.3, 0.08),
            pos_hint={"x":0.35,"y":0.05},
            background_color=(1,0,0,1)
        )
        btn_clear.bind(on_release=lambda x: self.paint_widget.clear_canvas())
        self.layout.add_widget(btn_clear)

        # Botón volver
        btn_back = RoundButton(
            text="Volver al menú",
            size_hint=(0.4,0.08),
            pos_hint={"center_x":0.5,"y":0.15},
            background_color=(0.7,0.2,0.2,1)
        )
        btn_back.bind(on_release=lambda x: setattr(self.manager,'current','main'))
        self.layout.add_widget(btn_back)

        # Lista de tareas
        self.tasks = [
            {"audio":"sounds/apple.wav", "color":(1,0,0,1), "ref_image":"images/apple.png"},
            {"audio":"sounds/sun.wav", "color":(1,1,0,1), "ref_image":"images/sun.png"},
            {"audio":"sounds/tree.wav", "color":(0,1,0,1), "ref_image":"images/tree.png"}
        ]
        self.current_task_index = -1
        self.ref_widget = None
        self.audio = None

        # Botón reproducir instrucción
        btn_play = RoundButton(
            text="Reproducir instrucción",
            size_hint=(0.4,0.08),
            pos_hint={"center_x":0.3,"y":0.05},
            background_color=(0.2,0.5,1,1)
        )
        btn_play.bind(on_release=lambda x: self.play_audio())
        self.layout.add_widget(btn_play)

        # Botón terminé
        btn_done = RoundButton(
            text="Terminé",
            size_hint=(0.4,0.08),
            pos_hint={"center_x":0.7,"y":0.05},
            background_color=(0.5,1,0.5,1)
        )
        btn_done.bind(on_release=lambda x: self.show_reference())
        self.layout.add_widget(btn_done)

        # Inicializar primera tarea
        self.next_task()

    def next_task(self):
        self.current_task_index += 1
        if self.current_task_index >= len(self.tasks):
            self.current_task_index = 0  # ciclo infinito

        self.current_task = self.tasks[self.current_task_index]

        # Cambiar color del pincel
        self.paint_widget.set_color(self.current_task["color"])
        self.paint_widget.clear_canvas()
        self.paint_widget.flood_fill_active = True

        # Cargar audio
        audio_path = self.current_task["audio"]
        if os.path.exists(audio_path):
            if self.audio:  # detener audio anterior
                self.audio.stop()
            self.audio = SoundLoader.load(audio_path)
        else:
            self.audio = None
            print(f"No se encontró el audio {audio_path}")

        # Cargar imagen de referencia
        ref_path = self.current_task.get("ref_image")
        if self.ref_widget and self.ref_widget in self.layout.children:
            self.layout.remove_widget(self.ref_widget)
            self.ref_widget = None

        if ref_path and os.path.exists(ref_path):
            try:
                self.ref_widget = Widget(size_hint=(0.3,0.3), pos_hint={"center_x":0.5,"y":0.7})
                with self.ref_widget.canvas:
                    self.ref_texture = CoreImage(ref_path).texture
                    self.ref_rect = Rectangle(texture=self.ref_texture,
                                              pos=self.ref_widget.pos,
                                              size=self.ref_widget.size)
                self.ref_widget.bind(pos=self.update_ref_rect, size=self.update_ref_rect)
                self.layout.add_widget(self.ref_widget)
                self.ref_widget.opacity = 0
            except Exception as e:
                print(f"Error al cargar imagen de referencia: {e}")
                self.ref_widget = None
        else:
            self.ref_widget = None

    def update_ref_rect(self, *args):
        if self.ref_widget and hasattr(self, 'ref_rect'):
            self.ref_rect.pos = self.ref_widget.pos
            self.ref_rect.size = self.ref_widget.size

    def play_audio(self):
        if self.audio:
            self.audio.stop()  # reiniciar audio
            self.audio.play()

    def show_reference(self):
        if self.ref_widget:
            self.ref_widget.opacity = 1
        Clock.schedule_once(lambda dt: self.next_task(), 2.0)

# ---------------------------
# Pantalla Videos
# ---------------------------
class VideosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.add_widget(layout)

        btn_open_yk = RoundButton(
            text="Abrir YouTube Kids",
            size_hint=(0.6,0.2),
            pos_hint={"center_x":0.5, "center_y":0.5},
            background_color=(0.2,0.6,1,1)
        )
        btn_open_yk.bind(on_release=lambda x: open_youtube_kids())
        layout.add_widget(btn_open_yk)

        # Botón volver al menú
        btn_back = RoundButton(
            text="Volver al menú",
            size_hint=(0.4,0.1),
            pos_hint={"center_x":0.5, "y":0.1},
            background_color=(1,0.2,0.2,1)
        )
        btn_back.bind(on_release=lambda x: setattr(self.manager,'current','main'))
        layout.add_widget(btn_back)


# ---------------------------
# App principal
# ---------------------------
class GordinchisApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=0.3))
        sm.add_widget(MainMenu(name='main'))
        sm.add_widget(PaintScreen(name='paint'))
        sm.add_widget(GamesScreen(name='games'))
        sm.add_widget(VideosScreen(name='videos'))
        sm.add_widget(WhackAMoleScreen(name='whack'))
        sm.add_widget(PaintByAudioScreen(name='paint_audio'))


        return sm

if __name__ == "__main__":
    GordinchisApp().run()





































