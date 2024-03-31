from datetime import date, datetime, timedelta
import os
import pickle


class SnusTime:
    def __init__(self, time):
        self._time = time

    @property
    def time(self):
        return self._time

    @property
    def time_string(self):
        return self._time.strftime("%d/%m %H:%M")

    def next(self, time_diff):
        time = self._time + timedelta(minutes=time_diff)
        return SnusTime(time)


class DayPlan:
    start_time = datetime(year=1970, month=1, day=1, hour=7, minute=0, second=0)
    end_time = datetime(year=1970, month=1, day=1, hour=21, minute=0, second=0)

    def __init__(self, plan_date, day_dose):
        self._plan_date = plan_date
        self._day_dose = day_dose
        self._day_plan = self._get_day_plan()

    def _get_date_time(self, time):
        return datetime(year=self._plan_date.year,
                        month=self._plan_date.month,
                        day=self._plan_date.day,
                        hour=time.hour,
                        minute=time.minute,
                        second=time.second)

    def _get_delta_min(self):
        day_start = self._get_date_time(self.start_time)
        day_end = self._get_date_time(self.end_time)
        day_in_min = self._get_day_in_min(self._day_dose, day_start, day_end)
        return int(day_in_min/(self._day_dose-1))

    @staticmethod
    def _get_day_in_min(dose_today, start_time, end_time):
        day_in_min = (end_time.hour - start_time.hour) * 60 + (end_time.minute - start_time.minute)
        if dose_today > 1:
            return int(day_in_min - (day_in_min/dose_today) * 0.5)
        else:
            return day_in_min

    def _get_day_plan(self):
        plan = []
        day_start = self._get_date_time(self.start_time)
        delta_min = self._get_delta_min()
        snus_time = SnusTime(day_start)
        plan.append(snus_time)
        if self._day_dose > 1:
            for i in range(self._day_dose-1):
                snus_time = snus_time.next(delta_min)
                plan.append(snus_time)
        plan.reverse()
        return plan

    def next_day(self):
        self._plan_date = datetime.now() + timedelta(days=1)
        self._day_plan = self._get_day_plan()

    def pop(self):
        return self._day_plan.pop()

    @property
    def date(self):
        return self._plan_date

    @date.setter
    def date(self, plan_date):
        self._plan_date = plan_date
        self._day_plan = self._get_day_plan()

    @property
    def next(self):
        return self._day_plan[-1]

    @property
    def dose(self):
        return self._day_dose

    @dose.setter
    def dose(self, day_dose):
        self._day_dose = day_dose

    @property
    def done(self):
        return not self._day_plan

    def __str__(self):
        string = ""
        for snus_time in self._day_plan:
            string += f"{snus_time.time_string}\n"
        return string
