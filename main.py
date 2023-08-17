from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout

from Plan.Plan import Plan
from datetime import datetime


plan = Plan()

class Setup(BoxLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.main_app = main_app

        # Settings Box
        settings_box = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(0.8, 0.2))
        horizontal_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.05))

        cnt_label = Label(text="Current daily snus:", color=(1, 1, 1, 1), size_hint=(0.4, 1))
        horizontal_box.add_widget(cnt_label)

        self.cnt_box = TextInput(hint_text="Enter daily snus consumption", text=str(plan._state['daily_dose']), multiline=False, size_hint=(0.1, 1))
        horizontal_box.add_widget(self.cnt_box)

        settings_box.add_widget(horizontal_box)
        self.add_widget(settings_box)


        # OK and Back Buttons
        btn_layout = FloatLayout(size_hint=(1, None), height=50)  # Specify a height for the FloatLayout
        back_btn = Button(text="Back", on_release=self.back_btn_clicked, size_hint=(None, None), size=(100, 50), pos_hint={'left': 1, 'y': 0})
        ok_btn = Button(text="OK", on_release=lambda instance: self.push_btn(int(self.cnt_box.text)), size_hint=(None, None), size=(100, 50), pos_hint={'right': 1, 'y': 0})

        btn_layout.add_widget(back_btn)
        btn_layout.add_widget(ok_btn)

        self.add_widget(btn_layout)

    def back_btn_clicked(self, instance):
        self.main_app.root_window()

    def push_btn(self, no_of_snus):
        plan.setup(no_of_snus)
        self.main_app.root_window()


class MainWindow(FloatLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app

        # Setup button in the top right corner
        setup_btn = Button(text="Setup", on_release=self.push_setup_btn, size_hint=(None, None), size=(100, 50), pos_hint={'right': 1, 'top': 1})
        self.add_widget(setup_btn)

        # Center container for main_btn and next_snus_label
        center_box = BoxLayout(orientation='vertical', spacing=20, width=200, size_hint=(None, None), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.main_btn = Button(text="SNUS", on_release=self.push_main_btn, size_hint=(None, None), size=(200, 200))
        center_box.add_widget(self.main_btn)

        self.next_snus_label = Label(
                                    text=f"Next snus: {plan.get_next_snus_time_string()}",
                                    color=(1, 1, 1, 1),
                                    size_hint=(1, None),  # This ensures the Label takes up the full width of the BoxLayout
                                    height=44,  # Adjust height as needed
                                    halign='center',   # Horizontally centers the text inside the label
                                    valign='center',   # Vertically centers the text inside the label
                                    text_size=(200, None)  # This will allow the text to be aligned inside the given width.
                                )

        center_box.add_widget(self.next_snus_label)

        self.add_widget(center_box)

        self.update_main_button()
        self._event = Clock.schedule_interval(self.update_main_button, 1)

    def update_main_button(self, *args):
        if self.time_for_next():
            self.main_btn.background_color = (0, 1, 0, 1)
            self.main_btn.disabled = False
        else:
            self.main_btn.background_color = (1, 0, 0, 1)
            self.main_btn.disabled = True

    def time_for_next(self):
        now = datetime.now()
        day_plan = plan._state['day_plan']
        if day_plan:
            next = day_plan[-1]
            if now > next:
                return True
            else:
                return False
        else:
            return False

    def push_setup_btn(self, instance):
        self.main_app.setup_window()

    def push_main_btn(self, instance):
        plan.get_next()
        self.next_snus_label.text = f"Next snus: {plan.get_next_snus_time_string()}"

class SnusManagerApp(App):
    def build(self):
        self.title = 'Snus Manager'
        return MainWindow(main_app=self)

    def setup_window(self):
        self.root.clear_widgets()
        self.root.add_widget(Setup(main_app=self))

    def root_window(self):
        self.root.clear_widgets()
        self.root.add_widget(MainWindow(main_app=self))

if __name__ == "__main__":
    SnusManagerApp().run()
