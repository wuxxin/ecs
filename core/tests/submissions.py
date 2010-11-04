# -*- coding: utf-8 -*-
import datetime
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from ecs.core.models import Submission, SubmissionForm, EthicsCommission, Investigator
from ecs.core.views.submissions import diff
from ecs.notifications.models import Notification, NotificationType, ProgressReportNotification, CompletionReportNotification
from ecs.documents.models import Document
from ecs.core.models.submissions import attach_to_submissions
from ecs.utils.countries.models import Country
from ecs.utils.testcases import EcsTestCase
from ecs.core.diff import diff_submission_forms

class SubmissionFormTest(EcsTestCase):
    def test_creation(self):
        sub = Submission()
        sub.save()
        sform = SubmissionForm(
            submission = sub,
            project_title="High Risk Neuroblastoma Study 1 of SIOP-Europe (SIOPEN)",
            eudract_number="2006-001489-17",
            sponsor_name="CCRI",
            sponsor_address1="Kinderspitalg. 6",
            sponsor_address2="",
            sponsor_zip_code="1090",
            sponsor_city="Wien",
            sponsor_phone="+43 1 40170",
            sponsor_fax="+43 1 4017070",
            sponsor_email="helmut.gadner@stanna.at",
            sponsor_agrees_to_publishing=False,
            invoice_name="",
            invoice_address1="",
            invoice_address2="",
            invoice_zip_code="",
            invoice_city="",
            invoice_phone="",
            invoice_fax="",
            invoice_email="",
            invoice_uid="",
            project_type_non_reg_drug=True,
            project_type_reg_drug=False,
            project_type_reg_drug_within_indication=False,
            project_type_reg_drug_not_within_indication=False,
            project_type_medical_method=False,
            project_type_medical_device=False,
            project_type_medical_device_with_ce=False,
            project_type_medical_device_without_ce=False,
            project_type_medical_device_performance_evaluation=False,
            project_type_basic_research=False,
            project_type_genetic_study=False,
            project_type_register=False,
            project_type_biobank=False,
            project_type_retrospective=False,
            project_type_questionnaire=False,
            project_type_education_context=None,
            project_type_misc=None,
            specialism="Pädiatrische Onkologie / Immunologie",
            pharma_checked_substance="1) R1 Randomisierung CEM - MAT/SCR",
            pharma_reference_substance="1) R1 Randomisierung BUMEL - MAT/SCR",
            medtech_checked_product="",
            medtech_reference_substance="",
            clinical_phase="III",
            already_voted=True,
            subject_count=175,
            subject_minage=0,
            subject_maxage=21,
            subject_noncompetents=True,
            subject_males=True,
            subject_females=True,
            subject_childbearing=True,
            subject_duration="48 months",
            subject_duration_active="12 months",
            subject_duration_controls="36 months",
            subject_planned_total_duration="to short max_length!",
            substance_preexisting_clinical_tries=True,
            substance_p_c_t_phase="III",
            #substance_p_c_t_period="Anti-GD2-Phase I: 1989-1992, Phase III 2002",
            substance_p_c_t_period="to long",
            substance_p_c_t_application_type="IV in children",
            substance_p_c_t_gcp_rules=True,
            substance_p_c_t_final_report=True,

            medtech_product_name="",
            medtech_manufacturer="",
            medtech_certified_for_exact_indications=False,
            medtech_certified_for_other_indications=False,
            medtech_ce_symbol=False,
            medtech_manual_included=False,
            medtech_technical_safety_regulations="",
            medtech_departure_from_regulations="",
            insurance_name="Zürich Veresicherungs-Aktiengesellschaft",
            insurance_address_1="Schwarzenbergplatz 15",
            insurance_phone="50125",
            insurance_contract_number="WF-07218230-8",
            insurance_validity="01.10.2005 bis 01.10.2006",
            additional_therapy_info="long blabla",
            german_project_title="bla bla bla",
            german_summary="bla bla bla",
            german_preclinical_results="bla bla bla",
            german_primary_hypothesis="bla bla bla",
            german_inclusion_exclusion_crit="bla bla bla",
            german_ethical_info="bla bla bla",
            german_protected_subjects_info="bla bla bla",
            german_recruitment_info="bla bla bla",
            german_consent_info="bla bla bla",
            german_risks_info="bla bla bla",
            german_benefits_info="bla bla bla",
            german_relationship_info="bla bla bla",
            german_concurrent_study_info="bla bla bla",
            german_sideeffects_info="bla bla bla",
            german_statistical_info="bla bla bla",
            german_dataprotection_info="bla bla bla",
            german_aftercare_info="bla bla bla",
            german_payment_info="bla bla bla",
            german_abort_info="bla bla bla",
            german_dataaccess_info="bla bla bla",
            german_financing_info="bla bla bla",
            german_additional_info="bla bla bla",
            study_plan_blind=0,
            study_plan_observer_blinded=False,
            study_plan_randomized=True,
            study_plan_parallelgroups=True,
            study_plan_controlled=True,
            study_plan_cross_over=False,
            study_plan_placebo=False,
            study_plan_factorized=False,
            study_plan_pilot_project=False,
            study_plan_equivalence_testing=False,
            study_plan_misc=None,
            study_plan_number_of_groups="two sequential randomisations, each with 2 arms",
            study_plan_stratification="Age, Stage, National Groups",
            study_plan_sample_frequency=None,
            study_plan_primary_objectives="Event Free Survival",
            study_plan_null_hypothesis=False,
            study_plan_alternative_hypothesis="Arm A = Arm B R1: 3yrs pEFS=45%, R2: 3yrs pEFS=50%",
            study_plan_secondary_objectives="Difference in EFS: R1: 10%, R2: 12,5%",
            study_plan_alpha="0.05",
            study_plan_power="0.80",
            study_plan_statalgorithm="Lachin and Foulkes",
            study_plan_multiple_test_correction_algorithm="",
            study_plan_dropout_ratio="0",
            study_plan_population_intention_to_treat=True,
            study_plan_population_per_protocol=False,
            study_plan_abort_crit="Peto",
            study_plan_planned_statalgorithm="log rank test",
            study_plan_dataquality_checking="National coordinators cross check in local audits patient file data with electronic data. In addition the RDE system holds electronic plausibility controls.",
            study_plan_datamanagement="Date entry and management through the SIOPEN-R-Net platform including the RDE system",
            study_plan_biometric_planning="Mag. rer.soc.oec. Ulrike Pötschger / Statistikerin",
            study_plan_statistics_implementation="Mag. rer.soc.oec. Ulrike Pötschger / Statistikerin",
            #study_plan_dataprotection_anonalgoritm="Electronically generated unique patient number within SIOPEN-R-Net",
            study_plan_dataprotection_anonalgoritm="to long",
            study_plan_dataprotection_dvr="",
            study_plan_dataprotection_reason="",
            submitter_contact_gender="f",
            submitter_contact_first_name="Ruth",
            submitter_contact_title="Univ. Doz. Dr.",
            submitter_contact_last_name="Ladenstein",
            submitter_organisation="St. Anna Kinderspital",
            submitter_jobtitle="OA am St. Anna Kinderspital",
            submitter_is_coordinator=True,
            submitter_is_main_investigator=False,
            submitter_is_sponsor=False,
            submitter_is_authorized_by_sponsor=False,
            )
        sform.save()
        sform.substance_registered_in_countries = []
        sform.substance_p_c_t_countries = Country.objects.filter(Q(iso='DE')|Q(iso='US')|Q(iso='AT'))
        sform.save()
        # normal way would be to fetch one, but the test database does not contain the data rows :(
        ek1 = EthicsCommission(address_1 = u'Borschkegasse 8b/E 06', chairperson = u'Univ.Prof.Dr.Ernst Singer', city = u'Wien', contactname = u'Fr. Dr.Christiane Druml', email = u'ethik-kom@meduniwien.ac.at', fax = u'(01) 40400-1690', name = u'EK Med.Universit\xe4t Wien', phone = u'(01) 40400-2147, -2248, -2241', url = u'www.meduniwien.ac.at/ethik', zip_code = u'A-1090')
        ek1.save()
        Investigator.objects.create(submission_form=sform, main=True, contact_last_name="Univ. Doz. Dr. Ruth Ladenstein", subject_count=1, ethics_commission=ek1)

