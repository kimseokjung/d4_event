from rest_framework import serializers
from .models import Countdown


class CountdownSerializer(serializers.ModelSerializer):

    class Meta:
        model = Countdown
        fields = '__all__'
