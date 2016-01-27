from django.http import Http404
from django.shortcuts import get_object_or_404

from ecs.docstash.models import DocStash
from ecs.utils.security import readonly
from ecs.documents.models import Document
from ecs.documents.views import handle_download


@readonly()
def download_document(request, docstash_key=None, document_pk=None, view=False):
    docstash = get_object_or_404(DocStash, key=docstash_key, owner=request.user)
    if int(document_pk) not in docstash.current_value['document_pks']:
        raise Http404()
    return handle_download(request, Document.objects.get(pk=document_pk), view=view)


@readonly()
def view_document(request, docstash_key=None, document_pk=None):
    return download_document(request, docstash_key, document_pk, view=True)