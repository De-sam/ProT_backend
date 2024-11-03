from django.db import models
from django.core.exceptions import ValidationError
from userauth.models import CustomUser  # Import the CustomUser model
import logging

logger = logging.getLogger(__name__)


class Design(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='designs/', blank=True, null=True)
    tailor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="designs")

    def __str__(self):
        return f"{self.name} by {self.tailor}"

    def save(self, *args, **kwargs):
        logger.info(f"Design {self.name} saved")
        super().save(*args, **kwargs)


class Order(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    design = models.ForeignKey(Design, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    escrow_address = models.CharField(max_length=58, blank=True, null=True)  # Smart contract address
    asa_id = models.PositiveIntegerField(null=True, blank=True)  # ASA Token ID
    is_released = models.BooleanField(default=False)  # Payment release flag
    transaction_id = models.CharField(max_length=64, unique=True, blank=True, null=True)
    payment_status = models.CharField(
        max_length=10,
        choices=[('PENDING', 'Pending'), ('CONFIRMED', 'Confirmed')],
        default='PENDING'
    )

    def __str__(self):
        return f"Order {self.id} by {self.customer} for {self.design.name}"
    
    def save(self, *args, **kwargs):
        logger.info(f"Order {self.id} saved")
        super().save(*args, **kwargs)


class MeasurementCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        logger.info(f"Measurement category {self.name} saved")
        super().save(*args, **kwargs)


class Measurement(models.Model):
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='measurements')
    date_taken = models.DateField(auto_now_add=True)
    category = models.ForeignKey(MeasurementCategory, on_delete=models.CASCADE, related_name='measurements')

    # Common measurements
    neck_circumference_cm = models.FloatField(blank=True, null=True)
    shoulder_width_cm = models.FloatField(blank=True, null=True)
    chest_bust_circumference_cm = models.FloatField(blank=True, null=True)
    waist_circumference_cm = models.FloatField(blank=True, null=True)
    hip_circumference_cm = models.FloatField(blank=True, null=True)
    arm_length_cm = models.FloatField(blank=True, null=True)
    upper_arm_circumference_cm = models.FloatField(blank=True, null=True)
    wrist_circumference_cm = models.FloatField(blank=True, null=True)
    inseam_length_cm = models.FloatField(blank=True, null=True)
    outseam_length_cm = models.FloatField(blank=True, null=True)
    thigh_circumference_cm = models.FloatField(blank=True, null=True)
    knee_circumference_cm = models.FloatField(blank=True, null=True)
    calf_circumference_cm = models.FloatField(blank=True, null=True)
    ankle_circumference_cm = models.FloatField(blank=True, null=True)
    total_height_cm = models.FloatField(blank=True, null=True)

    # Female-specific measurements
    bust_point_to_bust_point_cm = models.FloatField(blank=True, null=True)
    bust_point_to_waist_cm = models.FloatField(blank=True, null=True)
    back_waist_length_cm = models.FloatField(blank=True, null=True)
    front_waist_length_cm = models.FloatField(blank=True, null=True)
    underbust_circumference_cm = models.FloatField(blank=True, null=True)

    # Male-specific measurements
    chest_width_cm = models.FloatField(blank=True, null=True)
    back_width_cm = models.FloatField(blank=True, null=True)
    sleeve_length_cm = models.FloatField(blank=True, null=True)
    crotch_depth_cm = models.FloatField(blank=True, null=True)

    def clean(self):
        # Validate gender-specific fields based on the customer's gender
        if self.customer.gender == 'M':
            # For male customers, female-specific fields should be empty
            if any([
                self.bust_point_to_bust_point_cm, self.bust_point_to_waist_cm,
                self.back_waist_length_cm, self.front_waist_length_cm,
                self.underbust_circumference_cm
            ]):
                raise ValidationError("Female-specific measurements are not applicable for male customers.")
        
        elif self.customer.gender == 'F':
            # For female customers, male-specific fields should be empty
            if any([
                self.chest_width_cm, self.back_width_cm,
                self.sleeve_length_cm, self.crotch_depth_cm
            ]):
                raise ValidationError("Male-specific measurements are not applicable for female customers.")

    def save(self, *args, **kwargs):
        logger.info(f"Measurement for {self.customer} saved")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} measurements for {self.customer} on {self.date_taken}"
