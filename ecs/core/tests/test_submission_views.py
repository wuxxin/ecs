# -*- coding: utf-8 -*-
import os
import json
from urlparse import urlsplit

from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group

from ecs.utils.testcases import LoginTestCase
from ecs.core.tests.test_submissions import create_submission_form
from ecs.core.models import MedicalCategory
from ecs.core import bootstrap
from ecs.checklists import bootstrap as checklists_bootstrap
from ecs.core.models import SubmissionForm
from ecs.core.models import EthicsCommission
from ecs.documents.models import DocumentType
from ecs.users.utils import get_or_create_user
from ecs.tasks.models import Task

VALID_SUBMISSION_FORM_DATA = {
    u'investigator-0-ethics_commission': [u'1'], u'study_plan_abort_crit': [u'Peto'], u'submitter_contact_title': [u'Univ. Doz. Dr.'], 
    u'study_plan_statistics_implementation': [u'Mag. rer.soc.oec. Jane Doe / Statistikerin'], u'investigator-1-contact_last_name': [u'Doe'], 
    u'sponsor_fax': [u'+430987654345678'], u'substance_p_c_t_final_report': [u'2'], u'substance_registered_in_countries': [u'AT',u'FR'], 
    u'pharma_reference_substance': [u'none'], u'medtech_product_name': [u''], u'study_plan_alpha': [u'0.03'], 
    u'investigatoremployee-0-investigator_index': [u'0'], u'study_plan_secondary_objectives': [u''], u'eudract_number': [u'2020-002323-99'], 
    u'study_plan_dropout_ratio': [u'0'], u'german_protected_subjects_info': [u'bla bla bla'], u'sponsor_contact_gender': [u'f'], 
    u'study_plan_misc': [u''], u'german_preclinical_results': [u'bla bla bla'], u'study_plan_biometric_planning': [u'Mag. rer.soc.oec. Jane Doe/ Statistikerin'], 
    u'investigatoremployee-0-title': [u''], u'nontesteduseddrug-INITIAL_FORMS': [u'0'], u'submitter_contact_last_name': [u'Doe'], 
    u'investigatoremployee-0-sex': [u''], u'study_plan_stratification': [u''], u'sponsor_agrees_to_publishing': [u'on'], u'german_recruitment_info': [u'bla bla bla'], 
    u'investigator-1-phone': [u''], u'submitter_email': [u''], u'invoice_uid': [u''], u'nontesteduseddrug-0-preparation_form': [u''], 
    u'investigator-1-contact_first_name': [u'John'], u'investigator-1-email': [u'rofl@copter.com'], u'german_concurrent_study_info': [u'bla bla bla'], 
    u'study_plan_planned_statalgorithm': [u'log rank test'], u'document-date': [u''], u'medtech_reference_substance': [u''], u'measure-MAX_NUM_FORMS': [u''], 
    u'study_plan_statalgorithm': [u'none'], u'foreignparticipatingcenter-TOTAL_FORMS': [u'1'], u'routinemeasure-MAX_NUM_FORMS': [u''], 
    u'invoice_contact_first_name': [u''], u'investigator-0-mobile': [u''], u'submitter_is_coordinator': [u'on'], u'insurance_validity': [u'keine'], 
    u'sponsor_name': [u'sponsor'], u'sponsor_contact_last_name': [u'last'], u'sponsor_email': [u'johndoe@example.com'], u'subject_duration': [u'96 months'], 
    u'submitter_contact_gender': [u'f'], u'nontesteduseddrug-0-generic_name': [u''], u'medtech_ce_symbol': [u'3'], u'investigator-0-contact_gender': [u'f'], 
    u'investigator-1-contact_gender': [u'm'], u'nontesteduseddrug-MAX_NUM_FORMS': [u''], u'investigatoremployee-INITIAL_FORMS': [u'0'], u'insurance_phone': [u'1234567'], 
    u'investigator-0-email': [u'rofl@copter.com'], u'measure-TOTAL_FORMS': [u'0'], u'medtech_manufacturer': [u''], u'subject_planned_total_duration': [u'10 months'], 
    u'german_summary': [u'Bei diesem Projekt handelt es sich um ein sowieso bla blu'], u'document-doctype': [u''], 
    u'investigator-0-contact_first_name': [u'Jane'], u'nontesteduseddrug-0-dosage': [u''], u'insurance_contract_number': [u'2323'], u'study_plan_power': [u'0.80'], 
    u'sponsor_phone': [u'+43 1 40170'], u'subject_maxage': [u'21'], u'investigator-1-ethics_commission': [u''], u'subject_noncompetents': [u'on'], 
    u'german_dataprotection_info': [u'bla bla bla'], u'german_risks_info': [u'bla bla bla'], 
    u'german_ethical_info': [u'bla bla bla'], u'foreignparticipatingcenter-0-id': [u''], u'investigatoremployee-TOTAL_FORMS': [u'1'], 
    u'specialism': [u'Immunologie'], u'investigator-1-subject_count': [u'4'], u'medtech_certified_for_other_indications': [u'3'], 
    u'german_payment_info': [u'bla bla bla'], u'investigator-0-contact_title': [u'Univ. Doz. Dr.'], 
    u'study_plan_dataprotection_anonalgoritm': [u'Electronically generated unique patient number'], 
    u'additional_therapy_info': [u'long blabla'], u'german_inclusion_exclusion_crit': [u'bla bla bla'], 
    u'medtech_technical_safety_regulations': [u''], u'foreignparticipatingcenter-MAX_NUM_FORMS': [u''], u'german_aftercare_info': [u'bla bla bla'], 
    u'investigator-1-fax': [u''], u'study_plan_null_hypothesis': [u''], u'investigator-1-mobile': [u''], u'invoice_address': [u''], 
    u'substance_preexisting_clinical_tries': [u'2'], u'substance_p_c_t_phase': [u'III'], u'subject_males': [u'on'], u'investigator-0-phone': [u''], 
    u'substance_p_c_t_period': [u'period'], u'german_benefits_info': [u'bla bla bla'], 
    u'german_abort_info': [u'bla bla bla'], u'insurance_address': [u'insurancestreet 1'], u'german_additional_info': [u'bla bla bla'], 
    u'investigatoremployee-MAX_NUM_FORMS': [u''], u'investigatoremployee-0-organisation': [u''], u'study_plan_primary_objectives': [u''], 
    u'study_plan_number_of_groups': [u''], u'invoice_contact_last_name': [u''], u'document-replaces_document': [u''], u'investigator-TOTAL_FORMS': [u'2'], 
    u'study_plan_dataprotection_reason': [u''], u'medtech_certified_for_exact_indications': [u'3'], u'sponsor_city': [u'Wien'], u'medtech_manual_included': [u'3'], 
    u'invoice_contact_gender': [u''], u'foreignparticipatingcenter-INITIAL_FORMS': [u'0'], u'study_plan_alternative_hypothesis': [u''], u'medtech_checked_product': [u''], 
    u'study_plan_dataprotection_dvr': [u''], u'investigator-0-fax': [u''], u'investigator-0-specialist': [u''], u'study_plan_sample_frequency': [u''], 
    u'investigator-1-contact_title': [u'Maga.'], u'submission_type': '1', u'investigator-1-contact_origanisation': [u'BlaBlu'],
    u'study_plan_dataquality_checking': [u'National coordinators'], u'project_type_nursing_study': [u'on'],
    u'project_type_non_reg_drug': [u'on'], u'german_relationship_info': [u'bla bla bla'], u'nontesteduseddrug-0-id': [u''], u'project_title': [u'FOOBAR POST Test'], 
    u'invoice_fax': [u''], u'investigator-MAX_NUM_FORMS': [u''], u'sponsor_zip_code': [u'2323'], u'subject_duration_active': [u'14 months'], 
    u'measure-INITIAL_FORMS': [u'0'], u'nontesteduseddrug-TOTAL_FORMS': [u'1'], u'already_voted': [u'on'], u'subject_duration_controls': [u'36 months'], 
    u'invoice_phone': [u''], u'submitter_jobtitle': [u'jobtitle'], u'investigator-1-specialist': [u''], u'german_sideeffects_info': [u'bla bla bla'], 
    u'subject_females': [u'on'], u'investigator-0-organisation': [u'orga'], u'sponsor_contact_first_name': [u'first'],
    u'pharma_checked_substance': [u'1'], u'investigator-0-subject_count': [u'1'], u'project_type_misc': [u''], 
    u'foreignparticipatingcenter-0-name': [u''], u'investigator-1-organisation': [u'orga'], u'invoice_city': [u''], u'german_financing_info': [u'bla bla bla'], 
    u'submitter_contact_first_name': [u'Jane'], u'foreignparticipatingcenter-0-investigator_name': [u''], u'german_dataaccess_info': [u'bla bla bla'], 
    u'documents': [], u'sponsor_contact_title': [u''], u'invoice_contact_title': [u''], 
    u'investigator-0-contact_last_name': [u'Doe'], u'medtech_departure_from_regulations': [u''], 
    u'routinemeasure-TOTAL_FORMS': [u'0'], u'invoice_zip_code': [u''], u'routinemeasure-INITIAL_FORMS': [u'0'], u'invoice_email': [u''], 
    u'csrfmiddlewaretoken': [u'9d8077845a05603196d32bea1cf25c28'], u'investigatoremployee-0-surname': [u''], u'study_plan_blind': [u'0'], 
    u'document-file': [u''], u'study_plan_datamanagement': [u'Date entry and management'], 
    u'german_primary_hypothesis': [u'bla bla bla'], u'subject_childbearing': [u'on'], u'substance_p_c_t_countries': [u'AT',u'DE',u'CH'], 
    u'insurance_name': [u'insurance'], u'project_type_education_context': [u''], u'clinical_phase': [u'II'], 
    u'investigator-INITIAL_FORMS': [u'1'], u'subject_count': [u'190'], u'substance_p_c_t_gcp_rules': [u'2'], u'subject_minage': [u'0'], 
    u'investigatoremployee-0-firstname': [u''], u'german_consent_info': [u'bla bla bla'], u'document-version': [u''], u'substance_p_c_t_application_type': [u'IV in children'], 
    u'german_project_title': [u'kjkjkjk'], u'submitter_organisation': [u'submitter orga'], u'study_plan_multiple_test_correction_algorithm': [u'Keines'], 
    u'sponsor_address': [u'sponsor address 1'], u'invoice_name': [u''], u'german_statistical_info': [u'bla bla bla'], u'submitter_email': [u'submitter@example.com'],
    u'study_plan_dataprotection_choice': [u'non-personal'], u'investigator-0-main': [u'on'], u'study_plan_alpha_sided': [u'0'],
}

