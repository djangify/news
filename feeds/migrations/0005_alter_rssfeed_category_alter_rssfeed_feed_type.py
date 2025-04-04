# Generated by Django 5.1.6 on 2025-02-25 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0004_alter_rssfeed_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rssfeed',
            name='category',
            field=models.CharField(choices=[('ai', 'Artificial Intelligence'), ('frontend', 'Frontend'), ('backend', 'Backend'), ('python', 'Python'), ('devops', 'DevOps'), ('news', 'News'), ('general', 'General')], default='GENERAL', max_length=50),
        ),
        migrations.AlterField(
            model_name='rssfeed',
            name='feed_type',
            field=models.CharField(choices=[('article', 'Article Feed'), ('youtube', 'YouTube Feed')], default='ARTICLE', max_length=10),
        ),
    ]
