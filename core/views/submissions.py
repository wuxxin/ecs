# -*- coding: utf-8 -*-
from datetime import datetime
import tempfile
import re
from StringIO import StringIO

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.core.files import File
from django.template import Context, loader
from django.shortcuts import get_object_or_404
from django.forms.models import model_to_dict
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test

from ecs.documents.models import Document
from ecs.utils.viewutils import render, redirect_to_next_url, render_pdf, pdf_response
from ecs.core.models import Submission, SubmissionForm, Investigator, ChecklistBlueprint, ChecklistQuestion, Checklist, ChecklistAnswer
from ecs.meetings.models import Meeting

from ecs.core.forms import SubmissionFormForm, MeasureFormSet, RoutineMeasureFormSet, NonTestedUsedDrugFormSet, ForeignParticipatingCenterFormSet, \
    InvestigatorFormSet, InvestigatorEmployeeFormSet, SubmissionEditorForm, DocumentForm, SubmissionListFilterForm
from ecs.core.forms.checklist import make_checklist_form
from ecs.core.forms.review import RetrospectiveThesisReviewForm, ExecutiveReviewForm, BefangeneReviewForm
from ecs.core.forms.layout import SUBMISSION_FORM_TABS
from ecs.core.forms.voting import VoteReviewForm, B2VoteReviewForm

from ecs.core import paper_forms
from ecs.core import signals
from ecs.core.serializer import Serializer
from ecs.docstash.decorators import with_docstash_transaction
from ecs.docstash.models import DocStash
from ecs.utils.diff_match_patch import diff_match_patch
from ecs.audit.models import AuditTrail
from ecs.core.models import Vote


def get_submission_formsets(data=None, instance=None, readonly=False):
    formset_classes = [
        # (prefix, formset_class, callable SubmissionForm -> initial data)
        ('measure', MeasureFormSet, lambda sf: sf.measures.filter(category='6.1')),
        ('routinemeasure', RoutineMeasureFormSet, lambda sf: sf.measures.filter(category='6.2')),
        ('nontesteduseddrug', NonTestedUsedDrugFormSet, lambda sf: sf.nontesteduseddrug_set.all()),
        ('foreignparticipatingcenter', ForeignParticipatingCenterFormSet, lambda sf: sf.foreignparticipatingcenter_set.all()),
        ('investigator', InvestigatorFormSet, lambda sf: sf.investigators.all()),
    ]
    formsets = {}
    for name, formset_cls, initial in formset_classes:
        kwargs = {'prefix': name, 'readonly': readonly, 'initial': []}
        if readonly:
            kwargs['extra'] = 0
        if instance:
            kwargs['initial'] = [model_to_dict(obj, exclude=('id',)) for obj in initial(instance).order_by('id')]
        formsets[name] = formset_cls(data, **kwargs)

    employees = []
    if instance:
        for index, investigator in enumerate(instance.investigators.order_by('id')):
            for employee in investigator.employees.order_by('id'):
                employee_dict = model_to_dict(employee, exclude=('id', 'investigator'))
                employee_dict['investigator_index'] = index
                employees.append(employee_dict)
    kwargs = {'prefix': 'investigatoremployee', 'readonly': readonly}
    if readonly:
        kwargs['extra'] = 0
    formsets['investigatoremployee'] = InvestigatorEmployeeFormSet(data, initial=employees or [], **kwargs)
    return formsets


def copy_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    
    docstash = DocStash.objects.create(group='ecs.core.views.submissions.create_submission_form', owner=request.user)
    with docstash.transaction():
        docstash.update({
            'form': SubmissionFormForm(data=None, initial=model_to_dict(submission_form)),
            'formsets': get_submission_formsets(instance=submission_form),
            'submission': submission_form.submission,
            'documents': list(submission_form.documents.all().order_by('pk')),
        })
        docstash.name = "%s" % submission_form.project_title
    return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': docstash.key}))
    

def copy_latest_submission_form(request, submission_pk=None):
    submission_form = get_object_or_404(SubmissionForm, current_for_submission__pk=submission_pk)
    return HttpResponseRedirect(reverse('ecs.core.views.copy_submission_form', kwargs={
        'submission_form_pk': submission_form.pk
    }))


