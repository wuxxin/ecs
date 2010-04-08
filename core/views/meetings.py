import datetime
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from ecs.core.views.utils import render
from ecs.core.models import Meeting, Participation
from ecs.core.forms.meetings import MeetingForm, TimeTableEntryForm

def create_meeting(request):
    form = MeetingForm(request.POST or None)
    if form.is_valid():
        meeting = form.save()
        return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))
    return render(request, 'meetings/form.html', {
        'form': form,
    })
    
def meeting_list(request):
    return render(request, 'meetings/list.html', {
        'meetings': Meeting.objects.filter(start__gte=datetime.datetime.now()).order_by('start')
    })

def add_timetable_entry(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    entry = meeting.add_entry(duration=datetime.timedelta(minutes=15))
    import random
    for user in User.objects.order_by('?')[:random.randint(0, 3)]:
        Participation.objects.create(entry=entry, user=user)
    return HttpResponseRedirect(reverse('ecs.core.views.timetable_editor', kwargs={'meeting_pk': meeting.pk}))

def timetable_editor(request, meeting_pk=None):
    meeting = get_object_or_404(Meeting, pk=meeting_pk)
    return render(request, 'meetings/timetable/editor.html', {
        'meeting': meeting,
    })
    