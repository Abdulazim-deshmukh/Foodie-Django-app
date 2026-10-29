from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("foodapp", "0016_orders_is_paid"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="customer",
            options={
                "ordering": ["name"],
                "verbose_name": "Customer",
                "verbose_name_plural": "Customers",
            },
        ),

        migrations.AlterModelOptions(
            name="foodcart",
            options={
                "ordering": ["-added_at"],
                "verbose_name": "Cart Item",
                "verbose_name_plural": "Cart Items",
            },
        ),

        migrations.AlterModelOptions(
            name="fooditem",
            options={
                "ordering": ["name"],
                "verbose_name": "Food Item",
                "verbose_name_plural": "Food Items",
            },
        ),

        migrations.AlterModelOptions(
            name="orders",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Order",
                "verbose_name_plural": "Orders",
            },
        ),

        migrations.AlterModelOptions(
            name="payment",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Payment",
                "verbose_name_plural": "Payments",
            },
        ),

        # ---------------------------------------------------------
        # IMPORTANT:
        # The existing PostgreSQL database has a foreign key from
        # foodapp_foodcart.food_item_id -> foodapp_fooditem.Id.
        #
        # We must remove that database constraint BEFORE removing
        # the old FoodItem.Id column.
        # ---------------------------------------------------------
        migrations.RunSQL(
            sql="""
                ALTER TABLE "foodapp_foodcart"
                DROP CONSTRAINT IF EXISTS
                "foodapp_foodcart_food_item_id_b31edf99_fk_foodapp_fooditem_Id";
            """,
            reverse_sql="""
                ALTER TABLE "foodapp_foodcart"
                ADD CONSTRAINT
                "foodapp_foodcart_food_item_id_b31edf99_fk_foodapp_fooditem_Id"
                FOREIGN KEY ("food_item_id")
                REFERENCES "foodapp_fooditem" ("Id")
                DEFERRABLE INITIALLY DEFERRED;
            """,
        ),

        # ---------------------------------------------------------
        # Remove old FoodItem primary key: Id
        # ---------------------------------------------------------
        migrations.RemoveField(
            model_name="fooditem",
            name="Id",
        ),

        # ---------------------------------------------------------
        # Add normal Django primary key: id
        # ---------------------------------------------------------
        migrations.AddField(
            model_name="fooditem",
            name="id",
            field=models.BigAutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),

        # ---------------------------------------------------------
        # Customer
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="customer",
            name="emailId",
            field=models.EmailField(
                max_length=100,
                primary_key=True,
                serialize=False,
            ),
        ),

        # ---------------------------------------------------------
        # FoodCart customer relationship
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="foodcart",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="foodapp.customer",
            ),
        ),

        # ---------------------------------------------------------
        # FoodCart food relationship
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="foodcart",
            name="food_item",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cart_items",
                to="foodapp.fooditem",
            ),
        ),

        # ---------------------------------------------------------
        # FoodCart quantity
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="foodcart",
            name="quantity",
            field=models.PositiveIntegerField(
                default=1,
                validators=[
                    MinValueValidator(1),
                ],
            ),
        ),

        # ---------------------------------------------------------
        # FoodItem image
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="fooditem",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="food/",
            ),
        ),

        # ---------------------------------------------------------
        # FoodItem price
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="fooditem",
            name="price",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
                validators=[
                    MinValueValidator(0),
                ],
            ),
        ),

        # ---------------------------------------------------------
        # Orders address
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="orders",
            name="address",
            field=models.CharField(
                max_length=255,
            ),
        ),

        # ---------------------------------------------------------
        # Orders customer relationship
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="orders",
            name="customer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="orders",
                to="foodapp.customer",
            ),
        ),

        # ---------------------------------------------------------
        # Orders order number
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="orders",
            name="orderNo",
            field=models.CharField(
                max_length=100,
                unique=True,
            ),
        ),

        # ---------------------------------------------------------
        # Orders phone number
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="orders",
            name="phoneno",
            field=models.CharField(
                max_length=15,
            ),
        ),

        # ---------------------------------------------------------
        # Orders pincode
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="orders",
            name="pincode",
            field=models.CharField(
                max_length=8,
            ),
        ),

        # ---------------------------------------------------------
        # Orders total bill
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="orders",
            name="totalbill",
            field=models.DecimalField(
                decimal_places=2,
                default=0.0,
                max_digits=10,
                validators=[
                    MinValueValidator(0),
                ],
            ),
        ),

        # ---------------------------------------------------------
        # Payment amount
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="payment",
            name="amount",
            field=models.DecimalField(
                decimal_places=2,
                max_digits=10,
            ),
        ),

        # ---------------------------------------------------------
        # Payment -> Order relationship
        # ---------------------------------------------------------
        migrations.AlterField(
            model_name="payment",
            name="order",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payment",
                to="foodapp.orders",
            ),
        ),

        # ---------------------------------------------------------
        # Recreate FoodCart -> FoodItem foreign key.
        #
        # It now points to the new FoodItem.id column.
        # ---------------------------------------------------------
        migrations.RunSQL(
            sql="""
                ALTER TABLE "foodapp_foodcart"
                ADD CONSTRAINT
                "foodapp_foodcart_food_item_id_b31edf99_fk_foodapp_fooditem_id"
                FOREIGN KEY ("food_item_id")
                REFERENCES "foodapp_fooditem" ("id")
                DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
                ALTER TABLE "foodapp_foodcart"
                DROP CONSTRAINT IF EXISTS
                "foodapp_foodcart_food_item_id_b31edf99_fk_foodapp_fooditem_id";
            """,
        ),

        # ---------------------------------------------------------
        # Prevent the same food item from being added twice to
        # the same customer's cart.
        # ---------------------------------------------------------
        migrations.AddConstraint(
            model_name="foodcart",
            constraint=models.UniqueConstraint(
                fields=("customer", "food_item"),
                name="unique_customer_food_item",
            ),
        ),
    ]
