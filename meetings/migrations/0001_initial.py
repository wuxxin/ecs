# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AssignedMedicalCategory'
        db.create_table('meetings_assignedmedicalcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.MedicalCategory'])),
            ('board_member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='assigned_medical_categories', null=True, to=orm['auth.User'])),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='medical_categories', to=orm['meetings.Meeting'])),
        ))
        db.send_create_signal('meetings', ['AssignedMedicalCategory'])

        # Adding unique constraint on 'AssignedMedicalCategory', fields ['category', 'meeting']
        db.create_unique('meetings_assignedmedicalcategory', ['category_id', 'meeting_id'])

        # Adding model 'Meeting'
        db.create_table('meetings_meeting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('optimization_task_id', self.gf('django.db.models.fields.TextField')(null=True)),
            ('started', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('ended', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('comments', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('deadline_diplomathesis', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('meetings', ['Meeting'])

        # Adding model 'TimetableEntry'
        db.create_table('meetings_timetableentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='timetable_entries', to=orm['meetings.Meeting'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('timetable_index', self.gf('django.db.models.fields.IntegerField')()),
            ('duration_in_seconds', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('is_break', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(related_name='timetable_entries', null=True, to=orm['core.Submission'])),
            ('sponsor_invited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('optimal_start', self.gf('django.db.models.fields.TimeField')(null=True)),
            ('is_open', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('meetings', ['TimetableEntry'])

        # Adding model 'Participation'
        db.create_table('meetings_participation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(related_name='participations', to=orm['meetings.TimetableEntry'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meeting_participations', to=orm['auth.User'])),
            ('medical_category', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='meeting_participations', null=True, to=orm['core.MedicalCategory'])),
        ))
        db.send_create_signal('meetings', ['Participation'])

        # Adding model 'Constraint'
        db.create_table('meetings_constraint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meeting', self.gf('django.db.models.fields.related.ForeignKey')(related_name='constraints', to=orm['meetings.Meeting'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meeting_constraints', to=orm['auth.User'])),
            ('start_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('end_time', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.FloatField')(default=0.5)),
        ))
        db.send_create_signal('meetings', ['Constraint'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'AssignedMedicalCategory', fields ['category', 'meeting']
        db.delete_unique('meetings_assignedmedicalcategory', ['category_id', 'meeting_id'])

        # Deleting model 'AssignedMedicalCategory'
        db.delete_table('meetings_assignedmedicalcategory')

        # Deleting model 'Meeting'
        db.delete_table('meetings_meeting')

        # Deleting model 'TimetableEntry'
        db.delete_table('meetings_timetableentry')

        # Deleting model 'Participation'
        db.delete_table('meetings_participation')

        # Deleting model 'Constraint'
        db.delete_table('meetings_constraint')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'core.ethicscommission': {
            'Meta': {'object_name': 'EthicsCommission'},
            'address_1': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'address_2': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'chairperson': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'contactname': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '120'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'core.expeditedreviewcategory': {
            'Meta': {'object_name': 'ExpeditedReviewCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'expedited_review_categories'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'core.investigator': {
            'Meta': {'object_name': 'Investigator'},
            'certified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'contact_title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'ethics_commission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigators'", 'null': 'True', 'to': "orm['core.EthicsCommission']"}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jus_practicandi': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'main': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mobile': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'organisation': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'specialist': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigators'", 'to': "orm['core.SubmissionForm']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'investigations'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'core.medicalcategory': {
            'Meta': {'object_name': 'MedicalCategory'},
            'abbrev': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'users': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'medical_categories'", 'symmetrical': 'False', 'to': "orm['auth.User']"})
        },
        'core.submission': {
            'Meta': {'object_name': 'Submission'},
            'additional_reviewers': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'additional_review_submission_set'", 'blank': 'True', 'to': "orm['auth.User']"}),
            'befangene': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'befangen_for_submissions'", 'null': 'True', 'to': "orm['auth.User']"}),
            'billed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'current_submission_form': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'current_for_submission'", 'unique': 'True', 'null': 'True', 'to': "orm['core.SubmissionForm']"}),
            'ec_number': ('django.db.models.fields.PositiveIntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'expedited': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'expedited_review_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.ExpeditedReviewCategory']"}),
            'external_reviewer': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'external_reviewer_billed_at': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'external_reviewer_name': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reviewed_submissions'", 'null': 'True', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insurance_review_required': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_amg': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'is_mpg': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medical_categories': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submissions'", 'blank': 'True', 'to': "orm['core.MedicalCategory']"}),
            'next_meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'_current_for_submissions'", 'null': 'True', 'to': "orm['meetings.Meeting']"}),
            'remission': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'retrospective': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'sponsor_required_for_next_meeting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'thesis': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        'core.submissionform': {
            'Meta': {'object_name': 'SubmissionForm'},
            'acknowledged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'additional_therapy_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'already_voted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'clinical_phase': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'current_pending_vote': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'_currently_pending_for'", 'unique': 'True', 'null': 'True', 'to': "orm['core.Vote']"}),
            'current_published_vote': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'_currently_published_for'", 'unique': 'True', 'null': 'True', 'to': "orm['core.Vote']"}),
            'date_of_receipt': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'documents': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submission_forms'", 'null': 'True', 'to': "orm['documents.Document']"}),
            'ethics_commissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'submission_forms'", 'symmetrical': 'False', 'through': "orm['core.Investigator']", 'to': "orm['core.EthicsCommission']"}),
            'eudract_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'external_reviewer_suggestions': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_abort_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_additional_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_aftercare_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_benefits_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_concurrent_study_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_consent_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_dataaccess_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_dataprotection_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_ethical_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_financing_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_inclusion_exclusion_crit': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_payment_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_preclinical_results': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_primary_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_project_title': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_protected_subjects_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_recruitment_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_relationship_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_risks_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_sideeffects_info': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'german_statistical_info': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'german_summary': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insurance_address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'insurance_contract_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'insurance_name': ('django.db.models.fields.CharField', [], {'max_length': '125', 'null': 'True', 'blank': 'True'}),
            'insurance_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'insurance_validity': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_address': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'invoice_city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'invoice_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'invoice_contact_gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'invoice_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'invoice_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'invoice_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'invoice_fax': ('django.db.models.fields.CharField', [], {'max_length': '45', 'null': 'True', 'blank': 'True'}),
            'invoice_name': ('django.db.models.fields.CharField', [], {'max_length': '160', 'null': 'True', 'blank': 'True'}),
            'invoice_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'invoice_uid': ('django.db.models.fields.CharField', [], {'max_length': '35', 'null': 'True', 'blank': 'True'}),
            'invoice_uid_verified_level1': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'invoice_uid_verified_level2': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'invoice_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'medtech_ce_symbol': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_certified_for_exact_indications': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_certified_for_other_indications': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_checked_product': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_departure_from_regulations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_manual_included': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'medtech_product_name': ('django.db.models.fields.CharField', [], {'max_length': '210', 'null': 'True', 'blank': 'True'}),
            'medtech_reference_substance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'medtech_technical_safety_regulations': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pdf_document': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'submission_form'", 'unique': 'True', 'null': 'True', 'to': "orm['documents.Document']"}),
            'pharma_checked_substance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'pharma_reference_substance': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'presenter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'presented_submission_forms'", 'to': "orm['auth.User']"}),
            'primary_investigator': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['core.Investigator']", 'unique': 'True', 'null': 'True'}),
            'project_title': ('django.db.models.fields.TextField', [], {}),
            'project_type_basic_research': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_biobank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_education_context': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'project_type_genetic_study': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_medical_device': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_medical_device_performance_evaluation': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_medical_device_with_ce': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_medical_device_without_ce': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_medical_method': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_misc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'project_type_non_reg_drug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_psychological_study': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_questionnaire': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_reg_drug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_reg_drug_not_within_indication': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_reg_drug_within_indication': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_register': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'project_type_retrospective': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'protocol_number': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'specialism': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'sponsor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sponsored_submission_forms'", 'null': 'True', 'to': "orm['auth.User']"}),
            'sponsor_address': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'}),
            'sponsor_agrees_to_publishing': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sponsor_city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True'}),
            'sponsor_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'sponsor_contact_gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'sponsor_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'sponsor_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sponsor_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'sponsor_fax': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'sponsor_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            'sponsor_phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'sponsor_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True'}),
            'study_plan_abort_crit': ('django.db.models.fields.CharField', [], {'max_length': '265'}),
            'study_plan_alpha': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_alternative_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_biometric_planning': ('django.db.models.fields.CharField', [], {'max_length': '260'}),
            'study_plan_blind': ('django.db.models.fields.SmallIntegerField', [], {}),
            'study_plan_controlled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_cross_over': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_datamanagement': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dataprotection_anonalgoritm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_dataprotection_dvr': ('django.db.models.fields.CharField', [], {'max_length': '180', 'blank': 'True'}),
            'study_plan_dataprotection_reason': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'study_plan_dataquality_checking': ('django.db.models.fields.TextField', [], {}),
            'study_plan_dropout_ratio': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_equivalence_testing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_factorized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_misc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_multiple_test_correction_algorithm': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'study_plan_null_hypothesis': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_number_of_groups': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_observer_blinded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_parallelgroups': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_pilot_project': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_placebo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_planned_statalgorithm': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_population_intention_to_treat': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_population_per_protocol': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_power': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'study_plan_primary_objectives': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_randomized': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'study_plan_sample_frequency': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_secondary_objectives': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'study_plan_statalgorithm': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'study_plan_statistics_implementation': ('django.db.models.fields.CharField', [], {'max_length': '270'}),
            'study_plan_stratification': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'subject_childbearing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_count': ('django.db.models.fields.IntegerField', [], {}),
            'subject_duration': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_duration_active': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_duration_controls': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_females': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_males': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_maxage': ('django.db.models.fields.IntegerField', [], {}),
            'subject_minage': ('django.db.models.fields.IntegerField', [], {}),
            'subject_noncompetents': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subject_planned_total_duration': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'forms'", 'to': "orm['core.Submission']"}),
            'submission_type': ('django.db.models.fields.SmallIntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'submitter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'submitted_submission_forms'", 'null': 'True', 'to': "orm['auth.User']"}),
            'submitter_contact_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'submitter_contact_gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'submitter_contact_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'submitter_contact_title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'submitter_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True'}),
            'submitter_is_authorized_by_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submitter_is_coordinator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submitter_is_main_investigator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submitter_is_sponsor': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submitter_jobtitle': ('django.db.models.fields.CharField', [], {'max_length': '130'}),
            'submitter_organisation': ('django.db.models.fields.CharField', [], {'max_length': '180'}),
            'substance_p_c_t_application_type': ('django.db.models.fields.CharField', [], {'max_length': '145', 'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_countries': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['countries.Country']", 'symmetrical': 'False', 'blank': 'True'}),
            'substance_p_c_t_final_report': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_gcp_rules': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_period': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'substance_p_c_t_phase': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'substance_preexisting_clinical_tries': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'db_column': "'existing_tries'", 'blank': 'True'}),
            'substance_registered_in_countries': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'submission_forms'", 'blank': 'True', 'db_table': "'submission_registered_countries'", 'to': "orm['countries.Country']"})
        },
        'core.vote': {
            'Meta': {'object_name': 'Vote'},
            'executive_review_required': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_final': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'published_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True'}),
            'signed_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'submission_form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'votes'", 'to': "orm['core.SubmissionForm']"}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'top': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'vote'", 'unique': 'True', 'null': 'True', 'to': "orm['meetings.TimetableEntry']"})
        },
        'countries.country': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Country', 'db_table': "'country'"},
            'iso': ('django.db.models.fields.CharField', [], {'max_length': '2', 'primary_key': 'True'}),
            'iso3': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'numcode': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'printable_name': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        'documents.document': {
            'Meta': {'object_name': 'Document'},
            'allow_download': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'branding': ('django.db.models.fields.CharField', [], {'default': "'b'", 'max_length': '1'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'deleted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'doctype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.DocumentType']", 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '250', 'null': 'True'}),
            'hash': ('django.db.models.fields.SlugField', [], {'max_length': '32', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimetype': ('django.db.models.fields.CharField', [], {'default': "'application/pdf'", 'max_length': '100'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True'}),
            'original_file_name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'pages': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'replaces_document': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['documents.Document']", 'null': 'True', 'blank': 'True'}),
            'uuid_document': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '36', 'db_index': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        'documents.documenttype': {
            'Meta': {'object_name': 'DocumentType'},
            'helptext': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'meetings.assignedmedicalcategory': {
            'Meta': {'unique_together': "(('category', 'meeting'),)", 'object_name': 'AssignedMedicalCategory'},
            'board_member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'assigned_medical_categories'", 'null': 'True', 'to': "orm['auth.User']"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['core.MedicalCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'medical_categories'", 'to': "orm['meetings.Meeting']"})
        },
        'meetings.constraint': {
            'Meta': {'object_name': 'Constraint'},
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'constraints'", 'to': "orm['meetings.Meeting']"}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_constraints'", 'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.FloatField', [], {'default': '0.5'})
        },
        'meetings.meeting': {
            'Meta': {'object_name': 'Meeting'},
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'deadline_diplomathesis': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'ended': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optimization_task_id': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'started': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'submissions': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'meetings'", 'symmetrical': 'False', 'through': "orm['meetings.TimetableEntry']", 'to': "orm['core.Submission']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'meetings.participation': {
            'Meta': {'object_name': 'Participation'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'participations'", 'to': "orm['meetings.TimetableEntry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medical_category': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meeting_participations'", 'null': 'True', 'to': "orm['core.MedicalCategory']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_participations'", 'to': "orm['auth.User']"})
        },
        'meetings.timetableentry': {
            'Meta': {'object_name': 'TimetableEntry'},
            'duration_in_seconds': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_break': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'timetable_entries'", 'to': "orm['meetings.Meeting']"}),
            'optimal_start': ('django.db.models.fields.TimeField', [], {'null': 'True'}),
            'sponsor_invited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'timetable_entries'", 'null': 'True', 'to': "orm['core.Submission']"}),
            'timetable_index': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['meetings']
