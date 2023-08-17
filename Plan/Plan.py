from datetime import date, time, datetime, timedelta
import math
import os
import pickle


class Plan:
    def __init__(self):
        self.done = False
        self._days_on_daily_dose = 3
        self._pace = 0.1
        self._bed_time = self._get_bed_time(date.today())
        self._wake_up_time = self._get_wake_up_time(date.today())
        self._plan_file = "Data/plan.pkl"
        self._state = {"date": date.today(), "daily_dose": 0, "days_left_on_current_dose": 0, "day_plan": []}
        self._load_state()

    def get_next_snus_time_string(self):
        day_plan = self._state['day_plan']
        if day_plan:
            next_snus_time = self._state['day_plan'][-1]
            return next_snus_time.strftime('%d/%m %H:%M')
        else:
            return '--:--'

    def get_next_snus_time(self):
        day_plan = self._state['day_plan']
        if day_plan:
            return self._state['day_plan'][-1]
        else:
            self.get_next()
            self.get_next_snus_time()

    def _get_bed_time(self, now):
        return datetime(year=now.year, month=now.month, day=now.day, hour=19, minute=0)

    def _get_wake_up_time(self, now):
        return datetime(year=now.year, month=now.month, day=now.day, hour=7, minute=0)

    def setup(self, initial_daily_dose):
        self.done = False
        self._set_state(date.today(), initial_daily_dose, self._days_on_daily_dose, self._get_daily_plan(initial_daily_dose))
        self._save_state()

    def _set_state(self, current_date, daily_dose, days_left_on_current_dose, day_plan):
        self._state["date"] = current_date
        self._state["daily_dose"] = daily_dose
        self._state["days_left_on_current_dose"] = days_left_on_current_dose
        self._state["day_plan"] = day_plan
        self._wake_up_time = self._get_wake_up_time(self._state['date'])
        self._bed_time = self._get_bed_time(self._state['date'])
        if not self._state['day_plan']:
            self._update_state()

    def _get_daily_plan(self, daily_amount):
        daily_plan = []
        if daily_amount > 0:
            snus_time = self._wake_up_time
            day_in_min = (self._bed_time.hour - self._wake_up_time.hour) * 60 + (self._bed_time.minute - self._wake_up_time.minute)
            if daily_amount > 1:
                min_between_snus = int(day_in_min/(daily_amount-1))
            self._append_snus_time(daily_plan, snus_time)
            for i in range(daily_amount-1):
                snus_time += timedelta(minutes=min_between_snus)
                self._append_snus_time(daily_plan, snus_time)
            daily_plan.reverse()
        return self._remove_passed(daily_plan)

    def _remove_passed(self, daily_plan):
        out_l = []
        now = datetime.now()
        for d in daily_plan:
            if d > now:
                out_l.append(d)
        return out_l

    def _append_snus_time(self, plan, snus_time):
        if datetime.now() < snus_time:
            plan.append(snus_time)

    def get_next(self):
        if not self.done:
            self._load_state()
            if self._state['day_plan']:
                self._state['day_plan'].pop()
            if not self._state['day_plan']:
                self._update_state()
            self._save_state()
        if self._state['daily_dose'] == 0:
            self.done = True

    def _update_state(self):
        if not (self._state['days_left_on_current_dose'] == 0 and self._state['daily_dose'] == 0):
            self._state['days_left_on_current_dose'] -= 1
            if self._state['days_left_on_current_dose'] <= 0 and self._state['daily_dose'] > 0:
                self._state['daily_dose'] -= math.ceil(self._state['daily_dose'] * self._pace)
                if self._state['daily_dose'] == 0:
                    self._state['days_left_on_current_dose'] = 0
                else:
                    self._state['days_left_on_current_dose'] = int(self._days_on_daily_dose / (self._state['daily_dose']/24))

        self._state['date'] += timedelta(days=1)
        self._wake_up_time = self._get_wake_up_time(self._state['date'])
        self._bed_time = self._get_bed_time(self._state['date'])
        self._state['day_plan'] = self._get_daily_plan(self._state['daily_dose'])
        if self._state['daily_dose'] == 0:
            self.done = True

    def _save_state(self):
        with open(self._plan_file, 'wb') as f:
            pickle.dump(self._state, f)

    def _load_state(self):
        if os.path.isfile(self._plan_file):
            with open(self._plan_file, 'rb') as f:
                self._state = pickle.load(f)

    def __str__(self):
        return f"daily_snus:{ self._state['daily_dose']}\n" \
               f"days_left_on_dose: {self._state['days_left_on_current_dose']}\n" \
               f"date: {self._state['date']}\n" \
               f"plan: {self._state['day_plan']}"


if __name__ == '__main__':
    plan = Plan()
    plan.setup(6)

    while not plan.done:
        plan.get_next()
        print(plan)
