from .schemas import *
from .models import *
from ..authentication.routes import admin_oauth, user_oauth
from ..authentication.models import *
from fastapi import HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import json
from sqlalchemy import select, and_, or_
from ..authentication.crud import _upload_image_to_cloudinary

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
        

def upload_new_product(
    db: Session,
    associated_admin_user_id: str,
    name: str = Form(..., description="product name"),
    description: str = Form(..., description="description"),
    price: int = Form(..., description="price"),
    quantity: int = Form(..., description="quantity"),
    product_header_image: UploadFile = File(..., description="product_header_image"),
):
    existing_product_instance = db.execute(select(ProductModel).where(ProductModel.name == name)).scalar_one_or_none()
    if existing_product_instance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Products cannot have the exact same name"
        )
        
    valid_admin_user_instance = db.execute(select(AdminUserModel).where(AdminUserModel.id == associated_admin_user_id)).scalar_one_or_none()
    if not valid_admin_user_instance:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You dont have permission level to add a new product"
        )
        
    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity of products cannot be less than 0 or negative, please add valid numbers or else"
        )
        
    if len(description) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aight g hang it up, too much content 🤣☠️"
        )
        
    try:
        new_product_image_url = _upload_image_to_cloudinary(image_file=product_header_image)
        new_product_instance = ProductModel(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            product_header_image=new_product_image_url
        )
        
        db.add(new_product_instance)
        db.commit()
        
        db.refresh(new_product_instance)
        
        return new_product_instance
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to add new product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to add the new product"
        )
        

def view_all_products(
    db: Session,
    user_id: str 
):
    check_admin_user = db.execute(select(AdminUserModel).where(AdminUserModel.id == user_id)).scalar_one_or_none()
    check_normal_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    
    if not check_admin_user or not check_normal_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Why are you even here when you know you not supposed to be 🗿"
        )
        
    try:
        all_products = db.execute(select(ProductModel)).scalars().all()
        
        if not all_products:
            return []
        
        return all_products
        
    except Exception as e:
        print(f"Unable to fetch products from the db: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to fetch products at this time sorry"
        )
        
def view_single_product(
    db: Session,
    user_id: str ,
    product_id: str
):
    check_admin_user = db.execute(select(AdminUserModel).where(AdminUserModel.id == user_id)).scalar_one_or_none()
    check_normal_user = db.execute(select(UserModel).where(UserModel.id == user_id)).scalar_one_or_none()
    
    if not check_admin_user or not check_normal_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Why are you even here when you know you not supposed to be 🗿"
        )
        
    single_product_instance = db.execute(select(ProductModel).where(ProductModel.id == product_id)).scalar_one_or_none()
    if not single_product_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested product was not found, sorry"
        )
        
    try:
        return single_product_instance    
        
    except Exception as e:
        print(f"There was an error trying to get the product details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get details of this product at this time"
        )
        

def edit_a_product(
    db: Session,
    user_id: str,
    product_id: str,
    name: str = Form(None, description="new product name"),
    description: str = Form(None, description="new description"),
    price: int = Form(None, description="new product price"),
    quantity: int = Form(None, description="new product price"),
    product_header_image: UploadFile = File(None, description="new product header image"),
):
    check_admin_user = db.execute(select(AdminUserModel).where(AdminUserModel.id == user_id)).scalar_one_or_none()
    
    if not check_admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Why are you even here when you know you not supposed to be 🗿"
        )
        
    product_instance = db.execute(select(ProductModel).where(
        and_(
            ProductModel.id == product_id,
            ProductModel.associated_admin_user_id == check_admin_user.id
        )
    )).scalar_one_or_none()
    
    if not product_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested product to edit was not found sorry."
        )
        
    try:
        if product_header_image is not None:
            new_product_header_image_url = _upload_image_to_cloudinary(image_file=product_header_image)
            product_instance.product_header_image = new_product_header_image_url
        if name is not None:
            product_instance.name = name 
        if description is not None:
            product_instance.description = description
        if price is not None:
            product_instance.price = price 
        if quantity is not None:
            product_instance.quantity = quantity
            
        db.commit()
        db.refresh()
        
        return product_instance
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to edit the product details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to edit this product"
        )
        

def delete_a_product(
    db: Session,
    user_id: str,
    product_id: str
):
    check_admin_user = db.execute(select(AdminUserModel).where(AdminUserModel.id == user_id)).scalar_one_or_none()
    
    if not check_admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Why are you even here when you know you not supposed to be 🗿"
        )
        
    product_instance = db.execute(select(ProductModel).where(
        and_(
            ProductModel.id == product_id,
            ProductModel.associated_admin_user_id == check_admin_user.id
        )
    )).scalar_one_or_none()
    
    if not product_instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested product to edit was not found sorry."
        )
        
    try:
        db.delete(product_instance)
        db.commit()
        
        return { "message": "Product has been deleted" }
        
    except Exception as e:
        db.rollback()
        print(f"There was an error trying to delete the product: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the requested product due to an error 🤣"
        )