# Generated manually to fix test issues
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0008_customer_ville'),
    ]

    operations = [
        # Créer la table cities_light_city pour le modèle City fallback
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=200)),
            ],
            options={
                'db_table': 'cities_light_city',
                'managed': True,
            },
        ),
        # Ajouter le champ ville_id à Customer
        migrations.AddField(
            model_name='customer',
            name='ville',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='customer.city'),
        ),
    ]

