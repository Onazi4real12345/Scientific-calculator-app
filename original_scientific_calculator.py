from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.window import Window
import math
import re

class ScientificCalculatorApp(App):
    def build(self):
        self.is_shift = False
        self.equation = ""  
        
        # Solid dark slate device background
        Window.clearcolor = (0.11, 0.13, 0.17, 1) 
        
        # Root layout configuration
        main_layout = BoxLayout(orientation='vertical', padding=8, spacing=4)
        
        # --- DISPLAY DOCK ---
        display_container = BoxLayout(orientation='vertical', size_hint=(1, 0.22), padding=(15, 5))
        
        self.input_display = Label(
            text="",
            font_size='22sp',
            halign='left',
            valign='top',
            color=(0.65, 0.7, 0.75, 1),
            size_hint=(1, 0.4)
        )
        self.input_display.bind(size=self.input_display.setter('text_size'))
        
        self.output_display = Label(
            text="0",
            font_size='42sp',
            halign='right',
            valign='bottom',
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 0.6)
        )
        self.output_display.bind(size=self.output_display.setter('text_size'))
        
        display_container.add_widget(self.input_display)
        display_container.add_widget(self.output_display)
        main_layout.add_widget(display_container)
        
        # --- KEYBOARD SECTION ---
        keyboard_anchor = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint=(1, 0.78))
        keyboard_box = BoxLayout(orientation='vertical', spacing=4, size_hint=(1, 1))
        
        # Rebalanced grids after removing fraction keys
        self.func_gl = GridLayout(cols=5, spacing=4, size_hint=(1, 0.52))
        self.num_gl = GridLayout(cols=4, spacing=4, size_hint=(1, 0.48))
        
        # Safe layout settings using the standard root symbol string '\u221a'
        self.normal_func_layout = [
            ["SHIFT", "DEL", "C", "AC", "mod"],
            ["sin", "cos", "tan", "log", "ln"],
            ["pi", "e", "^", "x^2", "\u221a"],
            ["(", ")", "abs", "+/-", "/"]
        ]
        
        self.shift_func_layout = [
            ["SHIFT", "DEL", "C", "AC", "mod"],
            ["asin", "acos", "atan", "10^x", "e^x"],
            ["pi", "e", "^", "x^2", "\u221a"],
            ["(", ")", "abs", "+/-", "/"]
        ]
        
        self.num_layout = [
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "EXP", "="]
        ]
        
        self.build_keyboard(keyboard_box)
        keyboard_anchor.add_widget(keyboard_box)
        main_layout.add_widget(keyboard_anchor)
        
        return main_layout

    def build_keyboard(self, container):
        container.clear_widgets()
        self.func_gl.clear_widgets()
        self.num_gl.clear_widgets()
        
        current_func_layout = self.shift_func_layout if self.is_shift else self.normal_func_layout
        for row in current_func_layout:
            for text in row:
                btn = Button(
                    text=text,
                    font_size='15sp',
                    bold=True,
                    background_normal='',
                    background_color=self.get_button_style(text),
                    color=self.get_text_style(text)
                )
                btn.bind(on_press=self.on_button_click)
                self.func_gl.add_widget(btn)
                
        for row in self.num_layout:
            for text in row:
                btn = Button(
                    text=text,
                    font_size='20sp',
                    bold=True,
                    background_normal='',
                    background_color=self.get_button_style(text),
                    color=self.get_text_style(text)
                )
                btn.bind(on_press=self.on_button_click)
                self.num_gl.add_widget(btn)
                
        container.add_widget(self.func_gl)
        container.add_widget(self.num_gl)

    def get_button_style(self, text):
        if text == "SHIFT":
            return (0, 0.53, 0.35, 1) if self.is_shift else (0.15, 0.17, 0.2, 1)
        if text in ["DEL", "C", "AC"]:
            return (0.85, 0.32, 0.12, 1) if text == "AC" else (0.2, 0.22, 0.26, 1)
        if text in ["/", "*", "-", "+", "="]:
            return (0.22, 0.25, 0.3, 1)
        if text in ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ".", "EXP"]:
            return (0.13, 0.15, 0.18, 1)
        return (0.17, 0.19, 0.22, 1)

    def get_text_style(self, text):
        if text in ["SHIFT", "AC"]:
            return (1, 1, 1, 1)
        if text in ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ".", "EXP"]:
            return (0.9, 0.92, 0.95, 1)
        if text in ["/", "*", "-", "+", "="]:
            return (0.76, 0.58, 0.36, 1)
        return (0.35, 0.51, 0.68, 1) if not self.is_shift else (0.76, 0.58, 0.36, 1)

    def on_button_click(self, instance):
        char = instance.text
        
        if char == "SHIFT":
            self.is_shift = not self.is_shift
            self.build_keyboard(self.func_gl.parent)
            return

        if char == "AC":
            self.equation = ""
            self.input_display.text = ""
            self.output_display.text = "0"
        elif char == "C":
            self.equation = ""
            self.output_display.text = "0"
        elif char == "DEL":
            self.equation = self.equation[:-1]
            self.input_display.text = self.equation
        elif char == "=":
            self.calculate_result()
        elif char == "x^2":
            self.equation += "^2"
            self.input_display.text = self.equation
        elif char == "\u221a":
            self.equation += "\u221a("
            self.input_display.text = self.equation
        elif char == "+/-":
            if self.equation:
                if self.equation.startswith("-"):
                    self.equation = self.equation[1:]
                else:
                    self.equation = "-" + self.equation
                self.input_display.text = self.equation
        else:
            self.equation += char
            self.input_display.text = self.equation
            
        if char != "SHIFT" and self.is_shift and char not in ["DEL", "C", "AC"]:
            self.is_shift = False
            self.build_keyboard(self.func_gl.parent)

    def calculate_result(self):
        try:
            expr = self.equation
            
            safe_dict = {
                "math": math,
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "asin": lambda x: math.degrees(math.asin(x)),
                "acos": lambda x: math.degrees(math.acos(x)),
                "atan": lambda x: math.degrees(math.atan(x)),
                "log10": math.log10,
                "log": math.log,
                "sqrt": math.sqrt,
                "abs": abs
            }
            
            # Map the clean layout strings to functional executable Python structures
            replacements = {
                "pi": str(math.pi), "e": str(math.e), "mod": "%", "^": "**",
                "\u221a": "sqrt", "10^x": "10**", "e^x": "math.exp",
                "asin": "asin", "acos": "acos", "atan": "atan",
                "sin": "sin", "cos": "cos", "tan": "tan",
                "log": "log10", "ln": "log"
            }
            
            for label, py_func in replacements.items():
                expr = expr.replace(label, py_func)
                
            result = eval(expr, {"__builtins__": None}, safe_dict)
            
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 8)
                
            self.output_display.text = str(result)
        except Exception:
            self.output_display.text = "Error"

if __name__ == "__main__":
    ScientificCalculatorApp().run()
