from datetime import date, datetime, timedelta
import os
import pickle


class Day:
    def __init__(self, current_date, weekday, dose, wake_up_time, bed_time):
        self.date = current_date
        self.dose = dose
        self.wake_up_time = self._get_wake_up_time(wake_up_time)
        self.bed_time = self._get_bed_time(bed_time)
        self.weekday = weekday
        self.plan = self.get_plan()

    def get_next_string(self):
        if self.is_done():
            return "--:--"
        else:
            return self.plan[-1].strftime("%d/%m %H:%M")

    def get_next(self):
        if self.is_done():
            return None
        else:
            return self.plan[-1]

    def take_one(self):
        self.plan.pop()

    def _get_wake_up_time(self, wake_up_time):
        return datetime(year=self.date.year,
                        month=self.date.month,
                        day=self.date.day,
                        hour=wake_up_time.hour,
                        minute=wake_up_time.minute,
                        second=wake_up_time.second)

    def _get_bed_time(self, bed_time):
        return datetime(year=self.date.year,
                        month=self.date.month,
                        day=self.date.day,
                        hour=bed_time.hour,
                        minute=bed_time.minute,
                        second=bed_time.second)

    def get_plan(self):
        daily_plan = []
        snus_time = self.wake_up_time
        day_in_min = self.get_snus_day_in_min()
        daily_plan.append(snus_time)
        if self.dose > 1:
            min_between_snus = int(day_in_min/(self.dose-1))
            for i in range(self.dose-1):
                snus_time += timedelta(minutes=min_between_snus)
                daily_plan.append(snus_time)
        daily_plan.reverse()
        return self.remove_passed(daily_plan)

    def get_snus_day_in_min(self):
        day_in_min = (self.bed_time.hour - self.wake_up_time.hour) * 60 + (self.bed_time.minute - self.wake_up_time.minute)
        if self.dose > 1:
            return int(day_in_min - (day_in_min/self.dose) * 0.5)
        else:
            return day_in_min



    def is_done(self):
        return False if self.plan else True

    @staticmethod
    def remove_passed(daily_plan):
        out_l = []
        now = datetime.now()
        for time in daily_plan:
            if time > now:
                out_l.append(time)
        return out_l

    def __str__(self):
        return f"(Date: {self.date}, " \
               f"Weekday: {self.weekday}," \
               f" Dose: {self.dose}, " \
               f"Wake up time: {self.wake_up_time}, " \
               f"Bedtime: {self.bed_time}, " \
               f"Plan: {self.plan})"


