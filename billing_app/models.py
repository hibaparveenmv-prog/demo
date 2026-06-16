from decimal import Decimal

from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.FloatField()
    stock = models.IntegerField()
    gst = models.FloatField()

    def __str__(self):
        return self.name

class Bill(models.Model):
    customer_name = models.CharField(max_length=100)
    total_amount = models.FloatField()
    discount_amount = models.FloatField()
    final_amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.customer_name

class Billitem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal = models.FloatField()

    @property
    def gst_amount(self):
        return Decimal(str(self.product.gst)) * Decimal(str(self.subtotal)) / Decimal('100')

    @property
    def total_with_gst(self):
        return Decimal(str(self.subtotal)) + self.gst_amount

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
