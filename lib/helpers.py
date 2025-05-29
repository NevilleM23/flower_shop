import inquirer
import os
from tabulate import tabulate
from sqlalchemy import or_, func
from db.models import Flower, Customer, Order, OrderItem
from datetime import datetime, timedelta

#  Ui helper functions

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_header(title):
    """Display a header with title"""
    clear_screen()
    print(f"=== MyShop Flower Shop ===")
    print(f"=== {title} ===")
    print()

def press_enter():
    """Prompt user to press Enter to continue"""
    input("\nPress Enter to continue...")

def format_currency(amount):
    """Format number as currency"""
    return f"${amount:.2f}"

def print_table(headers, data):
    """Print data in a table format"""
    print(tabulate(data, headers=headers, tablefmt="grid")) 

#  databse initialization

def init_database():
    """Initialize the database if needed"""
    from db.session import engine
    from db.models import Base
    if not os.path.exists("myshop.db"):
        print("Initializing database...")
        Base.metadata.create_all(engine)
        from db.seed import seed_database
        seed_database()


#  Menu Navigation

def main_menu():
    """Display main menu and get user choice"""
    display_header("Main Menu")
    questions = [
        inquirer.List('choice',
            message="What would you like to manage?",
            choices=[
                ('Stock Management', 'stock'),
                ('Customer Management', 'customer'),
                (' Order Management', 'order'),
                ('Reports', 'reports'),
                (' Exit', 'exit')
            ],
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers['choice'] if answers else 'exit'


#  Stock Management

def stock_menu(db):
    """Stock management menu"""
    while True:
        display_header("Stock Management")
        choice = inquirer.prompt([
            inquirer.List('action',
                message="What would you like to do?",
                choices=[
                    ('View All Flowers', 'view'),
                    ('Add New Flower', 'add'),
                    ('Update Flower', 'update'),
                    ('Remove Flower', 'remove'),
                    ('Search Flowers', 'search'),
                    ('Check Low Stock', 'low_stock'),
                    ('Back to Main Menu', 'back')
                ],
            )
        ])['action']
        
        if choice == 'view': view_flowers(db)
        elif choice == 'add': add_flower(db)
        elif choice == 'update': update_flower(db)
        elif choice == 'remove': remove_flower(db)
        elif choice == 'search': search_flowers(db)
        elif choice == 'low_stock': check_low_stock(db)
        elif choice == 'back': return

def view_flowers(db):
    """View all flowers in stock"""
    display_header("All Flowers")
    flowers = db.query(Flower).order_by(Flower.name).all()
    
    if not flowers:
        print("No flowers in inventory")
        press_enter()
        return
    
    data = [[
        f.id, f.name, format_currency(f.price), 
        f.quantity, f.category, 
        "Low" if f.quantity < f.low_stock_threshold else " Ok"
    ] for f in flowers]
    
    print_table(["ID", "Name", "Price", "Qty", "Category", "Status"], data)
    press_enter()

def add_flower(db):
    """Add a new flower to inventory"""
    display_header("Add New Flower")
    answers = inquirer.prompt([
        inquirer.Text('name', "Flower name"),
        inquirer.Text('price', "Price per unit", validate=lambda _, x: x.replace('.','',1).isdigit()),
        inquirer.Text('quantity', "Initial quantity", validate=lambda _, x: x.isdigit()),
        inquirer.Text('category', "Category (e.g., Roses, Tulips)"),
        inquirer.Text('threshold', "Low stock threshold", default="10", validate=lambda _, x: x.isdigit()),
    ])
    
    try:
        flower = Flower(
            name=answers['name'],
            price=float(answers['price']),
            quantity=int(answers['quantity']),
            category=answers['category'],
            low_stock_threshold=int(answers['threshold'])
        )
        db.add(flower)
        db.commit()
        print(f"\n Added {flower.name} successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
    
    press_enter()

def update_flower(db):
    """Update flower details"""
    display_header("Update Flower")
    flowers = db.query(Flower).all()
    
    if not flowers:
        print("No flowers available")
        press_enter()
        return
    
    choices = [(f"{f.name} (ID: {f.id})", f.id) for f in flowers]
    flower_id = inquirer.prompt([
        inquirer.List('id', "Select flower to update", choices=choices)
    ])['id']
    
    flower = db.query(Flower).get(flower_id)
    if not flower:
        print("Flower not found")
        press_enter()
        return
    
    answers = inquirer.prompt([
        inquirer.Text('name', "Name", default=flower.name),
        inquirer.Text('price', "Price", default=str(flower.price)),
        inquirer.Text('quantity', "Quantity", default=str(flower.quantity)),
        inquirer.Text('category', "Category", default=flower.category),
        inquirer.Text('threshold', "Low stock threshold", default=str(flower.low_stock_threshold)),
    ])
    
    try:
        flower.name = answers['name']
        flower.price = float(answers['price'])
        flower.quantity = int(answers['quantity'])
        flower.category = answers['category']
        flower.low_stock_threshold = int(answers['threshold'])
        db.commit()
        print(f"\n Updated {flower.name} successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n Error: {str(e)}")
    
    press_enter()

def remove_flower(db):
    """Remove a flower from inventory"""
    display_header("Remove Flower")
    flowers = db.query(Flower).all()
    
    if not flowers:
        print("No flowers available")
        press_enter()
        return
    
    choices = [(f"{f.name} (ID: {f.id})", f.id) for f in flowers]
    answers = inquirer.prompt([
        inquirer.List('id', "Select flower to remove", choices=choices),
        inquirer.Confirm('confirm', "Are you sure?", default=False)
    ])
    
    if not answers['confirm']:
        return
    
    flower = db.query(Flower).get(answers['id'])
    if not flower:
        print("Flower not found")
        press_enter()
        return
    
    try:
        order_items = db.query(OrderItem).filter_by(flower_id=flower.id).count()
        if order_items > 0:
            print(f"Cannot remove - found in {order_items} orders")
        else:
            db.delete(flower)
            db.commit()
            print(f"\n Removed {flower.name} successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n Error: {str(e)}")
    
    press_enter()

def search_flowers(db):
    """Search flowers by name or category"""
    display_header("Search Flowers")
    query = inquirer.prompt([
        inquirer.Text('query', "Search by name or category")
    ])['query']
    
    if not query:
        return
    
    flowers = db.query(Flower).filter(
        or_(
            Flower.name.ilike(f"%{query}%"),
            Flower.category.ilike(f"%{query}%")
        )
    ).all()
    
    if not flowers:
        print("No matching flowers found")
        press_enter()
        return
    
    data = [[
        f.id, f.name, format_currency(f.price), 
        f.quantity, f.category
    ] for f in flowers]
    
    print_table(["ID", "Name", "Price", "Qty", "Category"], data)
    press_enter()

def check_low_stock(db):
    """Check low stock items"""
    display_header("Low Stock Alert")
    flowers = db.query(Flower).filter(
        Flower.quantity < Flower.low_stock_threshold
    ).all()
    
    if not flowers:
        print(" All items are well stocked!")
        press_enter()
        return
    
    data = [[
        f.id, f.name, f.quantity, 
        f.low_stock_threshold, f.category
    ] for f in flowers]
    
    print(" Low stock items:")
    print_table(["ID", "Name", "Current", "Threshold", "Category"], data)
    press_enter()

