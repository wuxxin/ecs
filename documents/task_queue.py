from celery.decorators import task
from haystack import site
from ecs.utils.pdfutils import pdftotext
from ecs.utils.storagevault import getVault
from ecs.documents.models import Document, Page

@task()
def upload_to_storagevault(document_pk=None, **kwargs):
    try:
        doc = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.warning("Warning, Document with pk %s does not exist" % str(document_pk))
        return
    vault = getVault()
    with open(doc.file.path,"rb") as f:
        try:
            vault.add(doc.uuid_document, f)
        except KeyError:
            pass # FIXME/mediaserver

    # TODO: prime mediaserver
    return True
    
@task()
def extract_and_index_pdf_text(document_pk=None, **kwargs):
    logger = extract_and_index_pdf_text.get_logger(**kwargs)
    logger.debug("indexing doc with pk %s" % document_pk)
    try:
        doc = Document.objects.get(pk=document_pk)
    except Document.DoesNotExist:
        logger.warning("Warning, Document with pk %s does not exist" % str(document_pk))
        return
    if not doc.pages or doc.mimetype != 'application/pdf':
        logger.info("Warning, doc.pages (%s) not set or doc.mimetype (%s) != 'application/pdf'" % (str(doc.pages), str(doc.mimetype)))
        return
    logger.debug("filename path %s %s" % (str(doc.file.path), str(doc.file.name)))
    for p in xrange(1, doc.pages + 1):
        text = pdftotext(doc.file.path, p)
        doc.page_set.create(num=p, text=text)
    index = site.get_index(Page)
    index.backend.update(index, doc.page_set.all())
