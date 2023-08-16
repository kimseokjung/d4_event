from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import async_to_sync
from datetime import datetime, timedelta
import asyncio
import requests

from api.models import Countdown

from firebase_admin import messaging


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
                countdown.stop_countdown()
                break
            countdown.update_countdown()

            if countdown.remaining_time.total_seconds() == 0:
                if countdown.countdown_in_progress:
                    countdown_data = {
                        'command': 'countdown_started',
                        'message': '1시간 15분 카운트 다운 종료'
                    }
                    await self.send_firebase_notification(
                        message_title='D4 Tracker',
                        message_body='지옥물결이 시작되었습니다.',
                    )
                else:
                    countdown_data = {
                        'command': 'countdown_finished',
                        'message': '1시간 카운트 다운 종료'
                    }
                await self.channel_layer_group_send(countdown_data)
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

    async def send_firebase_notification(self, message_title, message_body):
        server_key = "AAAAk_iyOjs:APA91bHPslDKOj1gNdSdpHjt2meWYqV7Eu9gXNPjuykJuRATMOoMbN0J_6fUG_XH-K9b0M1quDDrtJA4cm7IPdhTDDXUealB0Ysdb0zkU6mvguEZuvBYA_6CWVUcsQTFRbEb8hF667gq"
        url = 'https://fcm.googleapis.com/fcm/send'

        message = {
            'notification': {
                'title': message_title,
                'body': message_body,
            },
            'to': '/topics/countdown_finished'
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'key={server_key}'
        }

        try:
            response = requests.post(
                url,
                json=message,
                headers=headers,
            )
            print('Successfully sent message:', response)
        except Exception as e:
            print(f"Error : {e}")
