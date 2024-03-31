from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from Plan import DayPlan
from pathlib import Path

from datetime import datetime, date
import copy


# Set the desired window size
#scale = 0.5
#Window.size = (700*scale, 1280*scale)  # <-- For example, this sets the window size to 500x700 pixels.


class MainWindow(FloatLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.plan = main_app.plan

        # Center container for main_btn and next_snus_label
        center_box = BoxLayout(orientation='vertical', spacing=40, size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.main_btn = Button(text="SNUS", on_release=self.push_main_btn, size_hint=(1, 0.95))

         # Adjustments box with decrease button, label, and increase button
        adjustments_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=50)
        self.dec_btn = Button(text="-", on_release=self.decrease_value)
        self.inc_btn = Button(text="+", on_release=self.increase_value)
        self.value_label = Label(text=str(self.main_app.current_dose), size_hint=(1, 1), halign='center', valign='center')

        adjustments_box.add_widget(self.dec_btn)
        adjustments_box.add_widget(self.value_label)
        adjustments_box.add_widget(self.inc_btn)

        center_box.add_widget(adjustments_box)
        center_box.add_widget(self.main_btn)

        self.next_snus_label = Label(
                                    text=f"Next snus: {self.plan.get_next_time_string()}",
                                    color=(0, 1, 0, 1),
                                    size_hint=(1, 0.05),  # This ensures the Label takes up the full width of the BoxLayout
                                    halign='center',   # Horizontally centers the text inside the label
                                    valign='center',   # Vertically centers the text inside the label
                                    )

        center_box.add_widget(self.next_snus_label)

        self.add_widget(center_box)

        self.update_main_button()
        self._event = Clock.schedule_interval(self.update_main_button, 1)

    def increase_value(self, instance):
        # Increase the value and update the label
        self.main_app.current_dose += 1  # Assuming `current_dose` is an integer
        self.value_label.text = str(self.main_app.current_dose)
        self._save_current_dose(self.main_app.current_dose)

    def decrease_value(self, instance):
        # Decrease the value and update the label, ensuring it doesn't go below a minimum value (e.g., 0)
        if self.main_app.current_dose > 0:
            self.main_app.current_dose -= 1
        self.value_label.text = str(self.main_app.current_dose)
        self._save_current_dose(self.main_app.current_dose)

    def _save_current_dose(self, dose):
        with open(self.main_app.state_storage, 'w+') as f:
            f.write(str(dose))

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
        if not self.plan.done:
            next_time = self.plan.get_next_time()
            if next_time and now > next_time:
                return True
            else:
                return False
        else:
            return False

    def push_main_btn(self, instance):
        self.plan.next()
        if self.plan.done:
            self.main_app.plan = self.plan.get_next_day(self.main_app.current_dose)
        print(f'{self.plan}')
        #self.next_snus_label.text = f"Next snus: {self.plan.get_next_time_string()}"
        self.main_app.root_window()

    @staticmethod
    def is_passed(time):
        if time < datetime.now():
            return True
        else:
            return False


class SnusManagerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state_storage = Path(r"state_storage.pkl")
        self.current_dose = self._get_current_dose()
        self.plan = DayPlan(date.today(), self.current_dose)

    def _get_current_dose(self):
        if self.state_storage.exists():
            with open(self.state_storage, 'r') as f:
                value = int(f.read())
                if value != '':
                    return int(value)
        else:
            return 7

    def build(self):
        self.title = 'Snus Manager'
        return MainWindow(main_app=self)

    def root_window(self):
        self.root.clear_widgets()
        self.root.add_widget(MainWindow(main_app=self))


if __name__ == "__main__":
    SnusManagerApp().run()
