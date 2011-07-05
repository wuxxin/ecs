from ecs.core.views.submissions import (create_submission_form, copy_submission_form, submission_pdf,
    readonly_submission_form, categorization_review, checklist_review, copy_latest_submission_form,
    vote_review, export_submission, import_submission_form, befangene_review, diff, wizard, submission_widget,
    submission_list, upload_document_for_submission, delete_document_from_submission,
    delete_docstash_entry, view_submission,
    all_submissions, my_submissions, assigned_submissions, delete_task,
)
from ecs.core.views.votes import show_html_vote, show_pdf_vote, download_signed_vote, vote_sign, vote_sign_finished
from ecs.core.views.checklists import checklist_comments
from ecs.core.views.autocomplete import autocomplete

# remove the following lines for the final product
from ecs.core.views.developer import developer_test_pdf, test_pdf_html, test_render_pdf
