from pydantic import BaseModel, Field
from datetime import datetime


class CreateProductSchema(BaseModel):
    name: str = Field(..., description="product name")
    description: str = Field(..., description="product description")
    product_header_image: str = Field(..., description="product header image")
    quantity: int = Field(..., description="quantity")
    price: float = Field(..., description="price of product")
    
    class Config:
        from_attributes = True 
        
        
class DisplayProductSchema(BaseModel):
    id: str 
    name: str 
    description: str 
    product_header_image: str 
    quantity: int 
    price: float 
    
    class Config:
        from_attributes = True 
        