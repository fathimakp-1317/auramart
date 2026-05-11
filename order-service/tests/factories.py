"""
Test Factories
==============
Creates fake test data quickly.
Instead of manually creating
objects in every test,
factories do it automatically.
"""

import factory
import uuid
from apps.orders.models import Order, OrderItem
from apps.inventory.models import Inventory
from apps.payments.models import Payment


class OrderFactory(factory.django.DjangoModelFactory):
    """Creates fake orders for testing."""

    class Meta:
        model = Order

    id           = factory.LazyFunction(uuid.uuid4)
    user_id      = factory.LazyFunction(
                       lambda: str(uuid.uuid4())
                   )
    status       = "pending"
    total_amount = factory.Faker(
                       "pydecimal",
                       left_digits=3,
                       right_digits=2,
                       positive=True
                   )
    stripe_payment_id = ""


class OrderItemFactory(factory.django.DjangoModelFactory):
    """Creates fake order items for testing."""

    class Meta:
        model = OrderItem

    id         = factory.LazyFunction(uuid.uuid4)
    order      = factory.SubFactory(OrderFactory)
    product_id = factory.LazyFunction(
                     lambda: str(uuid.uuid4())
                 )
    vendor_id  = factory.LazyFunction(
                     lambda: str(uuid.uuid4())
                 )
    quantity   = factory.Faker(
                     "random_int",
                     min=1,
                     max=10
                 )
    unit_price = factory.Faker(
                     "pydecimal",
                     left_digits=3,
                     right_digits=2,
                     positive=True
                 )


class InventoryFactory(factory.django.DjangoModelFactory):
    """Creates fake inventory for testing."""

    class Meta:
        model = Inventory

    id         = factory.LazyFunction(uuid.uuid4)
    product_id = factory.LazyFunction(
                     lambda: str(uuid.uuid4())
                 )
    quantity   = factory.Faker(
                     "random_int",
                     min=10,
                     max=100
                 )
    version    = 0


class PaymentFactory(factory.django.DjangoModelFactory):
    """Creates fake payments for testing."""

    class Meta:
        model = Payment

    id               = factory.LazyFunction(uuid.uuid4)
    order            = factory.SubFactory(OrderFactory)
    stripe_charge_id = factory.LazyFunction(
                           lambda: f"pi_{uuid.uuid4().hex}"
                       )
    amount           = factory.Faker(
                           "pydecimal",
                           left_digits=3,
                           right_digits=2,
                           positive=True
                       )
    status           = "pending"