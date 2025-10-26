import requests
import re
import json
from kivy.network.urlrequest import UrlRequest
from kivy.uix.slider import Slider
from kivy.core.clipboard import Clipboard
import sys
from kivy.utils import platform


# create_presplash.py
from PIL import Image, ImageDraw

def create_presplash():
    img = Image.new('RGB', (1920, 1080), (30, 100, 200))
    d = ImageDraw.Draw(img)
    img.save('presplash.png')
    print("presplash.png создан")

create_presplash()


# Проверка платформы перед импортом Android-специфичных модулей
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        from android.storage import app_storage_path
        from jnius import autoclass
    except ImportError as e:
        print(f"Android modules not available: {e}")

from kivy.config import Config

Config.set('graphics', 'orientation', 'portrait')
Config.set('graphics', 'resizable', '1')  # разрешаем изменение размера
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'minimum_width', '360')
Config.set('graphics', 'minimum_height', '640')
Config.set('graphics', 'position', 'auto')
Config.set('graphics', 'presplash', '')

Config.set('graphics', 'maxfps', 60)
Config.set('kivy', 'log_level', 'warning')
Config.set('kivy', 'exit_on_escape', '0')  # Отключаем автоматический выход по Escape

from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.switch import Switch
from kivy.properties import (StringProperty, BooleanProperty, NumericProperty, 
                           ListProperty, ObjectProperty, ColorProperty)
from kivy.properties import DictProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.graphics import Color, Rectangle, RoundedRectangle
import json
import os
import random

from kivy.graphics import Color, Rectangle, RoundedRectangle, Line

from kivy.core.window import Window





def get_app_storage_path():
    """Получение пути к хранилищу приложения"""
    if platform == 'android':
        try:
            from android.storage import app_storage_path
            return app_storage_path()
        except ImportError:
            return os.path.dirname(os.path.abspath(__file__))
    else:
        return os.path.dirname(os.path.abspath(__file__))



class ModernFileChooser(BoxLayout):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.app = App.get_running_app()
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        
        # БИНДИМ КЛАВИАТУРУ ДЛЯ ENTER
        self._keyboard_bind_added = False
        
        if platform != 'android' and platform != 'ios':
            if hasattr(Window, 'on_drop_file'):
                Window.bind(on_drop_file=self._on_file_drop)
            else:
                Window.bind(on_dropfile=self._on_file_drop)
                
        self.build_ui()

    def on_enter(self):
        """При входе - добавляем обработчик Enter"""
        if not self._keyboard_bind_added:
            Window.bind(on_key_down=self._on_key_down)
            self._keyboard_bind_added = True
    
    def on_leave(self):
        """При выходе - убираем обработчик"""
        if self._keyboard_bind_added:
            Window.unbind(on_key_down=self._on_key_down)
            self._keyboard_bind_added = False
    
    def _on_key_down(self, window, key, *args):
        """Обработка Enter для открытия файлового диалога"""
        if key == 13:  # Enter
            self.open_file_chooser(None)
            return True
        return False


    def _on_file_drop(self, *args):
        """Обработчик перетаскивания файла - УНИВЕРСАЛЬНАЯ ВЕРСИЯ"""
        try:
            if len(args) == 2:
                file_path = args[1]
            else:
                file_path = args[1]
            if isinstance(file_path, bytes):
                file_path = file_path.decode('utf-8')
            if not file_path.lower().endswith(('.txt', '.qst')):
                self.app.show_notification("Поддерживаются только файлы .txt и .qst")
                return
                
            self.callback(file_path)
        except Exception as e:
            self.app.show_notification(f'Ошибка загрузки файла: {str(e)}')
    
    def build_ui(self):
        self.drop_area = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.7),
            padding=dp(20)
        )
        
        with self.drop_area.canvas.before:
            Color(rgba=[0.95, 0.95, 0.95, 1])
            self.drop_rect = RoundedRectangle(
                pos=self.drop_area.pos,
                size=self.drop_area.size,
                radius=[dp(12)]
            )
        
        self.drop_label = AndroidLabel(
            text='[b]Перетащите файл теста сюда[/b]\n\nПоддерживаются .txt и .qst',
            color=[0.4, 0.4, 0.4, 1],
            font_size=self.app.get_font_size(16),
            halign='center',
            text_size=(Window.width * 0.8, None)
        )
        
        self.drop_area.add_widget(self.drop_label)
        self.file_btn = AndroidButton(
            text='Выбрать файл вручную',
            size_hint=(1, 0.10),
            font_size=self.app.get_font_size(14),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1)
        )
        self.file_btn.bind(on_press=self.open_file_chooser)
        
        self.add_widget(self.drop_area)
        self.add_widget(self.file_btn)
        
        self.drop_area.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.drop_rect.pos = self.drop_area.pos
        self.drop_rect.size = self.drop_area.size
    
    def open_file_chooser(self, instance):
        if platform == 'android':
            try:
                self.open_android_file_chooser()
            except Exception as e:
                self.app.show_notification(f"Ошибка выбора файла: {str(e)}")
                # Fallback to regular file chooser
                SimpleFileChooserPopup(callback=self.callback).open()
        else:
            SimpleFileChooserPopup(callback=self.callback).open()
    
    def open_android_file_chooser(self):
        """FileChooser для Android"""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("*/*")
            PythonActivity.mActivity.startActivityForResult(intent, 123)
        except Exception as e:
            raise e

class SimpleFileChooserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.app = App.get_running_app()
        self.title = 'Выберите файл теста'
        self.size_hint = (0.9, 0.9)
        self.background_color = self.app.bg_color
        
        layout = BoxLayout(orientation='vertical')
        self.filechooser = FileChooserListView(
            path=os.path.expanduser('~'),
            filters=['*.txt', '*.qst']
        )
        self._apply_theme_to_filechooser()
        layout.add_widget(self.filechooser)
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        cancel_btn = AndroidButton(
            text='Отмена',
            background_color=self.app.card_color,
            color=self.app.text_primary,
            font_size=self.app.get_font_size(14),

        )
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        
        select_btn = AndroidButton(
            text='Выбрать',
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14),

        )
        select_btn.bind(on_press=self.select_file)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        layout.add_widget(btn_layout)
        
        self.content = layout
        self.app.bind(bg_color=self.update_colors)
    
    def _apply_theme_to_filechooser(self):
        """Применяет тему к FileChooser"""
        try:
            if self.app.is_dark_theme:
                self.filechooser.background_color = [0.2, 0.2, 0.2, 1]
                self.filechooser.foreground_color = [1, 1, 1, 1]
            else:
                self.filechooser.background_color = [1, 1, 1, 1]
                self.filechooser.foreground_color = [0, 0, 0, 1]
        except Exception as e:
            print(f"Не удалось применить тему к FileChooser: {e}")
    
    def update_colors(self, instance, value):
        """Обновление цветов при смене темы"""
        self.background_color = self.app.bg_color
        self._apply_theme_to_filechooser()

    def select_file(self, instance):
        if self.filechooser.selection:
            selected_file = self.filechooser.selection[0]
            if selected_file.lower().endswith(('.txt', '.qst')):
                self.callback(selected_file)
                self.dismiss()
            else:
                self.app.show_notification("Выберите файл с расширением .txt или .qst")


class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.build_ui()
        Clock.schedule_once(self.go_to_main, 3.0)

    def build_ui(self):
        """Создание интерфейса заставки"""
        layout = BoxLayout(orientation='vertical', padding=dp(50))
        with layout.canvas.before:
            Color(rgba=self.app.primary_color)
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
        logo_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.8))
        icon_label = AndroidLabel(
            text='',
            font_size=self.app.get_font_size(80),
            color=(1, 1, 1, 1),
            halign='center'
        )
        title_label = AndroidLabel(
            text='[b]Ассистент 2.0[/b]',
            font_size=self.app.get_font_size(32),
            color=(1, 1, 1, 1),
            halign='center'
        )
        subtitle_label = AndroidLabel(
            text='Система подготовки к тестированию',
            font_size=self.app.get_font_size(18),
            color=(1, 1, 1, 0.8),
            halign='center'
        )
        
        logo_layout.add_widget(icon_label)
        logo_layout.add_widget(title_label)
        logo_layout.add_widget(subtitle_label)
        
        layout.add_widget(logo_layout)
        bottom_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(0.6, None),
            height=dp(4),
            pos_hint={'center_x': 0.5}
        )
        loading_label = AndroidLabel(
            text='Загрузка...',
            font_size=self.app.get_font_size(14),
            color=(1, 1, 1, 0.7),
            halign='center'
        )
        
        bottom_layout.add_widget(self.progress_bar)
        bottom_layout.add_widget(loading_label)
        layout.add_widget(bottom_layout)
        
        self.add_widget(layout)
        self.animate_progress()
        layout.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, instance, value):
        """Обновление фона заставки"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.app.primary_color)
            self.bg_rect = Rectangle(pos=instance.pos, size=instance.size)

    def animate_progress(self):
        """Анимация прогресс-бара"""
        anim = Animation(value=100, duration=2.0)
        anim.start(self.progress_bar)

    def go_to_main(self, dt):
        """Переход на главный экран"""
        self.app.screen_manager.current = 'main'



class ModernFileChooserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = 'Загрузка теста'
        self.size_hint = (0.9, 0.8)
        
        layout = ModernFileChooser(callback=self.on_file_selected)
        self.content = layout
    
    def on_file_selected(self, file_path):
        self.callback(file_path)
        self.dismiss()

class FileChooserPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = 'Выберите файл теста'
        self.size_hint = (0.9, 0.9)
        
        layout = BoxLayout(orientation='vertical')
        
        self.filechooser = FileChooserListView()
        layout.add_widget(self.filechooser)
        
        btn_layout = BoxLayout(size_hint=(1, 0.1), spacing=dp(10))
        cancel_btn = AndroidButton(text='Отмена')
        cancel_btn.bind(on_press=lambda x: self.dismiss())
        select_btn = AndroidButton(text='Выбрать')
        select_btn.bind(on_press=self.select_file)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(select_btn)
        layout.add_widget(btn_layout)
        
        self.content = layout
    
    def select_file(self, instance):
        if self.filechooser.selection:
            self.callback(self.filechooser.selection[0])
            self.dismiss()



class TestQuestion:
    def __init__(self, text, answers, correct_indices):
        self.text = text
        self.answers = answers
        self.correct_indices = correct_indices

class AndroidButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = kwargs.get('background_color', (0.3, 0.3, 0.3, 1))
        self.background_down = ''
        self.markup = True
        self.font_name = 'Roboto'
        self.background_disabled_normal = ''
        self.background_disabled_down = ''
        app = App.get_running_app()
        initial_font_size = kwargs.get('font_size', None)
        if initial_font_size is None:
            self.font_size = app.get_font_size(14)
        else:
            if isinstance(initial_font_size, (int, float)):
                self.font_size = app.get_font_size(initial_font_size)
            else:
                self.font_size = initial_font_size
        initial_color = kwargs.get('color', None)
        if initial_color is None:
            self.color = app.text_primary
        else:
            self.color = initial_color
        self.disabled_color = self.color
        
        initial_bg_color = kwargs.get('background_color', (0.3, 0.3, 0.3, 1))
        
        with self.canvas.before:
            self.rect_color = Color(rgba=initial_bg_color)
            self.rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[dp(4)]
            )
        
        self.bind(
            pos=self.update_rect, 
            size=self.update_rect,
            background_color=self.on_background_color
        )
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def on_background_color(self, instance, value):
        """Обновление цвета при изменении background_color"""
        if hasattr(self, 'rect_color'):
            self.rect_color.rgba = value
    
    def on_press(self):
        if not self.disabled:
            current_color = self.rect_color.rgba
            darkened = [c * 0.7 for c in current_color[:3]] + [current_color[3]]
            anim = Animation(rgba=darkened, duration=0.1)
            anim.start(self.rect_color)
    
    def on_release(self):
        if not self.disabled:
            anim = Animation(rgba=self.background_color, duration=0.1)
            anim.start(self.rect_color)


class AndroidLabel(Label):
    def __init__(self, **kwargs):
        self.short_text = False

        super().__init__(**kwargs)
        self.font_name = 'Roboto'
        self.markup = True
        self.halign = 'left'
        self.valign = 'top'
        self.text_size = (None, None)
        app = App.get_running_app()
        initial_font_size = kwargs.get('font_size', None)
        if initial_font_size is None:
            self.font_size = app.get_font_size(14)
        else:
            if isinstance(initial_font_size, (int, float)):
                self.font_size = app.get_font_size(initial_font_size)
            else:
                self.font_size = initial_font_size
        
    def on_size(self, *args):
        """Автоматически устанавливаем text_size при изменении размера"""
        if not self.short_text:
            self.text_size = (self.width, None)

class AdaptiveCard(BoxLayout):
    """Адаптивная карточка с автоматической высотой"""
    def __init__(self, background_color=None, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.padding = dp(16)
        self.spacing = dp(8)
        self.background_color = background_color or self.app.card_color
        self.bind(minimum_height=self.setter('height'))
        with self.canvas.before:
            Color(rgba=self.background_color)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )
        self.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, instance, value):
        """Обновление фона карточки"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.background_color)
            instance.bg_rect = RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(12)]
            )

class OptimizedNavPanel(GridLayout):
    """Оптимизированная панель навигации по вопросам"""
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.buttons = []
        self.cols = 1
        self.rows = 1
        self.size_hint_x = None
        self.spacing = dp(5)
        self.height = dp(45)

    def build_buttons(self, questions_count):
        self.clear_widgets()
        self.buttons = []
        self.cols = questions_count
        self.width = questions_count * (dp(45) + dp(5))
        
        for i in range(questions_count):
            btn_color, text_color = self.app.get_question_button_color(i)
            btn = AndroidButton(
                text=str(i+1),
                size_hint_x=None,
                width=dp(45),
                height=dp(45),
                background_color=btn_color,
                color=text_color
            )

            btn.bind(on_press=lambda instance, idx=i: self.app.go_to_question(idx))
            self.add_widget(btn)
            self.buttons.append(btn)
        self.minimum_width = self.width
    
    def update_colors(self):
        """Быстрое обновление только цветов кнопок с правильными цветами текста"""
        for i, btn in enumerate(self.buttons):
            btn_color, text_color = self.app.get_question_button_color(i)
            btn.background_color = btn_color
            btn.color = text_color


class CustomPresetCreatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.slot_index = 0  # Индекс ячейки для сохранения
        # Автоматическое имя на основе номера ячейки
        self.preset_name = f"Пресет {self.slot_index + 1}"
        
        # Инициализируем цвета ТЕКУЩЕЙ активной темы приложения
        self.colors = self.copy_current_theme_colors()
        self.build_ui()

    def build_ui(self):
        """Построение интерфейса создания пресета"""
        self.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # Заголовок с номером пресета
        title = AndroidLabel(
            text=f'[b]Создание пресета {self.slot_index + 1}[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.08),
            color=self.colors['text_primary']
        )
        main_layout.add_widget(title)
        
        # Область предпросмотра
        preview_label = AndroidLabel(
            text='Предпросмотр:',
            font_size=self.app.get_font_size(16),
            color=self.colors['text_primary'],
            size_hint_y=0.05
        )
        main_layout.add_widget(preview_label)
        
        self.preview_card = self.create_preview_card()
        main_layout.add_widget(self.preview_card)
        
        # Настройки цветов
        colors_label = AndroidLabel(
            text='Настройка цветов:',
            font_size=self.app.get_font_size(16),
            color=self.colors['text_primary'],
            size_hint_y=0.05
        )
        main_layout.add_widget(colors_label)
        
        scroll = ScrollView(size_hint=(1, 0.5))
        self.colors_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.colors_layout.bind(minimum_height=self.colors_layout.setter('height'))
        
        self.create_color_settings()
        
        scroll.add_widget(self.colors_layout)
        main_layout.add_widget(scroll)
        
        # Кнопки
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.1, spacing=dp(10))
        cancel_btn = AndroidButton(
            text='Отмена',
            background_color=[0.7, 0.7, 0.7, 1],
            color=(0, 0, 0, 1)
        )
        cancel_btn.bind(on_press=self.cancel)
        
        save_btn = AndroidButton(
            text='Сохранить пресет',
            background_color=self.colors['primary_color'],
            color=(1, 1, 1, 1)
        )
        save_btn.bind(on_press=self.save_preset)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        main_layout.add_widget(btn_layout)
        
        self.add_widget(main_layout)


    def save_preset(self, instance):
        """Сохранение пресета"""
        try:
            # Автоматическое имя на основе номера ячейки
            preset_name = f"Пресет {self.slot_index + 1}"
            
            # Сохраняем пресет с разделением на темы
            self.app.color_settings_screen.custom_presets[preset_name] = {
                'light': {  # Цвета для светлой темы
                    'bg_color': self.colors['bg_color'],
                    'card_color': self.colors['card_color'],
                    'text_primary': self.colors['text_primary'],
                    'text_secondary': self.colors['text_secondary'],
                    'primary_color': self.colors['primary_color'],
                    'correct_color': self.colors['correct_color'],
                    'error_color': self.colors['error_color']
                },
                'dark': {  # Цвета для темной темы (автоматически генерируем)
                    'bg_color': self._generate_dark_color(self.colors['bg_color']),
                    'card_color': self._generate_dark_color(self.colors['card_color']),
                    'text_primary': self._generate_dark_color(self.colors['text_primary'], invert=True),
                    'text_secondary': self._generate_dark_color(self.colors['text_secondary'], invert=True),
                    'primary_color': self.colors['primary_color'],  # Основной цвет оставляем таким же
                    'correct_color': self.colors['correct_color'],  # Цвета статусов оставляем
                    'error_color': self.colors['error_color']
                },
                'is_custom': True,
                'slot_index': self.slot_index
            }
            
            self.app.color_settings_screen.save_custom_presets()
            
            # НЕМЕДЛЕННО обновляем UI настроек цвета
            Clock.schedule_once(lambda dt: self.app.color_settings_screen.build_ui(), 0.1)
            
            self.app.screen_manager.current = 'color_settings'
            
        except Exception as e:
            print(f"Ошибка при сохранении пресета: {e}")
            self.app.show_quick_notification("Ошибка при сохранении пресета", 2)

    def _generate_dark_color(self, color, invert=False):
        """Генерация темного варианта цвета"""
        try:
            r, g, b, a = color
            
            if invert:
                # Для текста инвертируем яркость
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                if brightness > 0.5:
                    # Светлый текст -> темный текст
                    return [max(0, 1 - r * 0.7), max(0, 1 - g * 0.7), max(0, 1 - b * 0.7), a]
                else:
                    # Темный текст -> светлый текст
                    return [min(1, r + 0.6), min(1, g + 0.6), min(1, b + 0.6), a]
            else:
                # Для фонов уменьшаем яркость
                return [r * 0.3, g * 0.3, b * 0.3, a]
                
        except Exception as e:
            print(f"Ошибка генерации темного цвета: {e}")
            return color



    def copy_current_theme_colors(self):
        """Копирование цветов из текущей темы приложения"""
        return {
            'bg_color': self.app.bg_color[:],  # [:] создает копию списка
            'card_color': self.app.card_color[:],
            'text_primary': self.app.text_primary[:],
            'text_secondary': self.app.text_secondary[:],
            'primary_color': self.app.primary_color[:],
            'correct_color': self.app.correct_color[:],
            'error_color': self.app.error_color[:]
        }


    def create_preview_card(self):
        """Создание карточки предпросмотра"""
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(12)
        )
        
        with card_container.canvas.before:
            Color(rgba=self.colors['card_color'])
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(8)]
            )
        
        # Заголовок предпросмотра
        title_preview = AndroidLabel(
            text='Пример текста',
            font_size=self.app.get_font_size(16),
            color=self.colors['text_primary'],
            size_hint_y=0.4
        )
        card.add_widget(title_preview)
        
        # Кнопки предпросмотра
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.6, spacing=dp(8))
        
        primary_btn = AndroidButton(
            text='Основная',
            size_hint_x=0.5,
            background_color=self.colors['primary_color'],
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(12)
        )
        
        correct_btn = AndroidButton(
            text='Правильно',
            size_hint_x=0.25,
            background_color=self.colors['correct_color'],
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(10)
        )
        
        error_btn = AndroidButton(
            text='Ошибка',
            size_hint_x=0.25,
            background_color=self.colors['error_color'],
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(10)
        )
        
        btn_layout.add_widget(primary_btn)
        btn_layout.add_widget(correct_btn)
        btn_layout.add_widget(error_btn)
        card.add_widget(btn_layout)
        
        card_container.add_widget(card)
        card_container.bind(
            pos=self._update_preview_bg,
            size=self._update_preview_bg
        )
        
        return card_container

    def _update_preview_bg(self, instance, value):
        """Обновление фона предпросмотра"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.colors['card_color'])
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(8)]
                )

    def create_color_settings(self):
        """Создание настроек цветов"""
        color_settings = [
            ('Фон приложения', 'bg_color'),
            ('Фон карточек', 'card_color'),
            ('Основной текст', 'text_primary'),
            ('Вторичный текст', 'text_secondary'),
            ('Основной цвет', 'primary_color'),
            ('Цвет правильного ответа', 'correct_color'),
            ('Цвет ошибки', 'error_color')
        ]
        
        for label, color_key in color_settings:
            setting_layout = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(50),
                spacing=dp(10)
            )
            
            label_widget = AndroidLabel(
                text=label,
                color=self.colors['text_primary'],
                size_hint_x=0.6,
                halign='left'
            )
            
            color_btn = AndroidButton(
                text='Выбрать',
                size_hint_x=0.4,
                background_color=self.colors[color_key],
                color=(1, 1, 1, 1) if self._is_dark_color(self.colors[color_key]) else (0, 0, 0, 1)
            )
            color_btn.bind(on_press=lambda instance, key=color_key: self.open_color_picker(key))
            
            setting_layout.add_widget(label_widget)
            setting_layout.add_widget(color_btn)
            self.colors_layout.add_widget(setting_layout)

    def _is_dark_color(self, color):
        """Проверка, является ли цвет темным"""
        if len(color) < 3:
            return False
        r, g, b = color[0], color[1], color[2]
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 0.5

    def open_color_picker(self, color_key):
        """Открытие палитры цветов"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        color_picker = ColorPicker()
        color_picker.color = self.colors[color_key]
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Используем цвета из текущего пресета для кнопок
        cancel_btn = AndroidButton(
            text='Отмена',
            background_color=self.colors['card_color'],
            color=self.colors['text_primary'],
            font_size=self.app.get_font_size(14)
        )
        
        save_btn = AndroidButton(
            text='Применить',
            background_color=self.colors['primary_color'],
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        
        def save_color(instance):
            new_color = color_picker.color
            self.colors[color_key] = new_color
            # Просто перестраиваем весь интерфейс
            self.build_ui()
            popup.dismiss()
        
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        save_btn.bind(on_press=save_color)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        
        content.add_widget(color_picker)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title=f'Выбор цвета - {color_key}',
            content=content,
            size_hint=(0.9, 0.9),
            background_color=self.colors['bg_color']
        )
        popup.open()

    def cancel(self, instance):
        """Отмена создания пресета"""
        self.app.screen_manager.current = 'color_settings'


