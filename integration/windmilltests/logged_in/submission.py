# -*- coding: utf-8 -*-
import os
import random
import cicero

from ecs.integration.windmillsupport import authenticated

MENSCHENRECHTSERKLAERUNG = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tests', 'menschenrechtserklaerung.pdf')

def create_submission(client, amg=False, mpg=False, thesis=False, upload=False):
    client.click(id=u'userswitcher_input')
    client.waits.forPageLoad(timeout=u'20000')
    client.select(option=u'presenter1@example.org', id=u'userswitcher_input')
    client.waits.forPageLoad(timeout=u'3000')
    client.waits.forElement(link=u'presenter1@example.org', timeout=u'3000')
    client.click(xpath=u"//div[@id='usermenu']/ul/li[4]/span")
    client.click(link=u'Neuer Antrag')

    # Eckdaten
    client.waits.forPageLoad(timeout=u'3000')
    client.waits.sleep(milliseconds=u'2000')
    if amg:
        client.check(id=u'id_project_type_reg_drug_within_indication')
    if mpg:
        client.check(id=u'id_project_type_medical_device_without_ce')
    client.check(id=u'id_project_type_basic_research')
    client.check(id=u'id_project_type_biobank')
    if thesis:
        client.click(id=u'id_project_type_education_context')
        client.select(option=u'Dissertation', id=u'id_project_type_education_context')
        client.click(value=u'1')
    client.click(id=u'id_project_type_misc')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_project_type_misc')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_specialism')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_clinical_phase')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_external_reviewer_suggestions')

    # Teilnehmer
    client.click(link=u'Teilnehmer')
    client.click(id=u'id_subject_count')
    client.type(text=random.randint(0,999), id=u'id_subject_count')
    client.type(text=random.randint(0,999), id=u'id_subject_minage')
    client.type(text=random.randint(0,999), id=u'id_subject_maxage')
    client.check(id=u'id_subject_males')
    client.check(id=u'id_subject_females')
    client.check(id=u'id_subject_childbearing')
    client.click(id=u'id_subject_duration')
    client.type(text=random.randint(0,999), id=u'id_subject_duration')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_subject_duration')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_subject_duration_active')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_subject_duration_controls')
    client.type(text=cicero.sentences(n=1, min=8, max=8)[0], id=u'id_subject_planned_total_duration')

    # Kurzfassung
    client.click(link=u'Kurzfassung')
    client.click(id=u'id_project_title')

    project_title = cicero.sentences(n=1, min=8, max=8)[0]
    if not amg and not mpg and not thesis:
        project_title += ' (simple)'
    else:
        if amg:
            project_title += ' (AMG)'
        if mpg:
            project_title += ' (MPG)'
        if thesis:
            project_title += ' (thesis)'

    client.type(text=project_title, id=u'id_project_title')
    client.type(text=project_title, id=u'id_german_project_title')

    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_protocol_number')
    client.type(text='\n'.join(cicero.sentences(n=5)), id=u'id_german_summary')
    client.type(text='\n'.join(cicero.sentences(n=3)), id=u'id_german_preclinical_results')
    client.type(text='\n'.join(cicero.sentences(n=3)), id=u'id_german_primary_hypothesis')
    client.type(text='\n'.join(cicero.sentences(n=3)), id=u'id_german_inclusion_exclusion_crit')
    client.type(text='\n'.join(cicero.sentences(n=3)), id=u'id_german_ethical_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_protected_subjects_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_recruitment_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_consent_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_risks_info')
    client.type(text=cicero.sentences(n=1, min=15, max=15)[0], id=u'id_german_benefits_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_relationship_info')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_german_concurrent_study_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_sideeffects_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_statistical_info')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_german_dataprotection_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_aftercare_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_payment_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_abort_info')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_german_dataaccess_info')
    client.type(text=cicero.sentences(n=1, min=15, max=15)[0], id=u'id_german_financing_info')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_german_additional_info')

    # Sponsor
    client.click(link=u'Sponsor')
    client.click(id=u'id_sponsor_name')
    client.type(text=cicero.sentences(n=1, min=6, max=6)[0], id=u'id_sponsor_name')
    client.select(option=u'Herr', id=u'id_sponsor_contact_gender')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_sponsor_contact_title')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_sponsor_contact_first_name')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_sponsor_contact_last_name')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_sponsor_address')
    client.type(text=random.randint(10000,99999), id=u'id_sponsor_zip_code')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_sponsor_city')
    client.type(text=random.randint(100000000,999999999), id=u'id_sponsor_phone')
    client.type(text=random.randint(100000000,999999999), id=u'id_sponsor_fax')
    client.type(text='{0}@example.org'.format(cicero.words(n=1)[0]), id=u'id_sponsor_email')

    # Antragsteller
    client.click(link=u'Antragsteller')
    client.check(id=u'id_submitter_is_main_investigator')
    client.click(id=u'id_submitter_contact_gender')
    client.select(option=u'Frau', id=u'id_submitter_contact_gender')
    #client.click(xpath=u"//select[@id='id_submitter_contact_gender']/option[2]")
    client.click(id=u'id_submitter_contact_title')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_submitter_contact_title')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_submitter_contact_first_name')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_submitter_contact_last_name')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_submitter_organisation')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_submitter_jobtitle')

    # AMG
    if amg:
        client.click(link=u'AMG')
        client.click(id=u'id_eudract_number')
        client.type(text=random.randint(10000,99999), id=u'id_eudract_number')
        client.click(id=u'id_pharma_checked_substance')
        client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_pharma_checked_substance')
        client.click(id=u'id_pharma_reference_substance')
        client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_pharma_reference_substance')

        client.select(val=u'DE', id=u'id_substance_registered_in_countries')
        client.click(id=u'id_substance_preexisting_clinical_tries')
        client.select(val=u'DE', id=u'id_substance_p_c_t_countries')
        client.select(option=u'Nein', id=u'id_substance_preexisting_clinical_tries')
        client.click(value=u'3')
        client.click(id=u'id_substance_p_c_t_phase')
        client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_substance_p_c_t_phase')
        client.click(id=u'id_substance_p_c_t_period')
        client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_substance_p_c_t_period')
        client.click(id=u'id_substance_p_c_t_application_type')
        client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_substance_p_c_t_application_type')
        client.click(id=u'id_substance_p_c_t_gcp_rules')
        client.select(option=u'Ja', id=u'id_substance_p_c_t_gcp_rules')
        #client.click(xpath=u"//select[@id='id_substance_p_c_t_gcp_rules']/option[2]")
        client.click(id=u'id_substance_p_c_t_final_report')
        client.select(option=u'Nein', id=u'id_substance_p_c_t_final_report')

    # MPG
    if mpg:
        client.click(link=u'MPG')
        client.click(id=u'id_medtech_checked_product')
        client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_medtech_checked_product')
        client.click(id=u'id_medtech_reference_substance')
        client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_medtech_reference_substance')
        client.click(id=u'id_medtech_product_name')
        client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_medtech_product_name')
        client.click(id=u'id_medtech_manufacturer')
        client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_medtech_manufacturer')
        client.click(id=u'id_medtech_certified_for_exact_indications')
        client.select(option=u'Ja', id=u'id_medtech_certified_for_exact_indications')
        #client.click(xpath=u"//select[@id='id_medtech_certified_for_exact_indications']/option[2]")
        client.click(id=u'id_medtech_certified_for_other_indications')
        client.select(option=u'Ja', id=u'id_medtech_certified_for_other_indications')
        #client.click(xpath=u"//select[@id='id_medtech_certified_for_other_indications']/option[2]")
        client.click(id=u'id_medtech_ce_symbol')
        client.select(option=u'Nein', id=u'id_medtech_ce_symbol')
        #client.click(xpath=u"//select[@id='id_medtech_ce_symbol']/option[3]")
        client.click(id=u'id_medtech_manual_included')
        client.select(option=u'Nein', id=u'id_medtech_manual_included')
        #client.click(xpath=u"//select[@id='id_medtech_manual_included']/option[3]")
        client.click(id=u'id_medtech_technical_safety_regulations')
        client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_medtech_technical_safety_regulations')
        client.click(id=u'id_medtech_departure_from_regulations')
        client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_medtech_departure_from_regulations')

    # Maßnahmen
    client.click(link=u'Ma\xdfnahmen')
    client.click(xpath=u"//div[@id='tabs-8']/div[1]/a")
    client.click(id=u'id_measure-0-type')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_measure-0-type')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-0-count')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-0-period')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-0-total')
    client.click(xpath=u"//div[@id='tabs-8']/div[1]/a")
    client.click(id=u'id_measure-1-type')
    client.type(text=cicero.sentences(n=1, min=10, max=10)[0], id=u'id_measure-1-type')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-1-count')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-1-period')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-1-total')
    client.click(xpath=u"//div[@id='tabs-8']/div[1]/a")
    client.click(id=u'id_measure-2-type')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_measure-2-type')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-2-count')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-2-period')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_measure-2-total')
    client.click(xpath=u"//div[@id='tabs-8']/div[2]/a")
    client.click(id=u'id_routinemeasure-0-type')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_routinemeasure-0-type')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-0-count')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-0-period')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-0-total')
    client.click(xpath=u"//div[@id='tabs-8']/div[2]/a")
    client.click(id=u'id_routinemeasure-1-type')
    client.type(text=cicero.sentences(n=1, min=8, max=8)[0], id=u'id_routinemeasure-1-type')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-1-count')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-1-period')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-1-total')
    client.click(xpath=u"//div[@id='tabs-8']/div[2]/a")
    client.click(id=u'id_routinemeasure-2-type')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_routinemeasure-2-type')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-2-count')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-2-period')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_routinemeasure-2-total')
    client.click(xpath=u"//div[@id='tabs-8']/div[3]/a")
    client.click(id=u'id_nontesteduseddrug-0-generic_name')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-0-generic_name')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-0-preparation_form')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-0-dosage')
    client.click(xpath=u"//div[@id='tabs-8']/div[3]/a")
    client.click(id=u'id_nontesteduseddrug-1-generic_name')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_nontesteduseddrug-1-generic_name')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_nontesteduseddrug-1-preparation_form')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-1-dosage')
    client.click(xpath=u"//div[@id='tabs-8']/div[3]/a")
    client.click(id=u'id_nontesteduseddrug-2-generic_name')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-2-generic_name')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-2-preparation_form')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_nontesteduseddrug-2-dosage')
    client.click(id=u'id_additional_therapy_info')
    client.type(text=cicero.sentences(n=1, min=8, max=8)[0], id=u'id_additional_therapy_info')

    # Biometrie
    client.click(link=u'Biometrie')
    client.click(id=u'id_study_plan_blind')
    client.select(option=u'doppelblind', id=u'id_study_plan_blind')
    #client.click(xpath=u"//select[@id='id_study_plan_blind']/option[4]")
    client.check(id=u'id_study_plan_placebo')
    client.click(id=u'id_study_plan_misc')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_misc')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_number_of_groups')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_stratification')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_sample_frequency')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_study_plan_primary_objectives')
    client.type(text=cicero.sentences(n=1, min=4, max=4)[0], id=u'id_study_plan_null_hypothesis')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_alternative_hypothesis')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_secondary_objectives')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_alpha')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_power')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_statalgorithm')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_multiple_test_correction_algorithm')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_study_plan_dropout_ratio')
    client.check(id=u'id_study_plan_population_intention_to_treat')
    client.click(id=u'id_study_plan_abort_crit')
    client.type(text=cicero.sentences(n=1, min=4, max=4)[0], id=u'id_study_plan_abort_crit')
    client.click(id=u'id_study_plan_planned_statalgorithm')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_study_plan_planned_statalgorithm')
    client.type(text=cicero.sentences(n=1, min=8, max=8)[0], id=u'id_study_plan_dataquality_checking')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_study_plan_datamanagement')
    client.type(text=cicero.sentences(n=1, min=6, max=6)[0], id=u'id_study_plan_biometric_planning')
    client.type(text=cicero.sentences(n=1, min=8, max=8)[0], id=u'id_study_plan_statistics_implementation')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_study_plan_dataprotection_reason')
    client.type(text=cicero.sentences(n=1, min=4, max=4)[0], id=u'id_study_plan_dataprotection_dvr')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_study_plan_dataprotection_anonalgoritm')

    # Versicherung
    client.click(link=u'Versicherung')
    client.click(id=u'id_insurance_name')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_insurance_name')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_insurance_address')
    client.type(text=random.randint(100000000,999999999), id=u'id_insurance_phone')
    client.type(text=cicero.sentences(n=1, min=8, max=8)[0], id=u'id_insurance_contract_number')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_insurance_validity')

    # Unterlagen
    if upload:
        client.click(link=u'Unterlagen')
        client.execJS(js=u'ecs.windmill_upload("{0}");'.format(MENSCHENRECHTSERKLAERUNG))
        client.click(id=u'id_document-doctype')
        client.select(option=u'patient information', id=u'id_document-doctype')
        #client.click(xpath=u"//select[@id='id_document-doctype']/option[3]")
        client.click(id=u'id_document-name')
        client.type(text=u'Menschenrechtserkl\xe4rung', id=u'id_document-name')
        client.click(id=u'id_document-version')
        client.type(text=u'1', id=u'id_document-version')
        client.click(xpath=u"//div[@id='tabs-11']/div/div[2]/ol/li[5]/input[2]")
        client.type(xpath=u"//div[@id='tabs-11']/div/div[2]/ol/li[5]/input[2]", text=u'10.12.1948')
        client.click(id=u'document_upload_button')
        client.waits.forPageLoad(timeout=u'20000')
        client.waits.sleep(milliseconds=u'5000')

    # Auslandszentren
    client.click(link=u'Auslandszentren')
    client.click(xpath=u"//div[@id='tabs-12']/div/a")
    client.click(id=u'id_foreignparticipatingcenter-0-name')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_foreignparticipatingcenter-0-name')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_foreignparticipatingcenter-0-investigator_name')
    client.click(xpath=u"//div[@id='tabs-12']/div/a")
    client.click(id=u'id_foreignparticipatingcenter-1-name')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_foreignparticipatingcenter-1-name')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_foreignparticipatingcenter-1-investigator_name')
    client.click(xpath=u"//div[@id='tabs-12']/div/a")
    client.click(id=u'id_foreignparticipatingcenter-2-name')
    client.type(text=cicero.sentences(n=1, min=4, max=4)[0], id=u'id_foreignparticipatingcenter-2-name')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_foreignparticipatingcenter-2-investigator_name')

    # Zentrum 1
    client.click(link=u'Zentrum 1')
    client.click(id=u'id_investigator-0-organisation')
    client.type(text=cicero.sentences(n=1, min=6, max=6)[0], id=u'id_investigator-0-organisation')
    client.type(text=random.randint(0,999), id=u'id_investigator-0-subject_count')
    client.click(value=u'21')
    client.select(option=u'Ethikkomission der Medizinischen Universit\xe4t Wien', id=u'id_investigator-0-ethics_commission')
    #client.click(xpath=u"//select[@id='id_investigator-0-ethics_commission']/option[2]")
    client.click(id=u'id_investigator-0-contact_gender')
    client.select(option=u'Herr', id=u'id_investigator-0-contact_gender')
    #client.click(xpath=u"//select[@id='id_investigator-0-contact_gender']/option[3]")
    client.click(id=u'id_investigator-0-contact_title')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_investigator-0-contact_title')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_investigator-0-contact_first_name')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_investigator-0-contact_last_name')
    client.type(text=random.randint(100000000,999999999), id=u'id_investigator-0-phone')
    client.click(id=u'id_investigator-0-mobile')
    client.type(text=random.randint(100000000,999999999), id=u'id_investigator-0-mobile')
    client.type(text=random.randint(100000000,999999999), id=u'id_investigator-0-fax')
    client.click(id=u'id_investigator-0-email')
    client.type(text='{0}@example.org'.format(cicero.words(n=1)[0]), id=u'id_investigator-0-email')
    client.check(id=u'id_investigator-0-jus_practicandi')
    client.check(id=u'id_investigator-0-certified')
    client.click(id=u'id_investigator-0-specialist')
    client.type(text=cicero.sentences(n=1, min=5, max=5)[0], id=u'id_investigator-0-specialist')
    client.click(id=u'id_investigatoremployee-0-sex')
    client.select(option=u'Herr', id=u'id_investigatoremployee-0-sex')
    #client.click(xpath=u"//select[@id='id_investigatoremployee-0-sex']/option[2]")
    client.click(id=u'id_investigatoremployee-0-title')
    client.type(text=cicero.sentences(n=1, min=2, max=2)[0], id=u'id_investigatoremployee-0-title')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_investigatoremployee-0-surname')
    client.type(text=cicero.sentences(n=1, min=1, max=1)[0], id=u'id_investigatoremployee-0-firstname')
    client.type(text=cicero.sentences(n=1, min=3, max=3)[0], id=u'id_investigatoremployee-0-organisation')

    # and now submit!
    client.click(name=u'submit')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'5000')
    client.waits.forElement(timeout=u'10000', id=u'overlay')
    client.click(value=u'Ok')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.sleep(milliseconds=u'5000')
    # client.select(option=u'---------', id=u'userswitcher_input')
    # client.click(xpath=u"//select[@id='userswitcher_input']/option[1]")

@authenticated()
def test_submit_simplest(client):
    create_submission(client)

@authenticated()
def test_submit_simple(client):
    create_submission(client, upload=True)

@authenticated()
def test_submit_amg(client):
    create_submission(client, amg=True, upload=True)

@authenticated()
def test_submit_mpg(client):
    create_submission(client, mpg=True, upload=True)

@authenticated()
def test_submit_thesis(client):
    create_submission(client, thesis=True, upload=True)

@authenticated()
def test_submit_amg_mpg(client):
    create_submission(client, amg=True, mpg=True, upload=True)

@authenticated()
def test_submit_amg_thesis(client):
    create_submission(client, amg=True, thesis=True, upload=True)

@authenticated()
def test_submit_mpg_thesis(client):
    create_submission(client, mpg=True, thesis=True, upload=True)

@authenticated()
def test_submit_amg_mpg_thesis(client):
    create_submission(client, amg=True, mpg=True, thesis=True, upload=True)


