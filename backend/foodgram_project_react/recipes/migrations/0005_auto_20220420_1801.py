# Generated by Django 2.2.16 on 2022-04-20 15:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20220412_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredients',
            name='recipe',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipe_to_ingredient', to='recipes.Recipe'),
        ),
    ]
