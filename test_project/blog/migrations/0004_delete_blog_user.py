# Generated by Django 4.1.4 on 2023-10-20 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_blog_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Blog_user',
        ),
    ]
