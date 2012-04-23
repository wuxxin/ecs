from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify

from ecs.communication.utils import send_system_message_template
from ecs.utils import connect
from ecs.votes import signals
from ecs.users.utils import sudo
from ecs.tasks.models import Task
from ecs.votes.models import Vote
from ecs.documents.models import Document
from ecs.ecsmail.utils import deliver


@connect(signals.on_vote_creation)
def on_vote_creation(sender, **kwargs):
    vote = kwargs['vote']
    if vote.is_permanent:
        with sudo():
            Task.objects.for_data(vote.submission_form.submission).exclude(task_type__workflow_node__uid='b2_review').open().mark_deleted()

@connect(signals.on_vote_publication)
def on_vote_published(sender, **kwargs):
    vote = kwargs['vote']
    sf = vote.submission_form
    if sf and not sf.is_categorized_multicentric_and_local:
        parties = vote.submission_form.get_presenting_parties()
        reply_receiver = None
        with sudo():
            try:
                task = Task.objects.for_data(vote).closed().filter(task_type__groups__name='EC-Office').order_by('-closed_at')[0]
                reply_receiver = task.assigned_to
            except IndexError:
                pass
        parties.send_message(_('Vote {ec_number}').format(ec_number=vote.get_ec_number()), 'submissions/vote_publish.txt',
            {'vote': vote}, submission=vote.submission_form.submission, reply_receiver=reply_receiver)
    receivers = set()
    if (sf.is_amg and not sf.is_categorized_multicentric_and_local) or sf.is_mpg:
        receivers |= set(settings.ECS_AMG_MPG_VOTE_RECEIVERS)
    if sf.is_categorized_multicentric_and_main:
        investigators = sf.investigators.filter(ethics_commission__vote_receiver__isnull=False)
        receivers |= set(investigators.values_list('ethics_commission__vote_receiver', flat=True))
    bits = (
        'AMG' if sf.is_amg else None,
        'MPG' if sf.is_mpg else None,
        sf.eudract_number if sf.is_amg else sf.submission.ec_number,
        'Votum {0}'.format(vote.result),
    )
    name = slugify(u'_'.join(unicode(bit) for bit in bits if bit is not None))
    vote_ct = ContentType.objects.get_for_model(Vote)
    doc = Document.objects.get(content_type=vote_ct, object_id=vote.id)
    vote_pdf = doc.file.read()
    attachments = ((name + '.pdf', vote_pdf, 'application/pdf'),)
    for receiver in receivers:
        deliver(receiver, subject=name, message=_('Attached is the electronically signed vote.'), from_email=settings.DEFAULT_FROM_EMAIL, attachments=attachments)

@connect(signals.on_vote_expiry)
def on_vote_expiry(sender, **kwargs):
    print "vote expired", kwargs
    submission = kwargs['submission']
    submission.finish(expired=True)
