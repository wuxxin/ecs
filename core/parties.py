from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from ecs.users.utils import sudo

class Party(object):
    def __init__(self, organization=None, name=None, user=None, email=None, involvement=None, anonymous=False):
        self.organization = organization
        self._name = name
        self._email = email
        self.user = user
        self.involvement = involvement
        self._anonymous = anonymous
        
    @property
    def email(self):
        if self._email:
            return self._email
        if self.user:
            return self.user.email
        return None
    
    @property
    def name(self):
        name = self._name or self.user or self._email
        if self._anonymous or not name:
            return u'- anonymous -'
        return unicode(name)

@sudo()
def get_presenting_parties(sf, include_workflow=True):
    parties = [Party(organization=sf.sponsor_name, name=sf.sponsor_contact.full_name, user=sf.sponsor, email=sf.sponsor_email, involvement=_("Sponsor"))]

    if sf.invoice:
        parties.append(Party(organization=sf.invoice_name, 
            name=sf.invoice_contact.full_name, 
            email=sf.invoice_email, 
            user=sf.invoice,
            involvement=_("Invoice")
        ))
    parties.append(Party(organization=sf.submitter_organisation, 
        name=sf.submitter_contact.full_name, 
        email=sf.submitter_email,
        user=sf.submitter, 
        involvement=_("Submitter"),
    ))
    parties.append(Party(user=sf.presenter, involvement=_("Presenter")))

    for i in sf.investigators.filter(main=True):
        parties.append(Party(organization=i.organisation, name=i.contact.full_name, user=i.user, email=i.email, involvement=_("Primary Investigator")))

    return parties

@sudo()
def get_reviewing_parties(sf, include_workflow=True):
    from ecs.users.middleware import current_user_store

    parties = []

    anonymous = current_user_store._previous_user and not current_user_store._previous_user.ecs_profile.internal
    if include_workflow:
        from ecs.tasks.models import Task
        for task in Task.objects.filter(workflow_token__in=sf.submission.workflow.tokens.filter(consumed_at__isnull=False).values('pk').query).select_related('task_type'):
            if task.assigned_to == sf.submission.external_reviewer_name:
                parties.append(Party(user=task.assigned_to, involvement=task.task_type.trans_name, anonymous=anonymous))
            else:
                parties.append(Party(user=task.assigned_to, involvement=task.task_type.trans_name))

    for user in User.objects.filter(meeting_participations__entry__submission=sf.submission):
        parties.append(Party(user=user, involvement=_("Board Member Review")))

    for user in sf.submission.additional_reviewers.all():
        parties.append(Party(user=user, involvement=_("Additional Review"), anonymous=anonymous))

    return parties


def get_involved_parties(sf, include_workflow=True):
    presenting_parties = get_presenting_parties(sf, include_workflow=include_workflow)
    reviewing_parties = get_reviewing_parties(sf, include_workflow=include_workflow)

    return presenting_parties + reviewing_parties

