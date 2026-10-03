from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="GraceTime",
            fields=[
                ("id", models.AutoField(primary_key=True)),
                ("allowed_time", models.DurationField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="AttendanceLateComeEarlyOut",
            fields=[
                ("id", models.AutoField(primary_key=True)),
            ],
        ),
    ]
