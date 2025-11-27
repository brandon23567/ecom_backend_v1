from .crud import *
from .schemas import *
from ..authentication.routes import user_oauth, admin_oauth
from ..authentication.jwt_handeler import *
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends, UploadFile, File, Form, APIRouter
from ..database import get_db


router = APIRouter(
    prefix="/products",
    tags=["Products Endpoint"]
)


@router.post("/admin/new", status_code=status.HTTP_201_CREATED)
def create_new_product_route(
    db: Session = Depends(get_db),
    name: str = Form(..., description="product name"),
    description: str = Form(..., description="description"),
    price: int = Form(..., description="price"),
    quantity: int = Form(..., description="quantity"),
    product_header_image: UploadFile = File(..., description="product_header_image"),
    current_user_token: str = Depends(admin_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return upload_new_product(
        db=db,
        associated_admin_user_id=user_id,
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        product_header_image=product_header_image,
    )


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_products_route_user_side(
    db: Session = Depends(get_db),
    current_user_token: str = Depends(user_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return view_all_products(
        db=db ,
        user_id=user_id
    )
    

@router.get("/admin/products", status_code=status.HTTP_200_OK)
def get_all_products_route_admin_side(
    db: Session = Depends(get_db),
    current_user_token: str = Depends(admin_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return view_all_products(
        db=db ,
        user_id=user_id
    )
    

@router.get("/{product_id}", status_code=status.HTTP_200_OK)
def get_single_product_details_route_user_side(
    product_id: str,
    db: Session = Depends(get_db),
    current_user_token: str = Depends(user_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return view_single_product(
        db=db,
        user_id=user_id,
        product_id=product_id
    )
    

@router.get("/admin/{product_id}", status_code=status.HTTP_200_OK)
def get_single_product_details_route_user_side(
    product_id: str,
    db: Session = Depends(get_db),
    current_user_token: str = Depends(admin_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return view_single_product(
        db=db,
        user_id=user_id,
        product_id=product_id
    )
    

@router.put("/admin/edit/{product_id}", status_code=status.HTTP_202_ACCEPTED)
def edit_product_details_route(
    product_id: str,
    db: Session = Depends(get_db),
    name: str = Form(None, description="new product name"),
    description: str = Form(None, description="new description"),
    price: int = Form(None, description="new product price"),
    quantity: int = Form(None, description="new product price"),
    product_header_image: UploadFile = File(None, description="new product header image"),
    current_user_token: str = Depends(admin_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return edit_a_product(
        db=db,
        user_id=user_id,
        product_id=product_id,
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        product_header_image=product_header_image
    )
    

@router.delete("/admin/delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_route(
    product_id: str,
    db: Session = Depends(get_db),
    current_user_token: str = Depends(admin_oauth)
):
    current_user_details = get_current_user_handeler(access_token=current_user_token)
    user_id = current_user_details["user_id"]
    
    return delete_a_product(
        db=db,
        user_id=user_id,
        product_id=product_id
    )