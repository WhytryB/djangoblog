# Generated by Django 2.2.1 on 2019-05-21 03:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_auto_20190521_0616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author_post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Profile', verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор1'),
        ),
    ]
