from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from stores.models import Store
from inventory.models import Item, Category
from rentals.models import Rental, RentalItem
from rentals.services import RentalService
from inventory.services import InventoryService

User = get_user_model()


class RentalServiceTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.store = Store.objects.create(
            name='Test Store',
            slug='test-store'
        )
        
        self.category = Category.objects.create(
            name='Test Category',
            store=self.store
        )
        
        self.item = Item.objects.create(
            name='Test Item',
            sku='TEST001',
            store=self.store,
            category=self.category,
            price=Decimal('10.00'),
            rental_rate=Decimal('2.00'),
            quantity=5,
            is_rentable=True,
            is_sellable=True
        )
        
        # Create store user
        from accounts.models import StoreUser
        StoreUser.objects.create(
            user=self.user,
            store=self.store,
            role='admin'
        )

    def test_create_rental_atomic_operation(self):
        """Test that rental creation is atomic and reduces inventory correctly."""
        due_date = date.today() + timedelta(days=3)
        
        # Create rental
        rental = RentalService.create_rental(
            store=self.store,
            created_by=self.user,
            customer_name='John Doe',
            due_date=due_date,
            items=[{
                'item_id': self.item.id,
                'qty': 2,
                'per_day': Decimal('2.00')
            }]
        )
        
        # Verify rental was created
        self.assertIsNotNone(rental)
        self.assertEqual(rental.customer_name, 'John Doe')
        self.assertEqual(rental.store, self.store)
        self.assertEqual(rental.created_by, self.user)
        
        # Verify inventory was reduced
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 3)  # 5 - 2 = 3
        
        # Verify rental item was created
        rental_item = rental.items.first()
        self.assertIsNotNone(rental_item)
        self.assertEqual(rental_item.qty, 2)
        self.assertEqual(rental_item.per_day, Decimal('2.00'))
        
        # Verify inventory transaction was created
        transaction = self.item.transactions.filter(reason='rental').first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.delta, -2)

    def test_create_rental_insufficient_inventory(self):
        """Test that rental creation fails with insufficient inventory."""
        due_date = date.today() + timedelta(days=3)
        
        with self.assertRaises(Exception) as context:
            RentalService.create_rental(
                store=self.store,
                created_by=self.user,
                customer_name='John Doe',
                due_date=due_date,
                items=[{
                    'item_id': self.item.id,
                    'qty': 10,  # More than available (5)
                    'per_day': Decimal('2.00')
                }]
            )
        
        self.assertIn('Insufficient inventory', str(context.exception))
        
        # Verify inventory was not changed
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 5)

    def test_process_return_partial(self):
        """Test processing partial returns correctly."""
        # First create a rental
        due_date = date.today() + timedelta(days=3)
        rental = RentalService.create_rental(
            store=self.store,
            created_by=self.user,
            customer_name='John Doe',
            due_date=due_date,
            items=[{
                'item_id': self.item.id,
                'qty': 3,
                'per_day': Decimal('2.00')
            }]
        )
        
        # Verify initial state
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 2)  # 5 - 3 = 2
        
        # Process partial return
        RentalService.process_return(
            rental_id=rental.id,
            returned_items=[{
                'rental_item_id': rental.items.first().id,
                'qty': 1,
                'condition': 'good',
                'damage_cost': Decimal('0.00')
            }]
        )
        
        # Verify partial return
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 3)  # 2 + 1 = 3
        
        # Verify rental is still active (not all items returned)
        rental.refresh_from_db()
        self.assertEqual(rental.status, 'active')
        
        # Verify return report was created
        rental_item = rental.items.first()
        self.assertEqual(rental_item.returned_qty, 1)

    def test_process_return_complete(self):
        """Test processing complete returns correctly."""
        # First create a rental
        due_date = date.today() + timedelta(days=3)
        rental = RentalService.create_rental(
            store=self.store,
            created_by=self.user,
            customer_name='John Doe',
            due_date=due_date,
            items=[{
                'item_id': self.item.id,
                'qty': 2,
                'per_day': Decimal('2.00')
            }]
        )
        
        # Process complete return
        RentalService.process_return(
            rental_id=rental.id,
            returned_items=[{
                'rental_item_id': rental.items.first().id,
                'qty': 2,
                'condition': 'good',
                'damage_cost': Decimal('0.00')
            }]
        )
        
        # Verify complete return
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 5)  # 3 + 2 = 5 (back to original)
        
        # Verify rental is marked as returned
        rental.refresh_from_db()
        self.assertEqual(rental.status, 'returned')
        self.assertIsNotNone(rental.returned_date)

    def test_rental_due_date_validation(self):
        """Test that rental creation fails with past due date."""
        past_date = date.today() - timedelta(days=1)
        
        with self.assertRaises(Exception) as context:
            RentalService.create_rental(
                store=self.store,
                created_by=self.user,
                customer_name='John Doe',
                due_date=past_date,
                items=[{
                    'item_id': self.item.id,
                    'qty': 1,
                    'per_day': Decimal('2.00')
                }]
            )
        
        self.assertIn('Due date must be in the future', str(context.exception))