class SubmissionViewsTestCase(LoginTestCase):
    '''Several tests for different views of a submission form.
    
    Tests for accessibility and functioning of core submission-form views.
    '''
    
    def setUp(self):
        super(SubmissionViewsTestCase, self).setUp()
        checklists_bootstrap.checklist_blueprints()
        bootstrap.ethics_commissions()
        VALID_SUBMISSION_FORM_DATA[u'investigator-0-ethics_commission'] = [unicode(EthicsCommission.objects.all()[0].pk)]
        VALID_SUBMISSION_FORM_DATA[u'investigator-1-ethics_commission'] = [unicode(EthicsCommission.objects.all()[0].pk)]

        self.office_user, created = get_or_create_user('unittest-office@example.org')
        self.office_user.set_password('password')
        self.office_user.save()
        office_group = Group.objects.get(name='EC-Office')
        self.office_user.groups.add(office_group)
        profile = self.office_user.profile
        profile.is_internal = True
        profile.save()

    def get_docstash_url(self):
        url = reverse('ecs.core.views.submissions.create_submission_form')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url = response['Location']
        return url
        
    def get_post_data(self, update=None):
        data = VALID_SUBMISSION_FORM_DATA.copy()
        data['document-doctype'] = str(DocumentType.objects.get(identifier='protocol').pk)
        if update:
            data.update(update)
        return data

    def test_create_submission_form(self):
        '''Tests if the docstash is reachable.
        Also tests document count and versioning of the docstash for a submissionform.
        '''
        
        url = self.get_docstash_url()
        
        # post some data
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        
        # from docstash
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        upload_url = url.replace('new', 'doc/upload', 1)    # XXX: ugly

        # document upload
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'menschenrechtserklaerung.pdf')
        with open(file_path, 'rb') as f:
            response = self.client.post(upload_url, self.get_post_data({
                'document-file': f,
                'document-name': u'Menschenrechtserklärung',
                'document-version': '3.1415',
                'document-date': '26.10.2010',
            }))
        self.assertEqual(response.status_code, 200)
        first_doc = response.context['documents'][0]
        self.assertEqual(first_doc.version, '3.1415')
        
        # replace document
        with open(file_path, 'rb') as f:
            response = self.client.post(upload_url, self.get_post_data({
                'document-file': f,
                'document-name': u'Menschenrechtserklärung',
                'document-version': '3',
                'document-date': '26.10.2010',
                'document-replaces_document': first_doc.pk,
            }))
        self.assertEqual(response.status_code, 200)
        docs = response.context['documents']
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].version, '3')
        
        # posting valid data
        response = self.client.post(url, self.get_post_data({'submit': 'submit', 'documents': [str(doc.pk) for doc in docs]}))
        self.assertEqual(response.status_code, 302)
        sf = SubmissionForm.objects.get(project_title=u'FOOBAR POST Test')
        self.assertEqual(sf.documents.count(), 1)
        self.assertEqual(sf.documents.all()[0].version, '3')
        
    def test_readonly_submission_form(self):
        '''Tests if the readonly submissionform is accessible.
        '''
        
        submission_form = create_submission_form()
        response = self.client.get(reverse('readonly_submission_form', kwargs={'submission_form_pk': submission_form.pk}))
        self.assertEqual(response.status_code, 200)
        
    def test_submission_pdf(self):
        '''Tests if a pdf can be produced out of a pre existing submissionform.
        '''

        submission_form = create_submission_form()
        response = self.client.get(reverse('ecs.documents.views.download_document', kwargs={'document_pk': submission_form.pdf_document.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertEqual(next(response.streaming_content)[:5], '%PDF-')

    def test_submission_form_search(self):
        '''Tests if all submissions are searchable via the keyword argument.
        Tests that the correct count of submissions is returned by the search function.
        '''
        
        create_submission_form(20200001)
        create_submission_form(20200042)
        create_submission_form(20209942)
        url = reverse('ecs.core.views.all_submissions')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len([x for x in response.context['submissions'].object_list if not x.timetable_entries.count()]), 3)
        
        response = self.client.get(url, {'keyword': '42'})
        self.assertTrue(response.status_code, 200)
        self.assertEqual(len([x for x in response.context['submissions'].object_list if not x.timetable_entries.exists()]), 1)

        response = self.client.get(url, {'keyword': '42/2020'})
        self.assertTrue(response.status_code, 200)
        self.assertEqual(len([x for x in response.context['submissions'].object_list if not x.timetable_entries.exists()]), 1)
        
    def test_submission_form_copy(self):
        '''Tests if a submissionform can be copied. Compares initial version against copied version.
        '''
        
        submission_form = create_submission_form(presenter=self.user)
        response = self.client.get(reverse('ecs.core.views.copy_latest_submission_form', kwargs={'submission_pk': submission_form.submission.pk}))
        self.assertEqual(response.status_code, 302)
        url = reverse('ecs.core.views.copy_submission_form', kwargs={'submission_form_pk': submission_form.pk})
        self.assertEqual(url, urlsplit(response['Location']).path)
    
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        target_url = response['Location']
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].initial.get('project_title'), submission_form.project_title)
        
    def test_autocomplete(self):
        '''Tests the autocompletion feature of the system by comparing the count of objects returned by the autocompletion view.
        '''
        
        medical_categories_count = MedicalCategory.objects.all().count()
        response = self.client.get(reverse('ecs.core.views.autocomplete', kwargs={'queryset_name': 'medical_categories'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content)), medical_categories_count)

    def test_initial_review(self):
        submission_form = create_submission_form(presenter=self.user)

        self.client.logout()
        self.client.login(email=self.office_user.email, password='password')

        task = Task.objects.for_data(submission_form.submission).get(task_type__workflow_node__uid='initial_review')
        refetch = lambda: Task.objects.get(pk=task.pk)

        # accept initial review task
        response = self.client.post(reverse('ecs.tasks.views.accept_task', kwargs={'task_pk': task.pk}))
        self.assertEqual(response.status_code, 302)
        task = refetch()
        self.assertEqual(self.office_user, task.assigned_to)

        url = task.url

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # delegate the task back to the pool
        reponse = self.client.post(url, {'task_management-action': 'delegate', 'task_management-assign_to': '', 'task_management-submit': 'submit'})
        task = refetch()
        self.assertEqual(None, task.assigned_to)

        # accept the task again
        response = self.client.post(reverse('ecs.tasks.views.accept_task', kwargs={'task_pk': task.pk}))
        self.assertEqual(response.status_code, 302)
        task = refetch()
        self.assertEqual(self.office_user, task.assigned_to)

        # complete the task
        reponse = self.client.post(url, {'task_management-action': 'complete_0', 'task_management-submit': 'submit'})
        task = refetch()
        self.assertTrue(task.closed_at is not None)

        self.client.logout()
        self.client.login(email=self.user.email, password='password')