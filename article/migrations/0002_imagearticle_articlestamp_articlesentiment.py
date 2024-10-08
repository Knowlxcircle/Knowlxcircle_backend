# Generated by Django 4.2.9 on 2024-07-20 02:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("article", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImageArticle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("image", models.ImageField(upload_to="images/")),
                ("caption", models.CharField(max_length=100)),
                ("order", models.IntegerField()),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="article.articles",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArticleStamp",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("count_view", models.IntegerField(default=0)),
                ("count_comment", models.IntegerField(default=0)),
                ("time_view", models.DateTimeField(auto_now=True)),
                ("time_exit", models.DateTimeField(auto_now=True)),
                ("visited_at", models.DateTimeField(auto_now_add=True)),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="article.articles",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ArticleSentiment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sentiment",
                    models.CharField(
                        choices=[
                            ("positive", "positive"),
                            ("negative", "negative"),
                            ("neutral", "neutral"),
                        ],
                        default="neutral",
                        max_length=50,
                    ),
                ),
                ("score", models.FloatField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="article.articles",
                    ),
                ),
            ],
        ),
    ]
