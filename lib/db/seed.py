from session import SessionLocal
from models import Flower, Customer, Order, OrderItem
from datetime import datetime, timedelta
from faker import Faker
import random
from sqlalchemy import inspect

# Initialize Faker
fake = Faker()

def seed_database():
    db = SessionLocal()
    try:
        print("Starting database seeding...")
        

        print("Verifying table existence...")
        engine = db.get_bind()
        inspector = inspect(engine)
        
        tables_to_clear = {
            "order_items": OrderItem,
            "orders": Order,
            "flowers": Flower,
            "customers": Customer
        }
        
   
        print("Clearing existing data...")
        for table_name, model in tables_to_clear.items():
            if inspector.has_table(table_name):
                print(f"  Clearing {table_name}...")
                db.query(model).delete()
            else:
                print(f"  WARNING: {table_name} table does not exist. Skipping delete.")
        
        db.commit()
        
        # Seed flowers
        print("🌼 Seeding flowers...")
        flower_categories = ["Roses", "Tulips", "Lilies", "Orchids", "Sunflowers", 
                            "Daisies", "Carnations", "Peonies", "Hydrangeas", "Irises"]
        
        flowers = []
        for i in range(20):
            category = random.choice(flower_categories)
            flowers.append(Flower(
                name=f"{fake.color_name()} {category}",
                price=round(random.uniform(5.99, 29.99), 2),
                quantity=random.randint(5, 100),
                category=category,
            ))
        db.add_all(flowers)
        db.commit()
        print(f"Seeded {len(flowers)} flowers")
        
        # Seed customers
        print("👥 Seeding customers...")
        customers = []
        for _ in range(30):
            customers.append(Customer(
                name=fake.name(),
                phone=fake.phone_number(),
                email=fake.email(),
            ))
        db.add_all(customers)
        db.commit()
        print(f"Seeded {len(customers)} customers")
        
        # Create orders
        print("🛒 Seeding orders...")
        orders = []
        order_items = []
        
        # Create orders for the last 90 days
        for i in range(100):
            customer = random.choice(customers)
            order_date = fake.date_time_between(start_date="-90d", end_date="now")
            
            order = Order(
                customer_id=customer.id,
                status=random.choice(['pending', 'completed', 'cancelled']),
                created_at=order_date
            )
            orders.append(order)
            db.add(order)
            db.flush()  # Get order ID
            
            # Add 1-5 items to each order
            num_items = random.randint(1, 5)
            order_total = 0
            
            for _ in range(num_items):
                flower = random.choice(flowers)
                quantity = random.randint(1, 10)
                
                # Ensure we don't oversell
                if quantity > flower.quantity:
                    quantity = flower.quantity
                
                # Create order item
                item = OrderItem(
                    order_id=order.id,
                    flower_id=flower.id,
                    quantity=quantity
                )
                order_items.append(item)
                
                # Update order total
                item_total = flower.price * quantity
                order_total += item_total
                
                # Update stock (only for completed orders)
                if order.status == 'completed':
                    flower.quantity -= quantity
            
            # Set order total and add loyalty points
            order.total = round(order_total, 2)
            
        db.commit()
        print(f"Seeded {len(orders)} orders with {len(order_items)} items")
        
        # Create some low stock items
        print("⚠️ Creating low stock items...")
        low_stock_flowers = random.sample(flowers, 5)
        for flower in low_stock_flowers:
            flower.quantity = random.randint(1, flower.low_stock_threshold)
        db.commit()
        
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()