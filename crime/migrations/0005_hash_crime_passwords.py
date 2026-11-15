# encoding: utf-8
from crime.passwords import is_report_password_hash, make_report_password
from south.v2 import DataMigration


class Migration(DataMigration):

    def forwards(self, orm):
        Crime = orm['crime.Crime']
        for crime in Crime.objects.all().iterator():
            if not is_report_password_hash(crime.password):
                Crime.objects.filter(pk=crime.pk).update(
                    password=make_report_password(crime.password)
                )

    def backwards(self, orm):
        raise RuntimeError('Hashed report passwords cannot be converted back to plaintext.')

    models = {
        'crime.crime': {
            'Meta': {'object_name': 'Crime'},
            'author': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'details': ('django.db.models.fields.TextField', [], {}),
            'headline': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'icon': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_removed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'lat': ('django.db.models.fields.FloatField', [], {}),
            'lng': ('django.db.models.fields.FloatField', [], {}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'remote_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zoom': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['crime']