def create_submission_form(ec_number=None):
    sub = Submission(ec_number=ec_number)
    sub.save()
    sform = SubmissionForm(
        submission = sub,
        project_title="High Risk Neuroblastoma Study 1 of SIOP-Europe (SIOPEN)",
        eudract_number="2006-001489-17",
        sponsor_name="CCRI",
        sponsor_address1="Kinderspitalg. 6",
        sponsor_address2="",
        sponsor_zip_code="1090",
        sponsor_city="Wien",
        sponsor_phone="+43 1 40170",
        sponsor_fax="+43 1 4017070",
        sponsor_email="helmut.gadner@stanna.at",
        sponsor_agrees_to_publishing=False,
        invoice_name="",
        invoice_address1="",
        invoice_address2="",
        invoice_zip_code="",
        invoice_city="",
        invoice_phone="",
        invoice_fax="",
        invoice_email="",
        invoice_uid="",
        project_type_non_reg_drug=True,
        project_type_reg_drug=False,
        project_type_reg_drug_within_indication=False,
        project_type_reg_drug_not_within_indication=False,
        project_type_medical_method=False,
        project_type_medical_device=False,
        project_type_medical_device_with_ce=False,
        project_type_medical_device_without_ce=False,
        project_type_medical_device_performance_evaluation=False,
        project_type_basic_research=False,
        project_type_genetic_study=False,
        project_type_register=False,
        project_type_biobank=False,
        project_type_retrospective=False,
        project_type_questionnaire=False,
        project_type_education_context=None,
        project_type_misc=None,
        specialism=u"Pädiatrische Onkologie / Immunologie",
        pharma_checked_substance="1) R1 Randomisierung CEM - MAT/SCR",
        pharma_reference_substance="1) R1 Randomisierung BUMEL - MAT/SCR",
        medtech_checked_product="",
        medtech_reference_substance="",
        clinical_phase="III",
        already_voted=True,
        subject_count=175,
        subject_minage=0,
        subject_maxage=21,
        subject_noncompetents=True,
        subject_males=True,
        subject_females=True,
        subject_childbearing=True,
        subject_duration="48 months",
        subject_duration_active="12 months",
        subject_duration_controls="36 months",
        subject_planned_total_duration="to short max_length!",
        substance_preexisting_clinical_tries=True,
        substance_p_c_t_phase="III",
        #substance_p_c_t_period="Anti-GD2-Phase I: 1989-1992, Phase III 2002",
        substance_p_c_t_period="to long",
        substance_p_c_t_application_type="IV in children",
        substance_p_c_t_gcp_rules=True,
        substance_p_c_t_final_report=True,

        medtech_product_name="",
        medtech_manufacturer="",
        medtech_certified_for_exact_indications=False,
        medtech_certified_for_other_indications=False,
        medtech_ce_symbol=False,
        medtech_manual_included=False,
        medtech_technical_safety_regulations="",
        medtech_departure_from_regulations="",
        insurance_name=u"Zürich Veresicherungs-Aktiengesellschaft",
        insurance_address_1="Schwarzenbergplatz 15",
        insurance_phone="50125",
        insurance_contract_number="WF-07218230-8",
        insurance_validity="01.10.2005 bis 01.10.2006",
        additional_therapy_info="long blabla",
        german_project_title="bla bla bla",
        german_summary="bla bla bla",
        german_preclinical_results="bla bla bla",
        german_primary_hypothesis="bla bla bla",
        german_inclusion_exclusion_crit="bla bla bla",
        german_ethical_info="bla bla bla",
        german_protected_subjects_info="bla bla bla",
        german_recruitment_info="bla bla bla",
        german_consent_info="bla bla bla",
        german_risks_info="bla bla bla",
        german_benefits_info="bla bla bla",
        german_relationship_info="bla bla bla",
        german_concurrent_study_info="bla bla bla",
        german_sideeffects_info="bla bla bla",
        german_statistical_info="bla bla bla",
        german_dataprotection_info="bla bla bla",
        german_aftercare_info="bla bla bla",
        german_payment_info="bla bla bla",
        german_abort_info="bla bla bla",
        german_dataaccess_info="bla bla bla",
        german_financing_info="bla bla bla",
        german_additional_info="bla bla bla",
        study_plan_blind=0,
        study_plan_observer_blinded=False,
        study_plan_randomized=True,
        study_plan_parallelgroups=True,
        study_plan_controlled=True,
        study_plan_cross_over=False,
        study_plan_placebo=False,
        study_plan_factorized=False,
        study_plan_pilot_project=False,
        study_plan_equivalence_testing=False,
        study_plan_misc=None,
        study_plan_number_of_groups="two sequential randomisations, each with 2 arms",
        study_plan_stratification="Age, Stage, National Groups",
        study_plan_sample_frequency=None,
        study_plan_primary_objectives="Event Free Survival",
        study_plan_null_hypothesis=False,
        study_plan_alternative_hypothesis="Arm A = Arm B R1: 3yrs pEFS=45%, R2: 3yrs pEFS=50%",
        study_plan_secondary_objectives="Difference in EFS: R1: 10%, R2: 12,5%",
        study_plan_alpha="0.05",
        study_plan_power="0.80",
        study_plan_statalgorithm="Lachin and Foulkes",
        study_plan_multiple_test_correction_algorithm="",
        study_plan_dropout_ratio="0",
        study_plan_population_intention_to_treat=True,
        study_plan_population_per_protocol=False,
        study_plan_abort_crit="Peto",
        study_plan_planned_statalgorithm="log rank test",
        study_plan_dataquality_checking="National coordinators cross check in local audits patient file data with electronic data. In addition the RDE system holds electronic plausibility controls.",
        study_plan_datamanagement="Date entry and management through the SIOPEN-R-Net platform including the RDE system",
        study_plan_biometric_planning=u"Mag. rer.soc.oec. Ulrike Pötschger / Statistikerin",
        study_plan_statistics_implementation=u"Mag. rer.soc.oec. Ulrike Pötschger / Statistikerin",
        #study_plan_dataprotection_anonalgoritm="Electronically generated unique patient number within SIOPEN-R-Net",
        study_plan_dataprotection_anonalgoritm="to long",
        study_plan_dataprotection_dvr="",
        study_plan_dataprotection_reason="",
        submitter_contact_gender="f",
        submitter_contact_first_name="Ruth",
        submitter_contact_title="Univ. Doz. Dr.",
        submitter_contact_last_name="Ladenstein",
        submitter_organisation="St. Anna Kinderspital",
        submitter_jobtitle="OA am St. Anna Kinderspital",
        submitter_is_coordinator=True,
        submitter_is_main_investigator=False,
        submitter_is_sponsor=False,
        submitter_is_authorized_by_sponsor=False,
        )
    sform.save()
    sform.substance_registered_in_countries = []
    sform.substance_p_c_t_countries = Country.objects.filter(Q(iso='DE')|Q(iso='US')|Q(iso='AT'))
    sform.save()
    doc = Document.objects.create_from_buffer("foobar", mimetype="text/plain", parent_object=sform)
    ek = EthicsCommission(address_1 = u'Borschkegasse 8b/E 06', chairperson = u'Univ.Prof.Dr.Ernst Singer', city = u'Wien', contactname = u'Fr. Dr.Christiane Druml', email = u'ethik-kom@meduniwien.ac.at', fax = u'(01) 40400-1690', name = u'EK Med.Universit\xe4t Wien', phone = u'(01) 40400-2147, -2248, -2241', url = u'www.meduniwien.ac.at/ethik', zip_code = u'A-1090')
    ek.save()
    Investigator.objects.create(submission_form=sform, main=True, contact_last_name="Univ. Doz. Dr. Ruth Ladenstein", subject_count=1, ethics_commission=ek)
    return sform


