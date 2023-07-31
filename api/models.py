from django.db import models
from django.utils import timezone
from datetime import timedelta


class Countdown(models.Model):
    remaining_time = models.DurationField(null=True, blank=True)
    countdown_in_progress = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Countdown: {self.remaining_time}"

    def stop_countdown(self):
        print('@ model stop call !!!')
        print(f'active : {self.active}')
        self.remaining_time = timedelta(hours=0, minutes=0)
        self.countdown_in_progress = False
        self.active = False
        self.save()

    def update_countdown(self):
        print('@ model update')
        print(f'active : {self.active}')
        if self.active and self.remaining_time.total_seconds() >= 0:
            self.remaining_time -= timedelta(seconds=1)
            self.save()
            print(f'time : {self.remaining_time.total_seconds()}')
        else:
            print('update error')

    def start_or_reset_countdown(self):
        print('@ model start call')
        if self.remaining_time.total_seconds() >= 0:
            # 0초가 되었을때 1시간 15분 또는 1시간 카운드 다운 설정
            if self.countdown_in_progress:
                print('1시간 카운트 다운')
                self.remaining_time = timedelta(seconds=10)
                self.countdown_in_progress = False
            else:
                print('1시간 15분 카운트 다운')
                self.remaining_time = timedelta(seconds=15)
                self.countdown_in_progress = True
        self.active = True
        self.save()