def readonly_submission_form(request, submission_form_pk=None, submission_form=None, extra_context=None, template='submissions/readonly_form.html', checklist_overwrite=None):
    if not submission_form:
        submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = SubmissionFormForm(initial=model_to_dict(submission_form), readonly=True)
    formsets = get_submission_formsets(instance=submission_form, readonly=True)
    documents = submission_form.documents.all().order_by('pk')
    vote = submission_form.current_vote
    submission = submission_form.submission

    retrospective_thesis_review_form = RetrospectiveThesisReviewForm(instance=submission, readonly=True)
    executive_review_form = ExecutiveReviewForm(instance=submission, readonly=True)
    befangene_review_form = BefangeneReviewForm(instance=submission, readonly=True)
    vote_review_form = VoteReviewForm(instance=vote, readonly=True)
    
    checklist_reviews = []
    for checklist in submission.checklists.all():
        if checklist_overwrite and checklist.blueprint in checklist_overwrite:
            checklist_form = checklist_overwrite[checklist.blueprint]
        else:
            checklist_form = make_checklist_form(checklist)(readonly=True)
        checklist_reviews.append((checklist.blueprint, checklist_form))
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'documents': documents,
        'readonly': True,
        'submission_form': submission_form,
        'vote': vote,
        'retrospective_thesis_review_form': retrospective_thesis_review_form,
        'executive_review_form': executive_review_form,
        'vote_review_form': vote_review_form,
        'checklist_reviews': checklist_reviews,
        'befangene_review_form': befangene_review_form,
        'pending_notifications': submission_form.notifications.all(),
        'answered_notficiations': [], # FIXME (FMD1)
        'pending_votes': submission_form.submission.votes.filter(published=False),
        'published_votes': submission_form.submission.votes.filter(published=True),
    }
    if extra_context:
        context.update(extra_context)
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, template, context)


def retrospective_thesis_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = RetrospectiveThesisReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        signals.post_thesis_review.send(submission_form.submission)
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'retrospective_thesis_review_form': form,})


def executive_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = ExecutiveReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'executive_review_form': form,})

def befangene_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    form = BefangeneReviewForm(request.POST or None, instance=submission_form.submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'befangene_review_form': form,})

def checklist_review(request, submission_form_pk=None, blueprint_pk=1):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    blueprint = get_object_or_404(ChecklistBlueprint, pk=blueprint_pk)
    checklist, created = Checklist.objects.get_or_create(blueprint=blueprint, submission=submission_form.submission, defaults={'user': request.user})
    if created:
        for question in blueprint.questions.order_by('text'):
            answer, created = ChecklistAnswer.objects.get_or_create(checklist=checklist, question=question)
    form_class = make_checklist_form(checklist)
    form = form_class(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        for i, question in enumerate(blueprint.questions.order_by('text')):
            answer = ChecklistAnswer.objects.get(checklist=checklist, question=question)
            answer.answer = form.cleaned_data['q%s' % i]
            answer.comment = form.cleaned_data['c%s' % i]
            answer.save()
    return readonly_submission_form(request, submission_form=submission_form, checklist_overwrite={blueprint: form})


def vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.current_vote
    if not vote:
        raise Http404("This SubmissionForm has no Vote yet.")
    vote_review_form = VoteReviewForm(request.POST or None, instance=vote)
    if request.method == 'POST' and vote_review_form.is_valid():
        vote_review_form.save()
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'vote_review_form': vote_review_form,})

def b2_vote_review(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    vote = submission_form.current_vote
    if not vote or not vote.result == '2':
        raise Http404("This SubmissionForm has no B2-Vote")
    b2_vote_review_form = B2VoteReviewForm(request.POST or None, initial={
        'text': vote.text,
    })
    if request.method == 'POST' and b2_vote_review_form.is_valid():
        v = b2_vote_review_form.save(commit=False)
        v.result = '1'
        v.text = b2_vote_review_form.cleaned_data['text']
        v.submission = vote.submission
        v.save()
        return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form_pk}) + '#vote_review_tab')
    return readonly_submission_form(request, submission_form=submission_form, extra_context={'b2_vote_review_form': b2_vote_review_form, 'b2_vote': vote})

