from datetime import datetime, timedelta
from math import floor
from itertools import count
from pathlib import Path
import pickle


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
        self._save_state()

    @property
    def last(self):
        return self._last

    @last.setter
    def last(self, time):
        self._last = time
        self._save_state()

    def get_next(self):
        self._last = next(self._plan)
        self._save_state()

    def _get_plan(self):
        return (self._last + self._delta() for _ in count(1))

    def _delta(self):
        hours_per_day = 16
        hours = floor(hours_per_day / self._dose)
        minutes = floor(((hours_per_day / self._dose) - hours) * 60)
        return timedelta(hours=hours, minutes=minutes)

    def new_day(self):
        self.last = datetime.now()

    def _save_state(self):
        state_storage = Path(r"day.pkl")
        state = {"time": self._last, "dose": self._dose}
        with open(state_storage, 'wb') as f:
            pickle.dump(state, f)
