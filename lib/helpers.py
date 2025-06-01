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
    print(f"=== MyShop ===")
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
                ('Order Management', 'order'),
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
        print(f"\n Error: {str(e)}")
    
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


# Customer Management 

def customer_menu(db):
    """Customer management menu"""
    while True:
        display_header("Customer Management")
        choice = inquirer.prompt([
            inquirer.List('action',
                message="What would you like to do?",
                choices=[
                    ('View All Customers', 'view'),
                    ('Add New Customer', 'add'),
                    ('Update Customer', 'update'),
                    ('Search Customers', 'search'),
                    ('View Purchase History', 'history'),
                    ('Back to Main Menu', 'back')
                ],
            )
        ])['action']
        
        if choice == 'view': view_customers(db)
        elif choice == 'add': add_customer(db)
        elif choice == 'update': update_customer(db)
        elif choice == 'search': search_customers(db)
        elif choice == 'history': view_customer_history(db)
        elif choice == 'back': return

def view_customers(db):
    """View all customers"""
    display_header("All Customers")
    customers = db.query(Customer).order_by(Customer.name).all()
    
    if not customers:
        print("No customers found")
        press_enter()
        return
    
    data = [[
        c.id, c.name, c.phone, 
        c.email, len(c.orders)
    ] for c in customers]
    
    print_table(["ID", "Name", "Phone", "Email", "Orders"], data)
    press_enter()

def add_customer(db):
    """Add a new customer"""
    display_header("Add New Customer")
    answers = inquirer.prompt([
        inquirer.Text('name', "Full name"),
        inquirer.Text('phone', "Phone number"),
        inquirer.Text('email', "Email address"),
    ])
    
    try:
        customer = Customer(
            name=answers['name'],
            phone=answers['phone'],
            email=answers['email']
        )
        db.add(customer)
        db.commit()
        print(f"\n Added customer {customer.name} successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n Error: {str(e)}")
    
    press_enter()

def update_customer(db):
    """Update customer details"""
    display_header("Update Customer")
    customers = db.query(Customer).all()
    
    if not customers:
        print("No customers available")
        press_enter()
        return
    
    choices = [(f"{c.name} (ID: {c.id})", c.id) for c in customers]
    customer_id = inquirer.prompt([
        inquirer.List('id', "Select customer to update", choices=choices)
    ])['id']
    
    customer = db.query(Customer).get(customer_id)
    if not customer:
        print("Customer not found")
        press_enter()
        return
    
    answers = inquirer.prompt([
        inquirer.Text('name', "Name", default=customer.name),
        inquirer.Text('phone', "Phone", default=customer.phone),
        inquirer.Text('email', "Email", default=customer.email),
    ])
    
    try:
        customer.name = answers['name']
        customer.phone = answers['phone']
        customer.email = answers['email']
        db.commit()
        print(f"\n Updated {customer.name} successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n Error: {str(e)}")
    
    press_enter()

def search_customers(db):
    """Search customers by name, phone, or email"""
    display_header("Search Customers")
    query = inquirer.prompt([
        inquirer.Text('query', "Search by name, phone, or email")
    ])['query']
    
    if not query:
        return
    
    customers = db.query(Customer).filter(
        or_(
            Customer.name.ilike(f"%{query}%"),
            Customer.phone.ilike(f"%{query}%"),
            Customer.email.ilike(f"%{query}%")
        )
    ).all()
    
    if not customers:
        print("No matching customers found")
        press_enter()
        return
    
    data = [[
        c.id, c.name, c.phone, 
        c.email
    ] for c in customers]
    
    print_table(["ID", "Name", "Phone", "Email"], data)
    press_enter()

def view_customer_history(db):
    """View customer purchase history"""
    display_header("Customer History")
    customers = db.query(Customer).all()
    
    if not customers:
        print("No customers available")
        press_enter()
        return
    
    choices = [(f"{c.name} (ID: {c.id})", c.id) for c in customers]
    customer_id = inquirer.prompt([
        inquirer.List('id', "Select customer", choices=choices)
    ])['id']
    
    customer = db.query(Customer).get(customer_id)
    if not customer:
        print("Customer not found")
        press_enter()
        return
    
    display_header(f"Purchase History: {customer.name}")
    print(f" Phone: {customer.phone}")
    print(f" Email: {customer.email}")
    print("\nOrders:")
    
    orders = customer.orders
    if not orders:
        print("No orders found")
        press_enter()
        return
    
    for order in orders:
        print(f"\n Order #{order.id} - {order.created_at.strftime('%Y-%m-%d')}")
        print(f"   Status: {order.status.capitalize()}")
        print(f"   Total: {format_currency(order.total)}")
        
        for item in order.items:
            print(f"   - {item.flower.name}: {item.quantity} x {format_currency(item.flower.price)}")
    
    press_enter()


#  Order Management

