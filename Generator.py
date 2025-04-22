from datetime import datetime, timedelta
from math import floor
from itertools import count


class Snuff:
    def __init__(self, dose, last):
        self._dose = dose
        self._last = last
        self._plan = self._get_plan()

    @property
    def dose(self):
        return self._dose

    @dose.setter
    def dose(self, set_dose):
        self._dose = set_dose

    @property
    def last(self):
        if not self._last:
            self._last = self.next
        return self._last

    @last.setter
    def last(self, time):
        self._last = time

    @property
    def delta(self):
        hours_per_day = 16
        hours = floor(hours_per_day/ self._dose)
        minutes = floor(((hours_per_day / self._dose) - hours) * 60)
        return timedelta(hours=hours, minutes=minutes)

    @property
    def next(self):
        self._last = next(self.plan)
        return self._last

    @property
    def plan(self):
        return self._plan

    def _get_plan(self):
        return (self._last + self.delta for _ in count(1))

    def new_day(self):
        self._last = datetime.now()
