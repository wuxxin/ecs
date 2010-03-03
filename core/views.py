# ecs core views

"""
Views for ecs.
"""

from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext, Context, loader, Template
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.list_detail import object_list
from django.forms.models import inlineformset_factory

import settings

from ecs.core.models import Document, BaseNotificationForm, NotificationType, Submission
from ecs.core.forms import DocumentUploadForm
from ecs.utils.htmldoc import htmldoc

## helpers

def render(request, template, context):
    if isinstance(template, (tuple, list)):
        template = loader.select_template(template)
    if not isinstance(template, Template):
        template = loader.get_template(template)
    return HttpResponse(template.render(RequestContext(request, context)))
    
def redirect_to_next_url(request, default_url=None):
    next = request.REQUEST.get('next')
    if not next or '//' in next:
        next = default_url or '/'
    return HttpResponseRedirect(next)

def file_uuid(doc_file):
    """returns md5 digest of a given file as uuid"""
    import hashlib
    s = doc_file.read()  # TODO optimize for large files! check if correct for binary files (e.g. random bytes)
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()

## views

def demo(request):
    return render_to_response('demo-django.html')

def index(request):
    return render(request, 'index.html', {})

def submission(request, id=''):
    return render(request, 'submission.html', {})
    
# documents
def download_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    response = HttpResponse(doc.file, content_type=doc.mimetype)
    response['Content-Disposition'] = 'attachment;filename=document_%s.pdf' % doc.pk
    return response
    
def delete_document(request, document_pk=None):
    doc = get_object_or_404(Document, pk=document_pk)
    doc.deleted = True
    doc.save()
    return redirect_to_next_url(request)

# notification form
def notification_list(request):
    return render(request, 'notifications/list.html', {
        'notifications': BaseNotificationForm.objects.all(),
    })

def view_notification(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    template_names = ['notifications/view/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    return render(request, template_names, {
        'documents': notification.documents.filter(deleted=False).order_by('doctype__name', '-date'),
        'notification_form': notification,
    })

def select_notification_creation_type(request):
    return render(request, 'notifications/select_creation_type.html', {
        'notification_types': NotificationType.objects.order_by('name')
    })

def create_notification(request, notification_type_pk=None):
    notification_type = get_object_or_404(NotificationType, pk=notification_type_pk)
    if request.method == 'POST':
        form = notification_type.form_cls(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.type = notification_type
            notification.save()
            notification.submission_forms = form.cleaned_data['submission_forms']
            notification.investigators = form.cleaned_data['investigators']
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))
    else:
        form = notification_type.form_cls()

    template_names = ['notifications/creation/%s.html' % name for name in (form.__class__.__name__, 'base')]
    return render(request, template_names, {
        'notification_type': notification_type,
        'form': form,
    })


def upload_document_for_notification(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    documents = notification.documents.filter(deleted=False).order_by('doctype__name', '-date')
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            # FIXME: this should be handled by the file storage system on the fly.
            document.uuid_document = file_uuid(document.file)
            document.uuid_document_revision = document.uuid_document
            document.file.seek(0)
            document.save()
            notification.documents.add(document)
            return HttpResponseRedirect(reverse('ecs.core.views.view_notification', kwargs={'notification_pk': notification.pk}))
    else:
        form = DocumentUploadForm()

    return render(request, 'notifications/upload_document.html', {
        'notification': notification,
        'documents': documents,
        'form': form,
    })


def notification_pdf(request, notification_pk=None):
    notification = get_object_or_404(BaseNotificationForm, pk=notification_pk)
    template_names = ['notifications/htmldoc/%s.html' % name for name in (notification.type.form_cls.__name__, 'base')]
    tpl = loader.select_template(template_names)
    html = tpl.render(Context({
        'notification': notification,
        'investigators': notification.investigators.order_by('ethics_commission__name', 'name'),
        'url': request.build_absolute_uri(),
    }))
    pdf = htmldoc(html.encode('ISO-8859-1'), webpage=True)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment;filename=notification_%s.pdf' % notification_pk
    return response

def submissiondetail(request, submissionid):
    submission = Submission.objects.get(id=int(submissionid))
    notifications = Notification.objects.filter(submission=submission)
    if submission:
        return object_list(request, queryset=notifications)
    return HttpResponse("BOOM")
