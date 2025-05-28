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
                ('💐 Stock Management', 'stock'),
                ('👥 Customer Management', 'customer'),
                ('🛒 Order Management', 'order'),
                ('📊 Reports', 'reports'),
                ('🚪 Exit', 'exit')
            ],
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers['choice'] if answers else 'exit'



