from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class Role(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    is_visible_to_users: bool = True

class Category(CategoryBase):
    id: int
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role_id: int
    department_id: Optional[int] = None
    is_active: bool = True

class User(UserBase):
    id: int
    created_at: datetime
    role: Optional[Role] = None

    class Config:
        from_attributes = True

class TicketBase(BaseModel):
    title: str
    description: str
    category_id: int
    priority: str = 'Media'

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: int
    status: str
    requester_id: int
    assignee_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    requester: Optional[User] = None
    assignee: Optional[User] = None
    category: Optional[Category] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    username: str
    password: str
