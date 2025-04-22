from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from Generator import Snuff
from pathlib import Path
from datetime import datetime
import pickle


# Set the desired window size
from kivy.core.window import Window
#scale = 0.5
#Window.size = (700*scale, 1280*scale)  # <-- For example, this sets the window size to 500x700 pixels.


class MainWindow(FloatLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.state_storage = Path(r"day.pkl")
        self.main_app = main_app
        self.plan = main_app.plan

        # Center container for main_btn and next_snus_label
        center_box = BoxLayout(orientation='vertical', spacing=40, size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.main_btn = Button(text="SNUS", on_release=self.push_main_btn, size_hint=(1, 0.95))
        center_box.add_widget(self.main_btn)
        self.add_widget(center_box)

        # New Day Button
        new_day_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), size=(200, 50), pos_hint={'left': 0.5, 'top': 0.95})
        self.new_day_btn = Button(text="Reset",
                                  on_release=self.push_new_day_btn,
                                  size_hint=(1, 0.95),
                                  background_normal='',
                                  background_color=(0, 0, 0, 1),
                                  color=(1, 1, 1, 0.5)
        )

        new_day_box.add_widget(self.new_day_btn)

        self.add_widget(new_day_box)


       # Adjustments box in the upper right corner
        adjustments_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(None, None), size=(200, 50), pos_hint={'right': 0.95, 'top': 0.95})
        self.dec_btn = Button(text="-", on_release=self.decrease_value,
                              background_normal='', background_color=(0, 0, 0, 1),
                              color=(1, 1, 1, 1))  # White text
        self.inc_btn = Button(text="+", on_release=self.increase_value,
                              background_normal='', background_color=(0, 0, 0, 1),
                              color=(1, 1, 1, 1))  # White text
        self.value_label = Label(text=str(self.main_app.plan.dose), size_hint=(None, None), size=(60, 50))
        adjustments_box.add_widget(self.dec_btn)
        adjustments_box.add_widget(self.value_label)
        adjustments_box.add_widget(self.inc_btn)

        # Adding adjustments box directly to the MainWindow layout
        self.add_widget(adjustments_box)

        # Configuration for the next_snus_label remains the same
        self.next_snus_label = Label(
                                    text=f"Next snus: {self.plan.last.strftime('%d/%m %H:%M')}",
                                    color=(0, 1, 0, 1),
                                    size_hint=(1, 0.05),
                                    halign='center',
                                    valign='center',
                                    )
        center_box.add_widget(self.next_snus_label)

        # Update main button and scheduling event remain unchanged
        self.update_main_button()
        self._event = Clock.schedule_interval(self.update_main_button, 1)

    def increase_value(self, instance):
        # Increase the value and update the label
        self.main_app.plan.dose += 1  # Assuming `current_dose` is an integer
        self.value_label.text = str(self.main_app.plan.dose)
        self.dump()
        self.main_app.root_window()

    def decrease_value(self, instance):
        # Decrease the value and update the label, ensuring it doesn't go below a minimum value (e.g., 0)
        if self.main_app.plan.dose > 0:
            self.main_app.plan.dose -= 1
        self.value_label.text = str(self.main_app.plan.dose)
        self.dump()
        self.main_app.root_window()

    def update_main_button(self, *args):
        if self.time_for_next():
            self.main_btn.disabled = False
            self.main_btn.background_color = (0, 1, 0, 1)
            self.next_snus_label.color = (0, 1, 0, 1)
        else:
            self.main_btn.disabled = True
            self.main_btn.background_color = (1, 0, 0, 1)
            self.next_snus_label.color = (1, 0, 0, 1)

    def time_for_next(self):
        now = datetime.now()
        if now > self.plan.last:
            return True
        else:
            return False

    def push_main_btn(self, instance):
        self.plan.next
        self.dump()
        self.main_app.root_window()

    def push_new_day_btn(self, instance):
        self.plan.new_day()
        self.dump()
        self.main_app.root_window()

    def dump(self):
        dump = {'time': self.plan.last, 'dose': self.plan.dose}
        with open(self.state_storage, 'wb') as f:
            pickle.dump(dump, f)


class SnusManagerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_storage = Path(r"day.pkl")
        self.plan = self._get_day_plan()

    def _get_day_plan(self):
        if self.state_storage.exists():
            dose, time = self.load()
            plan = Snuff(dose, time)
        else:
            plan = Snuff(5, datetime.now())
        return plan

    def load(self):
        with open(self.state_storage, 'rb') as f:
            dump = pickle.load(f)
        return dump['dose'], dump['time']

    def build(self):
        self.title = 'Snus Manager'
        return MainWindow(main_app=self)

    def root_window(self):
        self.root.clear_widgets()
        self.root.add_widget(MainWindow(main_app=self))


if __name__ == "__main__":
    SnusManagerApp().run()
