from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
import asyncio

from api.models import Countdown


class CountdownConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'countdown_group'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )
        # countdown = Countdown.objects.first()
        # countdown.stop_countdown()

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')

        if command == 'start_countdown':
            countdown = Countdown.objects.first()
            countdown.remaining_time = timedelta(seconds=0)
            countdown.countdown_in_progress = False
            countdown.start_or_reset_countdown()

            countdown_data = {
                'command': 'start_countdown',
                'remaining_seconds': int(countdown.remaining_time.total_seconds()),
            }
            await self.channel_layer_group_send(countdown_data)

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
            await self.channel_layer_group_send(countdown_data)

            await self.send_countdown_data(countdown_data)

        elif command == 'reserve_countdown':
            reservation_time_str = data.get('reservation_time')
            if reservation_time_str:
                reservation_time = datetime.fromisoformat(reservation_time_str)

                while reservation_time > datetime.now():
                    await asyncio.sleep(1)
                else:
                    countdown = Countdown.objects.first()
                    countdown.remaining_time = timedelta(seconds=0)
                    countdown.countdown_in_progress = False
                    countdown.start_or_reset_countdown()

                    countdown_data = {
                        'command': 'start_countdown',
                        'remaining_seconds': int(countdown.remaining_time.total_seconds()),
                    }
                    await self.channel_layer_group_send(countdown_data)

                    await self.send_countdown_data(countdown_data)
                    await self.start_countdown_timer(countdown)

    async def send_countdown_data(self, countdown_data):
        await self.send(text_data=json.dumps(countdown_data))

    async def countdown_tick(self, event):
        countdown_data = event['data']
        await self.send(text_data=json.dumps(countdown_data))

    async def start_countdown_timer(self, countdown):
        while countdown.active:
            countdown_data = {
                'command': 'countdown_tick',
                'remaining_seconds': int(countdown.remaining_time.total_seconds()),
            }

            await self.channel_layer_group_send(countdown_data)

            await self.send_countdown_data(countdown_data)
            await asyncio.sleep(1)

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

    async def channel_layer_group_send(self, countdown_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'countdown_tick',
                'data': countdown_data,
            }
        )