def order_menu(db):
    """Order management menu"""
    while True:
        display_header("Order Management")
        choice = inquirer.prompt([
            inquirer.List('action',
                message="What would you like to do?",
                choices=[
                    ('View All Orders', 'view'),
                    ('Create New Order', 'create'),
                    ('Update Order Status', 'update'),
                    ('View Order Details', 'details'),
                    ('Search Orders', 'search'),
                    ('Back to Main Menu', 'back')
                ],
            )
        ])['action']
        
        if choice == 'view': view_orders(db)
        elif choice == 'create': create_order(db)
        elif choice == 'update': update_order_status(db)
        elif choice == 'details': view_order_details(db)
        elif choice == 'search': search_orders(db)
        elif choice == 'back': return

def view_orders(db):
    """View all orders"""
    display_header("All Orders")
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    
    if not orders:
        print("No orders found")
        press_enter()
        return
    
    data = []
    for order in orders:
        status = ""
        if order.status == 'completed':
            status = "COMPLETED"
        elif order.status == 'cancelled':
            status = "CANCELLED"
        else:
            status = "PENDING"
        
        data.append([
            order.id, order.customer.name, 
            order.created_at.strftime('%Y-%m-%d'),
            format_currency(order.total), status
        ])
    
    print_table(["ID", "Customer", "Date", "Total", "Status"], data)
    press_enter()

def create_order(db):
    """Create a new order"""
    display_header("Create New Order")
    customers = db.query(Customer).all()
    
    if not customers:
        print("No customers available")
        press_enter()
        return
    
    # Select customer
    choices = [(f"{c.name} ({c.email})", c.id) for c in customers]
    customer_id = inquirer.prompt([
        inquirer.List('id', "Select customer", choices=choices)
    ])['id']
    
    # Create order
    order = Order(customer_id=customer_id)
    db.add(order)
    db.flush()  # Get ID without committing
    
    
    while True:
        flowers = db.query(Flower).filter(Flower.quantity > 0).all()
        if not flowers:
            print("No flowers available")
            break
        
        choices = [
            ('Add another item', 'add'),
            ('Finish order', 'finish'),
            ('Cancel order', 'cancel')
        ]
        action = inquirer.prompt([
            inquirer.List('action', "Add items to order?", choices=choices)
        ])['action']
        
        if action == 'finish':
            break
        elif action == 'cancel':
            db.rollback()
            print("\n Order canceled")
            press_enter()
            return
        
        # Select flower
        choices = [(f"{f.name} - {format_currency(f.price)} (Stock: {f.quantity})", f.id) for f in flowers]
        flower_id = inquirer.prompt([
            inquirer.List('id', "Select flower", choices=choices)
        ])['id']
        
        flower = db.query(Flower).get(flower_id)
        
        # Select quantity
        quantity = inquirer.prompt([
            inquirer.Text('qty', 
                f"How many? (1-{flower.quantity})", 
                validate=lambda _, x: x.isdigit() and 1 <= int(x) <= flower.quantity)
        ])['qty']
        quantity = int(quantity)
        
        # Add item
        order_item = OrderItem(
            order_id=order.id,
            flower_id=flower.id,
            quantity=quantity
        )
        db.add(order_item)
        
        # Update order total
        order.total = (order.total or 0) + (flower.price * quantity)
        print(f"Added {quantity} {flower.name} to order")
    
    # Finalize order
    if not order.items:
        db.rollback()
        print("\n Order canceled - no items added")
        press_enter()
        return
    
    # Set status
    status = inquirer.prompt([
        inquirer.List('status', "Order status", 
            choices=[('Completed', 'completed'), ('Pending', 'pending')],
            default='completed')
    ])['status']
    
    order.status = status
    
    # Update stock if completed
    if status == 'completed':
        for item in order.items:
            flower = db.query(Flower).get(item.flower_id)
            flower.quantity -= item.quantity
    
    try:
        db.commit()
        print(f"\n Order #{order.id} created successfully!")
        print(f"Total: {format_currency(order.total)}")
    except Exception as e:
        db.rollback()
        print(f"\n Error creating order: {str(e)}")
    
    press_enter()

def update_order_status(db):
    """Update order status"""
    display_header("Update Order Status")
    orders = db.query(Order).all()
    
    if not orders:
        print("No orders available")
        press_enter()
        return
    
    choices = [(f"Order #{o.id} - {o.customer.name} - {o.status}", o.id) for o in orders]
    answers = inquirer.prompt([
        inquirer.List('id', "Select order", choices=choices),
        inquirer.List('status', "New status", 
            choices=[('Completed', 'completed'), ('Pending', 'pending'), ('Cancelled', 'cancelled')])
    ])
    
    order = db.query(Order).get(answers['id'])
    if not order:
        print("Order not found")
        press_enter()
        return
    
    new_status = answers['status']
    
    try:
        # Handle status changes
        if new_status == 'completed' and order.status != 'completed':
            for item in order.items:
                flower = item.flower
                flower.quantity -= item.quantity
        
        elif new_status == 'cancelled' and order.status == 'completed':
            # Restore stock
            for item in order.items:
                flower = item.flower
                flower.quantity += item.quantity
        
        order.status = new_status
        db.commit()
        print(f"\n Order #{order.id} updated to {new_status} successfully!")
    except Exception as e:
        db.rollback()
        print(f"\n Error: {str(e)}")
    
    press_enter()

