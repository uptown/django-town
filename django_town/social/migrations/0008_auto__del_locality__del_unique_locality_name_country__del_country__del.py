# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SubLocality', fields ['name', 'parent']
        db.delete_unique(u'social_sublocality', ['name', 'parent'])

        # Removing unique constraint on 'Locality', fields ['name', 'country']
        db.delete_unique(u'social_locality', ['name', 'country_id'])

        # Deleting model 'Locality'
        db.delete_table(u'social_locality')

        # Deleting model 'Country'
        db.delete_table(u'social_country')

        # Deleting model 'SubLocality'
        db.delete_table(u'social_sublocality')

        # Adding model 'AddressComponent'
        db.create_table(u'social_addresscomponent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ascii_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.AddressComponent'])),
            ('type', self.gf('django.db.models.fields.SmallIntegerField')()),
        ))
        db.send_create_signal('social', ['AddressComponent'])

        # Adding unique constraint on 'AddressComponent', fields ['name', 'parent']
        db.create_unique(u'social_addresscomponent', ['name', 'parent_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'AddressComponent', fields ['name', 'parent']
        db.delete_unique(u'social_addresscomponent', ['name', 'parent_id'])

        # Adding model 'Locality'
        db.create_table(u'social_locality', (
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['social.Country'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('ascii_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal('social', ['Locality'])

        # Adding unique constraint on 'Locality', fields ['name', 'country']
        db.create_unique(u'social_locality', ['name', 'country_id'])

        # Adding model 'Country'
        db.create_table(u'social_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, unique=True)),
            ('ascii_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal('social', ['Country'])

        # Adding model 'SubLocality'
        db.create_table(u'social_sublocality', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('parent', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('level', self.gf('django.db.models.fields.SmallIntegerField')(db_index=True)),
            ('ascii_name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('social', ['SubLocality'])

        # Adding unique constraint on 'SubLocality', fields ['name', 'parent']
        db.create_unique(u'social_sublocality', ['name', 'parent'])

        # Deleting model 'AddressComponent'
        db.delete_table(u'social_addresscomponent')


    models = {
        'social.addresscomponent': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'AddressComponent'},
            'ascii_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.AddressComponent']"}),
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
            'token': ('django.db.models.fields.CharField', [], {'default': "'DcScxXiR4aslyX3ffjhNEdxYQ3HNLUoM9jXSGkB8sd9UIpLOteOLa5qhstxWHDkG'", 'max_length': '64', 'db_index': 'True'}),
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
            'token': ('django.db.models.fields.CharField', [], {'default': "'gzjgzjBYz317LfLj6EKW9yxrFSRaSxILURlkXBAmv9A3BY0El3hSe09U8kZMhXW0'", 'max_length': '64', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['social.User']", 'primary_key': 'True'})
        }
    }

    complete_apps = ['social']