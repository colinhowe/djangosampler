# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Query'
        db.create_table('djangosampler_query', (
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('total_duration', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('total_cost', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('djangosampler', ['Query'])

        # Adding model 'Stack'
        db.create_table('djangosampler_stack', (
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('stack', self.gf('django.db.models.fields.TextField')()),
            ('total_duration', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('total_cost', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('query', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangosampler.Query'])),
        ))
        db.send_create_signal('djangosampler', ['Stack'])

        # Adding model 'Sample'
        db.create_table('djangosampler_sample', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
            ('cost', self.gf('django.db.models.fields.FloatField')()),
            ('stack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangosampler.Stack'])),
            ('params', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangosampler', ['Sample'])


    def backwards(self, orm):
        
        # Deleting model 'Query'
        db.delete_table('djangosampler_query')

        # Deleting model 'Stack'
        db.delete_table('djangosampler_stack')

        # Deleting model 'Sample'
        db.delete_table('djangosampler_sample')


    models = {
        'djangosampler.query': {
            'Meta': {'object_name': 'Query'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'total_cost': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'total_duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'})
        },
        'djangosampler.sample': {
            'Meta': {'object_name': 'Sample'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'stack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangosampler.Stack']"})
        },
        'djangosampler.stack': {
            'Meta': {'object_name': 'Stack'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'query': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangosampler.Query']"}),
            'stack': ('django.db.models.fields.TextField', [], {}),
            'total_cost': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'total_duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'})
        }
    }

    complete_apps = ['djangosampler']
