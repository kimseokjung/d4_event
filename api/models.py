from django.db import models
from django.utils import timezone
from datetime import timedelta


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class Countdown(models.Model):
    remaining_time = models.DurationField(null=True, blank=True)
    countdown_in_progress = models.BooleanField(default=False)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"Countdown: {self.remaining_time}"

    def stop_countdown(self):
        print('@ model stop call !!!')
        print(f'active : {self.active}')
        self.remaining_time = timedelta()
        self.countdown_in_progress = False
        self.active = False
        self.save()

    def update_countdown(self):
        if self.active and self.remaining_time.total_seconds() > 0:
            self.remaining_time -= timedelta(seconds=1)
            self.save()
        else:
            self.stop_countdown()
            print('update error')

    def start_or_reset_countdown(self):
        print('@ model start call')
        self.active = True
        # 시간 15분 또는 1시간 카운트 다운 설정
        if self.countdown_in_progress:
            print('1시간 카운트 다운')
            self.remaining_time = timedelta(seconds=10)
            self.countdown_in_progress = False
        else:
            print('1시간 15분 카운트 다운')
            self.remaining_time = timedelta(seconds=15)
            self.countdown_in_progress = True

        self.save()

    def start_countdown_with_reservation(self, total_seconds):
        self.remaining_time = timedelta(seconds=total_seconds)
        self.countdown_in_progress = True
        self.active = True
        self.save()

    def send_countdown_data(self, data):
        channel_layer = get_channel_layer()
        channel_layer.group_send(
            'countdown_group',
            {
                'type': 'countdown.tick',
                'data': data,
            }
        )