@with_docstash_transaction
def create_submission_form(request):
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash['form']
        formsets = request.docstash['formsets']
    else:
        form = SubmissionFormForm(request.POST or None)
        formsets = get_submission_formsets(request.POST or None)

    document_form = DocumentForm(request.POST or None, request.FILES or None, document_pks=[x.pk for x in request.docstash.get('documents', [])], prefix='document')

    if request.method == 'POST':
        submit = request.POST.get('submit', False)
        autosave = request.POST.get('autosave', False)

        request.docstash.update({
            'form': form,
            'formsets': formsets,
            'documents': list(Document.objects.filter(pk__in=map(int, request.POST.getlist('documents')))),
        })
        request.docstash.name = "%s" % request.POST.get('project_title', '')

        if autosave:
            return HttpResponse('autosave successfull')
        
        if document_form.is_valid():
            documents = set(request.docstash['documents'])
            documents.add(document_form.save())
            replaced_documents = [x.replaces_document for x in documents if x.replaces_document]
            for doc in replaced_documents:  # remove replaced documents
                if doc in documents:
                    documents.remove(doc)
            request.docstash['documents'] = list(documents)
            document_form = DocumentForm(document_pks=[x.pk for x in documents], prefix='document')

        if submit and form.is_valid() and all(formset.is_valid() for formset in formsets.itervalues()):
            if not request.user.get_profile().approved_by_office:
                messages.add_message(request, messages.INFO, _('You cannot submit studies yet. Please wait until the office has approved your account.'))
            else:
                submission_form = form.save(commit=False)
                submission = request.docstash.get('submission') or Submission.objects.create()
                submission_form.submission = submission
                submission_form.save()
                form.save_m2m()
                submission_form.documents = request.docstash['documents']
            
                formsets = formsets.copy()
                investigators = formsets.pop('investigator').save(commit=False)
                for investigator in investigators:
                    investigator.submission_form = submission_form
                    investigator.save()
                for i, employee in enumerate(formsets.pop('investigatoremployee').save(commit=False)):
                    employee.investigator = investigators[int(request.POST['investigatoremployee-%s-investigator_index' % i])]
                    employee.save()

                for formset in formsets.itervalues():
                    for instance in formset.save(commit=False):
                        instance.submission_form = submission_form
                        instance.save()
                request.docstash.delete()
                return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    
    context = {
        'form': form,
        'tabs': SUBMISSION_FORM_TABS,
        'document_form': document_form,
        'documents': request.docstash.get('documents', []),
    }
    for prefix, formset in formsets.iteritems():
        context['%s_formset' % prefix] = formset
    return render(request, 'submissions/form.html', context)


def view_submission_form(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)
    return render(request, 'submissions/view.html', {
        'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
        'submission_form': submission_form,
        'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
    })


def submission_pdf(request, submission_form_pk=None):
    submission_form = get_object_or_404(SubmissionForm, pk=submission_form_pk)    
    filename = 'ek-%s-Einreichung.pdf' % submission_form.submission.ec_number.replace('/','-')
    
    if not submission_form.pdf_document:
        pdf = render_pdf(request, 'db/submissions/xhtml2pdf/view.html', {
            'paper_form_fields': paper_forms.get_field_info_for_model(SubmissionForm),
            'submission_form': submission_form,
            'documents': submission_form.documents.filter(deleted=False).order_by('doctype__name', '-date'),
        })
        doc = Document.objects.create_from_buffer(pdf)
        submission_form.pdf_document = doc
        submission_form.save()
        pdf = doc.file.read()
    
    submission_form.pdf_document.file.seek(0)
    pdf = submission_form.pdf_document.file.read()
    return pdf_response(pdf, filename=filename)


def submission_form_list(request):
    keyword = request.POST.get('keyword', None)

    if keyword:
        matched_submissions = set()
        search_query = Q(ec_number__icontains=keyword)

        m = re.match(r'(\d+)/(\d+)', keyword)
        if m:
            num = int(m.group(1))
            year = int(m.group(2))
            search_query |= Q(ec_number=('%04d/%04d' % (year, num)))
            search_query |= Q(ec_number=('%04d/%04d' % (num, year)))

        submissions = list()

        for submission in Submission.objects.filter(search_query):
            matched_submissions.add(submission)
        
        submission_forms = SubmissionForm.objects.exclude(current_for_submission=None).distinct()
        submission_form_pks = [sf.pk for sf in submission_forms]
        
        form_search_query = Q(project_title__icontains=keyword) | Q(german_project_title__icontains=keyword) | Q(sponsor_name__icontains=keyword) | Q(submitter_contact_last_name__icontains=keyword) | Q(investigators__contact_last_name__icontains=keyword) | Q(eudract_number__icontains=keyword)

        submission_forms = SubmissionForm.objects.filter(pk__in=submission_form_pks).filter(form_search_query)
        submissions += [sf.submission for sf in submission_forms]

        for submission in submissions:
            matched_submissions.add(submission)

        submissions = Submission.objects.filter(pk__in=[s.pk for s in matched_submissions]).distinct().order_by('ec_number')
        stashed_submission_forms = []  # FIXME: how to search in the docstash? (FMD1)
        meetings = [(meeting, meeting.submissions.filter(pk__in=submissions).distinct().order_by('ec_number')) for meeting in Meeting.objects.filter(submissions__in=submissions).order_by('-start').distinct()]
    else:
        submissions = Submission.objects.order_by('ec_number').distinct()
        stashed_submission_forms = DocStash.objects.filter(group='ecs.core.views.submissions.create_submission_form')
        meetings = [(meeting, meeting.submissions.order_by('ec_number').distinct()) for meeting in Meeting.objects.order_by('-start')]

    return render(request, 'submissions/list.html', {
        'unscheduled_submissions': submissions.filter(meetings__isnull=True),
        'meetings': meetings,
        'stashed_submission_forms': stashed_submission_forms,
    })


