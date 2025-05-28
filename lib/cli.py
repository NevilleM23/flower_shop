import sys
import os
from db.session import SessionLocal
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

if __name__ == '__main__':
    init_database()
    MyShopCLI()