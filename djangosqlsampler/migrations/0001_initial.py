# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Query'
        db.create_table('djangosqlsampler_query', (
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('sql', self.gf('django.db.models.fields.TextField')()),
            ('total_duration', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('total_cost', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
        ))
        db.send_create_signal('djangosqlsampler', ['Query'])

        # Adding model 'Stack'
        db.create_table('djangosqlsampler_stack', (
            ('hash', self.gf('django.db.models.fields.CharField')(max_length=32, primary_key=True)),
            ('stack', self.gf('django.db.models.fields.TextField')()),
            ('total_duration', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('total_cost', self.gf('django.db.models.fields.FloatField')(default=0, db_index=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('query', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangosqlsampler.Query'])),
        ))
        db.send_create_signal('djangosqlsampler', ['Stack'])

        # Adding model 'Sample'
        db.create_table('djangosqlsampler_sample', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sql', self.gf('django.db.models.fields.TextField')()),
            ('duration', self.gf('django.db.models.fields.FloatField')()),
            ('cost', self.gf('django.db.models.fields.FloatField')()),
            ('stack', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djangosqlsampler.Stack'])),
            ('params', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('djangosqlsampler', ['Sample'])


    def backwards(self, orm):
        
        # Deleting model 'Query'
        db.delete_table('djangosqlsampler_query')

        # Deleting model 'Stack'
        db.delete_table('djangosqlsampler_stack')

        # Deleting model 'Sample'
        db.delete_table('djangosqlsampler_sample')


    models = {
        'djangosqlsampler.query': {
            'Meta': {'object_name': 'Query'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'sql': ('django.db.models.fields.TextField', [], {}),
            'total_cost': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'total_duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'})
        },
        'djangosqlsampler.sample': {
            'Meta': {'object_name': 'Sample'},
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'duration': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'params': ('django.db.models.fields.TextField', [], {}),
            'sql': ('django.db.models.fields.TextField', [], {}),
            'stack': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangosqlsampler.Stack']"})
        },
        'djangosqlsampler.stack': {
            'Meta': {'object_name': 'Stack'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '32', 'primary_key': 'True'}),
            'query': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['djangosqlsampler.Query']"}),
            'stack': ('django.db.models.fields.TextField', [], {}),
            'total_cost': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'}),
            'total_duration': ('django.db.models.fields.FloatField', [], {'default': '0', 'db_index': 'True'})
        }
    }

    complete_apps = ['djangosqlsampler']
