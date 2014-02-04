# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UserGoogle'
        db.create_table(u'social_usergoogle', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.User'], primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(default='', max_length=75)),
            ('google_id', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=22, decimal_places=0, db_index=True)),
            ('is_show', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'social', ['UserGoogle'])

        # Adding model 'UserPasswordReset'
        db.create_table(u'social_userpasswordreset', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.User'], primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(default='EdteuQUmm2jTCcfyjNTohqFjcRS5DoSBa3mg6xOp0AimzdiB0KugyIdMX2N9NoVe', max_length=64, db_index=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'social', ['UserPasswordReset'])

        # Adding model 'UserFacebook'
        db.create_table(u'social_userfacebook', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.User'], primary_key=True)),
            ('facebook_id', self.gf('django.db.models.fields.BigIntegerField')(default=0, db_index=True)),
            ('access_token', self.gf('django.db.models.fields.CharField')(default='', max_length=400)),
            ('is_show', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'social', ['UserFacebook'])

        # Adding model 'UserEmailVerify'
        db.create_table(u'social_useremailverify', (
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.User'], primary_key=True)),
            ('token', self.gf('django.db.models.fields.CharField')(default='LVV0PJb58ATTeCciYZEB67SHKLuIEMiKPjJTI0hog0xfMhy1Ms6j4beoONLtt0vK', max_length=64, db_index=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=254)),
        ))
        db.send_create_signal(u'social', ['UserEmailVerify'])

        # Adding model 'User'
        db.create_table(u'social_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('dob', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('photo', self.gf('sorl.thumbnail.fields.ImageField')(max_length=100)),
            ('locale', self.gf('django.db.models.fields.CharField')(default='en', max_length=4)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='U', max_length=1, db_index=True)),
            ('bio', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('timezone_offset', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=3, decimal_places=1, blank=True)),
            ('email_tbd', self.gf('django.db.models.fields.CharField')(default='', max_length=75, blank=True)),
            ('is_super', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'social', ['User'])


    def backwards(self, orm):
        # Deleting model 'UserGoogle'
        db.delete_table(u'social_usergoogle')

        # Deleting model 'UserPasswordReset'
        db.delete_table(u'social_userpasswordreset')

        # Deleting model 'UserFacebook'
        db.delete_table(u'social_userfacebook')

        # Deleting model 'UserEmailVerify'
        db.delete_table(u'social_useremailverify')

        # Deleting model 'User'
        db.delete_table(u'social_user')


    models = {
        u'social.user': {
            'Meta': {'object_name': 'User'},
            'bio': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'email_tbd': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_super': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'locale': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '4'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'photo': ('sorl.thumbnail.fields.ImageField', [], {'max_length': '100'}),
            'timezone_offset': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '3', 'decimal_places': '1', 'blank': 'True'})
        },
        u'social.useremailverify': {
            'Meta': {'object_name': 'UserEmailVerify'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'LVV0PJb58ATTeCciYZEB67SHKLuIEMiKPjJTI0hog0xfMhy1Ms6j4beoONLtt0vK'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.User']", 'primary_key': 'True'})
        },
        u'social.userfacebook': {
            'Meta': {'object_name': 'UserFacebook'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'is_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.User']", 'primary_key': 'True'})
        },
        u'social.usergoogle': {
            'Meta': {'object_name': 'UserGoogle'},
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75'}),
            'google_id': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '22', 'decimal_places': '0', 'db_index': 'True'}),
            'is_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.User']", 'primary_key': 'True'})
        },
        u'social.userpasswordreset': {
            'Meta': {'object_name': 'UserPasswordReset'},
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'EdteuQUmm2jTCcfyjNTohqFjcRS5DoSBa3mg6xOp0AimzdiB0KugyIdMX2N9NoVe'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.User']", 'primary_key': 'True'})
        }
    }

    complete_apps = ['social']