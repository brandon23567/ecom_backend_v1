from sqlalchemy.orm import Session
from fastapi import HTTPException, status, File, Form, UploadFile, APIRouter, Depends
from ..database import get_db
from .jwt_handeler import *
from .schemas import *
from .crud import *
from fastapi.security.oauth2 import OAuth2PasswordBearer

admin_oauth = OAuth2PasswordBearer(tokenUrl="/admin/signin", description="admin_auth_tokens")
user_oauth = OAuth2PasswordBearer(tokenUrl="/signin", description="user_auth_tokens")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/admin/signup", status_code=status.HTTP_201_CREATED)
def signup_admin_user_route(
    db: Session = Depends(get_db),
    username: str = Form(..., description="username"),
    email: str = Form(..., description="email"),
    password: str = Form(..., description="password"),
    user_profile_image: UploadFile = File(None, description="user profile image"),
):
    return signup_admin_user(
        db=db,
        username=username,
        email=email,
        password=password,
        user_profile_image=user_profile_image,
    )
    

@router.post("/admin/signin", status_code=status.HTTP_200_OK)
def signin_admin_user_route(
    user_data: SigninAdminUserSchema,
    db: Session = Depends(get_db)
):
    return signin_admin_user(
        user_data=user_data,
        db=db
    )
    

@router.get("/admin/me", status_code=status.HTTP_200_OK)
def get_current_admin_user_route(
    db: Session = Depends(get_db),
    current_user_token: str = Depends(admin_oauth)
):
    return get_current_user_handeler(access_token=current_user_token)



@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup_nromal_user_route(
    db: Session = Depends(get_db),
    username: str = Form(..., description="username"),
    email: str = Form(..., description="email"),
    password: str = Form(..., description="password"),
    user_profile_image: UploadFile = File(None, description="user profile image"),
):
    return signup_user(
        db=db,
        username=username,
        email=email,
        password=password,
        user_profile_image=user_profile_image,
    )
    

@router.post("/signin", status_code=status.HTTP_200_OK)
def signin_normal_user_route(
    user_data: SigninNonAdminUserSchema,
    db: Session = Depends(get_db)
):
    return signin_user(
        user_data=user_data,
        db=db
    )


@router.get("/me", status_code=status.HTTP_200_OK)
def get_current_normal_user_route(
    db: Session = Depends(get_db),
    current_user_token: str = Depends(user_oauth)
):
    return get_current_user_handeler(access_token=current_user_token)