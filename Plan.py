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

    def __radd__(self, day_plan):
        day_plan.append(self)

    def next(self, time_diff):
        time = self._time + timedelta(minutes=time_diff)
        return SnusTime(time)


class DayPlan:
    start_time = datetime(year=1970, month=1, day=1, hour=7, minute=0, second=0)
    end_time = datetime(year=1970, month=1, day=1, hour=21, minute=0, second=0)

    def __init__(self, plan_date, dose_today):
        self._start_time = self._get_date_time(plan_date, self.start_time)
        self._end_time = self._get_date_time(plan_date, self.end_time)
        self._min_between = self._get_min_between(dose_today)
        self._day_plan = self._get_plan(dose_today)

    @property
    def done(self):
        return not self._day_plan

    @staticmethod
    def _get_date_time(date, time):
        return datetime(year=date.year,
                        month=date.month,
                        day=date.day,
                        hour=time.hour,
                        minute=time.minute,
                        second=time.second)

    def _get_min_between(self, dose_today):
        day_in_min = self._get_snus_day_in_min(dose_today, self._start_time, self._end_time)
        return int(day_in_min/(dose_today-1))

    @staticmethod
    def _get_snus_day_in_min(dose_today, start_time, end_time):
        day_in_min = (end_time.hour - start_time.hour) * 60 + (end_time.minute - start_time.minute)
        if dose_today > 1:
            return int(day_in_min - (day_in_min/dose_today) * 0.5)
        else:
            return day_in_min

    def _get_plan(self, dose_today):
        day_plan = []
        snus_time = SnusTime(self._start_time)
        day_plan.append(snus_time)
        if dose_today > 1:
            for i in range(dose_today-1):
                snus_time = snus_time.next(self._min_between)
                day_plan.append(snus_time)
        day_plan.reverse()
        return self._remove_passed(day_plan)

    @staticmethod
    def _remove_passed(daily_plan):
        out_l = []
        now = datetime.now()
        for time in daily_plan:
            if time.time > now:
                out_l.append(time)
        return out_l


    def next(self):
        self._day_plan.pop()

    def get_next_time(self):
        return self._day_plan[-1].time

    def get_next_time_string(self):
        return self._day_plan[-1].time_string

    def get_next_day(self, dose):
        plan_date = self._start_time + timedelta(days=1)
        return DayPlan(plan_date, dose)

    def __str__(self):
        string = ""
        for snus_time in self._day_plan:
            string += f"{snus_time.time_string}\n"
        return string


if __name__ == '__main__':
    dose = 7
    day_plan = DayPlan(dose)
    print(day_plan)
    day_plan.next()
    print(day_plan)