def edit_submission(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    
    form = SubmissionEditorForm(request.POST or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('ecs.core.views.submission_form_list'))
    
    return render(request, 'submissions/editor.html', {
        'form': form,
        'submission': submission,
    })

# FIXME: for testing purposes only (FMD1)
def start_workflow(request, submission_pk=None):
    submission = get_object_or_404(Submission, pk=submission_pk)
    from ecs.workflow.models import Graph
    wf = Graph.objects.get(model=Submission, auto_start=True).create_workflow(data=submission)
    wf.start()
    return HttpResponseRedirect(reverse('ecs.core.views.submission_form_list'))

def export_submission(request, submission_pk):
    submission = get_object_or_404(Submission, pk=submission_pk)
    submission_form = submission.current_submission_form
    serializer = Serializer()
    buf = StringIO()
    serializer.write(submission_form, buf)
    response = HttpResponse(buf.getvalue(), mimetype='application/ecx')
    response['Content-Disposition'] = 'attachment;filename=%s.ecx' % submission.ec_number.replace('/', '-')
    return response

def import_submission_form(request):
    if 'file' in request.FILES:
        serializer = Serializer()
        submission_form = serializer.read(request.FILES['file'])
        return HttpResponseRedirect(reverse('ecs.core.views.readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
    return render(request, 'submissions/import.html', {
    
    })

def _render_submission_form(instance, ignored_fields=[]):
    ignored_fields = list(ignored_fields)

    fields = [x for x in instance.__class__._meta.get_all_field_names() if not x in list(ignored_fields)+['id']]
    fields.sort()

    rendered_fields = {}
    for field in fields:
        try:
            value = getattr(instance, field) or ''
        except AttributeError:
            try:
                value = getattr(instance, '%s_set' % field) or ''
            except AttributeError, e:
                print 'Error: %s %s: %s' % (instance, field, e)
                continue
        except Exception, e:
            print 'Error: %s %s: %s' % (instance, field, e)
            continue

        if hasattr(value, 'all'):  # x-to-many-relation
            rendered = u', '.join([unicode(x) for x in value.all()])
        elif isinstance(value, models.Model):  # foreign-key
            rendered = unicode(value)
        else:  # all other values
            rendered = unicode(value).replace(u'\n', u'<br />\n')


        rendered_fields[field] = rendered

    return rendered_fields

def diff(request, old_submission_form_pk, new_submission_form_pk):
    old_submission_form = get_object_or_404(SubmissionForm, pk=old_submission_form_pk)
    new_submission_form = get_object_or_404(SubmissionForm, pk=new_submission_form_pk)

    sff = SubmissionFormForm(None, instance=old_submission_form)

    differ = diff_match_patch()
    diffs = []

    ignored_fields = ('submission', 'current_for', 'primary_investigator', 'current_for_submission', 'documents')
    old = _render_submission_form(old_submission_form, ignored_fields=ignored_fields)
    new = _render_submission_form(new_submission_form, ignored_fields=ignored_fields)

    for field in sorted(old.keys()):
        diff = differ.diff_main(old[field], new[field])
        if differ.diff_levenshtein(diff):
            try:
                label = sff.fields[field].label
            except KeyError:
                label = field
            differ.diff_cleanupSemantic(diff)
            diffs.append((label, diff))

    
    ctype = ContentType.objects.get_for_model(old_submission_form)
    old_document_creation_date = AuditTrail.objects.get(content_type__pk=ctype.id, object_id=old_submission_form.id, object_created=True).created_at
    new_document_creation_date = AuditTrail.objects.get(content_type__pk=ctype.id, object_id=new_submission_form.id, object_created=True).created_at

    ctype = ContentType.objects.get_for_model(Document)
    new_document_pks = [x.object_id for x in AuditTrail.objects.filter(content_type__pk=ctype.id, created_at__gt=old_document_creation_date, created_at__lte=new_document_creation_date)]

    ctype = ContentType.objects.get_for_model(old_submission_form)
    submission_forms = [x.pk for x in new_submission_form.submission.forms.all()]
    new_documents = Document.objects.filter(content_type__pk=ctype.id, object_id__in=submission_forms, pk__in=new_document_pks)

    print new_documents

    return render(request, 'submissions/diff.html', {
        'submission': new_submission_form.submission,
        'diffs': diffs,
        'new_documents': new_documents,
    })

@with_docstash_transaction
def wizard(request):
    from ecs.core.forms.wizard import get_wizard_form
    if request.method == 'GET' and request.docstash.value:
        form = request.docstash['form']
        screen_form = get_wizard_form('start')(prefix='wizard')
    else:
        form = SubmissionFormForm(request.POST or None)
        name = request.POST.get('wizard-name', 'start')
        screen_form = get_wizard_form(name)(request.POST or None, prefix='wizard')
        if screen_form.is_valid():
            if screen_form.is_terminal():
                request.docstash.group = 'ecs.core.views.submissions.create_submission_form'
                request.docstash.save()
                return HttpResponseRedirect(reverse('ecs.core.views.create_submission_form', kwargs={'docstash_key': request.docstash.key}))

            typ, obj = screen_form.get_next()
            if typ == 'wizard':
                screen_form = obj(prefix='wizard')
            elif typ == 'redirect':
                return HttpResponseRedirect(obj)
            else:
                raise ValueError

    return render(request, 'submissions/wizard.html', {
        'form': screen_form,
    })

@user_passes_test(lambda u: u.ecs_profile.internal)
def submission_widget(request, template='submissions/widget.html', limit=5):
    usersettings = request.user.ecs_settings

    filter_dict = {
        'new': usersettings.show_new_submissions,
        'next_meeting': usersettings.show_next_meeting_submissions,
        'b2': usersettings.show_b2_submissions,
        'amg': usersettings.show_amg_submissions,
        'mpg': usersettings.show_mpg_submissions,
        'thesis': usersettings.show_thesis_submissions,
        'other': usersettings.show_other_submissions,
    }
    submissionfilter_session_key = 'submissions:filter'
    filterform = SubmissionListFilterForm(request.POST or request.session.get(submissionfilter_session_key, filter_dict))
    filterform.is_valid()  # force clean
    request.session[submissionfilter_session_key] = filterform.cleaned_data
    request.session.save()
    
    usersettings.show_new_submissions = filterform.cleaned_data['new']
    usersettings.show_next_meeting_submissions = filterform.cleaned_data['next_meeting']
    usersettings.show_b2_submissions = filterform.cleaned_data['b2']
    usersettings.show_amg_submissions = filterform.cleaned_data['amg']
    usersettings.show_mpg_submissions = filterform.cleaned_data['mpg']
    usersettings.show_thesis_submissions = filterform.cleaned_data['thesis']
    usersettings.show_other_submissions = filterform.cleaned_data['other']
    usersettings.save()

    submission_pks=[]
    if usersettings.show_new_submissions:
        submission_pks += [x['pk'] for x in Submission.objects.new().values('pk')]
    if usersettings.show_next_meeting_submissions:
        try:
            next_meeting = Meeting.objects.all().order_by('-start')[0]
        except IndexError:
            pass
        else:
            submission_pks += [x.pk for x in next_meeting.submissions.all()]
    if usersettings.show_b2_submissions:
        submission_pks += [x['pk'] for x in Submission.objects.b2().values('pk')]
    submissions = Submission.objects.filter(pk__in=submission_pks)

    print submissions

    submission_pks=[]
    print submission_pks
    if usersettings.show_amg_submissions:
        submission_pks += [x['pk'] for x in submissions.amg().values('pk')]
    if usersettings.show_mpg_submissions:
        submission_pks += [x['pk'] for x in submissions.mpg().values('pk')]
    if usersettings.show_thesis_submissions:
        submission_pks += [x['pk'] for x in submissions.thesis().values('pk')]
        print 'thesis'
        print submission_pks
    if usersettings.show_other_submissions:
        submission_pks += [x['pk'] for x in submissions.exclude(is_amg=True).exclude(is_mpg=True).exclude(thesis=True).values('pk')]
    submissions = submissions.filter(pk__in=submission_pks).order_by('-current_submission_form__pk')
    if limit:
        submissions = submissions[:limit]

    return render(request, template, {
        'submissions': submissions,
        'submissions_count': Submission.objects.count(),
        'filterform': filterform,
    })

@user_passes_test(lambda u: u.ecs_profile.internal)
def submission_list(request, template='submissions/internal_list.html'):
    return submission_widget(request, template=template, limit=None)


