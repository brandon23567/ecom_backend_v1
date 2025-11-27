from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer, Double
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from uuid import uuid4
from ..database import Base

class ProductModel(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, index=True, default=lambda: uuid4().hex)
    associated_admin_user_id = Column(String, ForeignKey("admin_users.id"), nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=False)
    price = Column(Integer)
    quantity = Column(Integer, default=1)
    product_header_image = Column(String, nullable=False)
    date_posted = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    admin_user = relationship("AdminUserModel", back_populates="products")