from datetime import datetime

from service.models import Room, Booking


def _get_free_rooms(self):
    """
    Getting free rooms in the given time period.
    """
    start_time = datetime.strptime(self.request.GET.get('start_time'),
                                   '%y-%m-%d_%H:%M:%S').astimezone()
    end_time = datetime.strptime(self.request.GET.get('end_time'),
                                 '%y-%m-%d_%H:%M:%S').astimezone()
    indexes = []
    for room in Room.objects.all():
        flag = True
        for booking in Booking.objects.filter(room=room):
            if (start_time <= booking.start_time <= end_time or
                    booking.start_time <= start_time <= booking.end_time or
                    start_time < booking.start_time and end_time > booking.end_time or
                    booking.start_time < start_time and booking.end_time > end_time):
                flag = False
                break
        if flag:
            indexes.append(room.id)
    return Room.objects.filter(id__in=indexes)
