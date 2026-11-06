from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("sales", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="discount_mode",
            field=models.CharField(
                choices=[("amount", "amount"), ("percent", "percent")],
                default="amount",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="discount_input",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="tax_mode",
            field=models.CharField(
                choices=[("amount", "amount"), ("percent", "percent")],
                default="amount",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="invoice",
            name="tax_input",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=18, null=True),
        ),
    ]