class ColorSettingsScreen(Screen):

    def on_enter(self):
        """Вызывается при переходе на экран - обновляем UI для отображения смайликов"""
        # Принудительно проверяем и обновляем состояние активного пресета
        if hasattr(self.app, 'active_preset') and self.app.active_preset:
            # Перезагружаем кастомные пресеты
            self.custom_presets = self.load_custom_presets()
            
            # Проверяем, является ли активный пресет кастомным
            if self.app.active_preset in self.custom_presets:
                self.app.colors_modified = True
            else:
                self.app.colors_modified = False
        
        # Принудительно обновляем UI с небольшой задержкой
        Clock.schedule_once(lambda dt: self.build_ui(), 0.2)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.custom_presets = self.load_custom_presets()
        self.build_ui()

    def load_custom_presets(self):
        """Загрузка кастомных пресетов из хранилища"""
        if 'custom_presets' in self.app.settings_store:
            return self.app.settings_store.get('custom_presets')
        return {}

    def save_custom_presets(self):
        """Сохранение кастомных пресетов"""
        self.app.settings_store.put('custom_presets', **self.custom_presets)

    def update_color_settings(self):
        """Обновление настроек цветов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        self.content_layout.clear_widgets()
        presets_card = self.create_presets_panel()
        self.content_layout.add_widget(presets_card)
        
        # Добавляем карточку кастомных пресетов
        custom_presets_card = self.create_custom_presets_panel()
        self.content_layout.add_widget(custom_presets_card)

    def _update_custom_presets_bg(self, instance, value):
        """Обновление фона панели кастомных пресетов"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(8)]
                )

    def _is_dark_color(self, color):
        """Проверка, является ли цвет темным"""
        if len(color) < 3:
            return False
        r, g, b = color[0], color[1], color[2]
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 0.5
    
    def create_custom_presets_panel(self):
        """Создание панели кастомных пресетов"""
        base_height = dp(180)
        if len(self.custom_presets) > 4:
            base_height = dp(220)
        
        presets_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=base_height,
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        presets_card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(10),
            spacing=dp(5)
        )
        
        with presets_container.canvas.before:
            Color(rgba=self.app.card_color)
            presets_container.bg_rect = RoundedRectangle(
                pos=presets_container.pos,
                size=presets_container.size,
                radius=[dp(8)]
            )
            
        # Заголовок
        header_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        presets_label = AndroidLabel(
            text='[b]Мои пресеты[/b]',
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint_x=1,
            halign='left'
        )
        header_layout.add_widget(presets_label)
        presets_card.add_widget(header_layout)
        
        # Сетка кастомных пресетов
        cols = 4
        rows = 2
        presets_grid = GridLayout(
            cols=cols, 
            rows=rows,
            size_hint_y=0.75,
            spacing=dp(4),
            padding=dp(2)
        )
        
        # Создаем массив для всех 8 ячеек
        slot_presets = [None] * 8  # 8 ячеек, изначально все пустые
        
        # Заполняем массив пресетами по их slot_index
        for preset_name, preset_data in self.custom_presets.items():
            slot_index = preset_data.get('slot_index', 0)
            if 0 <= slot_index < 8:  # Проверяем валидность индекса
                slot_presets[slot_index] = (preset_name, preset_data)
        
        # Создаем кнопки для всех 8 ячеек
        for slot_index in range(8):
            if slot_presets[slot_index] is not None:
                # Ячейка занята пресетом
                preset_name, preset_data = slot_presets[slot_index]
                
                # ИСПРАВЛЕНИЕ: получаем primary_color из текущей темы
                theme = 'dark' if self.app.is_dark_theme else 'light'
                theme_colors = preset_data.get(theme, preset_data.get('light', {}))
                preset_color = theme_colors.get('primary_color', [0.5, 0.5, 0.5, 1])
                
                # ИСПРАВЛЕННАЯ ПРОВЕРКА АКТИВНОСТИ
                is_active = (self.app.active_preset == preset_name and 
                            self.app.colors_modified)
                
                # Текст кнопки: смайлик если активен, пусто если нет
                button_text = ';-)' if is_active else ''
                
                preset_btn = AndroidButton(
                    text=button_text,
                    size_hint=(1, 1),
                    background_color=preset_color,
                    color=(1, 1, 1, 1) if self._is_dark_color(preset_color) else (0, 0, 0, 1),
                    font_size=self.app.get_font_size(14)
                )
                
                # Создаем обработчик для долгого нажатия
                def create_preset_handlers(pid, btn_instance):
                    touch_start_time = 0
                    long_press_triggered = False
                    long_press_event = None
                    
                    def on_touch_down(instance, touch):
                        nonlocal touch_start_time, long_press_triggered, long_press_event
                        if btn_instance.collide_point(*touch.pos):
                            touch_start_time = touch.time_start
                            long_press_triggered = False
                            # Запускаем таймер для долгого нажатия
                            long_press_event = Clock.schedule_once(lambda dt: check_long_press(), 1.0)
                        return False
                    
                    def check_long_press():
                        nonlocal long_press_triggered
                        long_press_triggered = True
                        self.show_delete_confirmation(pid)
                    
                    def on_touch_up(instance, touch):
                        nonlocal long_press_triggered, long_press_event
                        if long_press_event:
                            Clock.unschedule(long_press_event)
                            long_press_event = None
                        
                        if btn_instance.collide_point(*touch.pos) and not long_press_triggered:
                            # Если не было долгого нажатия, применяем пресет
                            self.apply_custom_preset(pid)
                        long_press_triggered = False
                        return False
                    
                    return on_touch_down, on_touch_up
                
                # Создаем обработчики для этой кнопки
                touch_down_handler, touch_up_handler = create_preset_handlers(preset_name, preset_btn)
                preset_btn.bind(on_touch_down=touch_down_handler)
                preset_btn.bind(on_touch_up=touch_up_handler)
                
            else:
                # Пустая ячейка
                preset_btn = AndroidButton(
                    text='+',
                    size_hint=(1, 1),
                    background_color=[0.9, 0.9, 0.9, 0.3],
                    color=self.app.text_secondary,
                    font_size=self.app.get_font_size(16)
                )
                
                # Обработчик для создания пресета в этой ячейке
                def create_empty_handler(slot_idx, instance):
                    self.create_preset_in_slot(slot_idx)
                
                preset_btn.bind(on_press=lambda instance, slot_idx=slot_index: 
                            create_empty_handler(slot_idx, instance))
            
            presets_grid.add_widget(preset_btn)
        
        presets_card.add_widget(presets_grid)
        presets_container.add_widget(presets_card)
        presets_container.bind(
            pos=self._update_presets_bg,
            size=self._update_presets_bg
        )
        
        return presets_container

    def show_delete_confirmation(self, preset_name):
        """Показ подтверждения удаления пресета"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        message = AndroidLabel(
            text=f'Удалить пресет "{preset_name}"?',
            color=(1, 1, 1, 1),
            halign='center',
            font_size=self.app.get_font_size(16)
        )
        content.add_widget(message)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=dp(10))
        cancel_btn = AndroidButton(
            text='Отмена',
            background_color=self.app.card_color,
            color=self.app.text_primary,
            font_size=self.app.get_font_size(14)
        )
        delete_btn = AndroidButton(
            text='Удалить',
            background_color=self.app.error_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        
        def confirm_delete(instance):
            if preset_name in self.custom_presets:
                del self.custom_presets[preset_name]
                self.save_custom_presets()
                self.build_ui()  # Обновляем интерфейс
                popup.dismiss()
        
        def cancel_delete(instance):
            popup.dismiss()
        
        cancel_btn.bind(on_press=cancel_delete)
        delete_btn.bind(on_press=confirm_delete)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(delete_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Подтверждение удаления',
            content=content,
            size_hint=(0.7, 0.3),
            background_color=self.app.bg_color
        )
        popup.open()

    def create_preset_in_slot(self, slot_index):
        """Создание пресета в указанной ячейке"""
        if not hasattr(self.app, 'custom_preset_creator_screen'):
            self.app.custom_preset_creator_screen = CustomPresetCreatorScreen(name='custom_preset_creator')
            self.app.screen_manager.add_widget(self.app.custom_preset_creator_screen)
        
        # Передаем информацию о слоте в экран создания
        self.app.custom_preset_creator_screen.slot_index = slot_index
        
        # ОБНОВЛЯЕМ цвета на основе текущей темы
        self.app.custom_preset_creator_screen.colors = self.app.custom_preset_creator_screen.copy_current_theme_colors()
        
        self.app.custom_preset_creator_screen.build_ui()  # Обновляем UI
        self.app.screen_manager.current = 'custom_preset_creator'


    def show_add_preset_dialog(self, instance):
        """Переход на экран создания пресета"""
        if not hasattr(self.app, 'custom_preset_creator_screen'):
            self.app.custom_preset_creator_screen = CustomPresetCreatorScreen(name='custom_preset_creator')
            self.app.screen_manager.add_widget(self.app.custom_preset_creator_screen)
        
        self.app.screen_manager.current = 'custom_preset_creator'



    def apply_custom_preset(self, preset_name):
        """Применение кастомного пресета"""
        if preset_name in self.custom_presets:
            preset_data = self.custom_presets[preset_name]
            
            # Определяем текущую тему
            theme = 'dark' if self.app.is_dark_theme else 'light'
            
            # Применяем цвета из пресета для текущей темы
            theme_colors = preset_data.get(theme, preset_data.get('light', {}))
            
            for color_property, color_value in theme_colors.items():
                if (color_property != 'is_custom' and 
                    color_property != 'slot_index' and 
                    hasattr(self.app, color_property)):
                    setattr(self.app, color_property, color_value)
                    self.app.custom_colors[color_property] = color_value
            
            # Устанавливаем флаги для отображения смайлика
            self.app.colors_modified = True
            self.app.active_preset = preset_name
            
            self.app.save_custom_colors()
            self.app.save_active_preset()
            self.app.build_main_screen()
            
            if hasattr(self.app, 'optimized_test_screen'):
                self.app.optimized_test_screen.update_content()
            
            # Обновляем UI настроек цвета, чтобы показать смайлик
            self.build_ui()


    def delete_custom_preset(self, preset_name):
        """Удаление кастомного пресета с подтверждением"""
        if preset_name in self.custom_presets:
            content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
            
            message = AndroidLabel(
                text=f'Удалить пресет "{preset_name}"?',
                color=self.app.text_primary,
                halign='center'
            )
            content.add_widget(message)
            
            btn_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=dp(10))
            cancel_btn = AndroidButton(
                text='Отмена',
                background_color=self.app.card_color,
                color=self.app.text_primary
            )
            delete_btn = AndroidButton(
                text='Удалить',
                background_color=self.app.error_color,
                color=(1, 1, 1, 1)
            )
            
            def confirm_delete(instance):
                del self.custom_presets[preset_name]
                self.save_custom_presets()
                self.build_ui()  # Обновляем интерфейс
                popup.dismiss()
            
            def cancel_delete(instance):
                popup.dismiss()
            
            cancel_btn.bind(on_press=cancel_delete)
            delete_btn.bind(on_press=confirm_delete)
            
            btn_layout.add_widget(cancel_btn)
            btn_layout.add_widget(delete_btn)
            content.add_widget(btn_layout)
            
            popup = Popup(
                title='Подтверждение удаления',
                content=content,
                size_hint=(0.7, 0.3),
                background_color=self.app.bg_color
            )
            popup.open()

    def create_donate_card(self):
        """Создание АДАПТИВНОЙ карточки для доната"""
        card = AdaptiveCard(background_color=self.app.card_color)
        title_label = AndroidLabel(
            text='[b]Поддержать разработчика[/b]',
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title_label)
        donate_label = AndroidLabel(
            text='+79294000474',
            font_size=self.app.get_font_size(14),
            color=self.app.primary_color,
            size_hint_y=None,
            height=dp(25),
            halign='center'
        )
        card.add_widget(donate_label)
        copy_btn = AndroidButton(
            text='Скопировать номер карты',
            size_hint_y=None,
            height=dp(40),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        copy_btn.bind(on_press=self.copy_donate_info)
        card.add_widget(copy_btn)
        
        return card



    def _update_donate_card_bg(self, instance, value):
        """Обновление фона карточки доната"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.app.card_color)
            instance.bg_rect = RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(12)]
            )

    def copy_donate_info(self, instance):
        """Копирование номера карты в буфер обмена"""
        from kivy.core.clipboard import Clipboard
        Clipboard.copy('2202 2050 3871 3111')
        self.app.show_quick_notification("Номер карты скопирован в буфер обмена", 2)


    def build_ui(self):
        """Построение UI - ИСПРАВЛЕННАЯ ВЕРСИЯ с фиксированной кнопкой"""
        self.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        title = AndroidLabel(
            text='[b]Настройки цвета[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.1),
            color=self.app.text_primary
        )
        main_layout.add_widget(title)
        scroll = ScrollView(size_hint=(1, 0.8))
        self.content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))

        self.update_color_settings()

        scroll.add_widget(self.content_layout)
        main_layout.add_widget(scroll)
        back_btn = AndroidButton(
            text='Назад в меню',
            size_hint_y=None,
            height=dp(60),
            font_size=self.app.get_font_size(14),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)

        self.add_widget(main_layout)


    def create_font_setting_card(self):
        """Создание карточки настройки размера шрифтов"""
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(16),
            spacing=dp(8)
        )
        with card_container.canvas.before:
            Color(rgba=self.app.card_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(12)]
            )
        title_label = AndroidLabel(
            text='[b]Размер шрифтов[/b]',
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint_y=0.3
        )
        card.add_widget(title_label)
        slider_layout = BoxLayout(orientation='horizontal', size_hint_y=0.4, spacing=dp(10))
        small_label = AndroidLabel(
            text='[b]а[/b]',
            font_size=self.app.get_font_size(12),
            color=self.app.text_secondary,
            size_hint_x=0.2
        )
        self.font_slider = Slider(
            min=0.8,
            max=1.1,
            value=self.app.font_scale,
            step=0.01,
            size_hint_x=0.6
        )
        self.font_slider.bind(value=self.on_font_scale_change)
        large_label = AndroidLabel(
            text='[b]А[/b]',
            font_size=self.app.get_font_size(12),
            color=self.app.text_secondary,
            size_hint_x=0.2
        )
        
        slider_layout.add_widget(small_label)
        slider_layout.add_widget(self.font_slider)
        slider_layout.add_widget(large_label)
        card.add_widget(slider_layout)
        value_layout = BoxLayout(orientation='horizontal', size_hint_y=0.3)
        self.value_label = AndroidLabel(
            text=f'Текущий размер: {int(self.app.font_scale * 100)}%',
            font_size=self.app.get_font_size(14),
            color=self.app.text_primary,
            halign='center'
        )
        value_layout.add_widget(self.value_label)
        card.add_widget(value_layout)
        
        card_container.add_widget(card)
        card_container.bind(
            pos=self._update_font_card_bg,
            size=self._update_font_card_bg
        )
        
        return card_container

    def _update_font_card_bg(self, instance, value):
        """Обновление фона карточки шрифтов"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.app.card_color)
            instance.bg_rect = RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(12)]
            )

    def on_font_scale_change(self, instance, value):
        """Обработчик изменения размера шрифтов"""
        try:
            self.app.font_scale = value
            self.app.save_font_settings()
            if hasattr(self, 'value_label'):
                self.value_label.text = f'Текущий размер: {int(value * 100)}%'
            
            # НЕМЕДЛЕННОЕ обновление шрифтов на всех экранах
            Clock.schedule_once(lambda dt: self.app.update_all_screens_fonts(), 0.05)
            
        except Exception as e:
            print(f"Ошибка при изменении размера шрифтов: {e}")


    def update_color_settings(self):
        """Обновление настроек цветов - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        self.content_layout.clear_widgets()
        
        # 1. Стандартные пресеты
        presets_card = self.create_presets_panel()
        self.content_layout.add_widget(presets_card)
        
        # 2. Кастомные пресеты (НОВАЯ КАРТОЧКА)
        custom_presets_card = self.create_custom_presets_panel()
        self.content_layout.add_widget(custom_presets_card)
        
        # 3. Настройки шрифтов
        font_card = self.create_font_setting_card()
        self.content_layout.add_widget(font_card)
        
        # 4. Донат
        donate_card = self.create_donate_card()
        self.content_layout.add_widget(donate_card)
            
    

    def create_presets_panel(self):
        """Создание панели цветовых пресетов с 24 пресетами"""
        presets_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(220),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        presets_card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(10)
        )
        with presets_container.canvas.before:
            Color(rgba=self.app.card_color)
            presets_container.bg_rect = RoundedRectangle(
                pos=presets_container.pos,
                size=presets_container.size,
                radius=[dp(8)]
            )
        presets_label = AndroidLabel(
            text='[b]Цветовые пресеты[/b]',
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint_y=0.15
        )
        presets_card.add_widget(presets_label)
        presets_grid = GridLayout(
            cols=6, 
            rows=4,
            size_hint_y=0.85,
            spacing=dp(4),
            padding=dp(2)
        )
        presets = [
            ('green_soft', '', [0.4, 0.7, 0.4, 1]),
            ('red_soft', '', [0.8, 0.4, 0.4, 1]),
            ('orange_soft', '', [0.9, 0.7, 0.4, 1]),
            ('blue_soft', '', [0.4, 0.6, 0.8, 1]),
            ('pink_soft', '', [0.9, 0.6, 0.7, 1]),
            ('purple_soft', '', [0.7, 0.6, 0.9, 1]),
            ('green_medium', '', [0.25, 0.65, 0.25, 1]),
            ('red_medium', '', [0.7, 0.25, 0.25, 1]),
            ('orange_medium', '', [0.85, 0.6, 0.25, 1]),
            ('blue_medium', '', [0.25, 0.5, 0.7, 1]),
            ('pink_medium', '', [0.85, 0.4, 0.6, 1]),
            ('purple_medium', '', [0.65, 0.4, 0.85, 1]),
            ('green_bold', '', [0.1, 0.6, 0.1, 1]),
            ('red_bold', '', [0.8, 0.1, 0.1, 1]),
            ('orange_bold', '', [0.9, 0.5, 0.1, 1]),
            ('blue_bold', '', [0.1, 0.4, 0.8, 1]),
            ('pink_bold', '', [0.9, 0.2, 0.5, 1]),
            ('purple_bold', '', [0.6, 0.2, 0.9, 1]),
            ('green_vivid', '', [0.05, 0.7, 0.05, 1]),
            ('red_vivid', '', [0.9, 0.05, 0.05, 1]),
            ('orange_vivid', '', [0.95, 0.55, 0.05, 1]),
            ('blue_vivid', '', [0.05, 0.3, 0.9, 1]),
            ('pink_vivid', '', [0.95, 0.1, 0.6, 1]),
            ('purple_vivid', '', [0.7, 0.1, 0.95, 1])
        ]
        
        for preset_id, preset_icon, preset_color in presets:
            preset_btn = AndroidButton(
                text=preset_icon,
                size_hint=(1, 1),
                background_color=preset_color,
                color=(1, 1, 1, 1),
                font_size=self.app.get_font_size(12),
                height=dp(30),
                padding=[dp(1), dp(1)]
            )
            is_active = (hasattr(self.app, 'active_preset') and 
                        self.app.active_preset == preset_id and 
                        not self.app.colors_modified)
            
            if is_active:
                preset_btn.text = preset_icon + ";-)"
            
            preset_btn.bind(on_press=lambda instance, pid=preset_id: self.apply_preset(pid))
            presets_grid.add_widget(preset_btn)
        
        presets_card.add_widget(presets_grid)
        presets_container.add_widget(presets_card)
        presets_container.bind(
            pos=self._update_presets_bg,
            size=self._update_presets_bg
        )
        
        return presets_container


    def _update_presets_bg(self, instance, value):
        """Обновление фона панели пресетов"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(8)]
                )
    
    def create_color_setting(self, label, color_property, current_color):
        """Создание настройки цвета"""
        layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(38))
        
        label_widget = AndroidLabel(
            text=label,
            color=self.app.text_primary,
            size_hint_x=0.6
        )
        
        color_btn = AndroidButton(
            text='Изменить',
            size_hint_x=0.4,
            background_color=current_color,
            color=(1, 1, 1, 1) if current_color != self.app.card_color else self.app.text_primary
        )
        
        color_btn.bind(on_press=lambda x: self.open_color_picker(color_property, color_btn))
        
        layout.add_widget(label_widget)
        layout.add_widget(color_btn)
        
        return layout
    
    def open_color_picker(self, color_property, color_btn):
        """Открытие палитры цветов"""
        content = BoxLayout(orientation='vertical')
        
        color_picker = ColorPicker()
        color_picker.color = getattr(self.app, color_property)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50))
        cancel_btn = AndroidButton(text='Отмена')
        save_btn = AndroidButton(text='Применить')
        
        def save_color(instance):
            new_color = color_picker.color
            setattr(self.app, color_property, new_color)
            self.app.custom_colors[color_property] = new_color
            self.app.colors_modified = True
            self.app.active_preset = ''
            
            self.app.save_custom_colors()
            self.app.save_active_preset()
            color_btn.background_color = new_color
            color_btn.color = (1, 1, 1, 1) if new_color != self.app.card_color else self.app.text_primary
            self.app.build_main_screen()
            if hasattr(self.app, 'optimized_test_screen'):
                self.app.optimized_test_screen.update_content()
            
            popup.dismiss()
        
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        save_btn.bind(on_press=save_color)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(save_btn)
        
        content.add_widget(color_picker)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title=f'Выбор цвета - {color_property}',
            content=content,
            size_hint=(0.9, 0.9),
            background_color=self.app.bg_color
        )
        popup.open()
    
    def apply_preset(self, preset_name):
        """Применение цветового пресета"""
        self.app.apply_color_preset(preset_name)
        # Обновляем UI, чтобы убрать смайлик с кастомных пресетов
        self.build_ui()
    
    def reset_colors(self, instance):
        """Сброс цветов к текущему пресету (зеленому)"""
        self.app.custom_colors = {}
        self.app.colors_modified = False
        self.app.active_preset = 'green_soft'
        
        self.app.settings_store.put('custom_colors', **{})
        self.app.save_active_preset()
        self.app.apply_color_preset('green_soft')
        self.build_ui()
    
    def go_back(self, instance):
        self.app.screen_manager.current = 'main'

class OptimizedTestScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.answer_buttons = []
        self.nav_buttons = []
        self.nav_panel = None
        self._first_update = True
        
        # ДОБАВЛЯЕМ СОСТОЯНИЯ ДЛЯ КЛАВИАТУРНОЙ НАВИГАЦИИ
        self.keyboard_mode = False  # Режим клавиатуры активен
        self.active_answer_index = -1  # Активный вариант ответа (-1 - нет активного)
        self.keyboard_bind_added = False  # Флаг привязки клавиатуры
        
        self.build_static_layout()
        Window.bind(on_resize=self._on_window_resize)
        if hasattr(self, 'nav_scroll'):
            self.nav_scroll.bind(on_scroll_start=self._enable_mouse_scroll)
            self.nav_scroll.bind(on_scroll_stop=self._disable_mouse_scroll)

    def reset_scroll_positions(self):
        """Сброс позиций прокрутки к началу"""
        # Сбрасываем прокрутку ответов в начало
        if hasattr(self, 'answers_scroll'):
            self.answers_scroll.scroll_y = 1.0  # Верхняя позиция в Kivy
        
        # Сбрасываем прокрутку вопроса в начало (если есть)
        if hasattr(self, 'question_scroll'):
            self.question_scroll.scroll_y = 1.0




    def update_question_area_instant(self, current_question):
        """Мгновенное обновление области вопроса - БЕЗ ЗАДЕРЖЕК"""
        self.question_label.text = current_question.text
        self.question_label.color = self.app.text_primary  # ОБНОВЛЯЕМ ЦВЕТ ТЕКСТА
        
        # ФИКСИРОВАННАЯ ширина - не меняется при обновлениях
        fixed_width = Window.width - dp(80)
        self.question_label.text_size = (fixed_width, None)
        self.question_label.width = fixed_width
        self.question_label.texture_update()  # МГНОВЕННОЕ ОБНОВЛЕНИЕ
        
        if self.question_label.texture_size:
            text_height = self.question_label.texture_size[1]
            question_height = text_height + dp(24)
            min_height = dp(80)
            max_height = dp(280)
            final_height = max(min_height, min(question_height, max_height))
            
            self.question_label.height = final_height - dp(24)


    def _enable_mouse_scroll(self, instance, touch):
        """Включаем обработку колесика мыши при начале прокрутки"""
        Window.bind(on_mousewheel=self._on_mousewheel)

    def _disable_mouse_scroll(self, instance, touch):
        """Отключаем обработку колесика мыши при окончании прокрутки"""
        Window.unbind(on_mousewheel=self._on_mousewheel)

    def _on_mousewheel(self, window, x, y, button, modifiers):
        """Обработчик колесика мыши для горизонтальной прокрутки навигационной панели"""
        if hasattr(self, 'nav_scroll') and self.nav_scroll and self.nav_scroll.collide_point(*Window.mouse_pos):
            scroll_speed = 0.2
            if button == 'scrolldown':
                self.nav_scroll.scroll_x = min(1.0, self.nav_scroll.scroll_x + scroll_speed)
            elif button == 'scrollup':
                self.nav_scroll.scroll_x = max(0.0, self.nav_scroll.scroll_x - scroll_speed)
            return True
        
        return False


    def update_button_font_sizes(self):
        """Обновление размера шрифтов для кнопок в тесте"""
        app = self.app
        if hasattr(self, 'nav_buttons'):
            for btn in self.nav_buttons:
                btn.font_size = app.get_font_size(14)
        if hasattr(self, 'answer_buttons'):
            for btn in self.answer_buttons:
                btn.font_size = app.get_font_size(14)
        if hasattr(self, 'back_btn'):
            self.back_btn.font_size = app.get_font_size(14)
        if hasattr(self, 'exit_btn'):
            self.exit_btn.font_size = app.get_font_size(14)
        if hasattr(self, 'action_btn'):
            self.action_btn.font_size = app.get_font_size(14)
        if hasattr(self, 'neuro_btn'):
            self.neuro_btn.font_size = app.get_font_size(14)
        if hasattr(self, 'copy_question_btn'):
            self.copy_question_btn.font_size = app.get_font_size(16)


    def _recalculate_heights(self):
        """Пересчет высот кнопок ответов при изменении размера окна"""
        if not hasattr(self, 'answer_buttons') or not self.answer_buttons:
            return
        
        available_width = self.answers_scroll.width - dp(30)
        
        for btn in self.answer_buttons:
            btn.text_size = (available_width, None)
            btn.texture_update()
            text_height = btn.texture_size[1] if hasattr(btn, 'texture_size') and btn.texture_size else dp(50)
            padding_vertical = dp(16)
            min_height = dp(50)
            calculated_height = text_height + padding_vertical
            
            button_height = max(calculated_height, min_height)
            button_height = min(button_height, dp(300))
            
            btn.height = button_height
        self._update_total_height()
    

    def build_header(self):
        """Строим верхнюю панель с красивой сеточной разметкой"""
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.25), spacing=dp(10))
        top_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=dp(10))
        
        self.test_name_label = AndroidLabel(
            text='', 
            font_size=self.app.get_font_size(18),
            color=self.app.text_primary,
            halign='left',
            size_hint_x=1.0
        )
        top_row.add_widget(self.test_name_label)
        header.add_widget(top_row)
        second_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.25), spacing=dp(10))
        self.progress_label = AndroidLabel(
            text='', 
            font_size=self.app.get_font_size(14), 
            color=self.app.text_primary,
            size_hint_x=0.6,
            halign='left'
        )
        self.copy_question_btn = AndroidButton(
            text='[b]Копировать[/b]',
            size_hint_x=0.4,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.copy_question_btn.bind(on_press=self.copy_current_question)
        
        second_row.add_widget(self.progress_label)
        second_row.add_widget(self.copy_question_btn)
        header.add_widget(second_row)
        third_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.2), spacing=dp(10))
        
        self.stats_label = AndroidLabel(
            text='', 
            font_size=self.app.get_font_size(14), 
            color=self.app.text_primary,
            size_hint_x=1.0,
            halign='left'
        )
        third_row.add_widget(self.stats_label)
        header.add_widget(third_row)
        nav_row = BoxLayout(orientation='horizontal', size_hint=(1, 0.25), spacing=dp(10))
        
        self.nav_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True, 
            do_scroll_y=False,
            scroll_type=['bars', 'content'],
            bar_width=dp(8),
            effect_cls='ScrollEffect'
        )
        
        self.nav_panel = OptimizedNavPanel(self.app, size_hint_x=None)
        self.nav_scroll.add_widget(self.nav_panel)
        
        nav_row.add_widget(self.nav_scroll)
        header.add_widget(nav_row)
        
        return header

    def copy_current_question(self, instance):
        """Копирование текущего вопроса в формате ассистента"""
        if not self.app.current_questions:
            return
            
        current_question = self.app.current_questions[self.app.current_question_index]
        lines = [f"?{current_question.text}"]
        for i, answer in enumerate(current_question.answers):
            if i in current_question.correct_indices:
                lines.append(f"+{answer}")
            else:
                lines.append(f"-{answer}")
        
        text_to_copy = "\n".join(lines)
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(text_to_copy)
        self.app.show_quick_notification("Вопрос скопирован в буфер обмена", 2)


    def update_nav_panel_width(self):
        """Обновляет ширину навигационной панели при изменении количества вопросов"""
        if hasattr(self, 'nav_panel') and self.nav_panel.buttons:
            questions_count = len(self.app.current_questions)
            required_width = questions_count * (dp(45) + dp(5))
            self.nav_panel.width = required_width
            self.nav_panel.minimum_width = required_width
            
            # Обновляем минимальную ширину для ScrollView
            if hasattr(self, 'nav_scroll'):
                self.nav_scroll.minimum_width = min(required_width, Window.width)

    def _update_exit_border(self, instance, value):
        """Обновление обводки кнопки выхода"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=[0.7, 0.1, 0.1, 1])
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(8)]
            )

    def scroll_nav_to_current_question(self):
        """Улучшенная прокрутка навигационной панели к текущему вопросу"""
        if not hasattr(self, 'nav_panel') or not self.nav_panel.buttons:
            return
        
        current_index = self.app.current_question_index
        buttons_count = len(self.nav_panel.buttons)
        
        if current_index >= buttons_count:
            return
        
        button_width = dp(45) + dp(5)
        nav_panel_width = self.nav_panel.width
        scroll_view_width = self.nav_scroll.width
        
        # Если панель уже помещается целиком, не прокручиваем
        if nav_panel_width <= scroll_view_width:
            return
        
        # Вычисляем позицию кнопки относительно всей панели
        button_center = (current_index * button_width) + (button_width / 2)
        
        # Вычисляем видимую область
        visible_start = self.nav_scroll.scroll_x * (nav_panel_width - scroll_view_width)
        visible_end = visible_start + scroll_view_width
        
        # Если кнопка не видна или находится близко к краям, прокручиваем
        button_start = current_index * button_width
        button_end = button_start + button_width
        
        margin = scroll_view_width * 0.2  # 20% отступ от краев
        
        if (button_start < visible_start + margin or 
            button_end > visible_end - margin or
            button_start >= visible_end or 
            button_end <= visible_start):
            
            # Вычисляем новую позицию прокрутки
            target_scroll = max(0, min(1, (button_center - scroll_view_width / 2) / (nav_panel_width - scroll_view_width)))
            
            # Плавная анимация прокрутки
            anim = Animation(scroll_x=target_scroll, duration=0.3)
            anim.start(self.nav_scroll)


    def build_question_area(self):
        """Строим область вопроса с ФИКСИРОВАННОЙ шириной"""
        question_area = BoxLayout(orientation='vertical', size_hint=(1, 0.75), spacing=dp(10))
        
        self.question_card_container = BoxLayout(  # СОХРАНЯЕМ ССЫЛКУ
            orientation='vertical',
            size_hint=(1, None),
            padding=[dp(6), dp(6), dp(6), dp(6)]
        )
        
        question_card = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            padding=dp(12)
        )
        
        with self.question_card_container.canvas.before:
            Color(rgba=self.app.card_color)
            self.question_card_container.bg_rect = RoundedRectangle(
                pos=self.question_card_container.pos,
                size=self.question_card_container.size,
                radius=[dp(12)]
            )
        
        # ФИКСИРУЕМ ширину текста вопроса - используем фиксированную ширину
        fixed_width = Window.width - dp(80)  # Отступы по 40px с каждой стороны
        
        self.question_label = AndroidLabel(
            text='',
            font_size=self.app.get_font_size(15),
            text_size=(fixed_width, None),  # ФИКСИРОВАННАЯ ширина
            size=(fixed_width, 0),  # ФИКСИРОВАННАЯ ширина
            color=self.app.text_primary,
            size_hint_y=None,
            size_hint_x=None,  # Отключаем size_hint_x для фиксированной ширины
            halign='left',
            valign='top'
        )
        
        def update_question_card_height(*args):
            if hasattr(self, 'question_label') and self.question_label.texture_size:
                text_height = self.question_label.texture_size[1]
                question_height = text_height + dp(24)
                min_height = dp(80)
                max_height = dp(280)
                final_height = max(min_height, min(question_height, max_height))
                
                self.question_label.height = final_height - dp(24)
                question_card.height = final_height
                self.question_card_container.height = final_height + dp(12)
        
        self.question_label.bind(texture_size=update_question_card_height)
        
        question_card.add_widget(self.question_label)
        self.question_card_container.add_widget(question_card)  # ИСПРАВЛЕНО: self.question_card_container
        self.question_card_container.bind(
            pos=self._update_question_card_rect,
            size=self._update_question_card_rect
        )
        
        question_area.add_widget(self.question_card_container)
        
        self.answers_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )
        
        self.answers_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(8))
        self.answers_layout.bind(minimum_height=self.answers_layout.setter('height'))
        
        self.answers_scroll.add_widget(self.answers_layout)
        question_area.add_widget(self.answers_scroll)
        
        return question_area
            
    
    def _update_question_card_rect(self, instance, value):
        """Обновление фона карточки вопроса при изменении размера"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)  # ИСПОЛЬЗУЕМ АКТУАЛЬНЫЙ ЦВЕТ
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(12)]
                )

    def build_bottom_panel(self):
        """Строим нижнюю панель с подсказкой по клавиатуре"""
        bottom_main = BoxLayout(orientation='vertical', size_hint=(1, None), spacing=dp(5))
        
        if self.app.gigachat_enabled:
            neuro_row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(40), spacing=dp(12))
            self.neuro_btn = AndroidButton(
                text='Спросить у GigaChat',
                size_hint_x=1,
                height=dp(40),
                background_color=[0.1, 0.5, 0.3, 1],
                color=(1, 1, 1, 1),
                font_size=self.app.get_font_size(14)
            )
            self.neuro_btn.bind(on_press=self.app.ask_neuro_network)
            
            neuro_row.add_widget(self.neuro_btn)
            bottom_main.add_widget(neuro_row)
        bottom = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), spacing=dp(12))
        self.back_btn = AndroidButton(
            text='Назад',
            size_hint_x=0.3,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            disabled=False,
            font_size=self.app.get_font_size(14)
        )
        self.back_btn.bind(on_press=lambda x: self.app.previous_question())
        self.exit_btn = AndroidButton(
            text='Выход в меню',
            size_hint_x=0.4,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.exit_btn.bind(on_press=self.app.return_to_menu)
        self.action_btn = AndroidButton(
            text='',
            size_hint_x=0.3,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.action_btn.bind(on_press=self.app.action_button_click)
        
        bottom.add_widget(self.back_btn)
        bottom.add_widget(self.exit_btn)
        bottom.add_widget(self.action_btn)
        
        bottom_main.add_widget(bottom)
        if self.app.gigachat_enabled:
            bottom_main.height = dp(95)
        else:
            bottom_main.height = dp(50)
        
        return bottom_main


    def update_content_for_new_question(self):
        """Обновление контента при переходе на новый вопрос (сбрасывает прокрутку)"""
        # Сбрасываем клавиатурное состояние при смене вопроса
        self._reset_keyboard_state()
        
        app = self.app
        
        if not app.current_questions:
            return
        
        current_index = app.current_question_index
        current_q = app.current_questions[current_index]
        test_name = app.current_test
        if len(test_name) > 40:
            display_name = test_name[:37] + "..."
        else:
            display_name = test_name
        
        self.test_name_label.text = f'[b]{display_name}[/b]'
        self.progress_label.text = f'Вопрос {current_index + 1} из {len(app.current_questions)}'
        self.stats_label.text = f'Правильно: {app.correct_answers}   Неправильно: {app.incorrect_answers}'
        self.update_nav_panel()
        
        # СБРАСЫВАЕМ ПОЗИЦИИ ПРОКРУТКИ К НАЧАЛУ (только для новых вопросов)
        self.reset_scroll_positions()
        
        self.update_question_area_instant(current_q)
        self.update_answer_buttons(current_q)
        self.update_action_buttons()
        app.update_check_button_state()
        
        self.do_layout()
        
        # ДОБАВЛЯЕМ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ ТЕКСТУР ДЛЯ ПЕРВОГО ВОПРОСА
        Clock.schedule_once(self._force_question_textures, 0.05)

    def _force_question_textures(self, dt):
        """Принудительное обновление текстур для текущего вопроса"""
        # Обновляем текстуру вопроса
        if hasattr(self, 'question_label'):
            self.question_label.texture_update()
            
            # Принудительно обновляем высоту вопроса после обновления текстуры
            if self.question_label.texture_size:
                text_height = self.question_label.texture_size[1]
                question_height = text_height + dp(24)
                min_height = dp(80)
                max_height = dp(280)
                final_height = max(min_height, min(question_height, max_height))
                
                self.question_label.height = final_height - dp(24)
        
        # Обновляем текстуры кнопок ответов
        if hasattr(self, 'answer_buttons'):
            for btn in self.answer_buttons:
                btn.texture_update()
                
                # Принудительно обновляем высоту кнопок после обновления текстуры
                if btn.texture_size:
                    text_height = btn.texture_size[1]
                    padding_vertical = dp(16)
                    min_height = dp(50)
                    calculated_height = text_height + padding_vertical
                    
                    button_height = max(calculated_height, min_height)
                    button_height = min(button_height, dp(300))
                    
                    btn.height = button_height
            
            # Пересчитываем общую высоту
            self._update_total_height()
        
        # Еще раз обновляем layout
        self.do_layout()


    def update_content_for_check_answer(self):
        """Обновление контента при проверке ответа (без сброса прокрутки)"""
        app = self.app
        
        if not app.current_questions:
            return
        
        current_index = app.current_question_index
        current_q = app.current_questions[current_index]
        test_name = app.current_test
        if len(test_name) > 40:
            display_name = test_name[:37] + "..."
        else:
            display_name = test_name
        
        self.test_name_label.text = f'[b]{display_name}[/b]'
        self.progress_label.text = f'Вопрос {current_index + 1} из {len(app.current_questions)}'
        self.stats_label.text = f'Правильно: {app.correct_answers}   Неправильно: {app.incorrect_answers}'
        self.update_nav_panel()
        
        # НЕ сбрасываем прокрутку при проверке ответа!
        # И НЕ сбрасываем активный индекс!
        
        self.update_question_area_instant(current_q)
        self.update_answer_buttons(current_q)
        self.update_action_buttons()
        app.update_check_button_state()
        
        self.do_layout()


    def update_content(self):
        """Быстрое и плавное обновление контента"""
        app = self.app
        
        if not app.current_questions:
            return
        
        current_index = app.current_question_index
        current_q = app.current_questions[current_index]
        test_name = app.current_test
        if len(test_name) > 40:
            display_name = test_name[:37] + "..."
        else:
            display_name = test_name
        
        self.test_name_label.text = f'[b]{display_name}[/b]'
        self.progress_label.text = f'Вопрос {current_index + 1} из {len(app.current_questions)}'
        self.stats_label.text = f'Правильно: {app.correct_answers}   Неправильно: {app.incorrect_answers}'
        
        # ОБНОВЛЯЕМ ЦВЕТА ВСЕГО ТЕКСТА
        self.test_name_label.color = app.text_primary
        self.progress_label.color = app.text_primary
        self.stats_label.color = app.text_primary
        self.question_label.color = app.text_primary  # ДОБАВЛЯЕМ ЦВЕТ ТЕКСТА ВОПРОСА
        
        self.update_nav_panel()
        self.reset_scroll_positions()
        self.update_question_area(current_q)
        self.update_answer_buttons(current_q)
        self.update_action_buttons()
        app.update_check_button_state()
        
        # ОБНОВЛЯЕМ ФОН КАРТОЧКИ ВОПРОСА
        if hasattr(self, 'question_card_container'):
            self._update_question_card_rect(self.question_card_container, None)
        
        Clock.schedule_once(self._smooth_finalize, 0.05)

    def _smooth_finalize(self, dt):
        """Плавная финализация - только если нужно"""
        if hasattr(self, 'answers_layout'):
            self.answers_layout.do_layout()



    def build_static_layout(self):
        """Строим статическую структуру один раз"""
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        self.header_layout = self.build_header()
        self.header_layout.size_hint = (1, None)
        self.header_layout.height = dp(200)
        main_layout.add_widget(self.header_layout)
        self.question_area = self.build_question_area()
        self.question_area.size_hint = (1, 1)
        main_layout.add_widget(self.question_area)
        self.bottom_panel = self.build_bottom_panel()
        self.bottom_panel.size_hint = (1, None)
        main_layout.add_widget(self.bottom_panel)
        
        self.add_widget(main_layout)
        Clock.schedule_once(self._initial_size_setup, 0.2)


    def _initial_size_setup(self, dt):
        """Начальная установка размеров после создания всех виджетов"""
        if hasattr(self.app, 'current_questions') and self.app.current_questions:
            self.update_content()
    
    def _force_layout_update(self, dt):
        """Принудительное обновление layout для многострочных вопросов и ответов"""
        if hasattr(self, 'question_label'):
            self.question_label.text_size = (self.question_label.width - dp(20), None)
        if hasattr(self, 'answer_buttons'):
            available_width = self.answers_scroll.width - dp(30)
            for btn in self.answer_buttons:
                btn.text_size = (available_width, None)
            self._recalculate_heights()

    def update_nav_buttons(self):
        """Обновляем кнопки навигации"""
        app = self.app
        self.nav_layout.clear_widgets()
        self.nav_buttons = []
        total_width = len(app.current_questions) * (dp(40) + dp(5))
        self.nav_layout.width = max(total_width, Window.width)
        self.nav_layout.cols = len(app.current_questions)
        
        for i in range(len(app.current_questions)):
            btn_color, text_color = app.get_question_button_color(i)
            question_btn = AndroidButton(
                text=str(i+1),
                size_hint_x=None,
                width=dp(40),
                height=dp(40),
                background_color=btn_color,
                color=text_color
            )
            question_btn.bind(on_press=lambda instance, idx=i: app.go_to_question(idx))
            self.nav_layout.add_widget(question_btn)
            self.nav_buttons.append(question_btn)

    def update_nav_panel(self):
        """Обновляем навигационную панель (создаем один раз)"""
        questions_count = len(self.app.current_questions)
        
        if not self.nav_panel.buttons or len(self.nav_panel.buttons) != questions_count:
            self.nav_panel.build_buttons(questions_count)
            self.update_nav_panel_width()
        self.nav_panel.update_colors()
    
    def _get_answer_button_color(self, answer_index, is_checked, saved_answer, correct_indices):
        """Возвращает цвет кнопки ответа и цвет текста"""
        if is_checked:
            if answer_index in correct_indices:
                return self.app.correct_color, (0, 0, 0, 1)
            elif saved_answer and answer_index in saved_answer:
                return self.app.error_color, (0, 0, 0, 1)
            else:
                return self.app.card_color, self.app.text_primary
        elif saved_answer and answer_index in saved_answer:
            return self.app.primary_color, (1, 1, 1, 1)
        return self.app.card_color, self.app.text_primary

    def _update_button_handlers(self, button, answer_index, is_checked):
        """Обновляет обработчики нажатия для кнопки"""
        button._do_press = None
        button._touch_down = None
        button._bound_events = {}
        if not is_checked:
            button.bind(on_press=lambda instance, idx=answer_index: self.app.select_answer(idx))


    def _select_answer_mouse(self, answer_index):
        """Обработчик выбора ответа мышкой - сбрасывает клавиатурный режим"""
        self.keyboard_mode = False
        self.active_answer_index = -1
        self.app.select_answer(answer_index)


    def update_answer_buttons(self, current_question):
        """Обновление кнопок ответов - МГНОВЕННАЯ ВЕРСИЯ"""
        app = self.app
        is_checked = app.question_checked[app.current_question_index]
        saved_answer = app.user_answers[app.current_question_index]
        self.answers_layout.clear_widgets()
        self.answer_buttons = []
        
        available_width = Window.width - dp(50)
        
        for i, answer in enumerate(current_question.answers):
            btn_color, text_color = self._get_answer_button_color(i, is_checked, saved_answer, current_question.correct_indices)
            
            # Учитываем активный элемент клавиатуры
            if self.keyboard_mode and i == self.active_answer_index:
                if btn_color == self.app.card_color:
                    btn_color = [
                        self.app.primary_color[0] * 0.3 + btn_color[0] * 0.7,
                        self.app.primary_color[1] * 0.3 + btn_color[1] * 0.7,
                        self.app.primary_color[2] * 0.3 + btn_color[2] * 0.7,
                        1
                    ]
                else:
                    btn_color = [
                        min(1.0, btn_color[0] * 1.2),
                        min(1.0, btn_color[1] * 1.2),
                        min(1.0, btn_color[2] * 1.2),
                        1
                    ]
            
            answer_btn = AndroidButton(
                text=answer,
                size_hint_y=None,
                height=dp(60),  # Временная высота
                background_color=btn_color,
                color=text_color,
                text_size=(available_width - dp(20), None),
                halign='left',
                valign='middle',
                padding=[dp(10), dp(8)],
                font_size=app.get_font_size(14),
                disabled=is_checked
            )
            
            if not is_checked:
                answer_btn.bind(on_press=lambda instance, idx=i: self._select_answer_mouse(idx))
            
            self.answers_layout.add_widget(answer_btn)
            self.answer_buttons.append(answer_btn)
        
        # МГНОВЕННЫЙ РАСЧЕТ ВЫСОТ ВМЕСТО ОТЛОЖЕННОГО
        self._calculate_heights_instant()

    def _calculate_heights_instant(self):
        """Мгновенный расчет высот кнопок ответов"""
        if not hasattr(self, 'answer_buttons') or not self.answer_buttons:
            return
        
        available_width = self.answers_scroll.width - dp(30)
        total_height = 0
        
        for btn in self.answer_buttons:
            btn.text_size = (available_width, None)
            btn.texture_update()  # МГНОВЕННОЕ ОБНОВЛЕНИЕ ТЕКСТУРЫ
            
            text_height = btn.texture_size[1] if hasattr(btn, 'texture_size') and btn.texture_size else dp(50)
            padding_vertical = dp(16)
            min_height = dp(50)
            calculated_height = text_height + padding_vertical
            
            button_height = max(calculated_height, min_height)
            button_height = min(button_height, dp(300))
            
            btn.height = button_height
            total_height += button_height + dp(8)
        
        self.answers_layout.height = total_height
        # МГНОВЕННОЕ ОБНОВЛЕНИЕ LAYOUT
        self.answers_layout.do_layout()

    def _calculate_heights_static(self):
        """Статический расчет высот без анимации"""
        if not hasattr(self, 'answer_buttons') or not self.answer_buttons:
            return
        
        available_width = self.answers_scroll.width - dp(30)
        total_height = 0
        
        for btn in self.answer_buttons:
            btn.text_size = (available_width, None)
            btn.texture_update()
            text_height = btn.texture_size[1] if hasattr(btn, 'texture_size') and btn.texture_size else dp(50)
            padding_vertical = dp(16)
            min_height = dp(50)
            calculated_height = text_height + padding_vertical
            button_height = max(calculated_height, min_height)
            button_height = min(button_height, dp(300))
            
            btn.height = button_height
            total_height += button_height + dp(8)
        self.answers_layout.height = total_height
    

    def _on_window_resize(self, window, width, height):
        """Упрощенный обработчик изменения размера окна - с обновлением фиксированной ширины"""
        # Обновляем фиксированную ширину вопроса при изменении размера окна
        if hasattr(self, 'question_label') and self.question_label:
            fixed_width = width - dp(80)
            self.question_label.text_size = (fixed_width, None)
            self.question_label.width = fixed_width
            self.question_label.texture_update()
        
        if hasattr(self, 'app') and hasattr(self.app, 'current_questions') and self.app.current_questions:
            Clock.schedule_once(lambda dt: self._calculate_heights_static(), 0.1)


    def update_question_area(self, current_question):
        """Обновление области вопроса"""
        self.question_label.text = f"{current_question.text}"
        self.question_label.color = self.app.text_primary  # ОБНОВЛЯЕМ ЦВЕТ ТЕКСТА
        available_width = Window.width - dp(80)
        self.question_label.text_size = (available_width, None)
        Clock.schedule_once(lambda dt: self.question_label.texture_update(), 0.1)


    def _update_question_height(self):
        """Внутренний метод для обновления высоты вопроса"""
        if hasattr(self, 'question_label') and self.question_label.text:
            available_width = self.width - dp(80)
            if available_width > 0:
                self.question_label.text_size = (available_width, None)
                self.question_label.texture_update()
                
                if self.question_label.texture_size:
                    text_height = self.question_label.texture_size[1]
                    self.question_label.height = max(text_height + dp(20), dp(80))


    def _update_total_height(self):
        """Обновляет общую высоту layout ответов"""
        total_height = 0
        for btn in self.answer_buttons:
            total_height += btn.height + dp(8)
        
        self.answers_layout.height = total_height



    def _update_answer_text_size(self, instance, size):
        """Обновление text_size для кнопок ответов при изменении размера"""
        instance.text_size = (size[0] - dp(20), None)

    def update_action_buttons(self):
        """Обновляем кнопки действий - включая кнопку GigaChat"""
        app = self.app
        is_checked = app.question_checked[app.current_question_index]
        if not is_checked:
            self.action_btn.text = "Проверить"
        elif app.current_question_index < len(app.current_questions) - 1:
            self.action_btn.text = "Далее"
        else:
            self.action_btn.text = "Завершить"
        if app.current_question_index == 0:
            self.back_btn.disabled = True
            self.back_btn.background_color = [
                app.primary_color[0],
                app.primary_color[1], 
                app.primary_color[2],
                app.primary_color[3] * 0.4
            ]
            self.back_btn.color = (1, 1, 1, 0.6)
        else:
            self.back_btn.disabled = False
            self.back_btn.background_color = app.primary_color
            self.back_btn.color = (1, 1, 1, 1)
        if hasattr(self, 'neuro_btn'):
            has_answers = app.user_answers[app.current_question_index] is not None and len(app.user_answers[app.current_question_index]) > 0
            if is_checked or has_answers:
                self.neuro_btn.disabled = False
                self.neuro_btn.background_color = [0.1, 0.5, 0.3, 1]
                self.neuro_btn.color = (1, 1, 1, 1)
            else:
                self.neuro_btn.disabled = True
                self.neuro_btn.background_color = [0.1, 0.5, 0.3, 0.4]
                self.neuro_btn.color = (1, 1, 1, 0.6)

    def on_enter(self):
        """Вызывается при входе на экран - добавляем обработчики клавиатуры"""
        if not self.keyboard_bind_added:
            Window.bind(on_key_down=self._on_keyboard_down)
            self.keyboard_bind_added = True
        
        # Сбрасываем прокрутку при входе на экран
        self.reset_scroll_positions()

    def on_leave(self):
        """Вызывается при выходе с экрана - убираем обработчики клавиатуры"""
        if self.keyboard_bind_added:
            Window.unbind(on_key_down=self._on_keyboard_down)
            self.keyboard_bind_added = False
        self.keyboard_mode = False
        self.active_answer_index = -1


    def _on_keyboard_down(self, window, key, scancode, codepoint, modifiers):
        """Обработчик нажатия клавиш с учетом проверенных вопросов"""
        # F1 обрабатывается в глобальном обработчике, пропускаем его здесь
        if key == 305:  # F1
            return False
        
        # Игнорируем, если нет вопросов
        if not self.app.current_questions:
            return False
            
        current_index = self.app.current_question_index
        is_checked = self.app.question_checked[current_index]

        # CTRL ДЛЯ КОПИРОВАНИЯ ВОПРОСА (левый или правый Ctrl)
        if key in [306] and hasattr(self, 'copy_question_btn'):  # Левый или правый Ctrl
            self.copy_question_btn.trigger_action(duration=0)
            return True
        
        # Стрелки влево/вправо работают всегда
        if key == 276:  # Стрелка влево - предыдущий вопрос
            if current_index > 0:
                self.app.current_question_index -= 1
                self._reset_keyboard_state()
                self.update_content_for_new_question()
                Clock.schedule_once(lambda dt: self.scroll_nav_to_current_question(), 0.1)
            return True
        elif key == 275:  # Стрелка вправо - следующий вопрос
            if current_index < len(self.app.current_questions) - 1:
                self.app.current_question_index += 1
                self._reset_keyboard_state()
                self.update_content_for_new_question()
                Clock.schedule_once(lambda dt: self.scroll_nav_to_current_question(), 0.1)
            return True
        
        # Для проверенных вопросов - навигация по ответам работает, но выбор отключен
        if is_checked:
            # В проверенном вопросе стрелочки вверх/вниз прокручивают ScrollView и перемещают выделение
            if key == 274:  # Стрелка вниз - перемещение вниз
                self._move_answer_selection(1)
                return True
            elif key == 273:  # Стрелка вверх - перемещение вверх
                self._move_answer_selection(-1)
                return True
            elif key == 13:  # Enter в проверенном вопросе
                self._handle_enter_key()
                return True
            # Пробел и другие клавиши выбора игнорируем для проверенных вопросов
            return False
        
        # Для непроверенных вопросов - полная навигация
        if key == 274:  # Стрелка вниз
            self._move_answer_selection(1)
            return True
        elif key == 273:  # Стрелка вверх
            self._move_answer_selection(-1)
            return True
        elif key == 32:  # Пробел - выбрать/снять выбор
            if self.active_answer_index != -1:
                self._toggle_answer_selection(self.active_answer_index)
                self._scroll_to_active_answer()
            return True
        elif key == 13:  # Enter - проверить/далее
            self._handle_enter_key()
            return True
        
        return False


    def _move_answer_selection(self, direction):
        """Перемещение выбора ответа стрелками вверх/вниз"""
        current_question = self.app.current_questions[self.app.current_question_index]
        answers_count = len(current_question.answers)
        
        if not self.keyboard_mode:
            # Первое нажатие - активируем режим клавиатуры
            self.keyboard_mode = True
            if direction > 0:  # Стрелка вниз - начинаем с первого
                self.active_answer_index = 0
            else:  # Стрелка вверх - начинаем с последнего
                self.active_answer_index = answers_count - 1
        else:
            # Двигаемся по кругу
            self.active_answer_index = (self.active_answer_index + direction) % answers_count
        
        self._update_answer_buttons_colors()
        self._scroll_to_active_answer()  # ДОБАВЛЯЕМ ПРОКРУТКУ
    


    def _scroll_to_active_answer(self):
        """Упрощенная версия прокрутки с гарантией видимости"""
        if (self.active_answer_index >= 0 and 
            hasattr(self, 'answers_scroll') and 
            hasattr(self, 'answer_buttons') and
            self.active_answer_index < len(self.answer_buttons)):
            
            try:
                scroll_view = self.answers_scroll
                total_height = self.answers_layout.height
                viewport_height = scroll_view.height
                
                # Если все ответы помещаются в видимой области - не прокручиваем
                if total_height <= viewport_height:
                    return
                
                # Простой расчет позиции на основе индекса
                total_buttons = len(self.answer_buttons)
                
                if self.active_answer_index == 0:  # Первая кнопка
                    target_scroll = 1.0
                elif self.active_answer_index == total_buttons - 1:  # Последняя кнопка
                    target_scroll = 0.0
                else:
                    # Для средних кнопок - равномерное распределение
                    position = (total_buttons - 1 - self.active_answer_index) / (total_buttons - 1)
                    target_scroll = position
                
                # Плавная анимация
                anim = Animation(scroll_y=target_scroll, duration=0.3)
                anim.start(scroll_view)
                    
            except Exception as e:
                print(f"Ошибка прокрутки ответов: {e}")


    def _toggle_answer_selection(self, answer_index):
        """Выбор/снятие выбора ответа пробелом с визуальной обратной связью"""
        # Если вопрос уже проверен - игнорируем выбор
        if self.app.question_checked[self.app.current_question_index]:
            return
            
        current_answers = self.app.user_answers[self.app.current_question_index]
        if current_answers is None:
            current_answers = []
        
        if answer_index in current_answers:
            current_answers.remove(answer_index)
        else:
            current_answers.append(answer_index)
        
        self.app.user_answers[self.app.current_question_index] = current_answers
        self.app.update_check_button_state()
        self._update_answer_buttons_colors()
        
        # Прокручиваем к выбранному ответу
        self.active_answer_index = answer_index
        self._scroll_to_active_answer()


    def _handle_enter_key(self):
        """Обработка клавиши Enter с учетом всех состояний"""
        current_index = self.app.current_question_index
        is_checked = self.app.question_checked[current_index]
        
        if not is_checked:
            # 1.1. Если вопрос не проверен и есть выбранные ответы - проверяем
            if self.app.user_answers[current_index] and len(self.app.user_answers[current_index]) > 0:
                self.app.check_answer()
                self._update_answer_buttons_colors()
                # После проверки НЕ сбрасываем клавиатурный режим и активный индекс
                # self.keyboard_mode = False  # УБИРАЕМ эту строку
                # self.active_answer_index = -1  # УБИРАЕМ эту строку
        else:
            # Вопрос уже проверен
            if current_index < len(self.app.current_questions) - 1:
                # 1.2. Если не последний вопрос - переходим к следующему
                self.app.current_question_index += 1
                self._reset_keyboard_state()  # Только при переходе между вопросами сбрасываем
                self.update_content_for_new_question()
                Clock.schedule_once(lambda dt: self.scroll_nav_to_current_question(), 0.1)
            else:
                # 1.3. Если последний вопрос - завершаем тест
                self.app.finish_test()

    def _reset_keyboard_state(self):
        """Сброс состояния клавиатурной навигации"""
        self.keyboard_mode = False
        self.active_answer_index = -1

    def _update_answer_buttons_colors(self):
        """Обновление цветов кнопок ответов с учетом клавиатурной навигации"""
        if not hasattr(self, 'answer_buttons') or not self.answer_buttons:
            return
            
        current_question = self.app.current_questions[self.app.current_question_index]
        is_checked = self.app.question_checked[self.app.current_question_index]
        saved_answer = self.app.user_answers[self.app.current_question_index]
        
        for i, button in enumerate(self.answer_buttons):
            # Базовый цвет как раньше
            base_color, text_color = self._get_answer_button_color(i, is_checked, saved_answer, current_question.correct_indices)
            
            # Подсветка активного элемента (работает и для проверенных вопросов)
            if self.keyboard_mode and i == self.active_answer_index:
                # Явная, но не агрессивная подсветка
                if base_color == self.app.card_color:
                    # Для обычных кнопок - легкий оттенок основного цвета
                    active_color = [
                        self.app.primary_color[0] * 0.15 + base_color[0] * 0.85,
                        self.app.primary_color[1] * 0.15 + base_color[1] * 0.85,
                        self.app.primary_color[2] * 0.15 + base_color[2] * 0.85,
                        1
                    ]
                else:
                    # Для уже выделенных кнопок - умеренное усиление цвета
                    active_color = [
                        min(1.0, base_color[0] * 1.15),
                        min(1.0, base_color[1] * 1.15),
                        min(1.0, base_color[2] * 1.15),
                        1
                    ]
                button.background_color = active_color
            else:
                button.background_color = base_color
                
            button.color = text_color


class ResultsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        Window.bind(on_resize=self._on_window_resize)
        self.build_ui()

    def _on_window_resize(self, window, width, height):
        """Обновление ширины текста при изменении размера окна"""
        if hasattr(self, 'wrong_answers_popup') and hasattr(self.wrong_answers_popup, 'is_open'):
            pass

    def on_enter(self):
        """Вызывается при переходе на экран результатов"""
        self.build_ui()

    def build_ui(self):
        """Строим интерфейс результатов с фиксированными высотами кнопок"""
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        title_label = AndroidLabel(
            text='[b]Результаты теста[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.15),
            color=self.app.text_primary,
            halign='center'
        )
        main_layout.add_widget(title_label)
        total = len(self.app.current_questions) if hasattr(self.app, 'current_questions') and self.app.current_questions else 0
        correct = getattr(self.app, 'correct_answers', 0)
        incorrect = getattr(self.app, 'incorrect_answers', 0)
        percentage = (correct / total) * 100 if total > 0 else 0
        
        stats_text = (
            f"Правильных: {correct}/{total}\n"
            f"Неправильных: {incorrect}/{total}\n"
            f"Процент: {percentage:.1f}%"
        )
        
        stats_label = AndroidLabel(
            text=stats_text,
            font_size=self.app.get_font_size(18),
            color=self.app.text_primary,
            halign='center',
            size_hint=(1, 0.2)
        )
        main_layout.add_widget(stats_label)
        spacer = BoxLayout(size_hint=(1, 1))
        main_layout.add_widget(spacer)
        current_test_wrong_questions = getattr(self.app, 'wrong_questions', [])
        wrong_questions = getattr(self.app, 'wrong_questions', [])
        
        button_count = 1
        if current_test_wrong_questions:
            button_count += 1
        else:
            button_count += 1
        if wrong_questions:
            button_count += 1
        button_height = dp(50)
        spacing = dp(8)
        total_buttons_height = (button_count * button_height) + ((button_count - 1) * spacing)
        
        buttons_layout = BoxLayout(
            orientation='vertical', 
            size_hint=(1, None),
            height=total_buttons_height,
            spacing=dp(8)
        )
        if current_test_wrong_questions:
            repeat_current_btn = AndroidButton(
                text='Повтор ошибок',
                size_hint=(1, None),
                height=button_height,
                background_color=self.app.error_color,
                color=(1, 1, 1, 1),
                font_size=self.app.get_font_size(14)
            )
            repeat_current_btn.bind(on_press=self.repeat_current_test_wrong_answers)
            buttons_layout.add_widget(repeat_current_btn)
        else:
            perfect_score_btn = AndroidButton(
                text='Вы решили тест без ошибок!',
                size_hint=(1, None),
                height=button_height,
                background_color=self.app.correct_color,
                color=(1, 1, 1, 1),
                disabled=True,
                font_size=self.app.get_font_size(14)
            )
            perfect_score_btn.disabled_color = (1, 1, 1, 1)
            buttons_layout.add_widget(perfect_score_btn)
        if wrong_questions:
            wrong_btn = AndroidButton(
                text='Показать ошибки',
                size_hint=(1, None),
                height=button_height,
                background_color=self.app.card_color,
                color=self.app.text_primary,
                font_size=self.app.get_font_size(14)
            )
            wrong_btn.bind(on_press=self.show_wrong_answers)
            buttons_layout.add_widget(wrong_btn)
        menu_btn = AndroidButton(
            text='Назад в меню',
            size_hint=(1, None),
            height=dp(60),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        menu_btn.bind(on_press=self.return_to_menu)
        buttons_layout.add_widget(menu_btn)
        
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
        Clock.schedule_once(self._force_layout_update, 0.05)
    
    def _force_layout_update(self, dt):
        """Принудительное обновление layout"""
        self.do_layout()
        for child in self.children:
            child.do_layout()


    def repeat_current_test_wrong_answers(self, instance):
        """Повторение ошибок только что пройденного теста"""
        wrong_questions = getattr(self.app, 'wrong_questions', [])
        current_test = getattr(self.app, 'current_test', 'Текущий тест')
        
        if not wrong_questions:
            self.app.show_notification("Нет ошибок для повторения в этом тесте")
            return
        test_questions = []
        for wrong in wrong_questions:
            correct_indices = []
            for correct_answer in wrong['correct_answers']:
                if correct_answer in wrong['all_answers']:
                    correct_indices.append(wrong['all_answers'].index(correct_answer))
            
            test_questions.append(TestQuestion(
                text=wrong['question'],
                answers=wrong['all_answers'],
                correct_indices=correct_indices
            ))
        self.start_wrong_answers_test_from_objects(test_questions, f"Повторение ошибок: {current_test}")

    def start_wrong_answers_test_from_objects(self, test_questions, test_name):
        """Запуск теста из объектов TestQuestion"""
        if not test_questions:
            self.app.show_notification("Нет вопросов для тестирования")
            return
        self.app.start_custom_test(test_name, test_questions)
    


    def show_wrong_answers(self, instance):
        """Переход на экран показа ошибок"""
        # Создаем экран если его нет
        if not hasattr(self.app, 'wrong_answers_screen') or not self.app.screen_manager.has_screen('wrong_answers'):
            self.app.wrong_answers_screen = WrongAnswersScreen(name='wrong_answers')
            self.app.screen_manager.add_widget(self.app.wrong_answers_screen)
        
        # Переходим на экран ошибок
        self.app.screen_manager.current = 'wrong_answers'


    def _color_to_hex(self, color):
        """Конвертирует цвет Kivy в hex формат для markup"""
        try:
            r = int(color[0] * 255)
            g = int(color[1] * 255)
            b = int(color[2] * 255)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#000000"

    def _update_wrong_card_rect(self, instance, value):
        """Обновление фона карточки при изменении размера"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)
                RoundedRectangle(
                    pos=instance.pos, 
                    size=instance.size, 
                    radius=[dp(12)]
                )

    def _update_wrong_labels_text_size(self, instance, size):
        """Обновление text_size для меток в карточке"""
        if hasattr(instance, 'children') and instance.children:
            wrong_card = instance.children[0]
            available_width = instance.width - dp(32)
            
            for label in wrong_card.children:
                if isinstance(label, AndroidLabel):
                    label.text_size = (available_width, None)
    
    def close_wrong_answers(self):
        """Закрытие попапа с неправильными ответами"""
        if hasattr(self, 'wrong_answers_popup'):
            self.wrong_answers_popup.dismiss()
    
    def return_to_menu(self, instance):
        """Возврат в главное меню"""
        self.app.screen_manager.current = 'main'


