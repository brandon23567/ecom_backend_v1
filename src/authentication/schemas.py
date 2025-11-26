from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class SignupAdminUser(BaseModel):
    username: str = Field(..., description="username")
    email: EmailStr = Field(..., description="email")
    password: str = Field(..., description="password")
    user_profile_image: Optional[str] = Field(None, description="user_profile image")
    
    class Config:
        from_attributes = True 
        

class SigninAdminUserSchema(BaseModel):
    email: EmailStr = Field(..., description="email")
    password: str = Field(..., description="password")
    
    class Config:
        from_attributes = True 
        
        
class DisplayAdminUserSchema(BaseModel):
    id: str 
    username: str 
    email: EmailStr 
    user_profile_image: Optional[str]
    
    class Config:
        from_attributes = True 
        

class SignupNonAdminUserSchema(BaseModel):
    username: str= Field(..., description="username")
    email: EmailStr = Field(..., description="email")
    password: str = Field(..., description="password")
    user_profile_image: Optional[str] = Field(None, description="profile image")
    
    class Config:
        from_attributes = True 
        

class SigninNonAdminUserSchema(BaseModel):
    username: str = Field(..., description="username")
    password: str = Field(..., description="password")
    
    class Config:
        from_attributes = True 


class DisplayNonAdminUserSchema(BaseModel):
    id: str 
    username: str 
    email: str 
    user_profile_image: Optional[str]
    
    class Config:
        from_attributes = True
        

class UserTokensSchema(BaseModel):
    access_token: str 
    refresh_token: str 
    
    class Config:
        from_attributes = True 