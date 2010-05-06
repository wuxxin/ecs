import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from ecs.workflow.models import Graph
from ecs.core.models import Submission
from ecs.workflow import patterns
from ecs.workflow.utils import make_dot

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--doit', dest='do_it', action='store_true', default=False, help=''),
        make_option('--format', dest='format', action='store', help="The output format type. Either a valid fixture format or 'dot'."),
        make_option('--indent', dest='indent', action='store', type='int', help="Indention output with INDENT spaces"),
    )

    @transaction.commit_manually
    def handle(self, do_it=False, **options):
        try:
            call_command('workflow_sync', quiet=True)
            
            from ecs.core import workflow as cwf
            
            g = Graph.objects.create(model=Submission, auto_start=True)

            initial_review = g.create_node(cwf.inspect_form_and_content_completeness, start=True)
            #change_submission_form = g.create_node(cwf.change_submission_form)
            not_retrospective_thesis = g.create_node(patterns.generic)
            reject = g.create_node(cwf.reject, end=True)
            accept = g.create_node(cwf.accept)
            thesis_review = g.create_node(cwf.review_retrospective_thesis, name='Thesis Review')
            thesis_review2 = g.create_node(cwf.review_retrospective_thesis, name='Executive Thesis Review')
            retro_thesis = g.create_node(patterns.generic, name="Retrospective Thesis", end=True)
            legal_and_patient_review = g.create_node(cwf.review_legal_and_patient_data, name="Legal+Patient R.")
            scientific_review = g.create_node(cwf.review_scientific_issues, name="Executive R.")
            statistical_review = g.create_node(cwf.review_statistical_issues, name="Statistical R.")
            insurance_review = g.create_node(cwf.review_insurance_issues, name="Insurance R.")
            contact_external_reviewer = g.create_node(cwf.contact_external_reviewer)
            do_external_review = g.create_node(cwf.do_external_review, name="External R.")
            review_sync = g.create_node(patterns.synchronization, end=True)
            scientific_review_complete = g.create_node(patterns.generic)
            
            initial_review.add_edge(reject, guard=cwf.is_accepted, negate=True)
            initial_review.add_edge(accept, guard=cwf.is_accepted)
            #reject.add_edge(change_submission_form)
            accept.add_edge(not_retrospective_thesis, guard=cwf.is_marked_as_thesis_by_submitter, negate=True)
            accept.add_edge(thesis_review, guard=cwf.is_marked_as_thesis_by_submitter)
            thesis_review.add_edge(thesis_review2, guard=cwf.is_thesis_and_retrospective)
            thesis_review.add_edge(not_retrospective_thesis, guard=cwf.is_thesis_and_retrospective, negate=True)
            thesis_review2.add_edge(retro_thesis, guard=cwf.is_thesis_and_retrospective)
            thesis_review2.add_edge(not_retrospective_thesis, guard=cwf.is_thesis_and_retrospective, negate=True)
            not_retrospective_thesis.add_edge(legal_and_patient_review)
            not_retrospective_thesis.add_edge(scientific_review)
            not_retrospective_thesis.add_edge(statistical_review)
            not_retrospective_thesis.add_edge(insurance_review)
            scientific_review.add_edge(contact_external_reviewer, guard=cwf.is_classified_for_external_review)
            scientific_review.add_edge(scientific_review_complete, guard=cwf.is_classified_for_external_review, negate=True)
            scientific_review_complete.add_edge(review_sync)
            do_external_review.add_edge(scientific_review_complete)
            #external_review.add_edge(contact_external_reviewer)
            contact_external_reviewer.add_edge(do_external_review)
            do_external_review.add_edge(scientific_review, deadline=True)
            statistical_review.add_edge(review_sync)
            insurance_review.add_edge(review_sync)
            legal_and_patient_review.add_edge(review_sync)
            self.output(g, **options)

        finally:
            if not do_it:
                transaction.rollback()
            else:
                transaction.commit()
            
    def output(self, g, format=None, **options):
        if format == 'dot':
            print make_dot(g)
        elif format is not None:
            call_command('dumpdata', 'workflow', format=format, **options)
