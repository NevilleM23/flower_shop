# MyShop - A Command Line Flower Shop Management System

## Problem Statement
Small local flower shops need an efficient way to manage inventory, customer relationships, and order processing without complex software solutions.

## The Solution
A Python-based CLI system for comprehensive shop management.

## MVP Features

### Stock Management
- Add/remove flowers with details (name, price, quantity, category)
- Update stock levels
- View all available flowers
- Low stock alerts
- Search/filter flowers by category/price

### Customer Management
- Add/edit customer profiles (name, contact, preferences)
- View customer purchase history
- Search customers by name/phone

### Order Management
- Calculate order totals
- Update order status (pending/fulfilled/cancelled)
- View order history with filters
- 
 ## Installation  
Clone repository with submodules

git clone https://github.com/NevilleM23/flower_shop
cd flower_shop

### Create virtual environment
pipenv --python 3.10

### Install dependencies
pipenv install

### Initialize database
pipenv run python lib/cli.py --init

### Start application
pipenv run python lib/cli.py
 
## Usage 
### Start the application
pipenv run python lib/cli.py

### Main Menu Navigation:
Scroll up and down using the arrow keys and press ENTER when hovered over one of the menu items 
### Stock Management
### Customer Management
### Order Management
### Reports
### Exit
