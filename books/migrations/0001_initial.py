# Generated by Django 5.1.1 on 2024-10-26 03:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='author_images/')),
                ('addedBy', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='addedBy', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('added_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='book_images/')),
                ('description', models.TextField()),
                ('price', models.PositiveIntegerField(default=0)),
                ('total_views', models.PositiveIntegerField(default=0)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('suggestions', models.TextField(blank=True, null=True)),
                ('link', models.URLField(blank=True, null=True)),
                ('link_clicked', models.PositiveIntegerField(default=0)),
                ('likes_counter', models.PositiveIntegerField(default=0)),
                ('published_time', models.DateField(auto_now_add=True)),
                ('pages', models.PositiveIntegerField(default=0)),
                ('language', models.CharField(blank=True, max_length=100, null=True)),
                ('chapters', models.PositiveIntegerField(default=0)),
                ('favorites_chapters', models.PositiveIntegerField(default=0)),
                ('favorites_quotes', models.TextField(blank=True, null=True)),
                ('series', models.CharField(blank=True, max_length=100, null=True)),
                ('reading_level', models.CharField(blank=True, max_length=50, null=True)),
                ('best_character', models.CharField(blank=True, max_length=100, null=True)),
                ('awards', models.TextField(blank=True, null=True)),
                ('format', models.CharField(blank=True, choices=[('Hardcover', 'Hardcover'), ('Paperback', 'Paperback'), ('eBook', 'eBook')], max_length=50, null=True)),
                ('authors', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='books.author')),
                ('likes', models.ManyToManyField(blank=True, related_name='likes', to=settings.AUTH_USER_MODEL)),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.category')),
            ],
        ),
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ReadingStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('to_read', 'To Read'), ('reading', 'Currently Reading'), ('completed', 'Completed')], max_length=20)),
                ('current_page', models.PositiveIntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
