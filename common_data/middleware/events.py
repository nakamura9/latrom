from messaging.models import Notification
from planner.models import Event
from django.db.models import Q
import datetime

class EventReminderMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        #skip api calls

        if 'api' in request.path or request.user.is_anonymous:
            return self.get_response(request)

        events = Event.objects.filter(
            Q(owner=request.user) & 
            Q(date__gte=datetime.date.today()) &
            Q(completed=False) &
            Q(reminder_notification__isnull=True))
        
        #there is a threshold for the reminder
        # if it has passed and no notification exists create the notification
        for event in events:
            event_start = datetime.datetime.combine(event.date, 
                event.start_time)
            event_reminder_time = event_start - event.reminder
            now = datetime.datetime.now()
            if now >= event_reminder_time:
                note = Notification.objects.create(
                    user=request.user,
                    title='Event reminder',
                    message=f"{event.label}: {event.description}"
                )
                event.reminder_notification = note
                event.save()

                for i in event.participants:
                    if i.employee and i.employee.user:
                         Notification.objects.create(
                            user=i.employee.user,
                            title='Event reminder',
                            message=f"{event.label}: {event.description}"
                        )

        return self.get_response(request)