def view_order_details(db):
    """View order details"""
    display_header("Order Details")
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(10).all()
    
    if not orders:
        print("No orders available")
        press_enter()
        return
    
    choices = [(f"Order #{o.id} - {o.customer.name} - {format_currency(o.total)}", o.id) for o in orders]
    order_id = inquirer.prompt([
        inquirer.List('id', "Select order", choices=choices)
    ])['id']
    
    order = db.query(Order).get(order_id)
    if not order:
        print("Order not found")
        press_enter()
        return
    
    display_header(f"Order #{order.id} Details")
    print(f"Customer: {order.customer.name}")
    print(f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"Status: {order.status.capitalize()}")
    print(f"Total: {format_currency(order.total)}\n")
    
    print("Items:")
    data = [[
        item.flower.name, item.quantity, 
        format_currency(item.flower.price), 
        format_currency(item.quantity * item.flower.price)
    ] for item in order.items]
    
    print_table(["Flower", "Qty", "Price", "Total"], data)
    press_enter()

def search_orders(db):
    """Search orders by ID or customer name"""
    display_header("Search Orders")
    query = inquirer.prompt([
        inquirer.Text('query', "Search by order ID or customer name")
    ])['query']
    
    if not query:
        return
    
    try:
        # Search by ID if query is numeric
        order_id = int(query)
        orders = db.query(Order).filter(Order.id == order_id).all()
    except ValueError:
        # Search by customer name
        orders = db.query(Order).join(Customer).filter(
            Customer.name.ilike(f"%{query}%")
        ).all()
    
    if not orders:
        print("No matching orders found")
        press_enter()
        return
    
    data = []
    for order in orders:
        status = " COMPLETED" if order.status == 'completed' else (
            " CANCELLED" if order.status == 'cancelled' else "🔄 PENDING"
        )
        data.append([
            order.id, order.customer.name, 
            order.created_at.strftime('%Y-%m-%d'),
            format_currency(order.total), status
        ])
    
    print_table(["ID", "Customer", "Date", "Total", "Status"], data)
    press_enter() 

    # General Expense Reports 

def reports_menu(db):
        """Reports menu"""
        while True:
            display_header("Reports")
            choice = inquirer.prompt([
                inquirer.List('action',
                    message="Select report",
                    choices=[
                        ('Sales Summary', 'sales'),
                        ('Top Selling Flowers', 'flowers'),
                        ('Top Customers', 'customers'),
                        ('Back to Main Menu', 'back')
                    ],
                )
            ])['action']
            
            if choice == 'sales': sales_summary(db)
            elif choice == 'flowers': top_flowers(db)
            elif choice == 'customers': top_customers(db)
            elif choice == 'back': return

def sales_summary(db):
    """Sales summary report"""
    display_header("Sales Summary")
    
    # Total sales
    total_sales = db.query(func.sum(Order.total)).filter(
        Order.status == 'completed'
    ).scalar() or 0
    
    # Recent sales (last 7 days)
    recent_sales = db.query(func.sum(Order.total)).filter(
        Order.status == 'completed',
        Order.created_at >= datetime.now() - timedelta(days=7)
    ).scalar() or 0
    
    # Order count
    order_count = db.query(Order).filter(
        Order.status == 'completed'
    ).count()
    
    print(f"Total Sales: {format_currency(total_sales)}")
    print(f"Recent Sales (7 days): {format_currency(recent_sales)}")
    print(f"Total Orders: {order_count}")
    press_enter()

def top_flowers(db):
    """Top selling flowers report"""
    display_header("Top Selling Flowers")
    
    results = db.query(
        Flower.name,
        func.sum(OrderItem.quantity).label('total_sold'),
        func.sum(OrderItem.quantity * Flower.price).label('total_revenue')
    ).join(OrderItem).join(Order).filter(
        Order.status == 'completed'
    ).group_by(Flower.name).order_by(
        func.sum(OrderItem.quantity).desc()
    ).limit(10).all()
    
    if not results:
        print("No sales data available")
        press_enter()
        return
    
    data = []
    for i, row in enumerate(results, 1):
        data.append([
            i, row.name, row.total_sold, format_currency(row.total_revenue)
        ])
    
    print_table(["Rank", "Flower", "Units Sold", "Revenue"], data)
    press_enter()

def top_customers(db):
    """Top customers report"""
    display_header("Top Customers")
    
    results = db.query(
        Customer.name,
        func.count(Order.id).label('order_count'),
        func.sum(Order.total).label('total_spent')
    ).join(Order).filter(
        Order.status == 'completed'
    ).group_by(Customer.name).order_by(
        func.sum(Order.total).desc()
    ).limit(10).all()
    
    if not results:
        print("No customer data available")
        press_enter()
        return
    
    data = []
    for i, row in enumerate(results, 1):
        data.append([
            i, row.name, row.order_count, format_currency(row.total_spent)
        ])
    
    print_table(["Rank", "Customer", "Orders", "Total Spent"], data)
    press_enter()