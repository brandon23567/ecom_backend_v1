from .schemas import *
from .models import *
from sqlalchemy import select, and_, or_ 
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile, File, Form
import os 
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import json
import bcrypt

load_dotenv()

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

if not CLOUDINARY_CLOUD_NAME or not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
    raise ValueError("Unable to load cloudinary config variables to connect to it")

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)

# function to handle file uploads to cloudinary

def _upload_image_to_cloudinary(
    image_file: UploadFile = File(..., description="Image file to upload")
) -> str:
    try:
        file_to_upload = cloudinary.uploader.upload(
            image_file.file,
            use_filename=True,
            unique_filename=True
        )
        
        image_url = json.loads(file_to_upload)["secure_url"]
        
        return image_url
        
    except Exception as e:
        print(f"There was an error trying to upload the image to cloudinary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to upload the image to cloudinary"
        )
        

def signup_admin_user(
    db: Session,
    username: str = Form(..., description="username"),
    email: str = Form(..., description="email"),
    password: str = Form(..., description="password"),
    user_profile_image: UploadFile = File(None, description="profile image"),
):
    existing_admin_user = db.execute(select(AdminUserModel).where(
        or_(
            AdminUserModel.email == email,
            AdminUserModel.username == username
        )    
    )).scalar_one_or_none()
        
    if existing_admin_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already have an account please login"
        )
            
    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        
        if user_profile_image:
            user_image_url = _upload_image_to_cloudinary(image_file=user_profile_image)
            new_admin_user_instance = AdminUserModel(
                username=username,
                email=email,
                password=hashed_password,
                user_profile_image=user_image_url
            )
            
            db.add(new_admin_user_instance)
            db.commit()
            
            db.refresh(new_admin_user_instance)
            
            return new_admin_user_instance

        new_admin_user_instance = AdminUserModel(
            username=username,
            email=email,
            password=hashed_password
        )
            
        db.add(new_admin_user_instance)
        db.commit()
            
        db.refresh(new_admin_user_instance)
            
        return new_admin_user_instance
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to signup the admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to signup the new admin user"
        )
        

def signin_admin_user(
    user_data: SigninAdminUserSchema,
    db: Session
):
    existing_admin_user_instance = db.execute(select(AdminUserModel).where(
        or_(
            AdminUserModel.email == user_data.email
        )
    )).scalar_one_or_none()
    
    if not existing_admin_user_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )
        
    try:
        checked_password = bcrypt.checkpw(user_data.password.encode("utf-8"), existing_admin_user_instance.password.encode("utf-8"))
        if not checked_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials used for login"
            )
            
        return existing_admin_user_instance
        
    except Exception as e:
        print(f"There was an error trying to signin the admin user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to signin an admin user"
        )
        

def signup_user(
    db: Session,
    username: str = Form(..., description="username"),
    email: str = Form(..., description="email"),
    password: str = Form(..., description="password"),
    user_profile_image: UploadFile = File(None, description="user profile image"),
):
    existing_user_instance = db.execute(select(UserModel).where(UserModel.username == username)).scalar_one_or_none()
    
    if not existing_user_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User was not found, please log in"
        )
        
    try:
        salt = bcrypt.gensalt(rounds=12)
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        
        if user_profile_image:
            user_image_url = _upload_image_to_cloudinary(image_file=user_profile_image)
            
            new_user_instance = UserModel(
                username=username,
                email=email,
                password=hashed_password,
                user_profile_image=user_image_url
            )
            
            db.add(new_user_instance)
            db.commit()
            
            db.refresh(new_user_instance)
            
            return new_user_instance
        
        new_user_instance = UserModel(
            username=username,
            email=email,
            password=hashed_password
        )
            
        db.add(new_user_instance)
        db.commit()
            
        db.refresh(new_user_instance)
            
        return new_user_instance
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to signup the user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to signup the new user"
        )
        

def signin_user(
    user_data: SigninNonAdminUserSchema,
    db: Session
):
    existing_user_instance = db.execute(select(UserModel).where(UserModel.username == user_data.username)).scalar_one_or_none()
    
    if not existing_user_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found,invalid credentials"
        )
        
    try:
        checked_password = bcrypt.checkpw(user_data.password.encode("utf-8"), existing_user_instance.password.encode("utf-8"))
        if not checked_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login credentials used"
            )
            
        return existing_user_instance
        
    except Exception as e:
        print(f"There was an error trying to signin the suer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to login the user"
        )