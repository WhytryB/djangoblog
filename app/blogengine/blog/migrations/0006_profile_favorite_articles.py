# Generated by Django 2.2.1 on 2019-05-21 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20190521_0627'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='favorite_articles',
            field=models.ManyToManyField(blank=True, to='blog.Post'),
        ),
    ]
