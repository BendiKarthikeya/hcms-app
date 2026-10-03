from django.db import migrations


def add_is_new_employee(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if connection.vendor == 'postgresql':
            cursor.execute("ALTER TABLE auth_user ADD COLUMN IF NOT EXISTS is_new_employee boolean DEFAULT false;")
        elif connection.vendor == 'sqlite':
            cur = connection.cursor()
            cur.execute("PRAGMA table_info(auth_user);")
            columns = [column[1] for column in cur.fetchall()]
            if 'is_new_employee' not in columns:
                cursor.execute("ALTER TABLE auth_user ADD COLUMN is_new_employee boolean DEFAULT false;")


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_docusignaccount_adobesignaccount'),
    ]

    operations = [
        migrations.RunPython(add_is_new_employee, reverse_code=migrations.RunPython.noop),
    ]
