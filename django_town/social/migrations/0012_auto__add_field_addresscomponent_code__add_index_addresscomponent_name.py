# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'AddressComponent', fields ['name', 'parent']
        db.delete_unique(u'social_addresscomponent', ['name', 'parent_id'])

        # Adding field 'AddressComponent.code'
        db.add_column(u'social_addresscomponent', 'code',
                      self.gf('django.db.models.fields.CharField')(default=0, unique=True, max_length=40),
                      keep_default=False)

        # Adding index on 'AddressComponent', fields ['name']
        db.create_index(u'social_addresscomponent', ['name'])

        # Removing index on 'AddressComponent', fields ['ascii_name']
        db.delete_index(u'social_addresscomponent', ['ascii_name'])

        # Adding unique constraint on 'AddressComponent', fields ['parent', 'name']
        db.create_unique(u'social_addresscomponent', ['parent_id', 'name'])


    def backwards(self, orm):
        # Removing unique constraint on 'AddressComponent', fields ['parent', 'name']
        db.delete_unique(u'social_addresscomponent', ['parent_id', 'name'])

        # Adding index on 'AddressComponent', fields ['ascii_name']
        db.create_index(u'social_addresscomponent', ['ascii_name'])

        # Removing index on 'AddressComponent', fields ['name']
        db.delete_index(u'social_addresscomponent', ['name'])

        # Deleting field 'AddressComponent.code'
        db.delete_column(u'social_addresscomponent', 'code')

        # Adding unique constraint on 'AddressComponent', fields ['name', 'parent']
        db.create_unique(u'social_addresscomponent', ['name', 'parent_id'])


    models = {
        'social.addresscomponent': {
            'Meta': {'unique_together': "(('parent', 'name'),)", 'object_name': 'AddressComponent'},
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'children_count': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['social.AddressComponent']", 'null': 'True'}),
            'ser_no': ('django.db.models.fields.SmallIntegerField', [], {'db_index': 'True'}),
            'type': ('django.db.models.fields.SmallIntegerField', [], {})
        },
        'social.page': {
            'Meta': {'object_name': 'Page'},
            'about': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'can_post': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['social.User']", 'null': 'True'})
        },
        'social.user': {
            'Meta': {'object_name': 'User'},
            'bio': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
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
        'social.useremailverify': {
            'Meta': {'object_name': 'UserEmailVerify'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '254'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'WSZUhIBR4UalrWgSEMhCVEVo5u6IblZqwpzzhyjINYASYBeGNcAldU57d7jgX2KK'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.User']", 'primary_key': 'True'})
        },
        'social.userfacebook': {
            'Meta': {'object_name': 'UserFacebook'},
            'access_token': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '400'}),
            'facebook_id': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'db_index': 'True'}),
            'is_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.User']", 'primary_key': 'True'})
        },
        'social.usergoogle': {
            'Meta': {'object_name': 'UserGoogle'},
            'email': ('django.db.models.fields.EmailField', [], {'default': "''", 'max_length': '75'}),
            'google_id': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '22', 'decimal_places': '0', 'db_index': 'True'}),
            'is_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.User']", 'primary_key': 'True'})
        },
        'social.userpasswordreset': {
            'Meta': {'object_name': 'UserPasswordReset'},
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'VyOAJrikCiZOdSn5BXlHx8eCX2DrRywbAQfGmQVEabfrscwolLGXexugTvskGVNb'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.User']", 'primary_key': 'True'})
        }
    }

    complete_apps = ['social']