from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers

from service.models import Room, Booking


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):

    client = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        for booking in Booking.objects.filter(room=data['room']):
            """
            Checking whether the booking time period does not intersect with the other ones.
            """

            start_time = data['start_time'].astimezone()
            end_time = data['start_time'].astimezone()
            if (
                    (
                        start_time <= booking.start_time <= end_time or
                        booking.start_time <= end_time <= booking.end_time or
                        start_time < booking.start_time and end_time > booking.end_time or
                        booking.start_time < start_time and booking.end_time > end_time
                    ) or timezone.now() > start_time
            ):
                raise serializers.ValidationError(
                    'The room is unavailable in the selected time period.'
                )
        return data
