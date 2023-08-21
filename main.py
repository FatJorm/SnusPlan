from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.uix.spinner import Spinner
from kivy.properties import NumericProperty
from kivy.factory import Factory
from kivy.uix.spinner import SpinnerOption
import time


from Plan import Plan, Day
from datetime import datetime, date


# Set the desired window size
scale = 0.5
Window.size = (700*scale, 1280*scale)  # <-- For example, this sets the window size to 500x700 pixels.

plan = Plan()


class CustomSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = 44  # Set this to a value that looks good for individual items


class CustomSpinner(Spinner):
    def _update_dropdown(self, dt=None):
        # Call the original method first
        super()._update_dropdown(dt)

        # Now, set the height based on the desired number of visible items
        visible_items = 5
        self.dropdown_cls.max_height = visible_items * 44  # Assuming each item is 44 pixels high


class DosePicker(BoxLayout):
    def __init__(self, dose, **kwargs):
        super().__init__(**kwargs)
        self.dose = dose
        self.orientation = 'horizontal'
        self.spacing = 10

        # Assuming each item should be 44 pixels high to show 5 items within 220 pixels
        item_height = 5

        self.doses = CustomSpinner(
            text=str(self.dose),
            values=[str(i) for i in range(1, 25)],  # This generates values from '1' to '24'
            size_hint=(0.5, 1),
            option_cls=Factory.get('SpinnerOption'),
            height=item_height * 5
        )
        self.doses.bind(text=self.on_dose_text)

        self.add_widget(self.doses)

    def on_dose_text(self, instance, value):
        self.adjust_dropdown_height(instance)

    def adjust_dropdown_height(self, instance):
        if instance._dropdown:
            visible_items = 5
            instance._dropdown.max_height = visible_items * 44  # Assuming each item is 44 pixels high

    def get_dose(self):
        """Return selected dose value."""
        return int(self.doses.text)


class TimePicker(BoxLayout):
    def __init__(self, time, **kwargs):
        super().__init__(**kwargs)
        self.time = time
        self.orientation = 'horizontal'
        self.spacing = 10

        # Assuming each item should be 44 pixels high to show 5 items within 220 pixels
        item_height = 5

        self.hours = CustomSpinner(
            text=str(self.time.hour),
            values=('00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
                   '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21',
                   '22', '23'),
            size_hint=(0.5, 1),
            # Adjust the height of the dropdown list
            option_cls=Factory.get('SpinnerOption'),
            height=item_height * 5
        )
        self.hours.bind(text=self.on_hours_text)

        self.minutes = CustomSpinner(
            text=str(self.time.minute),
            values=[f"{i:02}" for i in range(60)],  # This generates strings '00', '01', ... '59'
            size_hint=(0.5, 1),
            # Adjust the height of the dropdown list
            option_cls=Factory.get('SpinnerOption'),
            height=item_height * 5
        )
        self.minutes.bind(text=self.on_minutes_text)

        self.add_widget(self.hours)
        self.add_widget(self.minutes)

    def on_hours_text(self, instance, value):
        self.adjust_dropdown_height(instance)

    def on_minutes_text(self, instance, value):
        self.adjust_dropdown_height(instance)

    def adjust_dropdown_height(self, instance):
        if instance._dropdown:  # <-- Notice the underscore before dropdown
            visible_items = 5
            instance._dropdown.max_height = visible_items * 44  # Assuming each item is 44 pixels high


    def get_time(self):
        """Return selected time as (hour, minute) tuple."""
        return int(self.hours.text), int(self.minutes.text)


