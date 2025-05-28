from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Flower(Base):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    category = Column(String(50))
    
    order_items = relationship("OrderItem", back_populates="flower")

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True)
    email = Column(String(100))
    loyalty_points = Column(Integer, default=0)
    
    orders = relationship("Order", back_populates="customer")

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    flower_id = Column(Integer, ForeignKey('flowers.id'))
    quantity = Column(Integer)
    
    order = relationship("Order", back_populates="items")
    flower = relationship("Flower", back_populates="order_items")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    status = Column(String(20), default='pending')
    total = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")