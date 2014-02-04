# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'User.is_active'
        db.add_column(u'social_user', 'is_active',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


        # Changing field 'User.email'
        db.alter_column(u'social_user', 'email', self.gf('django_town.core.fields._EmailField')(unique=True, max_length=75))

    def backwards(self, orm):
        # Deleting field 'User.is_active'
        db.delete_column(u'social_user', 'is_active')


        # Changing field 'User.email'
        db.alter_column(u'social_user', 'email', self.gf('django.db.models.fields.EmailField')(max_length=75, unique=True))

    models = {
        u'social.user': {
            'Meta': {'object_name': 'User'},
            'bio': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django_town.core.fields._EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'email_tbd': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'U'", 'max_length': '1', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'token': ('django.db.models.fields.CharField', [], {'default': "'FRx1elTqg90PKvjiLY26DjtFa4Hb4mRMwDr8vKeIfjy4NbtMjvK7pwevnoaV7GcC'", 'max_length': '64', 'db_index': 'True'}),
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
            'token': ('django.db.models.fields.CharField', [], {'default': "'NrqUvgD3Z2ZT1BchTkIUzIHXtTAOSVFFo7Lsfi5tHLqoAWY2hJ3Z8BzhluaFLnGq'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['social.User']", 'primary_key': 'True'})
        }
    }

    complete_apps = ['social']