class Setup(FloatLayout):
    daily_dose_current_value = NumericProperty(0)  # This holds the current value for snus.
    wake_up_time_weekdays = NumericProperty(0)  # This holds the value for daily coffee intake.

    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app
        self.daily_dose_current_value = plan.get_current_dose()
        self.wake_up_time_weekdays = plan .get_current_wake_up_time_weekday()

        # Settings Box
        settings_box = AnchorLayout(anchor_x='center', anchor_y='top', size_hint=(0.8, 0.8), pos_hint={'top': 1})

        # Entries box
        entries_box = BoxLayout(orientation='vertical', spacing=20, size_hint=(1, 0.5), pos_hint={'top': 1})

        # Daily Dose
        daily_dose_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), pos_hint={'top': 1})

        self.dose_label = Label(text="Current daily dose:", size_hint=(0.7, 0.1))
        daily_dose_box.add_widget(self.dose_label)

        self.dose_picker = DosePicker(dose=plan.start_dose, size_hint=(0.1, 0.1))
        daily_dose_box.add_widget(self.dose_picker)

        entries_box.add_widget(daily_dose_box)

        # Wake Up Time
        time_box = BoxLayout(orientation='vertical', spacing=10, size_hint=(1, 1))

        wake_up_time_label_box = AnchorLayout(anchor_x='right', size_hint=(0.5, 0.5))

        wake_up_time_label = Label(text="Wake Up")
        wake_up_time_label_box.add_widget(wake_up_time_label)

        time_box.add_widget(wake_up_time_label_box)

        # Wake up time weekdays
        wake_up_time_weekdays_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.5))
        wake_up_time_weekdays_label = Label(text="Weekdays:", size_hint=(0.5, 1))
        wake_up_time_weekdays_box.add_widget(wake_up_time_weekdays_label)

        self.time_picker_wake_up_time_weekdays = TimePicker(time=plan.wake_up_time_weekday, size_hint=(0.3, 0.1))
        wake_up_time_weekdays_box.add_widget(self.time_picker_wake_up_time_weekdays)

        time_box.add_widget(wake_up_time_weekdays_box)

        # Wake up time weekends
        wake_up_time_weekends_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.5))
        wake_up_time_weekends_label = Label(text="Weekends:", size_hint=(0.5, 1))
        wake_up_time_weekends_box.add_widget(wake_up_time_weekends_label)

        self.time_picker_wake_up_time_weekends = TimePicker(time=plan.wake_up_time_weekend, size_hint=(0.3, 0.1))
        wake_up_time_weekends_box.add_widget(self.time_picker_wake_up_time_weekends)

        time_box.add_widget(wake_up_time_weekends_box)

        # Bed time
        bed_time_label_box = AnchorLayout(anchor_x='right', size_hint=(0.5, 0.5))

        bed_time_label = Label(text="Bed Time")
        bed_time_label_box.add_widget(bed_time_label)

        time_box.add_widget(bed_time_label_box)

        # Bed time weekdays
        bed_time_weekdays_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.5))
        bed_time_weekdays_label = Label(text="Weekdays:", size_hint=(0.5, 1))
        bed_time_weekdays_box.add_widget(bed_time_weekdays_label)

        self.time_picker_bed_time_weekdays = TimePicker(time=plan.bedtime_weekday, size_hint=(0.3, 0.1))
        bed_time_weekdays_box.add_widget(self.time_picker_bed_time_weekdays)

        time_box.add_widget(bed_time_weekdays_box)

        # Bed time weekends
        bed_time_weekends_box = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.5))
        bed_time_weekends_label = Label(text="Weekends:", size_hint=(0.5, 1))
        bed_time_weekends_box.add_widget(bed_time_weekends_label)

        self.time_picker_bed_time_weekends = TimePicker(plan.bedtime_weekend, size_hint=(0.3, 0.1))
        bed_time_weekends_box.add_widget(self.time_picker_bed_time_weekends)

        time_box.add_widget(bed_time_weekends_box)

        entries_box.add_widget(time_box)

        settings_box.add_widget(entries_box)

        self.add_widget(settings_box)

        # OK and Back Buttons
        btn_layout = FloatLayout(size_hint=(1, 0.1), pos_hint={'x': 0, 'y': 0})
        back_btn = Button(text="Back", on_release=self.back_btn_clicked, size_hint=(0.3, 1), pos_hint={'left': 1, 'y': 0})
        self.ok_btn = Button(text="OK", on_release=self.push_btn, size_hint=(0.3, 1), pos_hint={'right': 1, 'y': 0})

        btn_layout.add_widget(back_btn)
        btn_layout.add_widget(self.ok_btn)

        self.add_widget(btn_layout)

    def back_btn_clicked(self, instance):
        self.main_app.root_window()

    def push_btn(self, instance):
        start_date = date.today()
        wake_up_time_weekdays_hour, wake_up_time_weekdays_minute = self.time_picker_wake_up_time_weekdays.get_time()
        wake_up_time_weekends_hour, wake_up_time_weekends_minute = self.time_picker_wake_up_time_weekends.get_time()
        bed_time_weekdays_hour, bed_time_weekdays_minute = self.time_picker_bed_time_weekdays.get_time()
        bed_time_weekends_hour, bed_time_weekends_minute = self.time_picker_bed_time_weekends.get_time()
        wake_up_time_weekday = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=wake_up_time_weekdays_hour, minute=wake_up_time_weekdays_minute)
        wake_up_time_weekend = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=wake_up_time_weekends_hour, minute=wake_up_time_weekends_minute)
        bed_time_weekday = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=bed_time_weekdays_hour, minute=bed_time_weekdays_minute)
        bed_time_weekend = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=bed_time_weekends_hour, minute=bed_time_weekends_minute)
        plan.update(self.dose_picker.get_dose(), wake_up_time_weekday, wake_up_time_weekend, bed_time_weekday, bed_time_weekend)
        while plan.is_done():
            time.sleep(1)
        self.main_app.root_window()


class MainWindow(FloatLayout):
    def __init__(self, main_app, **kwargs):
        super().__init__(**kwargs)
        self.main_app = main_app

        # Setup button in the top right corner
        setup_btn = Button(text="Setup", on_release=self.push_setup_btn, size_hint=(0.3, 0.1), pos_hint={'right': 1, 'top': 1})
        self.add_widget(setup_btn)

        # Center container for main_btn and next_snus_label
        center_box = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.5, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.main_btn = Button(text="SNUS", on_release=self.push_main_btn, size_hint=(1, 0.95))
        center_box.add_widget(self.main_btn)

        self.next_snus_label = Label(
                                    text=f"Next snus: {plan.get_next_time_string()}",
                                    color=(1, 1, 1, 1),
                                    size_hint=(1, 0.05),  # This ensures the Label takes up the full width of the BoxLayout
                                    halign='center',   # Horizontally centers the text inside the label
                                    valign='center',   # Vertically centers the text inside the label
                                    )

        center_box.add_widget(self.next_snus_label)

        self.add_widget(center_box)

        self.update_main_button()
        self._event = Clock.schedule_interval(self.update_main_button, 1)

    def update_main_button(self, *args):
        if self.time_for_next():
            self.main_btn.disabled = False
            self.main_btn.background_color = (0, 1, 0, 1)
        else:
            self.main_btn.disabled = True
            self.main_btn.background_color = (1, 0, 0, 1)

    def time_for_next(self):
        now = datetime.now()
        if not plan.is_done():
            next_time = plan.get_next_time()
            if next_time and now > next_time:
                return True
            else:
                return False
        else:
            return False

    def push_setup_btn(self, instance):
        self.main_app.setup_window()

    def push_main_btn(self, instance):
        plan.take_one()
        self.next_snus_label.text = f"Next snus: {plan.get_next_time_string()}"

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
