# Generated by Django 3.2.20 on 2023-10-08 14:42

from django.db import migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('planning_poker_jira', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jiraconnection',
            name='password',
        ),
        migrations.AddField(
            model_name='jiraconnection',
            name='pat',
            field=encrypted_fields.fields.EncryptedCharField(blank=True, max_length=200, verbose_name='Personal Access Token'),
        ),
    ]
