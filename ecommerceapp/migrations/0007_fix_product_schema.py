# Generated manually to fix schema issues

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0006_alter_product_image'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Drop the current product table and recreate it with correct schema
            """
            DROP TABLE IF EXISTS ecommerceapp_product;
            CREATE TABLE ecommerceapp_product (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_name VARCHAR(100) NOT NULL,
                category VARCHAR(100) NOT NULL,
                subcategory VARCHAR(50) NOT NULL,
                price INTEGER NOT NULL,
                desc VARCHAR(300) NOT NULL,
                image VARCHAR(100) NOT NULL
            );
            """,
            # Reverse SQL (no-op, as we can't easily restore the table)
            "SELECT 1;"
        ),
    ] 