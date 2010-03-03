# -*- coding: utf-8 -*-
import os
import reversion

from django.db import models
from django.contrib.auth.models import User
from django.utils.importlib import import_module
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils._os import safe_join
from django.utils.encoding import smart_str

# metaclassen:
#  master control programm model:
#   date, time, user, uuid,  
class Workflow(models.Model):
    pass

class DocumentType(models.Model):
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.name

def upload_document_to(instance=None, filename=None):
    dirs = list(instance.uuid_document_revision[:6]) + [instance.uuid_document_revision]
    return os.path.join(settings.FILESTORE, *dirs)
    
class DocumentFileStorage(FileSystemStorage):
    def path(self, name):
        # We need to overwrite the default behavior, because django won't let us save documents outside of MEDIA_ROOT
        return smart_str(os.path.normpath(name))


class Document(models.Model):
    uuid_document = models.SlugField(max_length=32)
    uuid_document_revision = models.SlugField(max_length=32)
    # file path is derived from the uuid_document_revision
    file = models.FileField(null=True, upload_to=upload_document_to, storage=DocumentFileStorage())
    doctype = models.ForeignKey(DocumentType, null=True, blank=True)
    mimetype = models.CharField(max_length=100, default='application/pdf')

    version = models.CharField(max_length=250)
    date = models.DateTimeField()

    # this document is only being refered to, but it does not exist physically in the system:
    absent = models.BooleanField()


class EthicsCommission(models.Model):
    name = models.CharField(max_length=60)
    address_1 = models.CharField(max_length=60)
    address_2 = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=40)
    contactname = models.CharField(max_length=120, null=True)
    chairperson = models.CharField(max_length=120, null=True)
    email = models.EmailField(null=True)
    url = models.URLField(null=True)
    phone = models.CharField(max_length=30, null=True)
    fax = models.CharField(max_length=30, null=True)
    
    def __unicode__(self):
        return self.name

