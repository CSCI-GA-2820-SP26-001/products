"""
Test Factory to make fake objects for testing
"""

import factory
from factory.fuzzy import FuzzyDecimal
from service.models import Product


class ProductFactory(factory.Factory):
    """Creates fake products for testing"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("catch_phrase")
    description = factory.Faker("sentence")
    price = FuzzyDecimal(1.00, 999.99, precision=2)
    category = factory.Faker("word")
    available = factory.Faker("boolean")
