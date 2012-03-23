# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding index on 'Query', fields ['created_dt']
        db.create_index('djangosampler_query', ['created_dt'])


    def backwards(self, orm):
        
        # Removing index on 'Query', fields ['created_dt']
        db.delete_index('djangosampler_query', ['created_dt'])


    models = {
        'djangosampler.query': {
            'Meta': {'object_name': 'Query'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'query_type': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'}),
            'total_cost': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'total_duration': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'djangosampler.sample': {
            'Meta': {'object_name': 'Sample'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'created_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'stack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangosampler.Stack']"})
        },
        'djangosampler.stack': {
            'Meta': {'object_name': 'Stack'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'created_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'query': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangosampler.Query']"}),
            'stack': ('django.db.models.fields.TextField', [], {}),
            'total_cost': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'total_duration': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['djangosampler']
