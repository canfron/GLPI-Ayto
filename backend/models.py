from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)

    users = relationship("User", back_populates="role")

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)

    users = relationship("User", back_populates="department")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(100))
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    role = relationship("Role", back_populates="users")
    department = relationship("Department", back_populates="users")
    tickets_requested = relationship("Ticket", foreign_keys='Ticket.requester_id', back_populates="requester")
    tickets_assigned = relationship("Ticket", foreign_keys='Ticket.assignee_id', back_populates="assignee")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    is_visible_to_users = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent = relationship("Category", remote_side=[id], backref="children")
    tickets = relationship("Ticket", back_populates="category")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum('Nuevo', 'Asignado', 'En curso', 'Pendiente', 'Resuelto', 'Cerrado'), default='Nuevo')
    priority = Column(Enum('Baja', 'Media', 'Alta', 'Urgente'), default='Media')
    category_id = Column(Integer, ForeignKey("categories.id"))
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    category = relationship("Category", back_populates="tickets")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="tickets_requested")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="tickets_assigned")
    comments = relationship("TicketComment", back_populates="ticket")

class TicketComment(Base):
    __tablename__ = "ticket_comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")