class Plan:
    def __init__(self):
        self._plan_file = "plan.pkl"
        self._settings_file = "settings.pkl"
        self._start_date = date.today()
        self.start_dose = 12
        self.wake_up_time_weekday = datetime(year=self._start_date.year, month=self._start_date.month, day=self._start_date.day, hour=7, minute=0)
        self.wake_up_time_weekend = datetime(year=self._start_date.year, month=self._start_date.month, day=self._start_date.day, hour=8, minute=0)
        self.bedtime_weekday = datetime(year=self._start_date.year, month=self._start_date.month, day=self._start_date.day, hour=21, minute=0)
        self.bedtime_weekend = datetime(year=self._start_date.year, month=self._start_date.month, day=self._start_date.day, hour=22, minute=0)
        self.initial_days_in_plan = 0
        self._plan = []
        self._load()


    def _load(self):
        if(os.path.isfile(self._plan_file)):
            self._load_plan()
        if(os.path.isfile(self._settings_file)):
            self._load_settings()

    def get_current_wake_up_time_weekday(self):
        return self.wake_up_time_weekday.hour

    def take_one(self):
        if self._plan[-1].is_done():
            self._plan.pop()
        else:
            self._plan[-1].take_one()

    def get_next_time_string(self):
        if self.is_done():
            return "--:--"
        else:
            return self._plan[-1].get_next_string()

    def get_next_time(self):
        if self.is_done():
            return None
        else:
            return self._plan[-1].get_next()

    def get_current_dose(self):
        if self._plan:
            return self._plan[-1].dose
        else:
            return 0

    def get_end_date(self):
        return self._plan[0].date

    def is_done(self):
        return False if self._plan else True

    def update(self, dose, wake_up_time_weekday, wake_up_time_weekend, bed_time_weekday, bed_time_weekend):
        if dose > 0:
            self.wake_up_time_weekday = wake_up_time_weekday
            self.wake_up_time_weekend = wake_up_time_weekend
            self._bed_time_weekday = bed_time_weekday
            self._bed_time_weekend = bed_time_weekend
            self._start_date = date.today()
            self.start_dose = dose
            self._plan = self._create_plan()

    def update_wake_up_and_bed_time(self, wake_up_time_weekday, wake_up_time_weekend, bedtime_weekday, bedtime_weekend):
        if self.get_current_dose() > 0:
            self.wake_up_time_weekday = wake_up_time_weekday
            self.wake_up_time_weekend = wake_up_time_weekend
            self.bedtime_weekday = bedtime_weekday
            self.bedtime_weekend = bedtime_weekend
            current_day = self._plan[-1]
            self._start_date = current_day.date
            self.start_dose = current_day.dose
            self._plan = self._create_plan()

    def _get_master_plan(self):
        if os.path.isfile(self._plan_file):
            return self._load_plan()
        else:
            new_plan = self._create_plan()
            self._save_plan(new_plan)
            return new_plan

    def _create_plan(self):
        current_date = self._start_date
        current_dose = self.start_dose
        days_left_on_dose = self._get_days_left_on_dose(current_dose)
        new_plan = []
        if current_dose > 0:
            while True:
                wake_up_time = self._get_wake_up_time(current_date)
                bedtime = self._get_bedtime(current_date)
                weekday = self._get_weekday(current_date)
                new_plan.append(Day(current_date, weekday, current_dose, wake_up_time, bedtime))
                current_date += timedelta(days=1)
                days_left_on_dose -= 1
                if days_left_on_dose == 0:
                    current_dose -= 1
                    if current_dose == 0:
                        break;
                    else:
                        days_left_on_dose = self._get_days_left_on_dose(current_dose)
        new_plan.reverse()
        self.initial_days_in_plan = len(new_plan)
        self._save_plan(new_plan)
        self._save_settings()
        return new_plan

    def get_current_day(self):
        return self.initial_days_in_plan - len(self._plan)

    @staticmethod
    def _get_days_left_on_dose(current_dose):
        if current_dose > 0:
            return int(3 / (current_dose/24))
        else:
            return 0

    def _get_wake_up_time(self, current_date):
        day = self._get_weekday(current_date)
        if day in ['Saturday', 'Sunday']:
            return self.wake_up_time_weekend
        else:
            return self.wake_up_time_weekday

    def _get_bedtime(self, current_date):
        day = self._get_weekday(current_date)
        if day in ['Saturday', 'Sunday']:
            return self.bedtime_weekend
        else:
            return self.bedtime_weekday

    @staticmethod
    def _get_weekday(current_date):
        weekdays = ['Monday', 'TuesDay', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return weekdays[current_date.weekday()]

    def _save_plan(self, plan):
        with open(self._plan_file, 'wb') as f:
            pickle.dump(plan, f)

    def _load_plan(self):
        if os.path.isfile(self._plan_file):
            with open(self._plan_file, 'rb') as f:
                self._plan = pickle.load(f)

    def _save_settings(self):
        settings = {"time": [self.wake_up_time_weekday, self.wake_up_time_weekend, self.bedtime_weekday, self.bedtime_weekend],
                    "dose": self.start_dose,
                    "initial_days": self.initial_days_in_plan}
        with open(self._settings_file, 'wb') as f:
            pickle.dump(settings, f)

    def _load_settings(self):
        if os.path.isfile(self._settings_file):
            with open(self._settings_file, 'rb') as f:
                settings = pickle.load(f)
                self.wake_up_time_weekday, self.wake_up_time_weekend, self.bedtime_weekday, self.bedtime_weekend = settings["time"]
                self.start_dose = settings["dose"]
                self.initial_days_in_plan = settings["initial_days"]

    def __str__(self):
        str = "["
        for day in self._plan:
            str += f"{day}, "
        return str.strip().strip(',') + ']'


if __name__ == '__main__':
    start_date = date.today()
    dose = 7
    bedtime = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=19, minute=0)
    wake_up_time = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=7, minute=0)

    plan = Plan()
    plan.update(dose, wake_up_time, wake_up_time, bedtime, bedtime)
    print(plan)
    bedtime = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=21, minute=0)
    wake_up_time = datetime(year=start_date.year, month=start_date.month, day=start_date.day, hour=9, minute=0)
    plan.update(6, wake_up_time, wake_up_time, bedtime, bedtime)
    print(plan)
