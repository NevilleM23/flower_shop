import sys
import os
from db.session import SessionLocal, engine
from db.models import Base, Flower
from helpers import (
    main_menu, stock_menu, customer_menu, 
    order_menu, reports_menu, init_database
)

class MyShopCLI:
    def __init__(self):
        self.db = SessionLocal()
        self.run()

    def run(self):
        while True:
            choice = main_menu()
            
            if choice == 'stock':
                stock_menu(self.db)
            elif choice == 'customer':
                customer_menu(self.db)
            elif choice == 'order':
                order_menu(self.db)
            elif choice == 'reports':
                reports_menu(self.db)
            elif choice == 'exit':
                print("\nThank you for using MyShop. Goodbye!")
                self.db.close()
                sys.exit(0)

def initialize_database():
    """Initialize database tables and seed data if needed"""
    Base.metadata.create_all(bind=engine)
    

    db = SessionLocal()
    try:
        if db.query(Flower).count() == 0:
            print("Seeding database for the first time...")
            from db.seed import seed_database
            seed_database()
    finally:
        db.close()

if __name__ == '__main__':
    initialize_database()
    MyShopCLI()