from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('total', models.FloatField(default=0.0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_id', models.CharField(max_length=255)),
                ('vendor_id', models.CharField(max_length=255)),
                ('quantity', models.IntegerField()),
                ('price', models.FloatField()),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
            ],
            options={
                'db_table': 'order_items',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('currency', models.CharField(default='INR', max_length=10)),
                ('status', models.CharField(default='PENDING', max_length=20)),
                ('method', models.CharField(default='CARD', max_length=20)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=255, null=True)),
                ('stripe_charge_id', models.CharField(blank=True, max_length=255, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='orders.order')),
            ],
            options={
                'db_table': 'payments',
            },
        ),
    ]
