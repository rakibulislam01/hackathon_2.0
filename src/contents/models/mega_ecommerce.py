from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
        ]


class Address(BaseModel):
    # addresses = models.JSONField(default=list)  # List of dictionaries containing address details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_line = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)


class Product(BaseModel):
    product_id = models.IntegerField()  # Not unique, as it's repeated for each order
    product_name = models.CharField(max_length=255)
    product_description = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.CharField(max_length=100)
    product_subcategory = models.CharField(max_length=100)
    product_brand = models.CharField(max_length=100)
    product_stock = models.IntegerField()
    product_ratings = models.JSONField(default=list)  # List of dictionaries containing rating details

    class Meta:
        indexes = [models.Index(fields=["product_id"])]


class Order(BaseModel):
    order_id = models.IntegerField()  # Not unique, as it's repeated for each product in the order
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
    shipping_method = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        # This isn't a proper unique constraint, as it would prevent users from ordering the same product twice
        # It's just to illustrate the complexity of the denormalized model
        # unique_together = ("user_id", "order_id", "product_id")
        indexes = [
            models.Index(fields=["order_id"]),
            models.Index(fields=["user_id"]),
        ]


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    item_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        # This isn't a proper unique constraint, as it would prevent users from ordering the same product twice
        # It's just to illustrate the complexity of the denormalized model
        # unique_together = ("user_id", "order_id", "product_id")
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["order_id"]),
            models.Index(fields=["product_id"]),
            models.Index(fields=["payment_id"]),
        ]


class Payment(BaseModel):
    payment_id = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["payment_id"]),
            models.Index(fields=["order_id"]),
        ]


class Supplier(BaseModel):
    supplier_id = models.IntegerField()
    supplier_name = models.CharField(max_length=255)
    supplier_contact_name = models.CharField(max_length=255)
    supplier_email = models.EmailField()
    supplier_phone = models.CharField(max_length=20)


class Inventory(BaseModel):
    warehouse_id = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory")
    warehouse_name = models.CharField(max_length=255)
    warehouse_location = models.CharField(max_length=255)
    shelf_number = models.CharField(max_length=50)
    reorder_point = models.IntegerField()


class SupportTicket(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="support_tickets")
    support_ticket_id = models.IntegerField(null=True, blank=True)
    support_ticket_status = models.CharField(max_length=50, null=True, blank=True)
    support_agent_name = models.CharField(max_length=255, null=True, blank=True)


class MarketingCampaign(BaseModel):
    campaign_id = models.IntegerField(null=True, blank=True)
    campaign_name = models.CharField(max_length=255, null=True, blank=True)
    discount_code = models.CharField(max_length=50, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


class Wishlist(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Review(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    review_text = models.TextField(null=True, blank=True)
    review_rating = models.IntegerField(null=True, blank=True)
    review_date = models.DateTimeField(null=True, blank=True)