class SubmissionForm(models.Model):
    project_title = models.CharField(max_length=120)
    protocol_number = models.CharField(max_length=40, null=True)
    ethics_commissions = models.ManyToManyField(EthicsCommission, related_name='submission_forms', through='Investigator')
    date_of_protocol = models.DateField()
    eudract_number = models.CharField(max_length=40, null=True)
    isrctn_number = models.CharField(max_length=40, null=True)
    sponsor_name = models.CharField(max_length=80, null=True)
    sponsor_contactname = models.CharField(max_length=80, null=True)
    sponsor_address1 = models.CharField(max_length=60, null=True)
    sponsor_address2 = models.CharField(max_length=60, null=True)
    sponsor_zip_code = models.CharField(max_length=10, null=True)
    sponsor_city = models.CharField(max_length=40, null=True)
    sponsor_phone = models.CharField(max_length=30, null=True)
    sponsor_fax = models.CharField(max_length=30, null=True)
    sponsor_email = models.EmailField(null=True)
    invoice_name = models.CharField(max_length=80, null=True)
    invoice_contactname = models.CharField(max_length=80, null=True)
    invoice_address1 = models.CharField(max_length=60, null=True)
    invoice_address2 = models.CharField(max_length=60, null=True)
    invoice_zip_code = models.CharField(max_length=10, null=True)
    invoice_city = models.CharField(max_length=40, null=True)
    invoice_phone = models.CharField(max_length=30, null=True)
    invoice_fax = models.CharField(max_length=30, null=True)
    invoice_email = models.EmailField(null=True)
    invoice_uid = models.CharField(max_length=30, null=True) # 24? need to check
    invoice_uid_verified_level1 = models.DateTimeField(null=True) # can be done via EU API
    invoice_uid_verified_level2 = models.DateTimeField(null=True) # can be done manually via Tax Authority, local.
    # TODO: invoice_uid_verified_level2 should also have a field who handled the level2 verification.
    
    # page 2:

    for i in ("2_1_1", "2_1_2", "2_1_2_1", "2_1_2_2", 
              "2_1_3", "2_1_4", "2_1_4_1", "2_1_4_2", 
              "2_1_4_3", "2_1_5", "2_1_6", "2_1_7", 
              "2_1_8", "2_1_9"):
        exec "project_type_%s = models.BooleanField()" % i
    
    specialism = models.TextField(null=True) # choices???
    pharma_checked_substance = models.TextField(null=True)
    pharma_reference_substance = models.TextField(null=True)
    
    medtech_checked_product = models.TextField(null=True)
    medtech_reference_substance = models.TextField(null=True)

    clinical_phase = models.CharField(max_length=10)
    already_voted = models.BooleanField()
    
    subject_count = models.IntegerField()
    subject_minage = models.IntegerField()
    subject_maxage = models.IntegerField()
    subject_noncompetents = models.BooleanField()
    subject_males = models.BooleanField()    
    subject_females = models.BooleanField()
    subject_childbearing = models.BooleanField()
    subject_duration = models.CharField(max_length=20)
    subject_duration_active = models.CharField(max_length=20)
    subject_duration_controls = models.CharField(max_length=20)
    subject_planned_total_duration = models.CharField(max_length=20)

    # page 3:

    substance_registered_in_countries = models.CharField(max_length=300, null=True) # comma seperated 2 letter codes.
    substance_preexisting_clinical_tries = models.NullBooleanField()
    substance_p_c_t_countries = models.CharField(max_length=300, null=True) # comma seperated 2 letter codes.
    substance_p_c_t_phase = models.CharField(max_length=10, null=True)
    substance_p_c_t_period = models.TextField(null=True)
    substance_p_c_t_application_type = models.CharField(max_length=40, null=True)
    substance_p_c_t_gcp_rules = models.NullBooleanField()
    substance_p_c_t_final_report = models.NullBooleanField()

    medtech_product_name = models.CharField(max_length=80, null=True)
    medtech_manufacturer = models.CharField(max_length=80, null=True)
    medtech_certified_for_exact_indications = models.NullBooleanField()
    medtech_certified_for_other_indications = models.NullBooleanField()
    medtech_ce_symbol = models.NullBooleanField()
    medtech_manual_included = models.NullBooleanField()
    medtech_technical_safety_regulations = models.TextField(null=True)
    medtech_technical_safety_regulations = models.TextField(null=True)
    medtech_departure_from_regulations = models.TextField(null=True)

    insurance_name = models.CharField(max_length=60, null=True)
    insurance_address_1 = models.CharField(max_length=80, null=True)
    insurance_phone = models.CharField(max_length=30, null=True)
    insurance_contract_number = models.CharField(max_length=60, null=True)
    insurance_validity = models.CharField(max_length=60, null=True)

    # page 5
    
    additional_therapy_info = models.TextField()

    # page 6

    german_project_title = models.TextField(null=True)
    german_summary = models.TextField(null=True)
    german_preclinical_results = models.TextField(null=True)
    german_primary_hypothesis = models.TextField(null=True)
    german_inclusion_exclusion_crit = models.TextField(null=True)
    german_ethical_info = models.TextField(null=True)
    german_protected_subjects_info = models.TextField(null=True)
    german_recruitment_info = models.TextField(null=True)
    german_consent_info = models.TextField(null=True)
    german_risks_info = models.TextField(null=True)
    german_benefits_info = models.TextField(null=True)
    german_relationship_info = models.TextField(null=True)
    german_concurrent_study_info = models.TextField(null=True)
    german_sideeffects_info = models.TextField(null=True)

    # page 7
    german_statistical_info = models.TextField(null=True)
    german_dataprotection_info = models.TextField(null=True)
    german_aftercare_info = models.TextField(null=True)
    german_payment_info = models.TextField(null=True)
    german_abort_info = models.TextField(null=True)
    german_dataaccess_info = models.TextField(null=True)
    german_financing_info = models.TextField(null=True)
    #     @form_meta(tab=7, paper="7.20")
    #     def form_meta(**kw):
    #         def func(f):
    #             for k, v in kw.items():
    #                 setattr(f, k, v)
    #             return f
    #         return func
            
    german_additional_info = models.TextField(null=True)

    
    # page 8

    for i in range(1, 15):
        exec "study_plan_8_1_%d = models.BooleanField(default=False)" % i

    for i in range(15, 23):
        exec "study_plan_8_1_%d = models.TextField(default='', null=True)" % i

    study_plan_alpha = models.CharField(max_length=40)
    study_plan_power = models.CharField(max_length=40)
    study_plan_statalgorithm = models.CharField(max_length=40)
    study_plan_multiple_test_correction_algorithm = models.CharField(max_length=40)
    study_plan_dropout_ratio = models.CharField(max_length=40)

    study_plan_8_3_1 = models.BooleanField()
    study_plan_8_3_2 = models.BooleanField()
    study_plan_abort_crit = models.CharField(max_length=40)
    study_plan_planned_statalgorithm = models.CharField(max_length=40)

    study_plan_dataquality_checking = models.TextField()
    study_plan_datamanagement = models.TextField()

    study_plan_biometric_planning = models.CharField(max_length=120)
    study_plan_statistics_implementation = models.CharField(max_length=120)

    # either anonalgorith or reason or dvr may be set.
    study_plan_dataprotection_reason = models.CharField(max_length=120)
    study_plan_dataprotection_dvr = models.CharField(max_length=12)
    study_plan_dataprotection_anonalgoritm = models.TextField(null=True)

    # page 9
    
    submitter_name = models.CharField(max_length=80)
    submitter_organisation = models.CharField(max_length=80)
    submitter_jobtitle = models.CharField(max_length=80)
    submitter_is_coordinator = models.BooleanField()
    submitter_is_main_investigator = models.BooleanField()
    submitter_is_sponsor = models.BooleanField()
    submitter_is_authorized_by_sponsor = models.BooleanField()

    # needs to be nullable.
    submitter_sign_date = models.DateField()

    # page 11
    # wrong class???
    investigator_name = models.CharField(max_length=80)
    investigator_organisation = models.CharField(max_length=80)
    investigator_phone = models.CharField(max_length=30)
    investigator_mobile = models.CharField(max_length=30)
    investigator_fax = models.CharField(max_length=30)
    investigator_email = models.EmailField()
    investigator_jus_practicandi = models.BooleanField()
    investigator_specialist = models.CharField(max_length=80)
    investigator_certified = models.BooleanField()

