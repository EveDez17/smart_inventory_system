from django.test import TestCase
from warehouse.inventory.models import FoodProduct, Category, Supplier
from warehouse.tests.factories import CategoryFactory, FoodProductFactory, SupplierFactory

class CategoryModelTest(TestCase):
    def test_create_category(self):
        category = CategoryFactory()
        self.assertIsInstance(category, Category)
    
    def test_category_attributes(self):
        category = CategoryFactory(name="Electronics")
        self.assertEqual(category.name, "Electronics")
        self.assertTrue(category.slug.startswith("category-"))

    # Add more test cases for Category model as needed

class SupplierModelTest(TestCase):
    def test_create_supplier(self):
        supplier = SupplierFactory()
        self.assertIsInstance(supplier, Supplier)
    
    def test_supplier_attributes(self):
        supplier = SupplierFactory(name="ABC Inc.")
        self.assertEqual(supplier.name, "ABC Inc.")
        # Add more attribute assertions as needed

    # Add more test cases for Supplier model as needed

class FoodProductModelTest(TestCase):
    def test_create_food_product(self):
        product = FoodProductFactory()
        self.assertIsInstance(product, FoodProduct)
    
    def test_food_product_attributes(self):
        product = FoodProductFactory(name="Smartphone", quantity=10, unit_price=500)
        self.assertEqual(product.name, "Smartphone")
        self.assertEqual(product.quantity, 10)
        self.assertEqual(product.unit_price, 500)
        # Add more attribute assertions as needed

    # Add more test cases for FoodProduct model as needed