class SubmissionFormDiffTest(EcsTestCase):
    def setUp(self, *args, **kwargs):
        rval = super(SubmissionFormDiffTest, self).setUp(*args, **kwargs)
        self.old_sf = create_submission_form()
        self.new_sf = create_submission_form()

        # both submission forms have to belong to the same submission
        self.new_sf.submission.current_submission_form = None
        self.new_sf.submission.save()
        self.new_sf.submission = self.old_sf.submission
        self.new_sf.save()

        return rval

    def test_submission_form_diff(self):
        self.new_sf.project_title = 'roflcopter'
        diff = diff_submission_forms(self.old_sf, self.new_sf)
        self.failIf(not diff)
        self.failUnless(dict(diff).get('Project title', None))
        self.failIf(not (1, 'roflcopter') in dict(diff)['Project title'])


class SubmissionAttachUserTest(EcsTestCase):
    def setUp(self):
        self.email = 'foobar@test.test'

        self.user = User(username="foobar", email=self.email) 
        self.sender = User(username="root", email="root@root.root")
        self.sf = create_submission_form()

        self.sf.sponsor_email = self.email
        self.sf.investigator_email = self.email
        self.sf.submitter_email = self.email

        self.user.save()
        self.sender.save();
        self.sf.save()

    def test_submission_attach_user(self):
        attach_to_submissions(self.user)        
        self.sf = SubmissionForm.objects.get(project_title="High Risk Neuroblastoma Study 1 of SIOP-Europe (SIOPEN)")
        self.assertEquals(self.sf.sponsor, self.user)
        self.assertEquals(self.sf.submitter, self.user)

    def tearDown(self):
        self.user.delete()
