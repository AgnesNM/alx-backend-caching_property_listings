from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Property(models.Model):
    """
    Property model for storing property listing information.
    """
    title = models.CharField(max_length=200, help_text="Property title")
    description = models.TextField(help_text="Property description")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Property price"
    )
    location = models.CharField(max_length=100, help_text="Property location")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Creation timestamp")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp")

    class Meta:
        db_table = 'properties'
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'

    def __str__(self):
        return f"{self.title} - ${self.price}"

    def __repr__(self):
        return f"<Property: {self.title} (${self.price})>"
