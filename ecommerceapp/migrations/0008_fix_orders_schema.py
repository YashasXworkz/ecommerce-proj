# Generated manually to fix schema issues with Orders and OrderUpdate tables

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0007_fix_product_schema'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Create the Orders table with correct schema
            """
            DROP TABLE IF EXISTS ecommerceapp_orders;
            CREATE TABLE ecommerceapp_orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                items_json VARCHAR(5000) NOT NULL,
                amount INTEGER NOT NULL,
                name VARCHAR(90) NOT NULL,
                email VARCHAR(90) NOT NULL,
                address1 VARCHAR(200) NOT NULL,
                address2 VARCHAR(200) NOT NULL,
                city VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                zip_code VARCHAR(100) NOT NULL,
                oid VARCHAR(150) NULL,
                amountpaid VARCHAR(500) NULL,
                paymentstatus VARCHAR(20) NULL,
                phone VARCHAR(100) NOT NULL
            );
            
            DROP TABLE IF EXISTS ecommerceapp_orderupdate;
            CREATE TABLE ecommerceapp_orderupdate (
                update_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                update_desc VARCHAR(5000) NOT NULL,
                delivered BOOLEAN NOT NULL,
                timestamp DATE NOT NULL
            );
            """,
            # Reverse SQL (no-op)
            "SELECT 1;"
        ),
    ] 