class Investigator(models.Model):
    submission = models.ForeignKey(SubmissionForm, related_name='investigators')
    ethics_commission = models.ForeignKey(EthicsCommission, null=True, related_name='investigators')
    main = models.BooleanField(default=False, blank=True)

    name = models.CharField(max_length=80)
    organisation = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    fax = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    jus_practicandi = models.BooleanField(default=False, blank=True)
    specialist = models.CharField(max_length=80, blank=True)
    certified = models.BooleanField(default=False, blank=True)
    subject_count = models.IntegerField()
    sign_date = models.DateField()

class InvestigatorEmployee(models.Model):
    submission = models.ForeignKey(Investigator)

    sex = models.CharField(max_length=1, choices=[("m", "male"), ("f", "female"), ("?", "")])
    title = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    firstname = models.CharField(max_length=40)
    organisation = models.CharField(max_length=80)

class TherapiesApplied(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    type = models.CharField(max_length=30)    
    count = models.IntegerField(null=True)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)

class DiagnosticsApplied(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    type = models.CharField(max_length=30)    
    count = models.IntegerField(null=True)
    period = models.CharField(max_length=30)
    total = models.CharField(max_length=30)


class NonTestedUsedDrugs(models.Model):
    submission = models.ForeignKey(SubmissionForm)

    generic_name = models.CharField(max_length=40)
    preparation_form = models.CharField(max_length=40)
    dosage = models.CharField(max_length=40)

class ParticipatingCenter(models.Model):
    submission = models.ForeignKey(SubmissionForm)
    
    name = models.CharField(max_length=60)
    address_1 = models.CharField(max_length=60)
    address_2 = models.CharField(max_length=60)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=40)
    country = models.CharField(max_length=4)
    
class Amendment(models.Model):
    submissionform = models.ForeignKey(SubmissionForm)
    order = models.IntegerField()
    number = models.CharField(max_length=40)
    date = models.DateField()

