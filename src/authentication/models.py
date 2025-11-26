from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4 
from ..database import Base

class AdminUserModel(Base):
    __tablename__ = "admin_users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_profile_image = Column(String, nullable=True)
    role = Column(String, default="admin")
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    user_profile_image = Column(String, nullable=True)
    role = Column(String, default="non_admin")
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))