from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError, models
from loguru import logger


class BaseModel(models.Model):
    created = models.DateTimeField('Data de criação', auto_now_add=True)
    alteration = models.DateTimeField('Data de modificação', auto_now=True)
    active = models.BooleanField('Ativo?', default=True)
    description = models.CharField('Descrição', max_length=200, blank=True, null=True)

    class Meta:
        abstract = True  # não é criada em banco


# --------------------------------------------------


class Person(BaseModel):
    name = models.CharField('Name', max_length=200)
    address = models.CharField('Address', max_length=200)
    phone = models.CharField(max_length=255)


class Customer(Person):

    def __str__(self) -> str:
        return f"{self.name}"


# --------------------------------------------------


class CarColor(models.Model):
    name = models.CharField(max_length=255)

    # default colors are loaded in migrations
    def __str__(self) -> str:
        return self.name


class CarModel(models.Model):
    name = models.CharField(max_length=255)

    # default models are loaded in migrations
    def __str__(self) -> str:
        return self.name


class Car(BaseModel):

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    color = models.ForeignKey(CarColor, on_delete=models.PROTECT)
    model = models.ForeignKey(CarModel, on_delete=models.PROTECT)
    owner = models.ForeignKey(Customer, related_name='cars', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.color} {self.model} {self.name} @ ${self.price}"

    def save(self, *args, update=False, **kwargs):

        # a person can have at maximum 3 cars, this is validated here
        owner_count = self.owner.cars.count() if self.owner else 0
        if not update and owner_count >= 3:
            raise IntegrityError("A person can't have more than 3 cars.")

        return super().save(*args, **kwargs)


# --------------------------------------------------


class Sales(models.Model):
    salesperson = models.ForeignKey(User, on_delete=models.PROTECT)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    car = models.ForeignKey(Car, on_delete=models.PROTECT)
    purchase_date = models.DateField()

    class Meta:
        permissions = [
            ('can_sell',
             'Can sell cars'),
        ]

    def save(self, *args, **kwargs):
        if not self.salesperson.has_perm('car_sales.can_sell'):
            raise PermissionDenied("You don't have permission to make sells.")

        self.car.owner = self.customer
        self.car.save()

        super().save(*args, **kwargs)