class NotificationType(models.Model):
    name = models.CharField(max_length=40, unique=True)
    form = models.CharField(max_length=80, default='ecs.core.forms.BaseNotificationForm')
    model = models.CharField(max_length=80, default='ecs.core.models.BaseNotificationForm')
    
    @property
    def form_cls(self):
        if not hasattr(self, '_form_cls'):
            module, cls_name = self.form.rsplit('.', 1)
            self._form_cls = getattr(import_module(module), cls_name)
        return self._form_cls
    
    def __unicode__(self):
        return self.name


class BaseNotificationForm(models.Model):
    type = models.ForeignKey(NotificationType, null=True, related_name='notification_forms')    
    investigators = models.ManyToManyField(Investigator, related_name='notification_forms')
    submission_forms = models.ManyToManyField(SubmissionForm)    
    investigator = models.ForeignKey(Investigator, null=True, blank=True)
    documents = models.ManyToManyField(Document)

    comments = models.TextField(default="", blank=True)
    signed_on = models.DateField(null=True, blank=True)
    
    def __unicode__(self):
        return u"%s vom %s" % (self.type, self.signed_on)


class ExtendedNotificationForm(BaseNotificationForm):
    reason_for_not_started = models.TextField(null=True, blank=True)
    recruited_subjects = models.IntegerField(null=True, blank=True)
    finished_subjects = models.IntegerField(null=True, blank=True)
    aborted_subjects = models.IntegerField(null=True, blank=True)
    SAE_count = models.IntegerField(null=True, blank=True)
    SUSAR_count = models.IntegerField(null=True, blank=True)
    runs_till = models.DateField(null=True, blank=True)
    finished_on = models.DateField(null=True, blank=True)
    aborted_on = models.DateField(null=True, blank=True)
    extension_of_vote = models.BooleanField(default=False, blank=True)


class Checklist(models.Model):
    pass

class SubmissionSet(models.Model):
    submission = models.ForeignKey("Submission", related_name="sets")
    documents = models.ManyToManyField(Document)
    submissionform = models.ForeignKey(SubmissionForm)

class VoteReview(models.Model):   
    workflow = models.ForeignKey(Workflow)

class Vote(models.Model):
    votereview = models.ForeignKey(VoteReview)
    submissionset = models.ForeignKey(SubmissionSet)
    checklists = models.ManyToManyField(Checklist)
    workflow = models.ForeignKey(Workflow)

class SubmissionReview(models.Model):   
    workflow = models.ForeignKey(Workflow)

class Submission(models.Model):
    ec_number = models.CharField(max_length=50, null=True, blank=True)
    submissionreview = models.ForeignKey(SubmissionReview, null=True)
    vote = models.ForeignKey(Vote, null=True)
    workflow = models.ForeignKey(Workflow, null=True)

class NotificationAnswer(models.Model):
    workflow = models.ForeignKey(Workflow)
 
class Meeting(models.Model):
    submissions = models.ManyToManyField(Submission)
"""
class Revision(models.Model):
    pass

class Message(models.Model):
    pass

class AuditLog(models.Model):
    pass


class User(models.Model):
    pass

class Reviewer(models.Model):
    pass

class Annotation(models.Model):
    pass
"""

# Register models conditionally to avoid `already registered` errors when this module gets loaded twice.
if not reversion.is_registered(Amendment):
    reversion.register(Amendment) 
    reversion.register(Checklist) 
    reversion.register(DiagnosticsApplied) 
    reversion.register(Document) 
    reversion.register(EthicsCommission) 
    reversion.register(Meeting) 
    reversion.register(ParticipatingCenter) 
    reversion.register(Submission) 
    reversion.register(SubmissionForm) 
    reversion.register(SubmissionReview) 
    reversion.register(NonTestedUsedDrugs) 
    reversion.register(NotificationAnswer) 
    reversion.register(BaseNotificationForm) 
    reversion.register(ExtendedNotificationForm) 
    reversion.register(SubmissionSet) 
    reversion.register(Investigator) 
    reversion.register(InvestigatorEmployee) 
    reversion.register(TherapiesApplied) 
    reversion.register(Vote) 
    reversion.register(VoteReview) 
    reversion.register(Workflow)
                                             