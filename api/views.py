
import json
import asyncio

from rest_framework import viewsets
from .models import Countdown
from .serializers import CountdownSerializer
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from datetime import timedelta, datetime

from asgiref.sync import sync_to_async
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from channels.layers import get_channel_layer


# class EventViewSet(viewsets.ModelViewSet):
#     queryset = Countdown.objects.first()
#     serializer_class = CountdownSerializer


def index(request):
    return render(request, 'api/api_main.html')


# def start_countdown(request, event_id):
#     try:
#         countdown = Countdown.objects.first()
#         # countdown.start_countdown()

#         countdown_data = {
#             'command': 'start_countdown',
#             'remaining_seconds': int(countdown.remaining_time.total_seconds()),
#         }

#         return JsonResponse(countdown_data)
#     except Exception as e:
#         return JsonResponse({'Error': e})


def stop_countdown(request):
    try:
        print('00')
        countdown = Countdown.objects.first()
        countdown.stop_countdown()
        countdown_data = {
            'command': 'stop_countdown',
            'remaining_seconds': 0,
        }

        return JsonResponse(countdown_data)
    except Exception as e:
        return JsonResponse({'Error': e})


# @sync_to_async
# def start_countdown():
#     print("start countdown init")
#     countdown = Countdown.objects.get(id=63)
#     countdown.remaining_time = timedelta(hours=1, minutes=15)
#     countdown.save()
#     print(countdown.id)

#     print(f'remaining_time: {countdown.remaining_time}')

#     return countdown


# @sync_to_async
# def stop_countdown():
#     countdown = Countdown.objects.get(id=63)
#     countdown.stop_countdown()


# @sync_to_async
# def update_countdown():
#     countdown = Countdown.objects.get(id=63)
#     countdown.update_countdown()
# async def stop_countdown_view(request, event_id):
#     await stop_countdown()

#     countdown_data = {
#         'command': 'start_countdown',
#         'remaining_seconds': 0,
#     }
#     await send_countdown_data_to_all_clients(countdown_data)

#     return JsonResponse({'maessage': '카운트 다운 중지'})


# async def send_countdown_data_to_all_clients(countdown_data):
#     channel_layer = get_channel_layer()
#     await channel_layer.group_send(
#         "countdown_group", {
#             "type": "send_countdown_data",
#             "data": json.dumps(countdown_data)
#         })


# def start_hour_countdown(request, event_id):
#     countdown = Countdown.objects.first()
#     countdown.start_hour_countdown()
#     return JsonResponse({'message': '1시간 카운트 다운이 시작되었습니다.'})


# def stop_countdown(request, event_id):
#     countdown = Countdown.objects.get(id=63)
#     countdown.stop_countdown()

#     countdown_data = {
#         'command': 'stop_countdown',
#     }
#     send_countdown_data_to_all_clients(countdown_data)

#     return JsonResponse({'message': '카운트 다운이 중지되었습니다.'})