class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.app.bind(
            bg_color=self.update_colors,
            card_color=self.update_colors, 
            text_primary=self.update_colors,
            primary_color=self.update_colors
        )
        self.main_layout = None
        self.build_ui()

    def update_colors(self, *args):
        """Обновление цветов при смене темы"""
        if self.main_layout:
            self.build_ui()

    def on_enter(self):
        """Вызывается при переходе на экран - обновляем цвета"""
        self.build_ui()

    def build_ui(self):
        """Строим интерфейс статистики с учетом текущей темы"""
        if self.main_layout:
            self.remove_widget(self.main_layout)
            
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        title = AndroidLabel(
            text='[b]Статистика[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.1),
            color=self.app.text_primary,
            halign='center'
        )
        self.main_layout.add_widget(title)
        
        scroll = ScrollView(size_hint=(1, 0.8))
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15))
        content.bind(minimum_height=content.setter('height'))
        general_stats = self.get_general_stats()
        general_card = self.create_stat_card("Общая статистика", general_stats)
        content.add_widget(general_card)
        tests_card = self.create_tests_stats_card()
        content.add_widget(tests_card)
        
        scroll.add_widget(content)
        self.main_layout.add_widget(scroll)
        back_btn = AndroidButton(
            text='Назад в меню',
            size_hint_y=None,
            height=dp(60),
            font_size=self.app.get_font_size(14),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1)
        )
        back_btn.bind(on_press=lambda x: setattr(self.app.screen_manager, 'current', 'main'))
        self.main_layout.add_widget(back_btn)
        
        self.add_widget(self.main_layout)



    def create_stat_card(self, title, stats_dict):
        """Создание АДАПТИВНОЙ карточки со статистикой с правильным выравниванием"""
        card = AdaptiveCard(background_color=self.app.card_color)
        title_label = AndroidLabel(
            text=f'[b]{title}[/b]',
            font_size=self.app.get_font_size(18),
            color=self.app.text_primary,
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title_label)
        
        # Используем BoxLayout вместо GridLayout для лучшего контроля выравнивания
        stats_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        for key, value in stats_dict.items():
            # Создаем строку с двумя элементами
            row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
            
            # Ключ - занимает всю доступную ширину слева
            key_label = AndroidLabel(
                text=key + ':',
                color=self.app.text_primary,
                halign='left',
                font_size=self.app.get_font_size(14),
                text_size=(None, None)
            )
            
            # Значение - прижимается к правому краю с фиксированной шириной
            value_label = AndroidLabel(
                text=str(value),
                color=self.app.primary_color,
                halign='right',
                font_size=self.app.get_font_size(14),
                size_hint_x=None,
                width=dp(60),  # Фиксированная ширина для значений
                text_size=(None, None)
            )
            
            row_layout.add_widget(key_label)
            row_layout.add_widget(value_label)
            stats_layout.add_widget(row_layout)
        
        card.add_widget(stats_layout)
        
        return card


    def create_tests_stats_card(self):
        """Создание АДАПТИВНОЙ карточки со статистикой по ошибкам с идеальным выравниванием"""
        card = AdaptiveCard(background_color=self.app.card_color)
        
        title_label = AndroidLabel(
            text='[b]Статистика по ошибкам[/b]',
            font_size=self.app.get_font_size(18),
            color=self.app.text_primary,
            size_hint_y=None,
            height=dp(30)
        )
        card.add_widget(title_label)
        
        test_stats = self.get_tests_stats()
        
        # Используем BoxLayout вместо GridLayout для лучшего контроля
        stats_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        stats_layout.bind(minimum_height=stats_layout.setter('height'))
        
        stats_items = [
            ('Тестов с ошибками', str(test_stats['tests_with_errors'])),
            ('Всего ошибок в истории', str(test_stats['total_errors'])),
            ('Уникальные ошибки', str(test_stats['unique_wrong_questions']))
        ]
        
        for key, value in stats_items:
            # Создаем строку с двумя элементами
            row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
            
            # Ключ - занимает всю доступную ширину слева
            key_label = AndroidLabel(
                text=key + ':',
                color=self.app.text_primary,
                halign='left',
                font_size=self.app.get_font_size(14),
                text_size=(None, None)
            )
            
            # Значение - прижимается к правому краю
            value_label = AndroidLabel(
                text=str(value),
                color=self.app.primary_color,
                halign='right',
                font_size=self.app.get_font_size(14),
                size_hint_x=None,
                width=dp(60),  # Фиксированная ширина для значений
                text_size=(None, None)
            )
            
            row_layout.add_widget(key_label)
            row_layout.add_widget(value_label)
            stats_layout.add_widget(row_layout)
        
        card.add_widget(stats_layout)
        
        return card


    def get_general_stats(self):
        """Получение общей статистики"""
        stats = {
            'Всего тестов': '0',
            'Всего попыток': '0',
            'Средний результат': '0%',
            'Решённых вопросов': '0',
            'Правильных ответов': '0'
        }
        
        if 'progress' in self.app.test_store:
            progress_data = self.app.test_store.get('progress')
            total_tests = len(progress_data.keys())
            total_questions = 0
            total_correct = 0
            total_attempts = 0
            
            for test_name, results in progress_data.items():
                if isinstance(results, dict) and 'correct' in results and 'total' in results:
                    correct = results['correct']
                    total = results['total']
                    
                    total_questions += total
                    total_correct += correct
                    total_attempts += 1
            
            avg_score = (total_correct / total_questions) * 100 if total_questions > 0 else 0
            
            stats = {
                'Всего тестов': str(total_tests),
                'Всего попыток': str(total_attempts),
                'Средний результат': f'{avg_score:.1f}%',
                'Решённых вопросов': str(total_questions),
                'Правильных ответов': str(total_correct)
            }
        
        return stats

    def get_tests_stats(self):
        """Получение статистики по тестам"""
        stats = {
            'tests_with_errors': 0,
            'total_errors': 0,
            'unique_wrong_questions': 0
        }
        
        if hasattr(self.app, 'wrong_answers_history'):
            test_names = set()
            unique_questions = set()
            
            for key in self.app.wrong_answers_history.keys():
                if key != 'last_wrong':
                    entry = self.app.wrong_answers_history.get(key)
                    test_names.add(entry['test_name'])
                    stats['total_errors'] += len(entry['wrong_questions'])
                    
                    for wrong in entry['wrong_questions']:
                        unique_questions.add(wrong['question'])
            
            stats['tests_with_errors'] = len(test_names)
            stats['unique_wrong_questions'] = len(unique_questions)
        
        return stats


class GigaChatSettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.app.bind(
            bg_color=self.update_colors,
            card_color=self.update_colors,
            text_primary=self.update_colors,
            primary_color=self.update_colors,
            correct_color=self.update_colors
        )
        
        self._keyboard_bound = False
        self.build_ui()
        
    def on_enter(self):
        """Вызывается при переходе на экран"""
        if not self._keyboard_bound:
            Window.bind(on_keyboard=self._on_keyboard)
            self._keyboard_bound = True
        
    def on_leave(self):
        """Вызывается при выходе с экрана"""
        if self._keyboard_bound:
            Window.unbind(on_keyboard=self._on_keyboard)
            self._keyboard_bound = False
        
    def _on_keyboard(self, window, key, *args):
        """Обработка клавиш в настройках GigaChat - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        
        # Проверяем что мы все еще в этом экране (на случай быстрых переходов)
        if not self.parent or self.app.screen_manager.current != 'gigachat_settings':
            return False
            
        if key == 32:  # Space - переключение статуса
            self.app.gigachat_enabled = not self.app.gigachat_enabled
            self.app.save_gigachat_settings()
            self.build_ui()
            return True
        elif key == 13:  # Enter - тестирование подключения
            self.test_connection(None)
            return True
        elif key == 27:  # Escape - возврат назад
            self.app.screen_manager.current = 'main'
            return True
            
        return False

    # Остальные методы остаются без изменений...
    def update_colors(self, *args):
        """Мгновенное обновление цветов при смене темы"""
        if hasattr(self, 'content_layout'):
            if hasattr(self, 'main_layout') and hasattr(self.main_layout, 'bg_rect'):
                self.main_layout.canvas.before.clear()
                with self.main_layout.canvas.before:
                    Color(rgba=self.app.bg_color)
                    self.main_layout.bg_rect = Rectangle(pos=self.main_layout.pos, size=self.main_layout.size)
            Clock.schedule_once(lambda dt: self.build_ui(), 0.1)
    
    def _update_all_card_backgrounds(self):
        """Мгновенное обновление всех фонов карточек"""
        if not hasattr(self, 'content_layout'):
            return
            
        for child in self.content_layout.children:
            if hasattr(child, 'canvas') and hasattr(child, 'bg_rect'):
                child.canvas.before.clear()
                with child.canvas.before:
                    Color(rgba=self.app.card_color)
                    child.bg_rect = RoundedRectangle(
                        pos=child.pos,
                        size=child.size,
                        radius=[dp(12)]
                    )

    def build_ui(self):
        """Построение интерфейса настроек GigaChat - С КНОПКОЙ ВКЛЮЧЕНИЯ"""
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        with main_layout.canvas.before:
            Color(rgba=self.app.bg_color)
            main_layout.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
            
        title_label = AndroidLabel(
            text='[b]Настройки GigaChat API[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.08),
            color=self.app.text_primary
        )
        main_layout.add_widget(title_label)
        
        scroll_view = ScrollView(
            size_hint=(1, 0.84),
            do_scroll_x=False
        )
        
        self.content_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None,
            spacing=dp(14),
            padding=[dp(5), dp(5), dp(5), dp(5)]
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        # ЗАМЕНА: вместо карточки с тумблером создаем карточку с КНОПКОЙ
        enable_card = self.create_enable_button_card()
        self.content_layout.add_widget(enable_card)
        
        api_card = self.create_api_settings_card()
        self.content_layout.add_widget(api_card)
        
        test_card = self.create_test_card()
        self.content_layout.add_widget(test_card)
        
        scroll_view.add_widget(self.content_layout)
        main_layout.add_widget(scroll_view)
        
        back_btn = AndroidButton(
            text='Назад в меню',
            size_hint=(1, None),
            height=dp(60),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        main_layout.bind(
            pos=self._update_main_bg,
            size=self._update_main_bg
        )
        Clock.schedule_once(self._force_layout_update, 0.1)

    def create_enable_button_card(self):
        """Создает карточку с кнопкой включения/выключения GigaChat с поддержкой Space"""
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(16)
        )
        
        with card_container.canvas.before:
            Color(rgba=self.app.card_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos, 
                size=card_container.size, 
                radius=[dp(12)]
            )
            
        title_label = AndroidLabel(
            text='[b]Статус GigaChat[/b]',
            font_size=self.app.get_font_size(16),
            size_hint=(1, 0.4),
            color=self.app.text_primary
        )
        card.add_widget(title_label)
        
        # КНОПКА вместо тумблера
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6), spacing=dp(10))
        
        # Текст статуса
        status_text = "ВКЛЮЧЕН" if self.app.gigachat_enabled else "ВЫКЛЮЧЕН"
        status_color = self.app.correct_color if self.app.gigachat_enabled else self.app.error_color
        
        status_label = AndroidLabel(
            text=f'Текущий статус: {status_text}',
            color=self.app.text_primary,
            font_size=self.app.get_font_size(14),
            size_hint_x=0.6,
            halign='left'
        )
        
        # Кнопка переключения
        self.toggle_btn = AndroidButton(
            text='ВЫКЛ' if not self.app.gigachat_enabled else 'ВКЛ',
            size_hint_x=0.4,
            background_color=self.app.error_color if not self.app.gigachat_enabled else self.app.correct_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        
        def toggle_gigachat(instance):
            self.app.gigachat_enabled = not self.app.gigachat_enabled
            self.app.save_gigachat_settings()
            # Обновляем UI
            self.build_ui()
        
        self.toggle_btn.bind(on_press=toggle_gigachat)
        
        button_layout.add_widget(status_label)
        button_layout.add_widget(self.toggle_btn)
        card.add_widget(button_layout)
        
        card_container.add_widget(card)
        card_container.bind(
            pos=self._update_card_bg,
            size=self._update_card_bg
        )
        
        return card_container

    def _update_main_bg(self, instance, value):
        """Обновление фона основного layout"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.app.bg_color)
            instance.bg_rect = Rectangle(pos=instance.pos, size=instance.size)

    def _force_layout_update(self, dt):
        """Принудительное обновление layout"""
        if hasattr(self, 'content_layout'):
            self.content_layout.do_layout()

    def create_api_settings_card(self):
        """Создает карточку настроек API с ПЕРЕНАСОМ ТЕКСТА"""
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(280),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(16),
            spacing=dp(12)
        )
        with card_container.canvas.before:
            Color(rgba=self.app.card_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos, 
                size=card_container.size, 
                radius=[dp(12)]
            )
            
        title_label = AndroidLabel(
            text='[b]Authorization Key[/b]',
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint_y=0.15
        )
        card.add_widget(title_label)
        
        input_bg_color = [1, 1, 1, 1] if not self.app.is_dark_theme else [0.3, 0.3, 0.3, 1]
        input_text_color = [0, 0, 0, 1] if not self.app.is_dark_theme else [1, 1, 1, 1]
        
        client_id_layout = BoxLayout(orientation='vertical', size_hint_y=0.25, spacing=dp(5))
        client_id_label = AndroidLabel(
            text='Authorization Key:',
            color=self.app.text_primary,
            font_size=self.app.get_font_size(14),
            size_hint_y=0.4
        )
        
        # ИСПРАВЛЕННЫЙ TextInput с ПЕРЕНАСОМ ТЕКСТА
        self.client_id_input = TextInput(
            text=self.app.gigachat_client_secret,
            hint_text='Введите Authorization Key\nз.ы. Он должен заканчиваться на ==',
            size_hint_y=0.6,
            background_color=input_bg_color,
            foreground_color=input_text_color,
            multiline=True,  # РАЗРЕШАЕМ МНОГОСТРОЧНОСТЬ
            write_tab=False,
            font_size=self.app.get_font_size(14),
            padding=[dp(10), dp(10)],
            hint_text_color=[0.5, 0.5, 0.5, 1]
        )
        
        # Устанавливаем фиксированную высоту для многострочного ввода
        self.client_id_input.height = dp(80)
        
        client_id_layout.add_widget(self.client_id_input)
        card.add_widget(client_id_layout)
        
        save_btn = AndroidButton(
            text='Сохранить настройки API',
            size_hint_y=0.15,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        save_btn.bind(on_press=self.save_api_settings)
        card.add_widget(save_btn)
        
        card_container.add_widget(card)
        card_container.bind(
            pos=self._update_card_bg,
            size=self._update_card_bg
        )
        
        return card_container

    def create_test_card(self):
        """Создает карточку тестирования с динамическими цветами"""
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            padding=dp(16)
        )
        with card_container.canvas.before:
            Color(rgba=self.app.card_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos, 
                size=card_container.size, 
                radius=[dp(12)]
            )
        
        title_label = AndroidLabel(
            text='[b]Проверка подключения[/b]',
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint_y=0.4
        )

        test_btn = AndroidButton(
            text='Тестировать подключение',
            size_hint_y=0.6,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        test_btn.bind(on_press=self.test_connection)
        card.add_widget(test_btn)
        
        card_container.add_widget(card)
        
        card_container.bind(
            pos=self._update_card_bg,
            size=self._update_card_bg
        )
        
        return card_container

    def _update_card_bg(self, instance, value):
        """Обновление фона карточки с динамическим цветом"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.app.card_color)
            instance.bg_rect = RoundedRectangle(
                pos=instance.pos, 
                size=instance.size, 
                radius=[dp(12)]
            )

    def save_api_settings(self, instance):
        """Сохранение настроек API"""
        self.app.gigachat_client_secret = self.client_id_input.text.strip()
        self.app.gigachat_access_token = ""
        self.app.save_gigachat_settings()
        self.app.show_quick_notification("Настройки GigaChat сохранены", 2)
    
    def test_connection(self, instance):
        """Тестирование подключения к GigaChat с проверкой интернета"""
        
        # 1. Проверяем настройки API
        if not self.app.gigachat_client_secret:
            self.app.show_quick_notification("Сначала настройте Authorization Key", 3)
            return
        
        # 2. Проверяем интернет-соединение
        if not self.app.is_internet_available():
            self.app.show_quick_notification("❌ Нет интернет-соединения\nПроверьте подключение к сети", 3)
            return
        
        # 3. Показываем уведомление о начале теста
        self.app.show_quick_notification("🔍 Проверяем подключение к GigaChat...", 2)
        
        def test_gigachat(dt):
            # 4. Проверяем токен
            access_token, error = self.app.get_gigachat_access_token()
            if error:
                self._show_test_result_popup(f"❌ Ошибка подключения к GigaChat:\n\n{error}", False)
            else:
                self._show_test_result_popup("✅ Подключение к GigaChat успешно!", True)

        Clock.schedule_once(test_gigachat, 0.1)

    def _show_test_result_popup(self, message, is_success):
        """Показ результата тестирования с поддержкой Enter/Escape"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        message_label = AndroidLabel(
            text=message,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(16),
            halign='center'
        )
        content.add_widget(message_label)
        
        close_btn = AndroidButton(
            text='Закрыть',
            size_hint_y=None,  # Добавляем
            height=dp(60),     # Уменьшаем высоту
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Результат тестирования',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False,
            background_color=self.app.bg_color
        )
        
        def on_close(instance):
            popup.dismiss()
        
        close_btn.bind(on_press=on_close)
        
        # ОБРАБОТКА ENTER/ESCAPE
        def on_key_down(window, key, *args):
            if key == 13 or key == 27 or key == 32:  # Enter или Escape
                on_close(None)
                return True
            return False
        
        # Сохраняем ссылку на функцию для очистки
        popup._key_handler = on_key_down
        
        Window.bind(on_key_down=on_key_down)
        
        def cleanup_popup(instance):
            Window.unbind(on_key_down=popup._key_handler)
        
        popup.bind(on_dismiss=cleanup_popup)
        
        self.app.show_popup(popup)

    def go_back(self, instance):
        """Возврат в главное меню"""
        self.app.screen_manager.current = 'main'



class WrongAnswersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.main_layout = None
        self.build_ui()
    
    def on_enter(self):
        """Вызывается при переходе на экран"""
        self.build_ui()
    

    def build_ui(self):
        """Построение интерфейса показа ошибок - МГНОВЕННАЯ ВЕРСИЯ"""
        self.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        
        # 1. ЗАГОЛОВОК
        title_label = AndroidLabel(
            text='[b]Неправильные ответы[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.1),
            color=self.app.text_primary,  # ОБНОВЛЯЕМ ЦВЕТ
            halign='center'
        )
        main_layout.add_widget(title_label)
        
        # 2. SCROLL VIEW С КАРТОЧКАМИ ОШИБОК
        scroll_view = ScrollView(size_hint=(1, 0.8))
        self.wrongs_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None,
            spacing=dp(10)
        )
        self.wrongs_layout.bind(minimum_height=self.wrongs_layout.setter('height'))
        
        # Создаем карточки СРАЗУ
        self._build_wrong_answers_cards()
        
        scroll_view.add_widget(self.wrongs_layout)
        main_layout.add_widget(scroll_view)
        
        # 3. СТАНДАРТНАЯ КНОПКА НАЗАД
        back_btn = AndroidButton(
            text='Назад',
            size_hint_y=None,
            height=dp(60),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)
        
        self.add_widget(main_layout)
        self.main_layout = main_layout
        
        # МГНОВЕННОЕ ОБНОВЛЕНИЕ ВСЕГО ЭКРАНА
        self.do_layout()


    def _build_wrong_answers_cards(self):
        """Создание карточек с ошибками - МГНОВЕННАЯ ВЕРСИЯ"""
        self.wrongs_layout.clear_widgets()
        
        wrong_questions = getattr(self.app, 'wrong_questions', [])
        
        for i, wrong in enumerate(wrong_questions):
            # Создаем карточку с адаптивной высотой
            card = self._create_wrong_answer_card(i, wrong)
            self.wrongs_layout.add_widget(card)
        
        # МГНОВЕННОЕ ОБНОВЛЕНИЕ LAYOUT
        self.wrongs_layout.do_layout()


    def _create_wrong_answer_card(self, index, wrong_data):
        """Создание одной карточки с ошибкой - МГНОВЕННАЯ ВЕРСИЯ"""
        # Контейнер карточки
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        
        with card_container.canvas.before:
            Color(rgba=self.app.card_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(12)]
            )
        
        # Создаем вертикальный layout для содержимого
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        
        # Вопрос
        question_text = f'[b]{index + 1}. {wrong_data["question"]}[/b]'
        question_label = AndroidLabel(
            text=question_text,
            text_size=(Window.width - dp(80), None),
            color=self.app.text_primary,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=self.app.get_font_size(14)
        )
        
        # Ваши ответы
        user_answers = " • ".join(wrong_data["user_answers"]) if wrong_data["user_answers"] else "Нет ответа"
        user_text = f'[color={self._color_to_hex(self.app.error_color)}]Ваши ответы:[/color] {user_answers}'
        user_label = AndroidLabel(
            text=user_text,
            text_size=(Window.width - dp(80), None),
            color=self.app.text_primary,
            size_hint_y=None,
            halign='left',
            font_size=self.app.get_font_size(13)
        )
        
        # Правильные ответы
        correct_answers = " • ".join(wrong_data["correct_answers"])
        correct_text = f'[color={self._color_to_hex(self.app.correct_color)}]Правильные:[/color] {correct_answers}'
        correct_label = AndroidLabel(
            text=correct_text,
            text_size=(Window.width - dp(80), None),
            color=self.app.text_primary,
            size_hint_y=None,
            halign='left',
            font_size=self.app.get_font_size(13)
        )
        
        # Добавляем все метки
        content_layout.add_widget(question_label)
        content_layout.add_widget(user_label)
        content_layout.add_widget(correct_label)
        
        # МГНОВЕННЫЙ РАСЧЕТ ВЫСОТЫ
        def calculate_heights():
            # Принудительно обновляем текстуры СРАЗУ
            question_label.texture_update()
            user_label.texture_update()
            correct_label.texture_update()
            
            # Получаем реальные высоты текста
            question_height = question_label.texture_size[1] if question_label.texture_size else dp(20)
            user_height = user_label.texture_size[1] if user_label.texture_size else dp(20)
            correct_height = correct_label.texture_size[1] if correct_label.texture_size else dp(20)
            
            # Суммируем высоты
            total_text_height = question_height + user_height + correct_height
            
            # Добавляем отступы и промежутки
            total_height = total_text_height + dp(24) + (dp(8) * 2)  # padding + spacing
            
            # Устанавливаем минимальную высоту
            min_height = dp(120)
            final_height = max(total_height, min_height)
            
            # Устанавливаем высоту content_layout
            content_layout.height = final_height
            
            # Устанавливаем высоту каждой метки равной ее текстовой высоте
            question_label.height = question_height + dp(4)
            user_label.height = user_height + dp(4)
            correct_label.height = correct_height + dp(4)
            
            # Устанавливаем высоту card_container
            card_container.height = final_height + dp(16)  # + внешний padding
            
            return final_height
        
        # ВЫЗЫВАЕМ РАСЧЕТ СРАЗУ
        calculate_heights()
        
        # Биндим обновление высоты на случай изменения размера окна
        question_label.bind(texture_size=lambda instance, value: calculate_heights())
        user_label.bind(texture_size=lambda instance, value: calculate_heights())
        correct_label.bind(texture_size=lambda instance, value: calculate_heights())
        
        card_container.add_widget(content_layout)
        
        # Биндим обновление фона
        card_container.bind(
            pos=self._update_card_bg,
            size=self._update_card_bg
        )
        
        return card_container

    def _update_card_bg(self, instance, value):
        """Обновление фона карточки"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(12)]
                )
    
    def _color_to_hex(self, color):
        """Конвертирует цвет Kivy в hex формат для markup"""
        try:
            r = int(color[0] * 255)
            g = int(color[1] * 255)
            b = int(color[2] * 255)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return "#000000"
    
    def go_back(self, instance):
        """Возврат к предыдущему экрану"""
        self.app.screen_manager.current = 'results'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.keyboard_mode = False
        self.active_test_index = -1
        self.test_cards = []
        self.keyboard_bind_added = False
        self.last_key_press_time = 0
        self.key_press_delay = 0.5


    def _scroll_to_active_test(self):
        """Прокрутка к активному тесту с плавной анимацией"""
        if (self.active_test_index >= 0 and 
            hasattr(self.app, 'tests_layout') and 
            self.active_test_index < len(self.test_cards)):
            
            try:
                # ПРАВИЛЬНЫЙ ПУТЬ К SCROLLVIEW - через родительскую структуру
                scroll_view = None
                parent = self.app.tests_layout.parent
                while parent and not isinstance(parent, ScrollView):
                    parent = parent.parent
                
                if parent and hasattr(parent, 'scroll_y'):
                    scroll_view = parent
                    total_tests = len(self.test_cards)
                    
                    # Если все тесты помещаются в видимой области - не прокручиваем
                    if total_tests <= self._get_visible_test_count():
                        return
                    
                    # Простой расчет позиции на основе индекса
                    if self.active_test_index == 0:  # Первый тест
                        target_scroll = 1.0
                    elif self.active_test_index == total_tests - 1:  # Последний тест
                        target_scroll = 0.0
                    else:
                        # Для средних тестов - равномерное распределение
                        position = (total_tests - 1 - self.active_test_index) / (total_tests - 1)
                        target_scroll = position
                    
                    # Плавная анимация прокрутки
                    anim = Animation(scroll_y=target_scroll, duration=0.3)
                    anim.start(scroll_view)
                    
            except Exception as e:
                print(f"Ошибка прокрутки тестов: {e}")

    def _get_visible_test_count(self):
        """Оценивает количество тестов, которые помещаются в видимой области"""
        try:
            # Находим ScrollView
            scroll_view = None
            parent = self.app.tests_layout.parent
            while parent and not isinstance(parent, ScrollView):
                parent = parent.parent
            
            if parent and hasattr(parent, 'height'):
                # Высота одного теста (карточка + отступы)
                test_height = dp(140) + dp(8)  # высота карточки + spacing
                visible_count = parent.height // test_height
                return max(1, int(visible_count))
        except:
            pass
        return 3  # значение по умолчанию


    def _move_test_selection(self, direction):
        """Перемещение выбора теста стрелками вверх/вниз"""
        if not self.test_cards:
            return
            
        if not self.keyboard_mode:
            self.keyboard_mode = True
            self.active_test_index = 0
        else:
            self.active_test_index = (self.active_test_index + direction) % len(self.test_cards)
        
        self._update_test_cards_colors()
        self._scroll_to_active_test()  # ДОБАВЛЯЕМ ПРОКРУТКУ
    # Остальные методы остаются без изменений...



    def on_enter(self):
        """Вызывается при входе на экран - добавляем обработчики клавиатуры"""
        if not self.keyboard_bind_added:
            Window.bind(on_key_down=self._on_keyboard_down)
            self.keyboard_bind_added = True
        # Сбрасываем состояние навигации
        self.keyboard_mode = False
        self.active_test_index = -1
        # Получаем актуальный список тестов
        Clock.schedule_once(lambda dt: self._update_test_cards_list(), 0.1)
        
    def on_leave(self):
        """Вызывается при выходе с экрана - убираем обработчики клавиатуры"""
        if self.keyboard_bind_added:
            Window.unbind(on_key_down=self._on_keyboard_down)
            self.keyboard_bind_added = False
        self.keyboard_mode = False
        self.active_test_index = -1
        # Сбрасываем подсветку всех карточек
        self._reset_all_cards_colors()
        
    def _update_test_cards_list(self):
        """Обновление списка карточки тестов для клавиатурной навигации"""
        if hasattr(self.app, 'tests_layout'):
            self.test_cards = []
            # Собираем все контейнеры карточек тестов
            for child in self.app.tests_layout.children:
                if (isinstance(child, BoxLayout) and 
                    hasattr(child, 'canvas') and 
                    len(child.children) > 0):
                    # Проверяем, что это действительно карточка теста (имеет кнопки)
                    def has_test_buttons(widget):
                        if isinstance(widget, AndroidButton) and widget.text in ['Начать', 'Удалить']:
                            return True
                        if hasattr(widget, 'children'):
                            for child in widget.children:
                                if has_test_buttons(child):
                                    return True
                        return False
                    
                    if has_test_buttons(child):
                        self.test_cards.append(child)
            
            # Переворачиваем список, так как в GridLayout элементы идут снизу вверх
            self.test_cards.reverse()


    def _on_keyboard_down(self, window, key, scancode, codepoint, modifiers):
        """Обработчик нажатия клавиш в главном меню"""
        # F1 обрабатывается в глобальном обработчике, пропускаем его здесь
        if key == 305:  # F1
            return False

        # ОБНОВЛЯЕМ СПИСОК КАРТОЧЕК ПЕРЕД ОБРАБОТКОЙ
        self._update_test_cards_list()
        
        if not self.test_cards:
            return False
            
        # Стрелки вверх/вниз - навигация по тестам
        if key == 273:  # Стрелка вверх - ВВЕРХ
            self._move_test_selection(-1)
            return True
        elif key == 274:  # Стрелка вниз - ВНИЗ
            self._move_test_selection(1)
            return True
        elif key == 32 or key == 13:  # Пробел или Enter - начать выбранный тест
            # Защита от множественных нажатий
            current_time = Clock.get_time()
            if current_time - self.last_key_press_time < self.key_press_delay:
                return True
            
            self.last_key_press_time = current_time

            if self.active_test_index != -1:
                self._start_selected_test()
            return True
            
        return False

    
    def _update_test_cards_colors(self):
        """Обновление цветов карточек тестов с учетом клавиатурной навигации"""
        # Сначала сбрасываем все карточки к исходному цвету
        self._reset_all_cards_colors()
        
        # Затем подсвечиваем активную карточку
        if self.keyboard_mode and 0 <= self.active_test_index < len(self.test_cards):
            active_card = self.test_cards[self.active_test_index]
            self._highlight_card(active_card)
    
    def _reset_all_cards_colors(self):
        """Сброс цветов всех карточек к исходному состоянию"""
        for card in self.test_cards:
            self._reset_card_color(card)
    
    def _highlight_card(self, card):
        """Подсветка карточки - ограниченное увеличение яркости"""
        if hasattr(card, 'canvas') and hasattr(card, 'bg_rect'):
            card.canvas.before.clear()
            with card.canvas.before:
                # Ограниченное увеличение яркости (максимум +20%)
                original_color = self.app.card_color
                highlight_color = [
                    min(1.0, original_color[0] * 1.2),
                    min(1.0, original_color[1] * 1.2),
                    min(1.0, original_color[2] * 1.2),
                    1
                ]
                Color(rgba=highlight_color)
                card.bg_rect = RoundedRectangle(
                    pos=card.pos, 
                    size=card.size, 
                    radius=[dp(10)]
                )
                
                # Обводка для активной карточки
                Color(rgba=self.app.primary_color)
                Line(
                    rounded_rectangle=(
                        card.pos[0], card.pos[1], 
                        card.size[0], card.size[1], 
                        dp(10)
                    ),
                    width=dp(2)
                )
    
    def _reset_card_color(self, card):
        """Возврат карточки к исходному цвету"""
        if hasattr(card, 'canvas'):
            card.canvas.before.clear()
            with card.canvas.before:
                Color(rgba=self.app.card_color)
                RoundedRectangle(
                    pos=card.pos, 
                    size=card.size, 
                    radius=[dp(10)]
                )
                Color(rgba=[c * 0.8 for c in self.app.card_color[:3]] + [1])
                Line(
                    rounded_rectangle=(
                        card.pos[0], card.pos[1], 
                        card.size[0], card.size[1], 
                        dp(10)
                    ),
                    width=dp(1.2)
                )
            

    def _start_selected_test(self):
        """Запуск выбранного теста"""
        if (self.active_test_index >= 0 and 
            self.active_test_index < len(self.test_cards) and
            hasattr(self.app, 'tests_layout')):
            
            # Находим соответствующий тест в tests_layout
            test_card = self.test_cards[self.active_test_index]
            
            # Ищем кнопку "Начать" и имитируем нажатие
            start_button = None
            
            def find_start_button(widget):
                nonlocal start_button
                if isinstance(widget, AndroidButton) and widget.text == 'Начать':
                    start_button = widget
                elif hasattr(widget, 'children'):
                    for child in widget.children:
                        find_start_button(child)
            
            find_start_button(test_card)
            
            if start_button:
                # Получаем имя теста из карточки
                test_name = ""
                def find_test_name(widget):
                    nonlocal test_name
                    if (isinstance(widget, AndroidLabel) and 
                        hasattr(widget, 'text') and 
                        widget.text and 
                        not widget.text.startswith('Вопросов:')):
                        # Берем первый найденный текст, который не является количеством вопросов
                        if not test_name:  # Только если еще не нашли имя
                            test_name = widget.text
                    elif hasattr(widget, 'children'):
                        for child in widget.children:
                            find_test_name(child)
                
                find_test_name(test_card)
                
                if test_name:
                    # Запускаем тест
                    self.app.start_test(test_name.strip())

class TestApp(App):
    active_preset = StringProperty('')
    custom_theme_name = StringProperty('custom')
    colors_modified = BooleanProperty(False)
    custom_colors = DictProperty({})


    font_scale = NumericProperty(0.95)

    GIGACHAT_API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    GIGACHAT_AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    gigachat_client_id = StringProperty("")
    gigachat_client_secret = StringProperty("")
    gigachat_access_token = StringProperty("")
    gigachat_enabled = BooleanProperty(False)
    questions_mode = StringProperty('all')
    questions_count = NumericProperty(10)
    questions_start = NumericProperty(1)
    questions_end = NumericProperty(10)
    current_test = StringProperty("")
    current_questions = ListProperty([])
    user_answers = ListProperty([])
    question_checked = ListProperty([])
    question_results = ListProperty([])
    wrong_questions = ListProperty([])


    def is_internet_available(self):
        """Проверка доступности интернета"""
        try:
            if platform == 'android':
                return self._check_android_connectivity()
            else:
                return self._check_desktop_connectivity()
        except Exception as e:
            print(f"Ошибка проверки интернета: {e}")
            return False
    
    def _check_android_connectivity(self):
        """Проверка соединения на Android"""
        try:
            from jnius import cast
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            connectivity_manager = cast(
                'android.net.ConnectivityManager',
                activity.getSystemService(Context.CONNECTIVITY_SERVICE)
            )
            
            if connectivity_manager is None:
                return False
                
            network_info = connectivity_manager.getActiveNetworkInfo()
            return network_info is not None and network_info.isConnected()
            
        except Exception as e:
            print(f"Ошибка проверки Android connectivity: {e}")
            # Fallback к обычной проверке
            return self._check_desktop_connectivity()
    
    def _check_desktop_connectivity(self):
        """Проверка соединения на ПК/других платформах"""
        try:
            import socket
            # Таймаут 5 секунд
            socket.setdefaulttimeout(5)
            # Пробуем подключиться к DNS Google
            socket.create_connection(("8.8.8.8", 53))
            return True
        except OSError:
            return False
        finally:
            # Возвращаем таймаут к значению по умолчанию
            socket.setdefaulttimeout(None)

    def on_start(self):
        """Вызывается при запуске приложения"""
        if platform == 'android':
            self.request_android_permissions()
    
    def request_android_permissions(self):
        """Запрос разрешений на Android"""
        try:
            if platform == 'android':
                from android.permissions import request_permissions, Permission
                
                def callback(permissions, results):
                    if all(results):
                        print("Все разрешения предоставлены")
                    else:
                        print("Некоторые разрешения не предоставлены")
                
                request_permissions([
                    Permission.INTERNET,
                    Permission.WRITE_EXTERNAL_STORAGE, 
                    Permission.READ_EXTERNAL_STORAGE
                ], callback)
        except ImportError:
            print("Android permissions module not available")
        except Exception as e:
            print(f"Error requesting permissions: {e}")

    def update_all_screens_fonts(self):
        """Обновление размеров шрифтов на всех экранах"""
        try:
            if not hasattr(self, 'screen_manager') or not self.screen_manager:
                return
                
            current_screen = self.screen_manager.current
            
            # Обновляем главный экран
            if hasattr(self, 'main_screen'):
                self.build_main_screen()
            
            # Обновляем экран тестирования
            if hasattr(self, 'optimized_test_screen'):
                if current_screen == 'test':
                    self.optimized_test_screen.update_content()
                self.optimized_test_screen.update_button_font_sizes()
            
            # Обновляем экран результатов
            if hasattr(self, 'results_screen') and current_screen == 'results':
                self.results_screen.build_ui()
            
            # Обновляем экран настроек GigaChat
            if hasattr(self, 'gigachat_settings_screen') and current_screen == 'gigachat_settings':
                self.gigachat_settings_screen.build_ui()
            
            # Обновляем экран настроек цветов
            if current_screen == 'color_settings' and hasattr(self, 'color_settings_screen'):
                self.color_settings_screen.build_ui()
            
            # ОБНОВЛЯЕМ ЭКРАН ПОВТОРА ОШИБОК
            if hasattr(self, 'repeat_screen') and current_screen == 'repeat':
                self.repeat_screen.build_ui()
            
            # ОБНОВЛЯЕМ ЭКРАН СТАТИСТИКИ
            if hasattr(self, 'statistics_screen') and current_screen == 'statistics':
                self.statistics_screen.build_ui()
                
        except Exception as e:
            print(f"Ошибка при обновлении шрифтов: {e}")
        


    def create_adaptive_card(self, content_widgets, background_color=None):
        """Создает адаптивную карточку с автоматической высотой"""
        if background_color is None:
            background_color = self.card_color
            
        card_container = AdaptiveCard()
        with card_container.canvas.before:
            Color(rgba=background_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(12)]
            )
        for widget in content_widgets:
            card_container.add_widget(widget)
        card_container.bind(
            pos=self._update_adaptive_card_bg,
            size=self._update_adaptive_card_bg
        )
        
        return card_container

    def _update_adaptive_card_bg(self, instance, value):
        """Обновление фона адаптивной карточки"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.card_color)
            instance.bg_rect = RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(12)]
            )

    

    def update_font_sizes(self):
        """Обновление размеров шрифтов во всем приложении"""
        try:
            if not hasattr(self, 'screen_manager') or not self.screen_manager:
                return
                
            # Используем новый метод для обновления всех экранов
            self.update_all_screens_fonts()
            
        except Exception as e:
            print(f"Ошибка при обновлении шрифтов: {e}")
    
    def _on_window_resize(self, window, width, height):
        """Обновление размеров при изменении окна"""
        if hasattr(self, '_gigachat_popup') and self._gigachat_popup:
            for child in self._gigachat_popup.content.walk():
                if hasattr(child, 'text_size') and hasattr(child, 'text'):
                    child.text_size = (width * 0.85, None)
                    child.texture_update()
    is_dark_theme = BooleanProperty(False)
    light_bg = ListProperty([0.95, 0.98, 0.95, 1])
    light_card = ListProperty([1, 1, 1, 1])
    light_text_primary = ListProperty([0.07, 0.35, 0.07, 1])
    light_text_secondary = ListProperty([0.3, 0.5, 0.3, 1])
    light_primary = ListProperty([0.18, 0.63, 0.18, 1])
    light_correct = ListProperty([0.21, 0.76, 0.21, 1])
    light_error = ListProperty([0.86, 0.26, 0.21, 1])
    dark_bg = ListProperty([0.07, 0.15, 0.07, 1])
    dark_card = ListProperty([0.12, 0.22, 0.12, 1])
    dark_text_primary = ListProperty([0.9, 0.98, 0.9, 1])
    dark_text_secondary = ListProperty([0.7, 0.85, 0.7, 1])
    dark_primary = ListProperty([0.35, 0.78, 0.35, 1])
    dark_correct = ListProperty([0.45, 0.88, 0.45, 1])
    dark_error = ListProperty([0.91, 0.31, 0.27, 1])
    bg_color = ColorProperty([0.98, 0.98, 0.98, 1])
    card_color = ColorProperty([1, 1, 1, 1])
    text_primary = ColorProperty([0.13, 0.13, 0.13, 1])
    text_secondary = ColorProperty([0.46, 0.46, 0.46, 1])
    primary_color = ColorProperty([0.12, 0.53, 0.90, 1])
    correct_color = ColorProperty([0.30, 0.69, 0.31, 1])
    error_color = ColorProperty([0.96, 0.26, 0.21, 1])


    shuffle_questions = BooleanProperty(True)
    shuffle_answers = BooleanProperty(True)

    color_presets = {
        'green_soft': {
            'light': {
                'bg_color': [0.96, 0.98, 0.96, 1],
                'card_color': [0.99, 0.99, 0.99, 1],
                'text_primary': [0.15, 0.35, 0.15, 1],
                'text_secondary': [0.4, 0.5, 0.4, 1],
                'primary_color': [0.4, 0.7, 0.4, 1],
                'correct_color': [0.5, 0.8, 0.5, 1],
                'error_color': [0.9, 0.5, 0.5, 1]
            },
            'dark': {
                'bg_color': [0.1, 0.15, 0.1, 1],
                'card_color': [0.15, 0.2, 0.15, 1],
                'text_primary': [0.85, 0.95, 0.85, 1],
                'text_secondary': [0.7, 0.8, 0.7, 1],
                'primary_color': [0.5, 0.8, 0.5, 1],
                'correct_color': [0.6, 0.9, 0.6, 1],
                'error_color': [0.95, 0.6, 0.6, 1]
            }
        },
        'red_soft': {
            'light': {
                'bg_color': [0.98, 0.96, 0.96, 1],
                'card_color': [0.99, 0.99, 0.99, 1],
                'text_primary': [0.35, 0.15, 0.15, 1],
                'text_secondary': [0.5, 0.4, 0.4, 1],
                'primary_color': [0.8, 0.4, 0.4, 1],
                'correct_color': [0.5, 0.8, 0.5, 1],
                'error_color': [0.7, 0.3, 0.3, 1]
            },
            'dark': {
                'bg_color': [0.15, 0.1, 0.1, 1],
                'card_color': [0.2, 0.15, 0.15, 1],
                'text_primary': [0.95, 0.85, 0.85, 1],
                'text_secondary': [0.8, 0.7, 0.7, 1],
                'primary_color': [0.8, 0.5, 0.5, 1],
                'correct_color': [0.6, 0.9, 0.6, 1],
                'error_color': [0.9, 0.4, 0.4, 1]
            }
        },
        'orange_soft': {
            'light': {
                'bg_color': [0.98, 0.97, 0.95, 1],
                'card_color': [0.99, 0.99, 0.99, 1],
                'text_primary': [0.35, 0.25, 0.15, 1],
                'text_secondary': [0.5, 0.45, 0.4, 1],
                'primary_color': [0.9, 0.7, 0.4, 1],
                'correct_color': [0.5, 0.8, 0.5, 1],
                'error_color': [0.9, 0.5, 0.5, 1]
            },
            'dark': {
                'bg_color': [0.15, 0.12, 0.1, 1],
                'card_color': [0.2, 0.18, 0.15, 1],
                'text_primary': [0.95, 0.9, 0.85, 1],
                'text_secondary': [0.8, 0.75, 0.7, 1],
                'primary_color': [0.95, 0.75, 0.5, 1],
                'correct_color': [0.6, 0.9, 0.6, 1],
                'error_color': [0.95, 0.6, 0.6, 1]
            }
        },
        'blue_soft': {
            'light': {
                'bg_color': [0.96, 0.97, 0.98, 1],
                'card_color': [0.99, 0.99, 0.99, 1],
                'text_primary': [0.15, 0.25, 0.35, 1],
                'text_secondary': [0.4, 0.45, 0.5, 1],
                'primary_color': [0.4, 0.6, 0.8, 1],
                'correct_color': [0.5, 0.8, 0.5, 1],
                'error_color': [0.9, 0.5, 0.5, 1]
            },
            'dark': {
                'bg_color': [0.1, 0.12, 0.15, 1],
                'card_color': [0.15, 0.18, 0.2, 1],
                'text_primary': [0.85, 0.9, 0.95, 1],
                'text_secondary': [0.7, 0.75, 0.8, 1],
                'primary_color': [0.5, 0.7, 0.9, 1],
                'correct_color': [0.6, 0.9, 0.6, 1],
                'error_color': [0.95, 0.6, 0.6, 1]
            }
        },
        'pink_soft': {
            'light': {
                'bg_color': [0.98, 0.96, 0.97, 1],
                'card_color': [0.99, 0.99, 0.99, 1],
                'text_primary': [0.35, 0.15, 0.25, 1],
                'text_secondary': [0.5, 0.4, 0.45, 1],
                'primary_color': [0.9, 0.6, 0.7, 1],
                'correct_color': [0.5, 0.8, 0.5, 1],
                'error_color': [0.9, 0.5, 0.5, 1]
            },
            'dark': {
                'bg_color': [0.15, 0.1, 0.12, 1],
                'card_color': [0.2, 0.15, 0.18, 1],
                'text_primary': [0.95, 0.85, 0.9, 1],
                'text_secondary': [0.8, 0.7, 0.75, 1],
                'primary_color': [0.95, 0.7, 0.8, 1],
                'correct_color': [0.6, 0.9, 0.6, 1],
                'error_color': [0.95, 0.6, 0.6, 1]
            }
        },
        'purple_soft': {
            'light': {
                'bg_color': [0.97, 0.96, 0.98, 1],
                'card_color': [0.99, 0.99, 0.99, 1],
                'text_primary': [0.25, 0.15, 0.35, 1],
                'text_secondary': [0.45, 0.4, 0.5, 1],
                'primary_color': [0.7, 0.6, 0.9, 1],
                'correct_color': [0.5, 0.8, 0.5, 1],
                'error_color': [0.9, 0.5, 0.5, 1]
            },
            'dark': {
                'bg_color': [0.12, 0.1, 0.15, 1],
                'card_color': [0.18, 0.15, 0.2, 1],
                'text_primary': [0.9, 0.85, 0.95, 1],
                'text_secondary': [0.75, 0.7, 0.8, 1],
                'primary_color': [0.8, 0.7, 0.95, 1],
                'correct_color': [0.6, 0.9, 0.6, 1],
                'error_color': [0.95, 0.6, 0.6, 1]
            }
        },
        'green_medium': {
            'light': {
                'bg_color': [0.93, 0.97, 0.93, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.1, 0.3, 0.1, 1],
                'text_secondary': [0.3, 0.45, 0.3, 1],
                'primary_color': [0.25, 0.65, 0.25, 1],
                'correct_color': [0.35, 0.8, 0.35, 1],
                'error_color': [0.85, 0.35, 0.35, 1]
            },
            'dark': {
                'bg_color': [0.08, 0.13, 0.08, 1],
                'card_color': [0.13, 0.18, 0.13, 1],
                'text_primary': [0.88, 0.97, 0.88, 1],
                'text_secondary': [0.65, 0.78, 0.65, 1],
                'primary_color': [0.4, 0.85, 0.4, 1],
                'correct_color': [0.5, 0.95, 0.5, 1],
                'error_color': [0.97, 0.5, 0.5, 1]
            }
        },
        'red_medium': {
            'light': {
                'bg_color': [0.97, 0.93, 0.93, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.3, 0.1, 0.1, 1],
                'text_secondary': [0.45, 0.3, 0.3, 1],
                'primary_color': [0.7, 0.25, 0.25, 1],
                'correct_color': [0.35, 0.8, 0.35, 1],
                'error_color': [0.65, 0.2, 0.2, 1]
            },
            'dark': {
                'bg_color': [0.13, 0.08, 0.08, 1],
                'card_color': [0.18, 0.13, 0.13, 1],
                'text_primary': [0.97, 0.88, 0.88, 1],
                'text_secondary': [0.78, 0.65, 0.65, 1],
                'primary_color': [0.85, 0.4, 0.4, 1],
                'correct_color': [0.5, 0.95, 0.5, 1],
                'error_color': [0.95, 0.25, 0.25, 1]
            }
        },
        'orange_medium': {
            'light': {
                'bg_color': [0.97, 0.95, 0.9, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.3, 0.2, 0.1, 1],
                'text_secondary': [0.45, 0.38, 0.3, 1],
                'primary_color': [0.85, 0.6, 0.25, 1],
                'correct_color': [0.35, 0.8, 0.35, 1],
                'error_color': [0.85, 0.35, 0.35, 1]
            },
            'dark': {
                'bg_color': [0.13, 0.1, 0.08, 1],
                'card_color': [0.18, 0.15, 0.12, 1],
                'text_primary': [0.97, 0.92, 0.82, 1],
                'text_secondary': [0.78, 0.72, 0.62, 1],
                'primary_color': [0.95, 0.7, 0.35, 1],
                'correct_color': [0.5, 0.95, 0.5, 1],
                'error_color': [0.97, 0.5, 0.5, 1]
            }
        },
        'blue_medium': {
            'light': {
                'bg_color': [0.93, 0.95, 0.97, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.1, 0.2, 0.3, 1],
                'text_secondary': [0.3, 0.38, 0.45, 1],
                'primary_color': [0.25, 0.5, 0.7, 1],
                'correct_color': [0.35, 0.8, 0.35, 1],
                'error_color': [0.85, 0.35, 0.35, 1]
            },
            'dark': {
                'bg_color': [0.08, 0.1, 0.13, 1],
                'card_color': [0.12, 0.15, 0.18, 1],
                'text_primary': [0.88, 0.92, 0.97, 1],
                'text_secondary': [0.65, 0.72, 0.78, 1],
                'primary_color': [0.35, 0.65, 0.95, 1],
                'correct_color': [0.5, 0.95, 0.5, 1],
                'error_color': [0.97, 0.5, 0.5, 1]
            }
        },
        'pink_medium': {
            'light': {
                'bg_color': [0.97, 0.93, 0.95, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.3, 0.1, 0.2, 1],
                'text_secondary': [0.45, 0.3, 0.38, 1],
                'primary_color': [0.85, 0.4, 0.6, 1],
                'correct_color': [0.35, 0.8, 0.35, 1],
                'error_color': [0.85, 0.35, 0.35, 1]
            },
            'dark': {
                'bg_color': [0.13, 0.08, 0.1, 1],
                'card_color': [0.18, 0.13, 0.15, 1],
                'text_primary': [0.97, 0.88, 0.92, 1],
                'text_secondary': [0.78, 0.65, 0.7, 1],
                'primary_color': [0.95, 0.5, 0.75, 1],
                'correct_color': [0.5, 0.95, 0.5, 1],
                'error_color': [0.97, 0.5, 0.5, 1]
            }
        },
        'purple_medium': {
            'light': {
                'bg_color': [0.95, 0.93, 0.97, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.2, 0.1, 0.3, 1],
                'text_secondary': [0.38, 0.3, 0.45, 1],
                'primary_color': [0.65, 0.4, 0.85, 1],
                'correct_color': [0.35, 0.8, 0.35, 1],
                'error_color': [0.85, 0.35, 0.35, 1]
            },
            'dark': {
                'bg_color': [0.1, 0.08, 0.13, 1],
                'card_color': [0.15, 0.12, 0.18, 1],
                'text_primary': [0.92, 0.88, 0.97, 1],
                'text_secondary': [0.7, 0.65, 0.78, 1],
                'primary_color': [0.75, 0.55, 0.97, 1],
                'correct_color': [0.5, 0.95, 0.5, 1],
                'error_color': [0.97, 0.5, 0.5, 1]
            }
        },
        'green_bold': {
            'light': {
                'bg_color': [0.9, 0.95, 0.9, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.05, 0.25, 0.05, 1],
                'text_secondary': [0.2, 0.4, 0.2, 1],
                'primary_color': [0.1, 0.6, 0.1, 1],
                'correct_color': [0.2, 0.8, 0.2, 1],
                'error_color': [0.8, 0.2, 0.2, 1]
            },
            'dark': {
                'bg_color': [0.05, 0.1, 0.05, 1],
                'card_color': [0.1, 0.15, 0.1, 1],
                'text_primary': [0.8, 1, 0.8, 1],
                'text_secondary': [0.6, 0.8, 0.6, 1],
                'primary_color': [0.3, 0.9, 0.3, 1],
                'correct_color': [0.4, 1, 0.4, 1],
                'error_color': [1, 0.3, 0.3, 1]
            }
        },
        'red_bold': {
            'light': {
                'bg_color': [0.95, 0.9, 0.9, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.25, 0.05, 0.05, 1],
                'text_secondary': [0.4, 0.2, 0.2, 1],
                'primary_color': [0.8, 0.1, 0.1, 1],
                'correct_color': [0.2, 0.8, 0.2, 1],
                'error_color': [0.6, 0.1, 0.1, 1]
            },
            'dark': {
                'bg_color': [0.1, 0.05, 0.05, 1],
                'card_color': [0.15, 0.1, 0.1, 1],
                'text_primary': [1, 0.8, 0.8, 1],
                'text_secondary': [0.8, 0.6, 0.6, 1],
                'primary_color': [1, 0.2, 0.2, 1],
                'correct_color': [0.4, 1, 0.4, 1],
                'error_color': [1, 0.1, 0.1, 1]
            }
        },
        'orange_bold': {
            'light': {
                'bg_color': [0.95, 0.93, 0.85, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.3, 0.15, 0.05, 1],
                'text_secondary': [0.4, 0.3, 0.2, 1],
                'primary_color': [0.9, 0.5, 0.1, 1],
                'correct_color': [0.2, 0.8, 0.2, 1],
                'error_color': [0.8, 0.2, 0.2, 1]
            },
            'dark': {
                'bg_color': [0.1, 0.08, 0.05, 1],
                'card_color': [0.15, 0.12, 0.08, 1],
                'text_primary': [1, 0.9, 0.7, 1],
                'text_secondary': [0.8, 0.7, 0.5, 1],
                'primary_color': [1, 0.6, 0.2, 1],
                'correct_color': [0.4, 1, 0.4, 1],
                'error_color': [1, 0.3, 0.3, 1]
            }
        },
        'blue_bold': {
            'light': {
                'bg_color': [0.9, 0.93, 0.95, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.05, 0.15, 0.3, 1],
                'text_secondary': [0.2, 0.3, 0.4, 1],
                'primary_color': [0.1, 0.4, 0.8, 1],
                'correct_color': [0.2, 0.8, 0.2, 1],
                'error_color': [0.8, 0.2, 0.2, 1]
            },
            'dark': {
                'bg_color': [0.05, 0.08, 0.1, 1],
                'card_color': [0.08, 0.12, 0.15, 1],
                'text_primary': [0.8, 0.9, 1, 1],
                'text_secondary': [0.6, 0.7, 0.8, 1],
                'primary_color': [0.2, 0.6, 1, 1],
                'correct_color': [0.4, 1, 0.4, 1],
                'error_color': [1, 0.3, 0.3, 1]
            }
        },
        'pink_bold': {
            'light': {
                'bg_color': [0.95, 0.9, 0.93, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.3, 0.05, 0.15, 1],
                'text_secondary': [0.4, 0.2, 0.3, 1],
                'primary_color': [0.9, 0.2, 0.5, 1],
                'correct_color': [0.2, 0.8, 0.2, 1],
                'error_color': [0.8, 0.2, 0.2, 1]
            },
            'dark': {
                'bg_color': [0.1, 0.05, 0.08, 1],
                'card_color': [0.15, 0.1, 0.12, 1],
                'text_primary': [1, 0.8, 0.9, 1],
                'text_secondary': [0.8, 0.6, 0.7, 1],
                'primary_color': [1, 0.3, 0.7, 1],
                'correct_color': [0.4, 1, 0.4, 1],
                'error_color': [1, 0.3, 0.3, 1]
            }
        },
        'purple_bold': {
            'light': {
                'bg_color': [0.93, 0.9, 0.95, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.15, 0.05, 0.3, 1],
                'text_secondary': [0.3, 0.2, 0.4, 1],
                'primary_color': [0.6, 0.2, 0.9, 1],
                'correct_color': [0.2, 0.8, 0.2, 1],
                'error_color': [0.8, 0.2, 0.2, 1]
            },
            'dark': {
                'bg_color': [0.08, 0.05, 0.1, 1],
                'card_color': [0.12, 0.08, 0.15, 1],
                'text_primary': [0.9, 0.8, 1, 1],
                'text_secondary': [0.7, 0.6, 0.8, 1],
                'primary_color': [0.8, 0.4, 1, 1],
                'correct_color': [0.4, 1, 0.4, 1],
                'error_color': [1, 0.3, 0.3, 1]
            }
        },
        'green_vivid': {
            'light': {
                'bg_color': [0.85, 0.92, 0.85, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.02, 0.2, 0.02, 1],
                'text_secondary': [0.15, 0.35, 0.15, 1],
                'primary_color': [0.05, 0.7, 0.05, 1],
                'correct_color': [0.1, 0.9, 0.1, 1],
                'error_color': [0.9, 0.1, 0.1, 1]
            },
            'dark': {
                'bg_color': [0.03, 0.08, 0.03, 1],
                'card_color': [0.08, 0.12, 0.08, 1],
                'text_primary': [0.7, 1, 0.7, 1],
                'text_secondary': [0.5, 0.75, 0.5, 1],
                'primary_color': [0.2, 1, 0.2, 1],
                'correct_color': [0.3, 1, 0.3, 1],
                'error_color': [1, 0.2, 0.2, 1]
            }
        },
        'red_vivid': {
            'light': {
                'bg_color': [0.92, 0.85, 0.85, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.2, 0.02, 0.02, 1],
                'text_secondary': [0.35, 0.15, 0.15, 1],
                'primary_color': [0.9, 0.05, 0.05, 1],
                'correct_color': [0.1, 0.9, 0.1, 1],
                'error_color': [0.7, 0.05, 0.05, 1]
            },
            'dark': {
                'bg_color': [0.08, 0.03, 0.03, 1],
                'card_color': [0.12, 0.08, 0.08, 1],
                'text_primary': [1, 0.7, 0.7, 1],
                'text_secondary': [0.75, 0.5, 0.5, 1],
                'primary_color': [1, 0.1, 0.1, 1],
                'correct_color': [0.3, 1, 0.3, 1],
                'error_color': [1, 0.05, 0.05, 1]
            }
        },
        'orange_vivid': {
            'light': {
                'bg_color': [0.92, 0.9, 0.8, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.25, 0.12, 0.02, 1],
                'text_secondary': [0.35, 0.25, 0.15, 1],
                'primary_color': [0.95, 0.55, 0.05, 1],
                'correct_color': [0.1, 0.9, 0.1, 1],
                'error_color': [0.9, 0.1, 0.1, 1]
            },
            'dark': {
                'bg_color': [0.08, 0.06, 0.03, 1],
                'card_color': [0.12, 0.1, 0.06, 1],
                'text_primary': [1, 0.85, 0.6, 1],
                'text_secondary': [0.75, 0.65, 0.45, 1],
                'primary_color': [1, 0.7, 0.1, 1],
                'correct_color': [0.3, 1, 0.3, 1],
                'error_color': [1, 0.2, 0.2, 1]
            }
        },
        'blue_vivid': {
            'light': {
                'bg_color': [0.85, 0.9, 0.92, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.02, 0.12, 0.25, 1],
                'text_secondary': [0.15, 0.25, 0.35, 1],
                'primary_color': [0.05, 0.3, 0.9, 1],
                'correct_color': [0.1, 0.9, 0.1, 1],
                'error_color': [0.9, 0.1, 0.1, 1]
            },
            'dark': {
                'bg_color': [0.03, 0.06, 0.08, 1],
                'card_color': [0.06, 0.1, 0.12, 1],
                'text_primary': [0.7, 0.85, 1, 1],
                'text_secondary': [0.5, 0.65, 0.75, 1],
                'primary_color': [0.1, 0.7, 1, 1],
                'correct_color': [0.3, 1, 0.3, 1],
                'error_color': [1, 0.2, 0.2, 1]
            }
        },
        'pink_vivid': {
            'light': {
                'bg_color': [0.92, 0.85, 0.9, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.25, 0.02, 0.12, 1],
                'text_secondary': [0.35, 0.15, 0.25, 1],
                'primary_color': [0.95, 0.1, 0.6, 1],
                'correct_color': [0.1, 0.9, 0.1, 1],
                'error_color': [0.9, 0.1, 0.1, 1]
            },
            'dark': {
                'bg_color': [0.08, 0.03, 0.06, 1],
                'card_color': [0.12, 0.08, 0.1, 1],
                'text_primary': [1, 0.7, 0.85, 1],
                'text_secondary': [0.75, 0.5, 0.65, 1],
                'primary_color': [1, 0.2, 0.8, 1],
                'correct_color': [0.3, 1, 0.3, 1],
                'error_color': [1, 0.2, 0.2, 1]
            }
        },
        'purple_vivid': {
            'light': {
                'bg_color': [0.9, 0.85, 0.92, 1],
                'card_color': [1, 1, 1, 1],
                'text_primary': [0.12, 0.02, 0.25, 1],
                'text_secondary': [0.25, 0.15, 0.35, 1],
                'primary_color': [0.7, 0.1, 0.95, 1],
                'correct_color': [0.1, 0.9, 0.1, 1],
                'error_color': [0.9, 0.1, 0.1, 1]
            },
            'dark': {
                'bg_color': [0.06, 0.03, 0.08, 1],
                'card_color': [0.1, 0.06, 0.12, 1],
                'text_primary': [0.85, 0.7, 1, 1],
                'text_secondary': [0.65, 0.5, 0.75, 1],
                'primary_color': [0.9, 0.3, 1, 1],
                'correct_color': [0.3, 1, 0.3, 1],
                'error_color': [1, 0.2, 0.2, 1]
            }
        }
    }



    def apply_color_preset(self, preset_name):
        """Применение цветового пресета - ОБНОВЛЕННАЯ ВЕРСИЯ"""
        # Проверяем, является ли пресет кастомным
        if (hasattr(self, 'color_settings_screen') and 
            preset_name in self.color_settings_screen.custom_presets):
            
            preset_data = self.color_settings_screen.custom_presets[preset_name]
            for color_property, color_value in preset_data.items():
                if color_property != 'is_custom' and color_property != 'slot_index' and hasattr(self, color_property):
                    setattr(self, color_property, color_value)
                    self.custom_colors[color_property] = color_value
            
            self.active_preset = preset_name
            self.colors_modified = True
            
        elif preset_name in self.color_presets:
            # Стандартные пресеты
            self.active_preset = preset_name
            self.colors_modified = False
            
            theme = 'dark' if self.is_dark_theme else 'light'
            preset_colors = self.color_presets[preset_name][theme]
            for color_property, color_value in preset_colors.items():
                setattr(self, color_property, color_value)
                self.custom_colors[color_property] = color_value
        else:
            print(f"Пресет {preset_name} не найден, используем green_soft")
            self.apply_color_preset('green_soft')
            return
        
        self.save_custom_colors()
        self.save_active_preset()
        
        # ВАЖНО: СРАЗУ ОБНОВЛЯЕМ ТЕМУ
        self.update_theme()


    def save_active_preset(self):
        """Сохранение активного пресета в настройки"""
        if 'theme_settings' not in self.settings_store:
            self.settings_store.put('theme_settings', 
                active_preset=self.active_preset,
                is_dark_theme=self.is_dark_theme,
                colors_modified=self.colors_modified
            )
        else:
            theme_settings = self.settings_store.get('theme_settings')
            theme_settings.update({
                'active_preset': self.active_preset,
                'is_dark_theme': self.is_dark_theme,
                'colors_modified': self.colors_modified
            })
            self.settings_store.put('theme_settings', **theme_settings)

    def load_active_preset(self):
        """Загрузка активного пресета"""
        if 'theme_settings' in self.settings_store:
            theme_settings = self.settings_store.get('theme_settings')
            old_preset = theme_settings.get('active_preset', '')
            migration_map = {
                'green': 'green_soft',
                'red': 'red_soft', 
                'orange': 'orange_soft',
                'blue': 'blue_soft',
                'pink': 'pink_soft',
                'grayscale': 'purple_soft'
            }
            
            if old_preset in migration_map:
                self.active_preset = migration_map[old_preset]
                self.save_active_preset()
            else:
                # БЕЗОПАСНАЯ ПРОВЕРКА КАСТОМНЫХ ПРЕСЕТОВ
                if 'custom_presets' in self.settings_store:
                    custom_presets = self.settings_store.get('custom_presets')
                    if old_preset in custom_presets:
                        self.active_preset = old_preset
                        self.colors_modified = True
                    elif old_preset in self.color_presets:
                        self.active_preset = old_preset
                        self.colors_modified = False
                    else:
                        self.active_preset = 'green_soft'
                        self.colors_modified = False
                else:
                    self.active_preset = 'green_soft'
                    self.colors_modified = False
            
            self.is_dark_theme = theme_settings.get('is_dark_theme', False)
            # СРАЗУ ПРИМЕНЯЕМ ТЕМУ ПРИ ЗАГРУЗКЕ
            self.apply_color_preset(self.active_preset)
        else:
            self.active_preset = 'green_soft'
            self.is_dark_theme = False
            self.colors_modified = False
            # Применяем тему по умолчанию
            self.apply_color_preset('green_soft')

    def get_storage_path(self, filename):
        """Получение полного пути к файлу с учетом платформы"""
        base_path = get_app_storage_path()
        return os.path.join(base_path, filename)


    def lock_orientation(self):
        """Блокировка ориентации на Android"""
        try:
            from jnius import autoclass
            from jnius import cast
            
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            
            Context = autoclass('android.content.Context')
            WindowManager = autoclass('android.view.WindowManager')
            
            # Блокируем портретную ориентацию
            activity.setRequestedOrientation(1)  # 1 = PORTRAIT
        except Exception as e:
            print(f"Не удалось заблокировать ориентацию: {e}")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Оптимизации для мобильных устройств
        if platform == 'android' or platform == 'ios':
            Config.set('graphics', 'maxfps', 60)
            Config.set('kivy', 'log_level', 'warning')
            # Увеличиваем таймауты для медленных устройств
            self.key_press_delay = 0.8
            self.lock_orientation()

        storage_path = get_app_storage_path()
        self.test_store = JsonStore(os.path.join(storage_path, 'tests_data.json'))
        self.settings_store = JsonStore(os.path.join(storage_path, 'app_settings.json'))
        self.wrong_answers_history = JsonStore(os.path.join(storage_path, 'wrong_answers_history.json'))

        self.screen_manager = None
        self.app = self
        
        self.test_store = JsonStore('tests_data.json')
        self.settings_store = JsonStore('app_settings.json')
        
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.current_test = ""
        self.current_questions = []
        self.user_answers = []
        self.question_checked = []
        self.question_results = []
        self.wrong_questions = []

        self.wrong_answers_history = JsonStore('wrong_answers_history.json')
        self.active_preset = ''
        self.colors_modified = False
        
        self._active_popups = set()
        self._last_theme_switch_time = 0  # Таймер для задержки смены темы
        self._theme_switch_delay = 2.0    # Задержка 2 секунды
        Window.bind(on_request_close=self.on_window_close)


    def on_window_close(self, *args):
        """Обработчик закрытия окна через крестик"""
        # Если есть активные popup - закрываем их
        if self._active_popups:
            self.close_all_popups()
            return True  # Блокируем закрытие
        
        # Показываем подтверждение выхода
        self.show_exit_confirmation()
        return True  # Блокируем немедленное закрытие


    def show_popup(self, popup):
        """Безопасное отображение popup с защитой от дублирования"""
        # Закрываем все существующие popup того же типа
        self.close_all_popups()
        
        popup.bind(on_dismiss=lambda x: self._remove_popup(popup))
        self._active_popups.add(popup)
        popup.open()

    def _remove_popup(self, popup):
        """Удаление popup из списка активных"""
        if popup in self._active_popups:
            self._active_popups.remove(popup)

    def close_all_popups(self):
        """Закрытие всех активных popup"""
        for popup in list(self._active_popups):
            try:
                popup.dismiss()
            except:
                pass
        self._active_popups.clear()



    def on_keyboard(self, window, key, *args):
        """Обработка клавиатуры для закрытия уведомлений и выхода"""


        # Левый Ctrl - смена темы день/ночь (работает везде) с задержкой
        if key == 305:  # Левый Ctrl
            current_time = Clock.get_time()
            if current_time - self._last_theme_switch_time >= self._theme_switch_delay:
                self._last_theme_switch_time = current_time
                self.toggle_theme(None)
                return True
            else:
                return True


        # Если есть активные попапы - Escape обрабатывается в них, не здесь
        if self._active_popups and key == 27:  # Escape для активных попапов
            return False  # False позволяет попапу обработать Escape
        
        # Если находимся в настройках GigaChat - ВОЗВРАЩАЕМ False чтобы GigaChatSettingsScreen мог обработать
        if self.screen_manager.current == 'gigachat_settings':
            return False
        
        # Если находимся в тесте и нажаты клавиши навигации - не обрабатываем здесь
        if self.screen_manager.current == 'test' and key in [273, 274, 275, 276, 32, 13, 306]:
            return False
        
        # SPACE В ГЛАВНОМ МЕНЮ - СМЕНА ТЕМЫ
        if self.screen_manager.current == 'main' and key == 32:  # Space
            self.toggle_theme(None)
            return True
        
        if key == 27:  # ESC или кнопка назад на Android

            if platform == 'android':
                return self.handle_android_back_button()
            
            current_screen = self.screen_manager.current
            
            # Определяем, на каком экране находимся
            if current_screen == 'main':
                # В главном меню - показываем подтверждение выхода
                self.show_exit_confirmation()
                return True
            elif current_screen in ['color_settings', 'statistics', 'repeat', 'wrong_answers']:
                # В настройках и просмотре ошибок - возвращаемся в главное меню или назад
                if current_screen == 'wrong_answers':
                    # Из просмотра ошибок возвращаемся к результатам
                    self.screen_manager.current = 'results'
                else:
                    # Из настроек - в главное меню
                    self.screen_manager.current = 'main'
                return True
            elif current_screen == 'test':
                # В тесте - возвращаемся в главное меню с подтверждением
                self.show_exit_test_confirmation()
                return True
            elif current_screen == 'results':
                # На экране результатов - возвращаемся в главное меню
                self.screen_manager.current = 'main'
                return True
            elif current_screen == 'splash':
                # На заставке - игнорируем
                return True
        
        return False
    
    def handle_android_back_button(self):
        """Обработка back-кнопки на Android"""
        current_screen = self.screen_manager.current
        
        if current_screen == 'main':
            self.show_exit_confirmation()
            return True
        elif current_screen in ['test', 'results', 'color_settings', 'statistics']:
            self.screen_manager.current = 'main'
            return True
        elif current_screen == 'splash':
            return True  # Игнорируем на заставке
        
        return False

    def show_exit_confirmation(self):
        """Показ подтверждения выхода из приложения с поддержкой Enter/Escape"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        message_label = AndroidLabel(
            text='Вы точно хотите выйти из приложения?',
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(16),
            halign='center'
        )
        content.add_widget(message_label)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=dp(10))
        
        cancel_btn = AndroidButton(
            text='Отмена',
            background_color=self.card_color,
            color=self.text_primary,
            font_size=self.get_font_size(14)
        )
        
        exit_btn = AndroidButton(
            text='Выйти',
            background_color=self.error_color,
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(14)
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(exit_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Подтверждение выхода',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
            background_color=self.bg_color
        )
        
        def on_cancel(instance):
            popup.dismiss()
        
        def on_exit(instance):
            # Закрываем приложение
            self.stop()
            # На Windows также нужно закрыть окно
            if platform == 'win':
                Window.close()
        
        cancel_btn.bind(on_press=on_cancel)
        exit_btn.bind(on_press=on_exit)
        
        # ДОБАВЛЯЕМ ОБРАБОТКУ КЛАВИШИ ENTER И ESCAPE
        def on_key_down(window, key, *args):
            if key == 13:  # Enter - выход
                on_exit(None)
                return True
            elif key == 27:  # Escape - отмена (закрытие попапа)
                on_cancel(None)
                return True
            return False
        
        # Биндим обработчик клавиатуры
        Window.bind(on_key_down=on_key_down)
        
        def cleanup_popup(instance):
            # Отвязываем обработчик при закрытии попапа
            Window.unbind(on_key_down=on_key_down)
        
        popup.bind(on_dismiss=cleanup_popup)
        
        self.show_popup(popup)
        
        return True

    def show_exit_test_confirmation(self):
        """Показ подтверждения выхода из теста с поддержкой Enter/Escape"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(20))
        
        message_label = AndroidLabel(
            text='Вы точно хотите выйти из теста?\n\nПрогресс будет потерян!',
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(16),
            halign='center'
        )
        content.add_widget(message_label)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.4), spacing=dp(10))
        
        cancel_btn = AndroidButton(
            text='Отмена',
            background_color=self.card_color,
            color=self.text_primary,
            font_size=self.get_font_size(14)
        )
        
        exit_btn = AndroidButton(
            text='Выйти',
            background_color=self.error_color,
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(14)
        )
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(exit_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Подтверждение выхода',
            content=content,
            size_hint=(0.8, 0.3),
            auto_dismiss=False,
            background_color=self.bg_color
        )
        
        def on_cancel(instance):
            popup.dismiss()
        
        def on_exit(instance):
            # Возвращаемся в главное меню
            self.screen_manager.current = 'main'
            popup.dismiss()
        
        cancel_btn.bind(on_press=on_cancel)
        exit_btn.bind(on_press=on_exit)
        
        # ДОБАВЛЯЕМ ОБРАБОТКУ КЛАВИШИ ENTER И ESCAPE
        def on_key_down(window, key, *args):
            if key == 13:  # Enter - выход из теста
                on_exit(None)
                return True
            elif key == 27:  # Escape - отмена (закрытие попапа)
                on_cancel(None)
                return True
            return False
        
        # Биндим обработчик клавиатуры
        Window.bind(on_key_down=on_key_down)
        
        def cleanup_popup(instance):
            # Отвязываем обработчик при закрытии попапа
            Window.unbind(on_key_down=on_key_down)
        
        popup.bind(on_dismiss=cleanup_popup)
        
        self.show_popup(popup)
        
        return True



    def show_notification(self, message, duration=None):
        """Показ уведомления с защитой от дублирования"""
        try:
            # Закрываем предыдущие уведомления
            self.close_all_popups()
            
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            scroll = ScrollView(size_hint=(1, 0.8))
            message_container = BoxLayout(orientation='vertical', size_hint_y=None)
            message_container.bind(minimum_height=message_container.setter('height'))

            message_label = AndroidLabel(
                text=message,
                color=[1, 1, 1, 1],
                font_size=self.get_font_size(18),
                text_size=(Window.width * 0.8, None),
                halign='left',
                valign='top',
                size_hint_y=None
            )
            message_label.bind(texture_size=lambda instance, size: setattr(message_label, 'height', max(size[1], dp(80))))

            message_container.add_widget(message_label)
            scroll.add_widget(message_container)
            content.add_widget(scroll)
            
            close_btn = AndroidButton(
                text='Закрыть',
                size_hint_y=None,
                height=dp(50),
                background_color=[0.3, 0.6, 0.9, 1],
                color=[1, 1, 1, 1],
                font_size=self.get_font_size(16)
            )
            
            popup_height = min(Window.height * 0.8, message_label.height + dp(200))
            popup = Popup(
                title='',
                content=content,
                size_hint=(0.95, None),
                height=popup_height,
                auto_dismiss=False,
                background_color=[0.1, 0.1, 0.1, 0.95],
                separator_color=[0, 0, 0, 0],
                title_size=0
            )
            
            close_btn.bind(on_press=popup.dismiss)
            content.add_widget(close_btn)
            
            # Используем безопасное отображение
            self.show_popup(popup)
            
            if duration is not None:
                Clock.schedule_once(lambda dt: popup.dismiss(), duration)
                
        except Exception as e:
            print(f"Ошибка показа уведомления: {e}")

    def show_quick_notification(self, message, duration=3):
        """Показ быстрого уведомления с защитой от дублирования"""
        try:
            # Закрываем предыдущие уведомления
            self.close_all_popups()
            
            content = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=dp(15))
            label = AndroidLabel(
                text=message,
                text_size=(Window.width * 0.7, None),
                halign='center',
                valign='middle',
                font_size=self.get_font_size(16),
                color=(1, 1, 1, 1),
                size_hint_y=None
            )
            
            def calculate_height(instance, value):
                if instance.texture_size:
                    text_height = instance.texture_size[1]
                    calculated_height = max(dp(80), min(text_height + dp(40), Window.height * 0.4))
                    instance.height = text_height
                    if hasattr(instance, '_popup_ref'):
                        instance._popup_ref.height = calculated_height
            
            label.bind(texture_size=calculate_height)
            content.add_widget(label)
            
            popup = Popup(
                title='',
                content=content,
                size_hint=(0.8, None),
                height=dp(100),
                background_color=[0.2, 0.2, 0.2, 0.95],
                separator_height=0,
                auto_dismiss=True
            )
            
            label._popup_ref = popup
            popup.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            
            # Используем безопасное отображение
            self.show_popup(popup)
            
            label.texture_update()
            if duration is not None:
                Clock.schedule_once(lambda dt: popup.dismiss(), duration)
                
        except Exception as e:
            print(f"Ошибка показа уведомления: {e}")



    def load_font_settings(self):
        """Загрузка настроек шрифтов"""
        if 'font_settings' in self.settings_store:
            font_data = self.settings_store.get('font_settings')
            self.font_scale = font_data.get('scale', 1.0)
    
    def save_font_settings(self):
        """Сохранение настроек шрифтов"""
        font_data = {
            'scale': self.font_scale
        }
        self.settings_store.put('font_settings', **font_data)

    def get_font_size(self, base_size):
        """Получение размера шрифта с учетом коэффициента масштабирования"""
        return sp(base_size * self.font_scale)

    def load_gigachat_settings(self):
        """Загрузка настроек GigaChat"""
        if 'gigachat_settings' in self.settings_store:
            gigachat_data = self.settings_store.get('gigachat_settings')
            self.gigachat_client_id = gigachat_data.get('client_id', '')
            self.gigachat_client_secret = gigachat_data.get('client_secret', '')
            self.gigachat_access_token = gigachat_data.get('access_token', '')
            self.gigachat_enabled = gigachat_data.get('enabled', False)

    def save_gigachat_settings(self):
        """Сохранение настроек GigaChat"""
        gigachat_data = {
            'client_id': self.gigachat_client_id,
            'client_secret': self.gigachat_client_secret,
            'access_token': self.gigachat_access_token,
            'enabled': self.gigachat_enabled
        }
        self.settings_store.put('gigachat_settings', **gigachat_data)

    def setup_ssl_certificates(self):
        """Настройка SSL сертификатов для GigaChat API"""
        try:
            import ssl
            import certifi
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(certifi.where())
            
            return ssl_context
            
        except Exception as e:
            print(f"Ошибка настройки SSL: {e}")
            return None

    def get_gigachat_access_token(self):
        """Получение access token для GigaChat с проверкой интернета"""
        
        # Предварительная проверка интернета
        if not self.is_internet_available():
            return None, "❌ Нет интернет-соединения\nПроверьте подключение к сети"
        
        try:
            if not self.gigachat_client_secret:
                return None, "Не настроен Authorization Key для GigaChat"

            # ... остальная часть метода без изменений ...
            import base64
            auth_key = f"{self.gigachat_client_secret}"
            
            import uuid 
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
                'RqUID': str(uuid.uuid4()),
                "Authorization": f"Basic {auth_key}",
            }
            
            data = {'scope': 'GIGACHAT_API_PERS'}
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            try:
                response = requests.post(
                    self.GIGACHAT_AUTH_URL,
                    headers=headers,
                    data=data,
                    verify=False,
                    timeout=30  # Таймаут 30 секунд
                )
            except requests.exceptions.ConnectionError:
                return None, "❌ Ошибка подключения к серверу GigaChat\nПроверьте интернет-соединение"
            except requests.exceptions.Timeout:
                return None, "❌ Таймаут подключения к GigaChat\nСервер не отвечает"
            except UnicodeEncodeError:
                return None, "❌ Ошибка в Authorization Key! Используйте только латинские символы"
            except Exception as e:
                return None, f"❌ Ошибка сети: {str(e)}"

            if response.status_code == 200:
                token_data = response.json()
                self.gigachat_access_token = token_data['access_token']
                self.save_gigachat_settings()
                return self.gigachat_access_token, None
            else:
                error_msg = f"❌ Ошибка авторизации: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f"\n{error_detail}"
                except:
                    error_msg += f"\n{response.text}"
                return None, error_msg
                
        except Exception as e:
            return None, f"❌ Неожиданная ошибка: {str(e)}"



    def ask_gigachat(self, question_text, user_answers, correct_answers, all_answers):
        """Запрос к GigaChat API для объяснения вопроса с проверкой интернета"""
        try:
            # Предварительная проверка
            if not self.gigachat_enabled:
                return "❌ GigaChat отключен. Включите его в настройках."
            
            if not self.is_internet_available():
                return "❌ Нет интернет-соединения\nПроверьте подключение к сети"
            
            # Получение токена
            access_token, error = self.get_gigachat_access_token()
            if error:
                return f"❌ Ошибка авторизации:\n{error}"
            
            # Формирование запроса
            prompt = self._build_gigachat_prompt(question_text, user_answers, correct_answers, all_answers)
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            data = {
                'model': 'GigaChat-2',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            # Отправка запроса с обработкой ошибок сети
            try:
                response = requests.post(
                    self.GIGACHAT_API_URL,
                    headers=headers,
                    data=json.dumps(data),
                    verify=False,
                    timeout=30  # Таймаут 30 секунд
                )
            except requests.exceptions.ConnectionError:
                return "❌ Ошибка подключения к GigaChat\nПроверьте интернет-соединение"
            except requests.exceptions.Timeout:
                return "❌ Таймаут подключения к GigaChat\nСервер не отвежает"
            
            if response.status_code == 200:
                response_data = response.json()
                explanation = response_data['choices'][0]['message']['content']
                return self._clean_gigachat_response(explanation)
            else:
                return f"❌ Ошибка API GigaChat: {response.status_code}\n{response.text}"
                
        except Exception as e:
            return f"❌ Ошибка подключения к GigaChat:\n{str(e)}"


    def _build_gigachat_prompt(self, question_text, user_answers, correct_answers, all_answers):
        """Формирование промпта для GigaChat"""
        user_answers_text = ", ".join(user_answers) if user_answers else "пользователь еще не ответил"
        correct_answers_text = ", ".join(correct_answers)
        
        answers_list = "\n".join([f"{i+1}. {answer}" for i, answer in enumerate(all_answers)])
        
        prompt = f"""
        ВОПРОС: {question_text}

        ВАРИАНТЫ ОТВЕТОВ:
        {answers_list}

        ПРАВИЛЬНЫЕ ОТВЕТЫ ПО ТЕСТУ: {correct_answers_text}

        Объясни почему данный ответ/ответы правильный. Если в вопросе спрашивают про термин, то дай ему краткое определение. Если ты не согласен с указанными ответами, то объясни почему
        Будь кратким и точным.
        Не используй markdown разметку.
        """
        
        return prompt

    def _clean_gigachat_response(self, text):
        """Очистка и форматирование ответа от GigaChat"""
        try:
            text = re.sub(r'\n\s*\n', '\n\n', text)
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'__(.*?)__', r'\1', text)
            text = re.sub(r'_(.*?)_', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)
            text = re.sub(r'^\s*[\d•\-]\s*', '• ', text, flags=re.MULTILINE)
            if len(text) > 2000:
                text = text[:1997] + "..."
                
            return text.strip()
            
        except Exception as e:
            return f"Ошибка форматирования ответа: {str(e)}"


    def ask_neuro_network(self, instance):
        """Обработчик кнопки 'Спросить у нейросети' с проверкой интернета"""
        
        # 1. Проверяем базовые условия
        if not self.current_questions:
            self.show_quick_notification("Нет активного вопроса", 2)
            return
            
        if not self.gigachat_enabled:
            self.show_quick_notification("GigaChat отключен. Включите его в настройках.", 3)
            return
        
        # 2. Проверяем интернет-соединение
        if not self.is_internet_available():
            self.show_quick_notification("❌ Нет интернет-соединения\nПроверьте подключение к сети", 3)
            return
        
        # 3. Проверяем выбранные ответы
        current_question = self.current_questions[self.current_question_index]
        question_text = current_question.text
        user_answer_indices = self.user_answers[self.current_question_index] or []
        user_answers = [current_question.answers[i] for i in user_answer_indices]
        correct_answers = [current_question.answers[i] for i in current_question.correct_indices]
        all_answers = current_question.answers
        
        if not user_answers and not self.question_checked[self.current_question_index]:
            self.show_quick_notification("Сначала выберите ответы для получения объяснения", 3)
            return
        
        # 4. Показываем уведомление о начале запроса
        self.show_quick_notification("📡 Подключаемся к GigaChat...", 2)
        
        # 5. Запускаем запрос в отдельном потоке
        Clock.schedule_once(lambda dt: self._process_gigachat_request(
            question_text, user_answers, correct_answers, all_answers
        ), 0.1)

    def _process_gigachat_request(self, question_text, user_answers, correct_answers, all_answers):
        """Обработка запроса к GigaChat"""
        try:
            gigachat_explanation = self.ask_gigachat(question_text, user_answers, correct_answers, all_answers)
            Clock.schedule_once(lambda dt: self.show_gigachat_explanation(
                question_text, 
                user_answers, 
                correct_answers, 
                all_answers, 
                gigachat_explanation
            ), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_notification(f"❌ Ошибка GigaChat:\n{str(e)}"), 0)


    def show_gigachat_explanation(self, question_text, user_answers, correct_answers, all_answers, gigachat_explanation):
        """Показ структурированного объяснения от GigaChat"""
        try:
            # Проверяем, нет ли ошибок соединения
            if gigachat_explanation.startswith('❌'):
                # Показываем ошибку как уведомление
                self.app.show_notification(gigachat_explanation)
                return
            if hasattr(self, '_current_notification') and self._current_notification:
                try:
                    self._current_notification.dismiss()
                except:
                    pass
            
            content = BoxLayout(orientation='vertical', size_hint=(1, 1))
            
            scroll_view = ScrollView(size_hint=(1, 0.9))
            main_layout = BoxLayout(
                orientation='vertical', 
                size_hint_y=None,
                spacing=dp(15),
                padding=[dp(10), dp(10), dp(10), dp(10)]
            )
            main_layout.bind(minimum_height=main_layout.setter('height'))
            question_card = self._create_explanation_card("Вопрос", question_text)
            main_layout.add_widget(question_card)
            correct_answers_text = "\n".join([f"• {answer}" for answer in correct_answers])
            correct_card = self._create_explanation_card("Правильные ответы", correct_answers_text)
            main_layout.add_widget(correct_card)
            if user_answers:
                user_answers_text = "\n".join([f"• {answer}" for answer in user_answers])
                user_card = self._create_explanation_card("Ваши ответы", user_answers_text)
                main_layout.add_widget(user_card)
            explanation_card = self._create_explanation_card("Объяснение от GigaChat", gigachat_explanation)
            main_layout.add_widget(explanation_card)
            
            scroll_view.add_widget(main_layout)
            content.add_widget(scroll_view)
            close_btn = AndroidButton(
                text='Закрыть',
                size_hint=(1, 0.1),
                background_color=self.primary_color,
                color=(1, 1, 1, 1),
                font_size=self.get_font_size(16)
            )
            close_btn.bind(on_press=lambda x: self._close_gigachat_popup())
            content.add_widget(close_btn)
            
            self._gigachat_popup = Popup(
                title='📚 Разбор вопроса',
                content=content,
                size_hint=(0.95, 0.85),
                auto_dismiss=False,
                background_color=self.bg_color
            )
            
            self._current_notification = self._gigachat_popup
            def finalize_layout(dt):
                for card in main_layout.children:
                    if hasattr(card, 'do_layout'):
                        card.do_layout()
                main_layout.do_layout()
            
            Clock.schedule_once(finalize_layout, 0.2)
            
            self._gigachat_popup.open()
            
        except IndexError as e:
            print(f"Ошибка показа объяснения GigaChat: {e}")
            self.show_notification(f"GigaChat:\n\n{gigachat_explanation}")

    def _create_explanation_card(self, title, content_text):
        """Создание карточки для раздела объяснения"""
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        card = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            padding=dp(16),
            spacing=dp(8)
        )
        with card_container.canvas.before:
            Color(rgba=self.card_color)
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(12)]
            )
        title_label = AndroidLabel(
            text=f'[b]{title}[/b]',
            font_size=self.get_font_size(16),
            color=self.primary_color,
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        card.add_widget(title_label)
        separator = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(1))
        with separator.canvas.before:
            Color(rgba=[0.7, 0.7, 0.7, 0.3])
            Rectangle(pos=separator.pos, size=separator.size)
        card.add_widget(separator)
        content_label = AndroidLabel(
            text=content_text,
            text_size=(Window.width * 0.8, None),
            color=self.text_primary,
            size_hint_y=None,
            halign='left',
            valign='top',
            font_size=self.get_font_size(14)
        )
        def update_content_height(instance, value):
            if instance.texture_size:
                instance.height = instance.texture_size[1] + dp(10)
        
        content_label.bind(texture_size=update_content_height)
        card.add_widget(content_label)
        def update_card_height(instance, value):
            total_height = (title_label.height + separator.height + 
                        content_label.height + dp(32))
            card.height = total_height
            card_container.height = total_height + dp(16)
        
        content_label.bind(height=update_card_height)
        
        card_container.add_widget(card)
        card_container.bind(
            pos=self._update_card_background,
            size=self._update_card_background
        )
        separator.bind(
            pos=self._update_separator_line,
            size=self._update_separator_line
        )
        
        return card_container

    def _update_card_background(self, instance, value):
        """Обновление фона карточки"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.card_color)
            RoundedRectangle(
                pos=instance.pos, 
                size=instance.size, 
                radius=[dp(12)]
            )

    def _update_separator_line(self, instance, value):
        """Обновление разделительной линии"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=[0.7, 0.7, 0.7, 0.3])
            Rectangle(pos=instance.pos, size=instance.size)


    def _close_gigachat_popup(self):
        """Закрытие попапа GigaChat"""
        if hasattr(self, '_gigachat_popup') and self._gigachat_popup:
            self._gigachat_popup.dismiss()


            
    def can_check_answer(self):
        """Проверяет, можно ли проверять ответ (выбран ли хотя бы один вариант)"""
        if self.current_question_index >= len(self.user_answers):
            return False
        
        user_answer = self.user_answers[self.current_question_index]
        return user_answer is not None and len(user_answer) > 0

    def update_check_button_state(self):
        """Обновляет состояние кнопки проверки - ТОЛЬКО для кнопки 'Проверить'"""
        if hasattr(self, 'optimized_test_screen'):
            is_checked = self.question_checked[self.current_question_index]
            
            if not is_checked:
                can_check = self.can_check_answer()
                
                if can_check:
                    self.optimized_test_screen.action_btn.disabled = False
                    self.optimized_test_screen.action_btn.background_color = self.primary_color
                    self.optimized_test_screen.action_btn.color = (1, 1, 1, 1)
                else:
                    self.optimized_test_screen.action_btn.disabled = True
                    self.optimized_test_screen.action_btn.background_color = [
                        self.primary_color[0],
                        self.primary_color[1],
                        self.primary_color[2],
                        self.primary_color[3] * 0.4
                    ]
                    self.optimized_test_screen.action_btn.color = (1, 1, 1, 0.6)
            else:
                self.optimized_test_screen.action_btn.disabled = False
                self.optimized_test_screen.action_btn.background_color = self.primary_color
                self.optimized_test_screen.action_btn.color = (1, 1, 1, 1)
        
    def open_repeat_screen(self, instance):
        """Открывает экран повторения ошибок"""
        if not hasattr(self, 'wrong_answers_history'):
            self.wrong_answers_history = JsonStore('wrong_answers_history.json')
        has_wrong_answers = False
        for key in self.wrong_answers_history.keys():
            if key != 'last_wrong':
                has_wrong_answers = True
                break
        
        if not has_wrong_answers:
            self.show_notification("Нет ошибок в истории для повторения")
            return
        if not hasattr(self, 'repeat_screen') or not self.screen_manager.has_screen('repeat'):
            self.repeat_screen = RepeatWrongAnswersScreen(name='repeat')
            self.screen_manager.add_widget(self.repeat_screen)
        
        self.screen_manager.current = 'repeat'
    
    def open_statistics_screen(self, instance):
        """Открывает экран статистики"""
        if not hasattr(self, 'statistics_screen') or not self.screen_manager.has_screen('statistics'):
            self.statistics_screen = StatisticsScreen(name='statistics')
            self.screen_manager.add_widget(self.statistics_screen)
        
        self.screen_manager.current = 'statistics'


    def save_wrong_answers_to_history(self):
        """Сохранение неправильных ответов в историю"""
        if hasattr(self, 'wrong_questions') and self.wrong_questions:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = {
                'test_name': self.current_test,
                'timestamp': timestamp,
                'wrong_questions': self.wrong_questions,
                'total_questions': len(self.current_questions),
                'correct_count': self.correct_answers
            }
            self.wrong_answers_history.put(timestamp, **history_entry)
            self.wrong_answers_history.put('last_wrong', 
                test_name=self.current_test,
                wrong_count=len(self.wrong_questions),
                timestamp=timestamp
            )
    
    def get_all_wrong_questions(self):
        """Сбор всех неправильных вопросов из истории"""
        all_wrong_questions = []
        
        for key in self.wrong_answers_history.keys():
            if key != 'last_wrong':
                entry = self.wrong_answers_history.get(key)
                all_wrong_questions.extend(entry['wrong_questions'])
        
        return all_wrong_questions
    
    def get_wrong_questions_by_test(self, test_name):
        """Получение ошибок по конкретному тесту"""
        wrong_questions = []
        
        for key in self.wrong_answers_history.keys():
            if key != 'last_wrong':
                entry = self.wrong_answers_history.get(key)
                if entry['test_name'] == test_name:
                    wrong_questions.extend(entry['wrong_questions'])
        
        return wrong_questions
    

    def start_custom_test(self, test_name, questions):
        """Запуск кастомного теста (для режима повторения ошибок)"""
        self.current_test = test_name
        self.current_questions = questions
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        
        self.user_answers = [None] * len(self.current_questions)
        self.question_checked = [False] * len(self.current_questions)
        self.question_results = [False] * len(self.current_questions)
        self.wrong_questions = []
        if self.screen_manager.has_screen('test'):
            old_screen = self.screen_manager.get_screen('test')
            self.screen_manager.remove_widget(old_screen)
        
        self.optimized_test_screen = OptimizedTestScreen(name='test')
        self.screen_manager.add_widget(self.optimized_test_screen)
        self.optimized_test_screen.update_content()
        self.screen_manager.current = 'test'

    def apply_theme_changes(self):
        """Немедленное применение изменений темы"""
        Window.clearcolor = self.bg_color
        if not hasattr(self, 'screen_manager') or self.screen_manager is None:
            return
        if hasattr(self, 'main_screen'):
            self.build_main_screen()
        if hasattr(self, 'color_settings_screen'):
            self.color_settings_screen.update_color_settings()
        if hasattr(self, 'optimized_test_screen') and self.screen_manager.current == 'test':
            self.optimized_test_screen.update_content()
    
    def create_setting_card(self, title, settings_list):
        """Создает карточку настройки с заголовком и списком параметров"""
        card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), padding=dp(16))
        with card.canvas.before:
            Color(rgba=self.card_color)
            RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(8)])
        title_label = AndroidLabel(
            text=f'[b]{title}[/b]',
            font_size=self.get_font_size(18),
            size_hint=(1, 0.4),
            color=self.text_primary
        )
        card.add_widget(title_label)
        settings_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6))
        
        for setting_name, setting_type, initial_value, handler in settings_list:
            if setting_type == 'switch':
                switch_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1))
                switch_layout.add_widget(AndroidLabel(
                    text=setting_name, 
                    color=self.text_primary
                ))
                
                switch = Switch(active=initial_value)
                switch.bind(active=handler)
                switch_layout.add_widget(switch)
                
                settings_layout.add_widget(switch_layout)
        
        card.add_widget(settings_layout)
        return card  

    def load_custom_colors(self):
        """Загрузка кастомных цветов"""
        if 'custom_colors' in self.settings_store:
            saved_colors = self.settings_store.get('custom_colors')
            for color_name, color_value in saved_colors.items():
                if hasattr(self, color_name):
                    setattr(self, color_name, color_value)
                    self.custom_colors[color_name] = color_value
        
    def save_custom_colors(self):
        """Сохранение кастомных цветов"""
        saveable_colors = {}
        color_properties = [
            'bg_color', 'card_color', 'text_primary',
            'primary_color', 'correct_color', 'error_color'
        ]
        
        for color_name in color_properties:
            color_value = getattr(self, color_name)
            if hasattr(color_value, 'rgba'):
                saveable_colors[color_name] = color_value.rgba
            else:
                saveable_colors[color_name] = color_value
        
        self.settings_store.put('custom_colors', **saveable_colors)
        self.apply_theme_changes()
    
    def reset_custom_colors(self):
        """Сброс кастомных цветов"""
        self.custom_colors = {}
        self.settings_store.put('custom_colors', **{})
        self.update_theme()
    


    def update_theme(self):
        """Обновление цветов темы - УЛУЧШЕННАЯ ВЕРСИЯ"""
        if self.active_preset:
            theme = 'dark' if self.is_dark_theme else 'light'
            
            # ПРОВЕРЯЕМ СТАНДАРТНЫЕ ПРЕСЕТЫ
            if (not self.colors_modified and 
                self.active_preset in self.color_presets and 
                theme in self.color_presets[self.active_preset]):
                
                preset_colors = self.color_presets[self.active_preset][theme]
                for color_property, color_value in preset_colors.items():
                    setattr(self, color_property, color_value)
                    self.custom_colors[color_property] = color_value
                    
            # ПРОВЕРЯЕМ КАСТОМНЫЕ ПРЕСЕТЫ
            elif (self.colors_modified and 
                hasattr(self, 'color_settings_screen') and
                self.active_preset in self.color_settings_screen.custom_presets):
                
                preset_data = self.color_settings_screen.custom_presets[self.active_preset]
                theme_colors = preset_data.get(theme, preset_data.get('light', {}))
                
                for color_property, color_value in theme_colors.items():
                    if hasattr(self, color_property):
                        setattr(self, color_property, color_value)
                        self.custom_colors[color_property] = color_value
                        
            else:
                print(f"Невалидный пресет: {self.active_preset}, сбрасываем на green_soft")
                self.active_preset = 'green_soft'
                self.colors_modified = False
                self.save_active_preset()
                Clock.schedule_once(lambda dt: self.update_theme(), 0.1)
                return
        else:
            if self.is_dark_theme:
                base_bg = self.dark_bg
                base_card = self.dark_card
                base_text_primary = self.dark_text_primary
                base_text_secondary = self.dark_text_secondary
                base_primary = self.dark_primary
                base_correct = self.dark_correct
                base_error = self.dark_error
            else:
                base_bg = self.light_bg
                base_card = self.light_card
                base_text_primary = self.light_text_primary
                base_text_secondary = self.light_text_secondary
                base_primary = self.light_primary
                base_correct = self.light_correct
                base_error = self.light_error

            self.bg_color = self.custom_colors.get('bg_color', base_bg)
            self.card_color = self.custom_colors.get('card_color', base_card)
            self.text_primary = self.custom_colors.get('text_primary', base_text_primary)
            self.text_secondary = self.custom_colors.get('text_secondary', base_text_secondary)
            self.primary_color = self.custom_colors.get('primary_color', base_primary)
            self.correct_color = self.custom_colors.get('correct_color', base_correct)
            self.error_color = self.custom_colors.get('error_color', base_error)
        
        Window.clearcolor = self.bg_color
        
        # ДОБАВЛЯЕМ ПРОВЕРКУ НА СУЩЕСТВОВАНИЕ screen_manager
        if not hasattr(self, 'screen_manager') or self.screen_manager is None:
            return
        
        # ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ ВСЕХ ЭКРАНОВ
        self._force_update_all_screens()
        
    def _force_update_all_screens(self):
        """Принудительное обновление всех экранов"""
        try:
            # Главный экран
            if hasattr(self, 'main_screen'):
                self.build_main_screen()
            
            # Экран тестирования
            if hasattr(self, 'optimized_test_screen'):
                if hasattr(self.optimized_test_screen, 'update_content'):
                    self.optimized_test_screen.update_content()
            
            # Экран результатов
            if hasattr(self, 'results_screen') and hasattr(self.results_screen, 'build_ui'):
                self.results_screen.build_ui()
            
            # Экран неправильных ответов
            if hasattr(self, 'wrong_answers_screen') and hasattr(self.wrong_answers_screen, 'build_ui'):
                self.wrong_answers_screen.build_ui()
            
            # Экран настроек цвета
            if hasattr(self, 'color_settings_screen') and hasattr(self.color_settings_screen, 'build_ui'):
                self.color_settings_screen.build_ui()
            
            # Экран статистики
            if hasattr(self, 'statistics_screen') and hasattr(self.statistics_screen, 'build_ui'):
                self.statistics_screen.build_ui()
            
            # Экран повторения ошибок
            if hasattr(self, 'repeat_screen') and hasattr(self.repeat_screen, 'build_ui'):
                self.repeat_screen.build_ui()
            
            # Экран настроек GigaChat
            if hasattr(self, 'gigachat_settings_screen') and hasattr(self.gigachat_settings_screen, 'build_ui'):
                self.gigachat_settings_screen.build_ui()
                
        except Exception as e:
            print(f"Ошибка при обновлении экранов: {e}")



    def migrate_old_custom_presets(self):
        """Миграция старых кастомных пресетов в новую структуру"""
        if 'custom_presets' in self.settings_store:
            old_presets = self.settings_store.get('custom_presets')
            migrated = False
            
            for preset_name, preset_data in old_presets.items():
                # Если пресет в старом формате (без разделения на темы)
                if 'light' not in preset_data and 'dark' not in preset_data:
                    # Мигрируем в новый формат
                    old_presets[preset_name] = {
                        'light': {
                            'bg_color': preset_data.get('bg_color', [0.95, 0.98, 0.95, 1]),
                            'card_color': preset_data.get('card_color', [1, 1, 1, 1]),
                            'text_primary': preset_data.get('text_primary', [0.07, 0.35, 0.07, 1]),
                            'text_secondary': preset_data.get('text_secondary', [0.3, 0.5, 0.3, 1]),
                            'primary_color': preset_data.get('primary_color', [0.18, 0.63, 0.18, 1]),
                            'correct_color': preset_data.get('correct_color', [0.21, 0.76, 0.21, 1]),
                            'error_color': preset_data.get('error_color', [0.86, 0.26, 0.21, 1])
                        },
                        'dark': {
                            'bg_color': [c * 0.3 for c in preset_data.get('bg_color', [0.95, 0.98, 0.95, 1])[:3]] + [1],
                            'card_color': [c * 0.4 for c in preset_data.get('card_color', [1, 1, 1, 1])[:3]] + [1],
                            'text_primary': [min(1, c + 0.6) for c in preset_data.get('text_primary', [0.07, 0.35, 0.07, 1])[:3]] + [1],
                            'text_secondary': [min(1, c + 0.4) for c in preset_data.get('text_secondary', [0.3, 0.5, 0.3, 1])[:3]] + [1],
                            'primary_color': preset_data.get('primary_color', [0.18, 0.63, 0.18, 1]),
                            'correct_color': preset_data.get('correct_color', [0.21, 0.76, 0.21, 1]),
                            'error_color': preset_data.get('error_color', [0.86, 0.26, 0.21, 1])
                        },
                        'is_custom': preset_data.get('is_custom', True),
                        'slot_index': preset_data.get('slot_index', 0)
                    }
                    migrated = True
            
            if migrated:
                self.settings_store.put('custom_presets', **old_presets)


    def update_disabled_buttons_color(self):
        """Обновляет цвет текста у всех заблокированных кнопок в приложении"""
        if not hasattr(self, 'screen_manager') or self.screen_manager is None:
            return
        for screen_name in self.screen_manager.screen_names:
            screen = self.screen_manager.get_screen(screen_name)
            self._update_buttons_in_widget(screen)
        if hasattr(self, 'optimized_test_screen'):
            self._update_buttons_in_widget(self.optimized_test_screen)

    def _update_buttons_in_widget(self, widget):
        """Рекурсивно обновляет цвет текста у заблокированных кнопок в виджете"""
        if hasattr(widget, 'children'):
            for child in widget.children:
                if isinstance(child, AndroidButton) and child.disabled:
                    if self.is_dark_theme:
                        child.disabled_color = (1, 1, 1, 1)
                    else:
                        child.disabled_color = (0, 0, 0, 1)
                self._update_buttons_in_widget(child) 

    def force_portrait_orientation(self):
        """Принудительная установка портретной ориентации"""
        # Для Android
        if platform == 'android':
            try:
                from jnius import autoclass
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                # 1 = SCREEN_ORIENTATION_PORTRAIT
                activity.setRequestedOrientation(1)
                print("Ориентация заблокирована в портретном режиме")
            except Exception as e:
                print(f"Ошибка блокировки ориентации: {e}")
        
        # Для iOS (если нужно)
        elif platform == 'ios':
            try:
                from pyobjus import autoclass
                UIDevice = autoclass('UIDevice')
                # На iOS сложнее, но можно попробовать
                print("iOS: Рекомендуется настроить ориентацию в buildozer.spec")
            except:
                pass
        
        # Для ПК - настраиваем размер окна
        else:
            from kivy.core.window import Window
            Window.size = (360, 800)
            Window.minimum_width = 360
            Window.minimum_height = 640


    def build(self):

        # Блокируем ориентацию при запуске
        self.force_portrait_orientation()

        self.screen_manager = ScreenManager(transition=SlideTransition())
        self.splash_screen = SplashScreen(name='splash')
        self.screen_manager.add_widget(self.splash_screen)
    
        
        # ТЕПЕРЬ ЗАГРУЖАЕМ НАСТРОЙКИ ПОСЛЕ СОЗДАНИЯ screen_manager
        self.load_settings()
        self.load_custom_colors()
        self.load_gigachat_settings()
        self.load_font_settings()
        self.migrate_old_custom_presets()

        # СОЗДАЕМ ОСНОВНЫЕ ЭКРАНЫ
        self.main_screen = MainScreen(name='main')
        self.test_screen = OptimizedTestScreen(name='test')
        self.results_screen = ResultsScreen(name='results')

        # ДОБАВЛЯЕМ ВСЕ ВОЗМОЖНЫЕ ЭКРАНЫ
        self.wrong_answers_screen = WrongAnswersScreen(name='wrong_answers')
        self.color_settings_screen = ColorSettingsScreen(name='color_settings')
        self.statistics_screen = StatisticsScreen(name='statistics')
        self.repeat_screen = RepeatWrongAnswersScreen(name='repeat')
        self.gigachat_settings_screen = GigaChatSettingsScreen(name='gigachat_settings')

        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.test_screen)
        self.screen_manager.add_widget(self.results_screen)
        self.screen_manager.add_widget(self.wrong_answers_screen)
        self.screen_manager.add_widget(self.color_settings_screen)
        self.screen_manager.add_widget(self.statistics_screen)
        self.screen_manager.add_widget(self.repeat_screen)
        self.screen_manager.add_widget(self.gigachat_settings_screen)
        
        self.build_main_screen()
        self.screen_manager.current = 'splash'
        
        # ПРИМЕНЯЕМ ТЕМУ ПОСЛЕ СОЗДАНИЯ ВСЕХ ЭКРАНОВ
        self.update_theme()

        Window.bind(on_keyboard=self.on_keyboard)
        
        return self.screen_manager


    def open_gigachat_settings(self, instance):
        """Открывает экран настроек GigaChat с мгновенным обновлением"""
        if not hasattr(self, 'gigachat_settings_screen'):
            self.gigachat_settings_screen = GigaChatSettingsScreen(name='gigachat_settings')
            self.screen_manager.add_widget(self.gigachat_settings_screen)
        else:
            Clock.schedule_once(lambda dt: self.gigachat_settings_screen.build_ui(), 0.05)
        
        self.screen_manager.current = 'gigachat_settings'


    def build_main_screen(self):
        self.main_screen.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=dp(8), spacing=dp(6))
        top_half = BoxLayout(orientation='vertical', size_hint=(1, 0.30), spacing=dp(6))
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=dp(5))
        
        title_label = AndroidLabel(
            text='[b]Ассистент 2.0[/b]',
            font_size=self.get_font_size(20),
            color=self.text_primary,
            size_hint_x=0.6
        )
        control_layout = BoxLayout(orientation='horizontal', size_hint_x=0.4, spacing=dp(3))
        
        theme_btn = AndroidButton(
            text='День' if not self.is_dark_theme else 'Ночь',
            size_hint_x=0.33,
            background_color=self.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(12)
        )
        theme_btn.bind(on_press=self.toggle_theme)
        
        settings_btn = AndroidButton(
            text='Цвета',
            size_hint_x=0.33,
            background_color=self.card_color,
            color=self.text_primary,
            font_size=self.get_font_size(12)
        )
        settings_btn.bind(on_press=self.open_color_settings)
        gigachat_btn = AndroidButton(
            text='ИИ',
            size_hint_x=0.34,
            background_color=[0.1, 0.5, 0.3, 1] if self.gigachat_enabled else [0.5, 0.5, 0.5, 1],
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(12)
        )
        gigachat_btn.bind(on_press=self.open_gigachat_settings)
        
        control_layout.add_widget(theme_btn)
        control_layout.add_widget(settings_btn)
        control_layout.add_widget(gigachat_btn)
        
        header_layout.add_widget(title_label)
        header_layout.add_widget(control_layout)
        top_half.add_widget(header_layout)
        settings_header = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=dp(3))
        
        settings_title = AndroidLabel(
            text='[b]Настройки тестирования[/b]',
            font_size=self.get_font_size(16),
            color=self.text_primary,
            size_hint_x=1,
            halign='left'
        )
        
        settings_header.add_widget(settings_title)
        top_half.add_widget(settings_header)
        settings_card_container = BoxLayout(
            orientation='vertical', 
            size_hint=(1, 0.77),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        with settings_card_container.canvas.before:
            Color(rgba=[0.8, 0.8, 0.8, 1])
            settings_card_container.border_rect = RoundedRectangle(
                pos=settings_card_container.pos,
                size=settings_card_container.size,
                radius=[dp(6)]
            )
            Color(rgba=self.card_color)
            settings_card_container.bg_rect = RoundedRectangle(
                pos=[settings_card_container.pos[0] + dp(1), settings_card_container.pos[1] + dp(1)],
                size=[settings_card_container.size[0] - dp(2), settings_card_container.size[1] - dp(2)],
                radius=[dp(5)]
            )
        settings_card = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(4))
        settings_content = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(6))
        checks_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.4), spacing=dp(6))
        shuffle_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5), spacing=dp(5))
        shuffle_label = AndroidLabel(
            text='Перемешивать вопросы',
            color=self.text_primary,
            font_size=self.get_font_size(13),
            size_hint_x=0.7
        )
        shuffle_check = CheckBox(
            active=self.shuffle_questions,
            size_hint_x=0.3,
            color=[1, 1, 1, 1] if self.is_dark_theme else [0, 0,0, 1]
        )
        shuffle_check.bind(active=self.on_shuffle_questions_change)
        shuffle_layout.add_widget(shuffle_label)
        shuffle_layout.add_widget(shuffle_check)
        shuffle_answers_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5), spacing=dp(5))
        shuffle_answers_label = AndroidLabel(
            text='Перемешивать ответы',
            color=self.text_primary,
            font_size=self.get_font_size(13),
            size_hint_x=0.7
        )
        shuffle_answers_check = CheckBox(
            active=self.shuffle_answers,
            size_hint_x=0.3,
            color=[1, 1, 1, 1] if self.is_dark_theme else [0, 0,0, 1]
        )
        shuffle_answers_check.bind(active=self.on_shuffle_answers_change)
        shuffle_answers_layout.add_widget(shuffle_answers_label)
        shuffle_answers_layout.add_widget(shuffle_answers_check)
        
        checks_layout.add_widget(shuffle_layout)
        checks_layout.add_widget(shuffle_answers_layout)
        settings_content.add_widget(checks_layout)
        questions_settings_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.6), spacing=dp(4))
        self.questions_extra_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1), spacing=dp(4))
        self.update_questions_extra_settings()
        questions_settings_layout.add_widget(self.questions_extra_layout)
        
        settings_content.add_widget(questions_settings_layout)
        settings_card.add_widget(settings_content)
        settings_card_container.add_widget(settings_card)
        top_half.add_widget(settings_card_container)
        settings_card_container.bind(
            pos=self._update_settings_card_bg,
            size=self._update_settings_card_bg
        )
        
        main_layout.add_widget(top_half)
        middle_section = BoxLayout(orientation='vertical', size_hint=(1, 0.592), spacing=dp(6))
        tests_header = BoxLayout(orientation='horizontal', size_hint=(1, 0.08), spacing=dp(3))
        
        tests_label = AndroidLabel(
            text='[b]Доступные тесты[/b]',
            font_size=self.get_font_size(16),
            color=self.text_primary,
            size_hint_x=0.55
        )
        load_btn = AndroidButton(
            text='Загрузить тест',
            size_hint_x=0.5,
            background_color=self.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(14)
        )
        load_btn.bind(on_press=self.load_test_file)
        
        tests_header.add_widget(tests_label)
        tests_header.add_widget(load_btn)

        spacer = BoxLayout(size_hint_y=None, height=dp(5))
        middle_section.add_widget(spacer)
        middle_section.add_widget(tests_header)
        tests_frame = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.92),
            padding=[dp(2), dp(2), dp(2), dp(2)]
        )
        with tests_frame.canvas.before:
            Color(rgba=[0.8, 0.8, 0.8, 1])
            tests_frame.border_rect = RoundedRectangle(
                pos=tests_frame.pos,
                size=tests_frame.size,
                radius=[dp(6)]
            )
            Color(rgba=self.bg_color)
            tests_frame.bg_rect = RoundedRectangle(
                pos=[tests_frame.pos[0] + dp(1), tests_frame.pos[1] + dp(1)],
                size=[tests_frame.size[0] - dp(2), tests_frame.size[1] - dp(2)],
                radius=[dp(5)]
            )
        scroll_view = ScrollView(size_hint=(1, 1))
        self.tests_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(1))
        self.tests_layout.bind(minimum_height=self.tests_layout.setter('height'))
        
        self.load_tests_list()
        
        scroll_view.add_widget(self.tests_layout)
        tests_frame.add_widget(scroll_view)
        tests_frame.bind(
            pos=self._update_tests_frame,
            size=self._update_tests_frame
        )
        
        middle_section.add_widget(tests_frame)
        main_layout.add_widget(middle_section)
        bottom_section = BoxLayout(orientation='horizontal', size_hint=(1, 0.065), spacing=dp(3))
        
        repeat_btn = AndroidButton(
            text='Повтор ошибок',
            size_hint_x=0.5,
            background_color=self.error_color,
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(14)
        )
        repeat_btn.bind(on_press=self.open_repeat_screen)
        
        stats_btn = AndroidButton(
            text='Статистика',
            size_hint_x=0.5,
            background_color=self.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.get_font_size(14)
        )
        stats_btn.bind(on_press=self.open_statistics_screen)
        
        bottom_section.add_widget(repeat_btn)
        bottom_section.add_widget(stats_btn)
        main_layout.add_widget(bottom_section)
        
        self.main_screen.add_widget(main_layout)


    def _update_tests_frame(self, instance, value):
        """Обновление рамки области тестов"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=[0.8, 0.8, 0.8, 1])
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(6)]
            )
            Color(rgba=self.bg_color)
            RoundedRectangle(
                pos=[instance.pos[0] + dp(1), instance.pos[1] + dp(1)],
                size=[instance.size[0] - dp(2), instance.size[1] - dp(2)],
                radius=[dp(5)]
            )


    def _update_settings_card_bg(self, instance, value):
        """Обновление фона карточки настроек при изменении размера"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=[0.8, 0.8, 0.8, 1])
            RoundedRectangle(
                pos=instance.pos,
                size=instance.size,
                radius=[dp(6)]
            )
            Color(rgba=self.card_color)
            RoundedRectangle(
                pos=[instance.pos[0] + dp(1), instance.pos[1] + dp(1)],
                size=[instance.size[0] - dp(2), instance.size[1] - dp(2)],
                radius=[dp(5)]
            )

    def set_questions_mode(self, mode):
        """Установка режима вопросов с обновлением UI"""
        self.questions_mode = mode
        self.save_settings()
        if hasattr(self, 'main_screen'):
            self.build_main_screen()


    def update_questions_extra_settings(self):
        """Обновление дополнительных настроек вопросов - С СЕГМЕНТИРОВАННЫМИ КНОПКАМИ"""
        self.questions_extra_layout.clear_widgets()
        self.questions_extra_layout.orientation = 'vertical'
        self.questions_extra_layout.spacing = dp(4)
        mode_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.5), spacing=dp(4))
        self.all_questions_btn = AndroidButton(
            text='Все вопросы',
            size_hint_x=0.5,
            background_color=self.primary_color if self.questions_mode == 'all' else self.card_color,
            color=(1, 1, 1, 1) if self.questions_mode == 'all' else self.text_primary,
            font_size=self.get_font_size(13)
        )
        self.all_questions_btn.bind(on_press=lambda x: self.set_questions_mode('all'))
        self.range_questions_btn = AndroidButton(
            text='Диапазон',
            size_hint_x=0.5,
            background_color=self.primary_color if self.questions_mode == 'range' else self.card_color,
            color=(1, 1, 1, 1) if self.questions_mode == 'range' else self.text_primary,
            font_size=self.get_font_size(13)
        )
        self.range_questions_btn.bind(on_press=lambda x: self.set_questions_mode('range'))
        
        mode_layout.add_widget(self.all_questions_btn)
        mode_layout.add_widget(self.range_questions_btn)
        self.questions_extra_layout.add_widget(mode_layout)
        content_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.6))
        
        if self.questions_mode == 'range':
            range_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.8), spacing=dp(8))
            if self.is_dark_theme:
                input_bg_color = [0.3, 0.3, 0.3, 1]
                input_text_color = [1, 1, 1, 1]
                border_color = [0.5, 0.5, 0.5, 1]
            else:
                input_bg_color = [0.95, 0.95, 0.95, 1]
                input_text_color = [0, 0, 0, 1]
                border_color = [0.7, 0.7, 0.7, 1]
            from_layout = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(2))

            from_container = BoxLayout(
                orientation='vertical',
                size_hint_y=0.8,
                padding=[dp(1), dp(1)]
            )
            
            self.from_input = TextInput(
                text=str(self.questions_start),
                size_hint=(1, 1),
                multiline=False,
                background_color=input_bg_color,
                foreground_color=input_text_color,
                hint_text='1',
                padding=dp(6),
                background_normal='',
                background_active='',
                font_size=self.get_font_size(20),
                halign='center',
                write_tab=False,
                cursor_color=input_text_color
            )
            
            with from_container.canvas.before:
                Color(rgba=border_color)
                from_container.border_rect = RoundedRectangle(
                    pos=from_container.pos,
                    size=from_container.size,
                    radius=[dp(3)]
                )
            
            self.from_input.bind(text=self.on_questions_start_change)
            from_container.add_widget(self.from_input)
            from_container.bind(pos=self._update_input_border, size=self._update_input_border)
            
            from_layout.add_widget(from_container)
            dash_container = BoxLayout(orientation='horizontal', size_hint_x=0.2)
            dash_label = AndroidLabel(
                text='—>',
                color=self.text_primary,
                font_size=self.get_font_size(14),
                halign='center',
                valign='middle'
            )
            dash_container.add_widget(dash_label)
            to_layout = BoxLayout(orientation='vertical', size_hint_x=0.4, spacing=dp(2))
            
            to_container = BoxLayout(
                orientation='vertical',
                size_hint_y=0.8,
                padding=[dp(1), dp(1)]
            )
            
            self.to_input = TextInput(
                text=str(self.questions_end),
                size_hint=(1, 1),
                multiline=False,
                background_color=input_bg_color,
                foreground_color=input_text_color,
                hint_text='30',
                padding=dp(6),
                background_normal='',
                background_active='',
                font_size=self.get_font_size(20),
                halign='center',
                write_tab=False,
                cursor_color=input_text_color
            )
            
            with to_container.canvas.before:
                Color(rgba=border_color)
                to_container.border_rect = RoundedRectangle(
                    pos=to_container.pos,
                    size=to_container.size,
                    radius=[dp(3)]
                )
            
            self.to_input.bind(text=self.on_questions_end_change)
            to_container.add_widget(self.to_input)
            to_container.bind(pos=self._update_input_border, size=self._update_input_border)
            
            to_layout.add_widget(to_container)
            
            range_layout.add_widget(from_layout)
            range_layout.add_widget(dash_container)
            range_layout.add_widget(to_layout)
            content_layout.add_widget(range_layout)
            
        else:
            hint_layout = BoxLayout(orientation='horizontal', size_hint=(1, 1))
            hint_label = AndroidLabel(
                text='Будут прорешаны все вопросы теста',
                color=self.text_secondary,
                font_size=self.get_font_size(13),
                halign='center'
            )
            hint_layout.add_widget(hint_label)
            content_layout.add_widget(hint_layout)
        
        self.questions_extra_layout.add_widget(content_layout)

    def _update_input_border(self, instance, value):
        """Обновление обводки полей ввода"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'border_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                if self.is_dark_theme:
                    border_color = [0.5, 0.5, 0.5, 1]
                else:
                    border_color = [0.7, 0.7, 0.7, 1]
                
                Color(rgba=border_color)
                instance.border_rect = RoundedRectangle(
                    pos=instance.pos,
                    size=instance.size,
                    radius=[dp(4)]
                )

    def on_questions_count_change(self, spinner, text):
        """Обработчик изменения количества вопросов"""
        try:
            self.questions_count = int(text)
            self.save_settings()
        except ValueError:
            pass

    def on_questions_start_change(self, instance, text):
        """Обработчик изменения начального вопроса"""
        try:
            self.questions_start = int(text)
            self.save_settings()
        except ValueError:
            pass

    def on_questions_end_change(self, instance, text):
        """Обработчик изменения конечного вопроса"""
        try:
            self.questions_end = int(text)
            self.save_settings()
        except ValueError:
            pass
    
    def load_tests_list(self):
        """Загрузка списка тестов (оригинальная версия)"""
        self.tests_layout.clear_widgets()
        
        if 'tests' in self.test_store:
            tests_data = self.test_store.get('tests')
            for test_name, test_data in tests_data.items():
                test_card_container = BoxLayout(
                    orientation='vertical',
                    size_hint=(1, None),
                    height=dp(140),
                    padding=[dp(8), dp(8), dp(8), dp(8)]
                )
                
                test_card = BoxLayout(
                    orientation='vertical', 
                    size_hint=(1, 1),
                    padding=dp(12),
                    spacing=dp(6)
                )
                
                with test_card_container.canvas.before:
                    Color(rgba=self.card_color)
                    test_card_container.bg_rect = RoundedRectangle(
                        pos=test_card_container.pos, 
                        size=test_card_container.size, 
                        radius=[dp(10)]
                    )
                    Color(rgba=[c * 0.8 for c in self.card_color[:3]] + [1])
                    Line(
                        rounded_rectangle=(
                            test_card_container.pos[0], test_card_container.pos[1], 
                            test_card_container.size[0], test_card_container.size[1], 
                            dp(10)
                        ),
                        width=dp(1.2)
                    )
                    
                test_info = BoxLayout(orientation='vertical', size_hint=(1, 0.7))
                test_name_label = AndroidLabel(
                    text=f'{test_name}',
                    font_size=self.get_font_size(14),
                    color=self.text_primary,
                    size_hint_y=0.6,
                    text_size=(None, None),
                    halign='left'
                )
                
                total_questions = len(test_data['questions'])
                total_label = AndroidLabel(
                    text=f'Вопросов: {total_questions}',
                    font_size=self.get_font_size(13),
                    color=self.text_secondary,
                    size_hint_y=0.4
                )
                
                test_info.add_widget(test_name_label)
                test_info.add_widget(total_label)
                test_card.add_widget(test_info)
                btn_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.3), spacing=dp(8))
                
                start_btn = AndroidButton(
                    text='Начать',
                    background_color=self.primary_color,
                    color=(1, 1, 1, 1),
                    font_size=self.get_font_size(13),
                )
                start_btn.bind(on_press=lambda x, name=test_name: self.start_test(name))
                
                delete_btn = AndroidButton(
                    text='️Удалить',
                    background_color=self.error_color,
                    color=(1, 1, 1, 1),
                    font_size=self.get_font_size(13),
                )
                delete_btn.bind(on_press=lambda x, name=test_name: self.delete_test(name))
                
                btn_layout.add_widget(start_btn)
                btn_layout.add_widget(delete_btn)
                test_card.add_widget(btn_layout)
                
                test_card_container.add_widget(test_card)
                self.tests_layout.add_widget(test_card_container)
                
                test_card_container.bind(
                    pos=self._update_test_card_rect,
                    size=self._update_test_card_rect
                )
        else:
            no_tests_label = AndroidLabel(
                text='',
                color=self.text_secondary,
                font_size=self.get_font_size(16),
                halign='center'
            )
            self.tests_layout.add_widget(no_tests_label)
        
        # Обновляем навигацию в главном меню
        if hasattr(self, 'main_screen'):
            Clock.schedule_once(lambda dt: self.main_screen._update_test_cards_list(), 0.1)


    def _update_test_card_rect(self, instance, value):
        """Обновление фона карточки теста"""
        if hasattr(instance, 'canvas'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.card_color)
                RoundedRectangle(
                    pos=instance.pos, 
                    size=instance.size, 
                    radius=[dp(10)]
                )
                Color(rgba=[c * 0.8 for c in self.card_color[:3]] + [1])
                Line(
                    rounded_rectangle=(
                        instance.pos[0], instance.pos[1], 
                        instance.size[0], instance.size[1], 
                        dp(10)
                    ),
                    width=dp(1.2)
                )
    
    def build_test_screen(self):
        self.test_screen.clear_widgets()
        
        if not self.current_questions:
            return
            
        main_layout = BoxLayout(orientation='vertical', padding=dp(16), spacing=dp(16))
        header_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.25), spacing=dp(8))
        
        test_name_label = AndroidLabel(
            text=f'[b]📖 {self.current_test}[/b]',
            font_size=self.get_font_size(20),
            color=self.text_primary,
            size_hint=(1, 0.3)
        )
        
        progress_text = f'Вопрос {self.current_question_index + 1} из {len(self.current_questions)}'
        progress_label = AndroidLabel(
            text=progress_text,
            font_size=self.get_font_size(16),
            color=self.text_primary,
            size_hint=(1, 0.2)
        )
        
        stats_text = f'Правильных: {self.correct_answers}   Неправильных: {self.incorrect_answers}'
        stats_label = AndroidLabel(
            text=stats_text,
            font_size=self.get_font_size(16),
            color=self.text_primary,
            size_hint=(1, 0.2)
        )
        
        header_layout.add_widget(test_name_label)
        header_layout.add_widget(progress_label)
        header_layout.add_widget(stats_label)
        nav_layout = BoxLayout(orientation='vertical', size_hint=(1, 1.15))
        nav_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=True,
            do_scroll_y=False,
            scroll_type=['bars', 'content']
        )
        buttons_layout = GridLayout(
            cols=len(self.current_questions),
            rows=1,
            size_hint_x=None,
            height=dp(40),
            spacing=dp(5)
        )
        buttons_layout.bind(minimum_width=buttons_layout.setter('width'))
        buttons_layout.width = len(self.current_questions) * (dp(40) + dp(5))
        for i in range(len(self.current_questions)):
            btn_color = self.get_question_button_color(i)
            question_btn = AndroidButton(
                text=str(i+1),
                size_hint_x=None,
                width=dp(40),
                height=dp(40),
                background_color=btn_color,
                color=(1, 1, 1, 1) if btn_color != self.card_color else self.text_primary
            )
            question_btn.bind(on_press=lambda instance, idx=i: self.go_to_question(idx))
            buttons_layout.add_widget(question_btn)
        
        nav_scroll.add_widget(buttons_layout)
        nav_layout.add_widget(nav_scroll)
        header_layout.add_widget(nav_layout)
        exit_btn = AndroidButton(
            text='В меню',
            size_hint=(1, 1.0),
            background_color=self.card_color,
            color=self.text_primary
        )
        exit_btn.bind(on_press=self.return_to_menu)
        header_layout.add_widget(exit_btn)
        
        main_layout.add_widget(header_layout)
        question_area = BoxLayout(orientation='vertical', size_hint=(1, 0.75), spacing=dp(16))
        
        current_question = self.current_questions[self.current_question_index]
        question_label = AndroidLabel(
            text=current_question.text,
            font_size=self.get_font_size(18),
            text_size=(Window.width - dp(32), None),
            color=self.text_primary,
            size_hint=(1, 0.2)
        )
        question_area.add_widget(question_label)
        answers_scroll = ScrollView(size_hint=(1, 0.8))
        answers_layout = GridLayout(cols=1, size_hint_y=None, spacing=dp(10))
        answers_layout.bind(minimum_height=answers_layout.setter('height'))
        
        is_checked = self.question_checked[self.current_question_index]
        saved_answer = self.user_answers[self.current_question_index]
        
        for i, answer in enumerate(current_question.answers):
            btn_color, text_color = self.get_answer_button_color(i, is_checked, saved_answer, current_question.correct_indices)
            
            answer_btn = AndroidButton(
                text=answer,
                size_hint_y=None,
                height=dp(80),
                background_color=btn_color,
                color=text_color
            )
            answer_btn.bind(on_press=lambda x, idx=i: self.select_answer(idx))
            answers_layout.add_widget(answer_btn)
        
        answers_scroll.add_widget(answers_layout)
        question_area.add_widget(answers_scroll)
        
        main_layout.add_widget(question_area)
        bottom_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=dp(10))
        if self.current_question_index > 0:
            back_btn = AndroidButton(
                text='Назад',
                background_color=self.card_color,
                color=self.text_primary
            )
            back_btn.bind(on_press=lambda x: self.previous_question())
            bottom_layout.add_widget(back_btn)
        else:
            bottom_layout.add_widget(BoxLayout(size_hint_x=0.3))
        action_btn_text = self.get_action_button_text()
        action_btn = AndroidButton(
            text=action_btn_text,
            background_color=self.primary_color,
            color=(1, 1, 1, 1)
        )
        action_btn.bind(on_press=self.action_button_click)
        bottom_layout.add_widget(action_btn)
        
        main_layout.add_widget(bottom_layout)
        
        self.test_screen.add_widget(main_layout)
    
    def open_color_settings(self, instance):
        """Открывает экран настроек цветов"""
        # Проверяем, существует ли уже экран
        if not self.screen_manager.has_screen('color_settings'):
            # Если нет - создаем и добавляем
            self.color_settings_screen = ColorSettingsScreen(name='color_settings')
            self.screen_manager.add_widget(self.color_settings_screen)
        else:
            # Если существует - обновляем ссылку
            self.color_settings_screen = self.screen_manager.get_screen('color_settings')
        
        self.screen_manager.current = 'color_settings'
        
        self.screen_manager.current = 'color_settings'
        
    def get_question_button_color(self, question_index):
        """Возвращает цвет кнопки вопроса в зависимости от статуса"""
        if question_index == self.current_question_index:
            return [0.6, 0.6, 0.6, 1], (0, 0, 0, 1)
        
        if self.question_checked[question_index]:
            if self.question_results[question_index]:
                return self.correct_color, (0, 0, 0, 1)
            else:
                return self.error_color, (0, 0, 0, 1)
        elif self.user_answers[question_index] is not None:
            return self.primary_color, (1, 1, 1, 1)
        else:
            return [0.8, 0.8, 0.8, 1], (0, 0, 0, 1)
    
    def get_answer_button_color(self, answer_index, is_checked, saved_answer, correct_indices):
        """Возвращает цвет кнопки ответа и цвет текста"""
        if is_checked:
            if answer_index in correct_indices:
                return self.correct_color, (1, 1, 1, 1)
            elif saved_answer and answer_index in saved_answer:
                return self.error_color, (1, 1, 1, 1)
            else:
                return self.card_color, self.text_primary
        elif saved_answer and answer_index in saved_answer:
            return self.primary_color, (1, 1, 1, 1)
        return self.card_color, self.text_primary
    
    def get_action_button_text(self):
        """Возвращает текст кнопки действия"""
        if not self.question_checked[self.current_question_index]:
            return "Проверить"
        elif self.current_question_index < len(self.current_questions) - 1:
            return "Далее"
        else:
            return "Завершить"
    
    def toggle_theme(self, instance):
        """Переключение темы"""
        self.is_dark_theme = not self.is_dark_theme
        self.save_settings()
        self.save_active_preset()  # Сохраняем активный пресет с новой темой
        
        # ПРИМЕНЯЕМ АКТИВНЫЙ ПРЕСЕТ С НОВОЙ ТЕМОЙ
        if self.active_preset:
            self.apply_color_preset(self.active_preset)
        else:
            self.update_theme()
        
        # Обновляем кнопку только если instance передан и существует
        if instance and hasattr(instance, 'text'):
            instance.text = 'День' if not self.is_dark_theme else 'Ночь'
        
        # ДОПОЛНИТЕЛЬНОЕ ОБНОВЛЕНИЕ С ЗАДЕРЖКОЙ ДЛЯ УБЕДИТЕЛЬНОСТИ
        Clock.schedule_once(lambda dt: self._force_update_all_screens(), 0.1)
    
    def on_theme_switch(self, instance, value):
        """Обработчик переключателя темы"""
        self.is_dark_theme = value
        self.save_settings()
        self.update_theme()
        if hasattr(self, 'questions_extra_layout'):
            self.update_questions_extra_settings()
    
    def on_shuffle_questions_change(self, instance, value):
        """Обработчик изменения настройки перемешивания вопросов"""
        self.shuffle_questions = value
        self.save_settings()
    
    def on_shuffle_answers_change(self, instance, value):
        """Обработчик изменения настройки перемешивания ответов"""
        self.shuffle_answers = value
        self.save_settings()
    
    def reset_settings(self, instance):
        """Сброс настроек"""
        self.is_dark_theme = False
        self.shuffle_questions = True
        self.shuffle_answers = True
        self.save_settings()
        self.update_theme()
    
    def load_test_file(self, instance):
        """Загрузка файла с тестом"""

        ModernFileChooserPopup(callback=self.on_file_selected).open()
    
    def on_file_selected(self, file_path):
        """Обработчик выбора файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            questions = self.parse_test_content(content)
            if questions:
                test_name = os.path.basename(file_path).replace('.txt', '')
                self.save_test(test_name, questions)
                self.load_tests_list()
        except Exception as e:
            self.show_notification(f'Ошибка загрузки: {str(e)}')
    
    def parse_test_content(self, content):
        """Парсинг содержимого теста с поддержкой многострочных вопросов и ответов"""
        questions = []
        lines = content.split('\n')
        current_question = None
        collecting_question = False
        collecting_answer = False
        current_answer_text = ""
        current_answer_correct = False
        
        for line in lines:
            line = line.strip()
            if not line and (collecting_question or collecting_answer):
                continue
                
            if not line:
                continue
            if line.startswith('?'):
                if current_question:
                    if collecting_answer and current_answer_text:
                        current_question['answers'].append(current_answer_text.strip())
                        if current_answer_correct:
                            current_question['correct'].append(len(current_question['answers']) - 1)
                        collecting_answer = False
                        current_answer_text = ""
                    
                    questions.append(TestQuestion(
                        current_question['text'].strip(),
                        current_question['answers'],
                        current_question['correct']
                    ))
                current_question = {
                    'text': line[1:].strip(),
                    'answers': [],
                    'correct': []
                }
                collecting_question = True
                collecting_answer = False
                
            elif line.startswith('+') or line.startswith('-'):
                if current_question is None:
                    continue
                if collecting_answer and current_answer_text:
                    current_question['answers'].append(current_answer_text.strip())
                    if current_answer_correct:
                        current_question['correct'].append(len(current_question['answers']) - 1)
                collecting_question = False
                collecting_answer = True
                
                current_answer_text = line[1:].strip()
                current_answer_correct = line.startswith('+')
                    
            elif collecting_question and current_question is not None:
                current_question['text'] += '\n' + line
                
            elif collecting_answer and current_question is not None:
                current_answer_text += '\n' + line
        if current_question:
            if collecting_answer and current_answer_text:
                current_question['answers'].append(current_answer_text.strip())
                if current_answer_correct:
                    current_question['correct'].append(len(current_question['answers']) - 1)
            
            questions.append(TestQuestion(
                current_question['text'].strip(),
                current_question['answers'],
                current_question['correct']
            ))
        
        return questions
    
    def save_test(self, test_name, questions):
        """Сохранение теста"""
        test_data = {
            'questions': [
                {
                    'text': q.text,
                    'answers': q.answers,
                    'correct': q.correct_indices
                } for q in questions
            ]
        }
        
        if 'tests' not in self.test_store:
            self.test_store.put('tests', **{test_name: test_data})
        else:
            tests_data = self.test_store.get('tests')
            tests_data[test_name] = test_data
            self.test_store.put('tests', **tests_data)
    
    def delete_test(self, test_name):
        """Удаление теста"""
        if 'tests' in self.test_store:
            tests_data = self.test_store.get('tests')
            if test_name in tests_data:
                del tests_data[test_name]
                self.test_store.put('tests', **tests_data)
                self.load_tests_list()
    

    def start_test(self, test_name):
        """Начало тестирования с оптимизированным экраном"""
        self.current_test = test_name
        if 'tests' in self.test_store:
            tests_data = self.test_store.get('tests')
            if test_name in tests_data:
                test_data = tests_data[test_name]
                all_questions = [
                    TestQuestion(q['text'], q['answers'], q['correct']) 
                    for q in test_data['questions']
                ]
                if self.questions_mode == 'all':
                    self.current_questions = all_questions
                elif self.questions_mode == 'range':
                    start = max(1, self.questions_start) - 1
                    end = min(self.questions_end, len(all_questions))
                    
                    if start < len(all_questions):
                        self.current_questions = all_questions[start:end]
                    else:
                        self.current_questions = all_questions
                        self.show_notification("Начальный вопрос за пределами теста, прорешиваются все вопросы")
                if not self.current_questions:
                    self.show_notification("Нет вопросов для тестирования")
                    return
        if self.shuffle_questions:
            random.shuffle(self.current_questions)
        
        if self.shuffle_answers:
            for question in self.current_questions:
                answers = question.answers
                correct_indices = question.correct_indices
                
                combined = list(zip(answers, [i in correct_indices for i in range(len(answers))]))
                random.shuffle(combined)
                
                new_answers, new_correct_flags = zip(*combined)
                question.answers = list(new_answers)
                question.correct_indices = [i for i, is_correct in enumerate(new_correct_flags) if is_correct]
        
        self.current_question_index = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        
        self.user_answers = [None] * len(self.current_questions)
        self.question_checked = [False] * len(self.current_questions)
        self.question_results = [False] * len(self.current_questions)
        self.wrong_questions = []

        if self.screen_manager.has_screen('test'):
            old_screen = self.screen_manager.get_screen('test')
            self.screen_manager.remove_widget(old_screen)
        
        self.optimized_test_screen = OptimizedTestScreen(name='test')
        self.screen_manager.add_widget(self.optimized_test_screen)
        
        # МГНОВЕННОЕ ОБНОВЛЕНИЕ ВМЕСТО ОТЛОЖЕННОГО
        self.optimized_test_screen.update_content_for_new_question()
        
        # ДОБАВЛЯЕМ ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ ТЕКСТУР ПОСЛЕ СОЗДАНИЯ ИНТЕРФЕЙСА
        Clock.schedule_once(self._force_texture_update, 0.1)
        
        self.screen_manager.current = 'test'

    def _force_texture_update(self, dt):
        """Принудительное обновление текстур после создания интерфейса"""
        if hasattr(self, 'optimized_test_screen'):
            # Принудительно обновляем текстуры вопроса и ответов
            if hasattr(self.optimized_test_screen, 'question_label'):
                self.optimized_test_screen.question_label.texture_update()
            
            if hasattr(self.optimized_test_screen, 'answer_buttons'):
                for btn in self.optimized_test_screen.answer_buttons:
                    btn.texture_update()
            
            # Принудительное обновление layout
            self.optimized_test_screen.do_layout()



    def select_answer(self, answer_index):
        """Обработчик выбора ответа - ДОБАВЛЯЕМ ОБНОВЛЕНИЕ ТОЛЬКО КНОПОК"""
        if not hasattr(self, 'current_questions') or not self.current_questions:
            return
            
        if (self.current_question_index < len(self.user_answers) and 
            not self.question_checked[self.current_question_index]):
            current_answers = self.user_answers[self.current_question_index]
            if current_answers is None:
                current_answers = []
            if answer_index in current_answers:
                current_answers.remove(answer_index)
            else:
                current_answers.append(answer_index)
            
            self.user_answers[self.current_question_index] = current_answers
            self.update_check_button_state()
            # Только обновляем цвета кнопок, а не весь контент
            if hasattr(self, 'optimized_test_screen'):
                self.optimized_test_screen._update_answer_buttons_colors()


    def action_button_click(self, instance):
        """Обработчик нажатия на кнопку действия"""
        current_index = self.current_question_index
        is_checked = self.question_checked[current_index]
        
        if not is_checked:
            self.check_answer()  # Проверка - прокрутка не сбрасывается
        else:
            if current_index < len(self.current_questions) - 1:
                self.current_question_index += 1
                if hasattr(self, 'optimized_test_screen'):
                    self.optimized_test_screen.update_content_for_new_question()  # Переход - прокрутка сбрасывается
                    Clock.schedule_once(lambda dt: self.optimized_test_screen.scroll_nav_to_current_question(), 0.1)
            else:
                self.finish_test()


    def check_answer(self):
        """Проверка ответа"""
        current_question = self.current_questions[self.current_question_index]
        user_answer = self.user_answers[self.current_question_index] or []
        is_correct = set(user_answer) == set(current_question.correct_indices)
        self.question_checked[self.current_question_index] = True
        self.question_results[self.current_question_index] = is_correct
        
        if is_correct:
            self.correct_answers += 1
        else:
            self.incorrect_answers += 1
            self.wrong_questions.append({
                'question': current_question.text,
                'user_answers': [current_question.answers[i] for i in user_answer],
                'correct_answers': [current_question.answers[i] for i in current_question.correct_indices],
                'all_answers': current_question.answers
            })
        if hasattr(self, 'optimized_test_screen'):
            # Сохраняем клавиатурный режим и активный индекс после проверки
            # self.optimized_test_screen.keyboard_mode = True  # Оставляем режим включенным
            # self.optimized_test_screen.active_answer_index остается без изменений
            self.optimized_test_screen.update_content_for_check_answer()


    def go_to_question(self, index):
        """Переход к конкретному вопросу"""
        if 0 <= index < len(self.app.current_questions):
            self.app.current_question_index = index
            
            if hasattr(self, 'optimized_test_screen'):
                self.optimized_test_screen.update_content_for_new_question()  # Сбрасываем прокрутку
                Clock.schedule_once(lambda dt: self.optimized_test_screen.scroll_nav_to_current_question(), 0.1)

    def previous_question(self):
        """Переход к предыдущему вопросу"""
        if self.app.current_question_index > 0:
            self.app.current_question_index -= 1
            
            if hasattr(self, 'optimized_test_screen'):
                self.optimized_test_screen.update_content_for_new_question()  # Сбрасываем прокрутку
                Clock.schedule_once(lambda dt: self.optimized_test_screen.scroll_nav_to_current_question(), 0.1)

    def next_question(self):
        """Переход к следующему вопросу"""
        if self.app.current_question_index < len(self.app.current_questions) - 1:
            self.app.current_question_index += 1
            
            if hasattr(self, 'optimized_test_screen'):
                self.optimized_test_screen.update_content_for_new_question()  # Сбрасываем прокрутку
                Clock.schedule_once(lambda dt: self.optimized_test_screen.scroll_nav_to_current_question(), 0.1)



    def on_settings_pressed(self, instance):
        """Обработчик кнопки настроек (instance обязателен)"""
        self.screen_manager.current = 'settings'

    def on_theme_switch(self, instance, value):
        """Обработчик переключения темы (instance и value обязательны)"""
        self.is_dark_theme = value
        self.update_theme()


    def return_to_menu(self, instance):
        """Возврат в главное меню"""
        self.screen_manager.current = 'main'
    
    def finish_test(self):
        """Завершение теста с сохранением ошибок"""
        if 'progress' not in self.test_store:
            self.test_store.put('progress', **{
                self.current_test: {
                    'correct': self.correct_answers,
                    'total': len(self.current_questions)
                }
            })
        else:
            progress_data = self.test_store.get('progress')
            progress_data[self.current_test] = {
                'correct': self.correct_answers,
                'total': len(self.current_questions)
            }
            self.test_store.put('progress', **progress_data)
        self.save_wrong_answers_to_history()
        if self.screen_manager.has_screen('results'):
            self.screen_manager.remove_widget(self.screen_manager.get_screen('results'))
        
        self.results_screen = ResultsScreen(name='results')
        self.screen_manager.add_widget(self.results_screen)
        self.screen_manager.current = 'results'
        Clock.schedule_once(lambda dt: self.results_screen.build_ui(), 0.1)
    
    def show_results(self):
        """Показ результатов теста"""
        total = len(self.current_questions)
        percentage = (self.correct_answers / total) * 100 if total > 0 else 0
        
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        result_text = (
            f"Тест завершен!\n\n"
            f"Правильных: {self.correct_answers}/{total}\n"
            f"Неправильных: {self.incorrect_answers}/{total}\n"
            f"Процент: {percentage:.1f}%"
        )
        
        result_label = AndroidLabel(
            text=result_text,
            font_size=self.get_font_size(18),
            color=self.text_primary
        )
        content.add_widget(result_label)
        
        btn_layout = BoxLayout(size_hint=(1, 0.3), spacing=dp(10))
        
        if self.wrong_questions:
            wrong_btn = AndroidButton(
                text='Показать ошибки',
                background_color=self.error_color,
                color=(1, 1, 1, 1)
            )
            wrong_btn.bind(on_press=self.show_wrong_answers)
            btn_layout.add_widget(wrong_btn)
        
        menu_btn = AndroidButton(
            text='Вернуться в меню',
            background_color=self.primary_color,
            color=(1, 1, 1, 1)
        )
        menu_btn.bind(on_press=lambda x: setattr(self.screen_manager, 'current', 'main'))
        btn_layout.add_widget(menu_btn)
        
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Результаты теста',
            content=content,
            size_hint=(0.8, 0.6),
            background_color=self.bg_color,
            title_color=self.text_primary,
            separator_color=self.primary_color
        )
        popup.open()
    


    def _update_card_rect(self, instance, value):
        """Обновление фона карточки при изменении размера"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(rgba=self.card_color)
            RoundedRectangle(
                pos=instance.pos, 
                size=instance.size, 
                radius=[dp(12)]
            )
    
    def _close_popup(self):
        """Закрытие попапа с неправильными ответами"""
        if hasattr(self, 'wrong_answers_popup'):
            self.wrong_answers_popup.dismiss()


    def show_notification(self, message, duration=None):
        """Показ уведомления, которое закрывается только по клику"""
        try:
            if hasattr(self, '_current_notification') and self._current_notification:
                try:
                    self._current_notification.dismiss()
                except:
                    pass
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            scroll = ScrollView(size_hint=(1, 0.8))
            message_container = BoxLayout(orientation='vertical', size_hint_y=None)
            message_container.bind(minimum_height=message_container.setter('height'))

            message_label = AndroidLabel(
                text=message,
                color=[1, 1, 1, 1],
                font_size=self.get_font_size(15),
                text_size=(Window.width * 0.8, None),
                halign='left',
                valign='top',
                size_hint_y=None
            )
            message_label.bind(texture_size=lambda instance, size: setattr(message_label, 'height', max(size[1], dp(80))))

            message_container.add_widget(message_label)
            scroll.add_widget(message_container)
            content.add_widget(scroll)
            close_btn = AndroidButton(
                text='Закрыть',
                size_hint_y=None,
                height=dp(50),
                background_color=[0.3, 0.6, 0.9, 1],
                color=[1, 1, 1, 1],
                font_size=self.get_font_size(16)
            )
            popup_height = min(Window.height * 0.8, message_label.height + dp(200))
            popup = Popup(
                title='',
                content=content,
                size_hint=(0.95, None),
                height=popup_height,
                auto_dismiss=False,
                background_color=[0.1, 0.1, 0.1, 0.95],
                separator_color=[0, 0, 0, 0],
                title_size=0
            )
            close_btn.bind(on_press=popup.dismiss)
            content.add_widget(close_btn)
            self._current_notification = popup
            popup.open()
            if duration is not None:
                Clock.schedule_once(lambda dt: popup.dismiss(), duration)
                
        except Exception as e:
            print(f"Ошибка показа уведомления: {e}")

    def show_quick_notification(self, message, duration=3):
        """Показ быстрого уведомления с адаптивным размером"""
        try:
            if hasattr(self, '_current_quick_notification') and self._current_quick_notification:
                try:
                    self._current_quick_notification.dismiss()
                except:
                    pass
            content = BoxLayout(orientation='vertical', size_hint=(1, 1), padding=dp(15))
            label = AndroidLabel(
                text=message,
                text_size=(Window.width * 0.7, None),
                halign='center',
                valign='middle',
                font_size=self.get_font_size(16),
                color=(1, 1, 1, 1),
                size_hint_y=None
            )
            def calculate_height(instance, value):
                if instance.texture_size:
                    text_height = instance.texture_size[1]
                    calculated_height = max(dp(80), min(text_height + dp(40), Window.height * 0.4))
                    instance.height = text_height
                    if hasattr(instance, '_popup_ref'):
                        instance._popup_ref.height = calculated_height
            
            label.bind(texture_size=calculate_height)
            content.add_widget(label)
            popup = Popup(
                title='',
                content=content,
                size_hint=(0.8, None),
                height=dp(100),
                background_color=[0.2, 0.2, 0.2, 0.95],
                separator_height=0,
                auto_dismiss=True
            )
            label._popup_ref = popup
            popup.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
            
            self._current_quick_notification = popup
            popup.open()
            label.texture_update()
            Clock.schedule_once(lambda dt: popup.dismiss(), duration)
            
        except Exception as e:
            print(f"Ошибка показа уведомления: {e}")


    def load_settings(self):
        """Загрузка настроек"""
        if 'settings' in self.settings_store:
            settings = self.settings_store.get('settings')
            self.shuffle_questions = settings.get('shuffle_questions', True)
            self.shuffle_answers = settings.get('shuffle_answers', True)
            self.questions_mode = settings.get('questions_mode', 'all')
            self.questions_count = settings.get('questions_count', 10)
            self.questions_start = settings.get('questions_start', 1)
            self.questions_end = settings.get('questions_end', 5)
        self.load_active_preset()
    
    def save_settings(self):
        """Сохранение настроек"""
        settings = {
            'shuffle_questions': self.shuffle_questions,
            'shuffle_answers': self.shuffle_answers,
            'questions_mode': self.questions_mode,
            'questions_count': self.questions_count,
            'questions_start': self.questions_start,
            'questions_end': self.questions_end
        }
        self.settings_store.put('settings', **settings)
        self.save_active_preset()


class SmartRepeatEngine:
    def __init__(self):
        self.difficulty_weights = {
            'new': 3.0,
            'repeated': 2.0,
            'old': 1.0
        }
    
    def calculate_question_priority(self, wrong_question, test_history):
        """Расчет приоритета вопроса для повторения"""
        base_priority = 1.0
        error_count = self.get_error_frequency(wrong_question['question'], test_history)
        base_priority *= (1 + error_count * 0.5)
        days_passed = self.get_days_since_error(wrong_question)
        if days_passed > 30:
            base_priority *= 1.5
        elif days_passed > 7:
            base_priority *= 2.0
        else:
            base_priority *= 3.0
            
        return base_priority
    
    def get_error_frequency(self, question_text, test_history):
        """Подсчет частоты ошибок для вопроса"""
        count = 0
        for entry in test_history:
            for wrong in entry['wrong_questions']:
                if wrong['question'] == question_text:
                    count += 1
        return count
    
    def get_days_since_error(self, wrong_question):
        """Получение количества дней с момента ошибки"""
        if 'timestamp' in wrong_question:
            error_date = datetime.strptime(wrong_question['timestamp'], "%Y-%m-%d %H:%M:%S")
            return (datetime.now() - error_date).days
        return 0
    
    def create_optimized_repeat_test(self, wrong_questions, max_questions=20):
        """Создание оптимизированного теста для повторения"""
        if not wrong_questions:
            return []
        prioritized_questions = []
        for question in wrong_questions:
            priority = self.calculate_question_priority(question, [])
            prioritized_questions.append((priority, question))
        prioritized_questions.sort(key=lambda x: x[0], reverse=True)
        selected_questions = [q[1] for q in prioritized_questions[:max_questions]]
        test_questions = []
        for wrong in selected_questions:
            test_questions.append(TestQuestion(
                text=wrong['question'],
                answers=wrong['all_answers'],
                correct_indices=[wrong['all_answers'].index(ans) for ans in wrong['correct_answers']]
            ))
        
        return test_questions


class RepeatWrongAnswersScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        
        # ДОБАВЛЯЕМ ИНИЦИАЛИЗАЦИЮ repeat_engine
        self.repeat_engine = SmartRepeatEngine()
        
        self.app.bind(
            bg_color=self.update_colors,
            card_color=self.update_colors, 
            text_primary=self.update_colors,
            primary_color=self.update_colors,
            font_scale=self.update_fonts
        )
        self.main_layout = None
        self.build_ui()
    
    def build_ui(self):
        if self.main_layout:
            self.remove_widget(self.main_layout)
            
        self.main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
    
        title = AndroidLabel(
            text='[b]Повтор ошибок[/b]',
            font_size=self.app.get_font_size(24),
            size_hint=(1, 0.15),
            color=self.app.text_primary,
            halign='center'
        )
        self.main_layout.add_widget(title)
        stats = self.get_wrong_answers_stats()
        self.stats_label = AndroidLabel(
            text=f"Всего ошибок в истории: {stats['total_wrong']}\n"
                f"Уникальных вопросов: {stats['unique_questions']}\n"
                f"Тестов с ошибками: {stats['tests_with_errors']}",
            font_size=self.app.get_font_size(16),
            color=self.app.text_primary,
            size_hint=(1, 0.2),
            halign='center'
        )
        self.main_layout.add_widget(self.stats_label)
        spacer = BoxLayout(size_hint=(1, 1))
        self.main_layout.add_widget(spacer)
        button_count = 4
        button_height = dp(50)
        spacing = dp(8)
        total_buttons_height = (button_count * button_height) + ((button_count - 1) * spacing)
        
        mode_layout = BoxLayout(
            orientation='vertical', 
            size_hint=(1, None),
            height=total_buttons_height,
            spacing=dp(8)
        )
        self.last_wrong_btn = AndroidButton(
            text='Повторить последние ошибки',
            size_hint=(1, None),
            height=button_height,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.last_wrong_btn.bind(on_press=self.repeat_last_wrong)
        self.smart_repeat_btn = AndroidButton(
            text='Умное повторение',
            size_hint=(1, None),
            height=button_height,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.smart_repeat_btn.bind(on_press=self.smart_repeat)
        self.by_test_btn = AndroidButton(
            text='Ошибки по тестам',
            size_hint=(1, None),
            height=button_height,
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.by_test_btn.bind(on_press=self.show_tests_selection)
        self.back_btn = AndroidButton(
            text='Назад в меню',
            size_hint=(1, None),
            height=dp(60),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1),
            font_size=self.app.get_font_size(14)
        )
        self.back_btn.bind(on_press=self.go_back)
        
        mode_layout.add_widget(self.last_wrong_btn)
        mode_layout.add_widget(self.smart_repeat_btn)
        mode_layout.add_widget(self.by_test_btn)
        mode_layout.add_widget(self.back_btn)
        self.main_layout.add_widget(mode_layout)
        
        self.add_widget(self.main_layout)

    def update_colors(self, *args):
        """Обновление цветов при смене темы"""
        if self.main_layout:
            self.build_ui()

    def update_fonts(self, *args):
        """Обновление шрифтов при изменении масштаба"""
        if self.main_layout:
            self.build_ui()

    def on_enter(self):
        """Вызывается при переходе на экран - обновляем шрифты"""
        Clock.schedule_once(lambda dt: self.build_ui(), 0.05)
    
    def get_wrong_answers_stats(self):
        """Статистика по ошибкам"""
        stats = {
            'total_wrong': 0,
            'unique_questions': 0,
            'tests_with_errors': 0
        }
        
        test_names = set()
        unique_questions = set()
        
        for key in self.app.wrong_answers_history.keys():
            if key != 'last_wrong':
                entry = self.app.wrong_answers_history.get(key)
                stats['total_wrong'] += len(entry['wrong_questions'])
                test_names.add(entry['test_name'])
                
                for wrong in entry['wrong_questions']:
                    unique_questions.add(wrong['question'])
        
        stats['unique_questions'] = len(unique_questions)
        stats['tests_with_errors'] = len(test_names)
        
        return stats
    
    def repeat_last_wrong(self, instance):
        """Повторение последних ошибок"""
        wrong_questions = []
        latest_timestamp = None
        for key in self.app.wrong_answers_history.keys():
            if key != 'last_wrong':
                if latest_timestamp is None or key > latest_timestamp:
                    latest_timestamp = key
        
        if latest_timestamp:
            entry = self.app.wrong_answers_history.get(latest_timestamp)
            wrong_questions = entry['wrong_questions']
        
        if wrong_questions:
            self.start_wrong_answers_test(wrong_questions, "Повторение последних ошибок")
        else:
            self.app.show_notification("Нет последних ошибок для повторения")
    
    def smart_repeat(self, instance):
        """Умное повторение с приоритетом сложных вопросов"""
        all_wrong_questions = self.app.get_all_wrong_questions()
        
        if not all_wrong_questions:
            self.app.show_notification("Нет ошибок в истории")
            return
        optimized_questions = self.repeat_engine.create_optimized_repeat_test(all_wrong_questions)
        
        if optimized_questions:
            self.start_wrong_answers_test_from_objects(optimized_questions, "Умное повторение ошибок")
        else:
            self.app.show_notification("Не удалось создать тест для повторения")
    


    def show_tests_selection(self, instance):
        """Показ списка тестов с ошибками с датами и кнопкой удаления - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        content = BoxLayout(orientation='vertical', size_hint=(1, 1), spacing=dp(3))
        
        # ВОЗВРАЩАЕМ ФОНОВУЮ КАРТОЧКУ для заголовка, но убираем синюю полоску
        title_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            size_hint_x=1,
            height=dp(70),
            padding=[dp(8), dp(8), dp(8), dp(8)]
        )
        title_card = BoxLayout(
            orientation='horizontal',
            size_hint=(1, 1),
            padding=dp(10)
        )
        with title_container.canvas.before:
            Color(rgba=self.app.card_color)
            title_container.bg_rect = RoundedRectangle(
                pos=title_container.pos, 
                size=title_container.size, 
                radius=[dp(8)]
            )
            
        title_label = AndroidLabel(
            text='[b]Ошибки по тестам[/b]',
            font_size=self.app.get_font_size(18),
            color=self.app.text_primary,
            halign='center',
            valign='middle'
        )
        
        title_card.add_widget(title_label)
        title_container.add_widget(title_card)
        content.add_widget(title_container)
        title_container.bind(
            pos=self._update_title_card_rect,
            size=self._update_title_card_rect
        )
        
        spacer = BoxLayout(size_hint_y=None, height=dp(2))
        content.add_widget(spacer)
        
        scroll_view = ScrollView(size_hint=(1, 0.8))
        tests_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        tests_layout.bind(minimum_height=tests_layout.setter('height'))
        
        test_data = {}
        for key in self.app.wrong_answers_history.keys():
            if key != 'last_wrong':
                entry = self.app.wrong_answers_history.get(key)
                test_name = entry['test_name']
                timestamp = entry.get('timestamp', key)
                
                if test_name not in test_data:
                    test_data[test_name] = {
                        'wrong_count': 0,
                        'latest_date': timestamp,
                        'entries': []
                    }
                
                test_data[test_name]['wrong_count'] += len(entry['wrong_questions'])
                test_data[test_name]['entries'].append(entry)
                if timestamp > test_data[test_name]['latest_date']:
                    test_data[test_name]['latest_date'] = timestamp
        
        for test_name, data in test_data.items():
            try:
                date_obj = datetime.strptime(data['latest_date'], "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d.%m.%Y")
            except:
                formatted_date = data['latest_date']
                
            card_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                size_hint_x=1,
                height=dp(100),
                padding=[dp(8), dp(8), dp(8), dp(8)]
            )
            test_card = BoxLayout(
                orientation='horizontal',
                size_hint=(1, 1),
                padding=dp(10),
                spacing=dp(10)
            )
            
            with card_container.canvas.before:
                Color(rgba=self.app.card_color)
                card_container.bg_rect = RoundedRectangle(
                    pos=card_container.pos, 
                    size=card_container.size, 
                    radius=[dp(8)]
                )
                
            info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7, spacing=dp(2))
            display_name = test_name[:30] + "..." if len(test_name) > 30 else test_name
            name_label = AndroidLabel(
                text=f'{display_name}',
                color=self.app.text_primary,
                size_hint_y=0.4,
                halign='left',
                font_size=self.app.get_font_size(14)
            )
            details_label = AndroidLabel(
                text=f'Ошибок: {data["wrong_count"]}\n({formatted_date})',
                color=self.app.text_secondary,
                size_hint_y=0.6,
                halign='left',
                font_size=self.app.get_font_size(12)
            )
            
            info_layout.add_widget(name_label)
            info_layout.add_widget(details_label)
            
            buttons_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
            repeat_btn = AndroidButton(
                text='Повтор',
                size_hint_x=1,
                background_color=self.app.primary_color,
                color=(1, 1, 1, 1),
                font_size=self.app.get_font_size(12)
            )
            
            def create_repeat_handler(test_name):
                def handler(x):
                    self.repeat_test_wrong_answers(test_name)
                    popup.dismiss()
                return handler
            
            repeat_btn.bind(on_press=create_repeat_handler(test_name))
            
            delete_btn = AndroidButton(
                text='️Удалить',
                size_hint_x=1,
                background_color=self.app.error_color,
                color=(1, 1, 1, 1),
                font_size=self.app.get_font_size(12)
            )
            
            def create_delete_handler(test_name):
                def handler(x):
                    self.delete_test_wrong_answers(test_name)
                    popup.dismiss()
                return handler
            
            delete_btn.bind(on_press=create_delete_handler(test_name))
            
            buttons_layout.add_widget(repeat_btn)
            buttons_layout.add_widget(delete_btn)
            
            test_card.add_widget(info_layout)
            test_card.add_widget(buttons_layout)
            card_container.add_widget(test_card)
            tests_layout.add_widget(card_container)
            card_container.bind(
                pos=self._update_test_card_rect,
                size=self._update_test_card_rect
            )
        
        scroll_view.add_widget(tests_layout)
        content.add_widget(scroll_view)
        
        close_btn = AndroidButton(
            text='Закрыть',
            size_hint=(1, 0.1),
            background_color=self.app.primary_color,
            color=(1, 1, 1, 1)
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        # УБИРАЕМ СИНЮЮ ПОЛОСКУ через separator_height=0 и title=''
        popup = Popup(
            title='',  # Пустой заголовок убирает синюю полоску
            content=content,
            size_hint=(0.95, 0.8),
            background_color=self.app.bg_color,
            separator_height=0,  # Убираем разделитель полностью
            title_size=0  # Убираем место под заголовок
        )
        popup.open()


    def _update_title_card_rect(self, instance, value):
        """Обновление фона карточки заголовка при изменении размера"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos, 
                    size=instance.size, 
                    radius=[dp(8)]
                )
        
    def delete_test_wrong_answers(self, test_name):
        """Удаление истории ошибок для конкретного теста с динамическим обновлением"""
        keys_to_delete = []
        
        for key in self.app.wrong_answers_history.keys():
            if key != 'last_wrong':
                entry = self.app.wrong_answers_history.get(key)
                if entry['test_name'] == test_name:
                    keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.app.wrong_answers_history.delete(key)
        popup = None
        current_widget = self
        while current_widget and not hasattr(current_widget, 'title'):
            current_widget = current_widget.parent
            if isinstance(current_widget, Popup):
                popup = current_widget
                break
        
        if popup:
            popup.dismiss()
            Clock.schedule_once(lambda dt: self.show_tests_selection(None), 0.1)

    def _update_test_card_rect(self, instance, value):
        """Обновление фона карточки теста при изменении размера"""
        if hasattr(instance, 'canvas') and hasattr(instance, 'bg_rect'):
            instance.canvas.before.clear()
            with instance.canvas.before:
                Color(rgba=self.app.card_color)
                instance.bg_rect = RoundedRectangle(
                    pos=instance.pos, 
                    size=instance.size, 
                    radius=[dp(8)]
                )
    
    def repeat_test_wrong_answers(self, test_name):
        """Повторение ошибок конкретного теста"""
        wrong_questions = self.app.get_wrong_questions_by_test(test_name)
        
        if wrong_questions:
            self.start_wrong_answers_test(wrong_questions, f"Повторение ошибок: {test_name}")
        else:
            self.app.show_notification(f"Нет ошибок для теста '{test_name}'")
    
    def start_wrong_answers_test(self, wrong_questions, test_name):
        """Запуск теста из неправильных вопросов"""
        test_questions = []
        for wrong in wrong_questions:
            correct_indices = []
            for correct_answer in wrong['correct_answers']:
                if correct_answer in wrong['all_answers']:
                    correct_indices.append(wrong['all_answers'].index(correct_answer))
            
            test_questions.append(TestQuestion(
                text=wrong['question'],
                answers=wrong['all_answers'],
                correct_indices=correct_indices
            ))
        
        self.start_wrong_answers_test_from_objects(test_questions, test_name)
    
    def start_wrong_answers_test_from_objects(self, test_questions, test_name):
        """Запуск теста из объектов TestQuestion"""
        if not test_questions:
            self.app.show_notification("Нет вопросов для тестирования")
            return
        self.app.start_custom_test(test_name, test_questions)
        self.app.screen_manager.current = 'test'
    
    def go_back(self, instance):
        self.app.screen_manager.current = 'main'



if __name__ == '__main__':
    TestApp().run()
