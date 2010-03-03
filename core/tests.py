# -*- coding: utf-8 -*-

"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from core.models import Submission, SubmissionForm, SubmissionSet, EthicsCommission, InvolvedCommissionsForNotification, InvolvedCommissionsForSubmission, NotificationType
from core.models import BaseNotificationForm, ExtendedNotificationForm, Notification
import datetime

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class SubmissionFormTest(TestCase):
    def test_creation(self):
        sub = Submission()
        sub.save()
        sform = SubmissionForm(
            submission = sub,
            project_title="High Risk Neuroblastoma Study 1 of SIOP-Europe (SIOPEN)",
            protocol_number="HR-NBL-1",
            date_of_protocol=datetime.date(2002,2,2),
            eudract_number="2006-001489-17",
            isrctn_number="",
            sponsor_name="CCRI",
            sponsor_address1="Kinderspitalg. 6",
            sponsor_address2="",
            sponsor_zip_code="1090",
            sponsor_city="Wien",
            sponsor_phone="+43 1 40170",
            sponsor_fax="+43 1 4017070",
            sponsor_email="helmut.gadner@stanna.at",
            invoice_name="",
            invoice_address1="",
            invoice_address2="",
            invoice_zip_code="",
            invoice_city="",
            invoice_phone="",
            invoice_fax="",
            invoice_email="",
            invoice_uid="",
            project_type_2_1_1=True,
            project_type_2_1_2=False,
            project_type_2_1_2_1=False,
            project_type_2_1_2_2=False,
            project_type_2_1_3=False,
            project_type_2_1_4=False,
            project_type_2_1_4_1=False,
            project_type_2_1_4_2=False,
            project_type_2_1_4_3=False,
            project_type_2_1_5=False,
            project_type_2_1_6=False,
            project_type_2_1_7=False,
            project_type_2_1_8=False,
            project_type_2_1_9=False,
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
            substance_registered_in_countries="",
            substance_preexisting_clinical_tries=True,
            substance_p_c_t_countries="DE,US,AT",
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
            study_plan_8_1_1=True,
            study_plan_8_1_2=True,
            study_plan_8_1_3=True,
            study_plan_8_1_4=False,
            study_plan_8_1_5=False,
            study_plan_8_1_6=True,
            study_plan_8_1_7=False,
            study_plan_8_1_8=True,
            study_plan_8_1_9=False,
            study_plan_8_1_10=False,
            study_plan_8_1_11=False,
            study_plan_8_1_12=False,
            study_plan_8_1_13=False,
            study_plan_8_1_14=False,
            study_plan_8_1_15="",
            study_plan_8_1_16="two sequential randomisations, each with 2 arms",
            study_plan_8_1_17="Age, Stage, National Groups",
            study_plan_8_1_18="",
            study_plan_8_1_19="Event Free Survival",
            study_plan_8_1_20="Arm A = Arm B R1: 3yrs pEFS=45%, R2: 3yrs pEFS=50%",
            study_plan_8_1_21="Difference in EFS: R1: 10%, R2: 12,5%",
#            study_plan_8_1_22="response, survival, toxicity",
            study_plan_alpha="0.05",
            study_plan_power="0.80",
            study_plan_statalgorithm="Lachin and Foulkes",
            study_plan_multiple_test_correction_algorithm="",
            study_plan_dropout_ratio="0",
            study_plan_8_3_1=True,
            study_plan_8_3_2=False,
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
            submitter_name="Univ. Doz. Dr. Ruth Ladenstein",
            submitter_organisation="St. Anna Kinderspital",
            submitter_jobtitle="OA am St. Anna Kinderspital",
            submitter_is_coordinator=True,
            submitter_is_main_investigator=False,
            submitter_is_sponsor=False,
            submitter_is_authorized_by_sponsor=False,
            submitter_sign_date=datetime.date(1999,9,9),
            )
        sform.save()
        # normal way would be to fetch one, but the test database does not contain the data rows :(
        ek1 = EthicsCommission(address_1 = u'Borschkegasse 8b/E 06', chairperson = u'Univ.Prof.Dr.Ernst Singer', city = u'Wien', contactname = u'Fr. Dr.Christiane Druml', email = u'ethik-kom@meduniwien.ac.at', fax = u'(01) 40400-1690', name = u'EK Med.Universit\xe4t Wien', phone = u'(01) 40400-2147, -2248, -2241', url = u'www.meduniwien.ac.at/ethik', zip_code = u'A-1090')
        ek1.save()
        involved_com = InvolvedCommissionsForSubmission(commission=ek1, submission=sform, main=True, examiner_name="Univ. Doz. Dr. Ruth Ladenstein")
        involved_com.save()

