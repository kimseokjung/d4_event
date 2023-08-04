import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Countdown
from datetime import timedelta, datetime
from django.utils import timezone

from asgiref.sync import sync_to_async


class CountdownConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        countdown = Countdown.objects.first()
        countdown.stop_countdown()

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        print(f'command: {command}')

        if command == 'start_countdown':
            countdown = Countdown.objects.first()
            countdown.remaining_time = timedelta(seconds=0)
            countdown.countdown_in_progress = False
            countdown.start_or_reset_countdown()

            countdown_data = {
                'command': 'start_countdown',
                'remaining_seconds': int(countdown.remaining_time.total_seconds()),
            }

            await self.send_countdown_data(countdown_data)
            await self.start_countdown_timer(countdown)

        elif command == 'stop_countdown':
            countdown = Countdown.objects.first()
            countdown.active = False
            countdown.stop_countdown()

            countdown_data = {
                'command': 'stop_countdown',
                'remaining_seconds': 0,
            }

            await self.send_countdown_data(countdown_data)

        elif command == 'reserve_countdown':
            reservation_time_str = data.get('reservation_time')
            print(reservation_time_str)
            if reservation_time_str:
                reservation_time = timezone.datetime.fromisoformat(
                    reservation_time_str)
                print(reservation_time)

                # 예약시간 확인 루프
                while reservation_time > datetime.now():
                    # 1초마다 확인
                    await self.sleep_time(1)
                else:
                    # 루프를 벗어 났다면 예약시간!
                    print('== Start reservation! ==')
                    countdown = Countdown.objects.first()
                    countdown.remaining_time = timedelta(seconds=0)
                    countdown.countdown_in_progress = False
                    countdown.start_or_reset_countdown()

                    countdown_data = {
                        'command': 'start_countdown',
                        'remaining_seconds': int(countdown.remaining_time.total_seconds()),
                    }

                    await self.send_countdown_data(countdown_data)
                    await self.start_countdown_timer(countdown)

    async def send_countdown_data(self, countdown_data):
        await self.send(text_data=json.dumps(countdown_data))

    async def start_countdown_timer(self, countdown):
        while countdown.active:
            # print(f'progress : {countdown.countdown_in_progress}')
            countdown_data = {
                'command': 'countdown_tick',
                'remaining_seconds': int(countdown.remaining_time.total_seconds()),
            }
            await self.send_countdown_data(countdown_data)
            await self.sleep_time(1)

            countdown = Countdown.objects.first()
            if not countdown.active:
                break
            countdown.update_countdown()

            if countdown.remaining_time.total_seconds() == 0:
                if countdown.countdown_in_progress:
                    countdown_data = {
                        'command': 'countdown_finished',
                        'message': '1시간 15분 카운트 다운 종료'
                    }
                else:
                    countdown_data = {
                        'command': 'countdown_finished',
                        'message': '1시간 카운트 다운 종료'
                    }
                await self.send_countdown_data(countdown_data)
                countdown.start_or_reset_countdown()

    # async def countdown_tick(self, event):
    #     countdown_data = event['data']
    #     await self.send_countdown_data(countdown_data)

    async def sleep_time(self, seconds):
        await asyncio.sleep(seconds)