class NotificationFormTest(TestCase):
    def setUp(self):
        sub = Submission()
        sub.save()
        sform = SubmissionForm(
            submission = sub,
            project_title="High Risk Neuroblastoma Study 1 of SIOP-Europe (SIOPEN)",
            protocol_number="HR-NBL-1",
            date_of_protocol=datetime.date(2002,2,2),
            eudract_number="2006-001489-17",
            isrctn_number="",
            sponsor_name="CCRI",
            sponsor_address1="Kinderspitalg. 6",
            sponsor_address2="",
            sponsor_zip_code="1090",
            sponsor_city="Wien",
            sponsor_phone="+43 1 40170",
            sponsor_fax="+43 1 4017070",
            sponsor_email="helmut.gadner@stanna.at",
            invoice_name="",
            invoice_address1="",
            invoice_address2="",
            invoice_zip_code="",
            invoice_city="",
            invoice_phone="",
            invoice_fax="",
            invoice_email="",
            invoice_uid="",
            project_type_2_1_1=True,
            project_type_2_1_2=False,
            project_type_2_1_2_1=False,
            project_type_2_1_2_2=False,
            project_type_2_1_3=False,
            project_type_2_1_4=False,
            project_type_2_1_4_1=False,
            project_type_2_1_4_2=False,
            project_type_2_1_4_3=False,
            project_type_2_1_5=False,
            project_type_2_1_6=False,
            project_type_2_1_7=False,
            project_type_2_1_8=False,
            project_type_2_1_9=False,
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
            substance_registered_in_countries="",
            substance_preexisting_clinical_tries=True,
            substance_p_c_t_countries="DE,US,AT",
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
            study_plan_8_1_1=True,
            study_plan_8_1_2=True,
            study_plan_8_1_3=True,
            study_plan_8_1_4=False,
            study_plan_8_1_5=False,
            study_plan_8_1_6=True,
            study_plan_8_1_7=False,
            study_plan_8_1_8=True,
            study_plan_8_1_9=False,
            study_plan_8_1_10=False,
            study_plan_8_1_11=False,
            study_plan_8_1_12=False,
            study_plan_8_1_13=False,
            study_plan_8_1_14=False,
            study_plan_8_1_15="",
            study_plan_8_1_16="two sequential randomisations, each with 2 arms",
            study_plan_8_1_17="Age, Stage, National Groups",
            study_plan_8_1_18="",
            study_plan_8_1_19="Event Free Survival",
            study_plan_8_1_20="Arm A = Arm B R1: 3yrs pEFS=45%, R2: 3yrs pEFS=50%",
            study_plan_8_1_21="Difference in EFS: R1: 10%, R2: 12,5%",
#            study_plan_8_1_22="response, survival, toxicity",
            study_plan_alpha="0.05",
            study_plan_power="0.80",
            study_plan_statalgorithm="Lachin and Foulkes",
            study_plan_multiple_test_correction_algorithm="",
            study_plan_dropout_ratio="0",
            study_plan_8_3_1=True,
            study_plan_8_3_2=False,
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
            submitter_name="Univ. Doz. Dr. Ruth Ladenstein",
            submitter_organisation="St. Anna Kinderspital",
            submitter_jobtitle="OA am St. Anna Kinderspital",
            submitter_is_coordinator=True,
            submitter_is_main_investigator=False,
            submitter_is_sponsor=False,
            submitter_is_authorized_by_sponsor=False,
            submitter_sign_date=datetime.date(1999,9,9),
            )
        sform.save()
        # normal way would be to fetch one, but the test database does not contain the data rows :(
        ek1 = EthicsCommission(address_1 = u'Borschkegasse 8b/E 06', chairperson = u'Univ.Prof.Dr.Ernst Singer', city = u'Wien', contactname = u'Fr. Dr.Christiane Druml', email = u'ethik-kom@meduniwien.ac.at', fax = u'(01) 40400-1690', name = u'EK Med.Universit\xe4t Wien', phone = u'(01) 40400-2147, -2248, -2241', url = u'www.meduniwien.ac.at/ethik', zip_code = u'A-1090')
        ek1.save()
        involved_com = InvolvedCommissionsForSubmission(commission=ek1, submission=sform, main=True, examiner_name="Univ. Doz. Dr. Ruth Ladenstein")
        involved_com.save()
        self.submission = sub
        self.submission_form = sform

    def test_notification_creation(self):
        some_notification_type = NotificationType.objects.create(name='Test')
        some_date = datetime.date(2010, 3, 1)

        notif = Notification(submission=self.submission)
        notif.save()
        nform = BaseNotificationForm(notification=notif, type=some_notification_type, comments="we need longer to torture our victims! Really.", signed_on=some_date)
        nform.save()
        nform.submission_forms = [self.submission_form]
        
        extended_form = ExtendedNotificationForm(notification=notif, type=some_notification_type, comments="foo", signed_on=some_date,
            SAE_count=1, SUSAR_count=2, aborted_subjects=3, finished_subjects=4, recruited_subjects=5, 
            reason_for_not_started='bar', runs_till=some_date, finished_on=some_date, aborted_on=some_date, extension_of_vote=True,
        )
        extended_form.save()
        ecs = EthicsCommission.objects.all()[:3]
        for ec in ecs:
            InvolvedCommissionsForNotification.objects.create(commission=ec, submission=extended_form, main=False)
        
