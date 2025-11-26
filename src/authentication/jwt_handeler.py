from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os 
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 14

if not JWT_SECRET or not JWT_ALGORITHM:
    raise ValueError("Tokens env variables ar enot being loaded on the backend")


def generate_access_token(user_data: dict) -> str:
    try:
        access_token_data = user_data.copy()
        expires_in = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_data.update({ "exp": int(expires_in.timestamp()), "type": "access" })
        
        access_token = jwt.encode(access_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return access_token
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate access token"
        )
        

def generate_refresh_token(user_data: dict) -> str:
    try:
        refresh_token_data = user_data.copy()
        expires_in = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_data.update({ "exp": int(expires_in.timestamp()), "type": "refresh" })
        
        refresh_token = jwt.encode(refresh_token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return refresh_token
        
    except Exception as e:
        print(f"There was an error trying to generate the refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate refresh token"
        )
        
def generate_user_tokens(user_data: dict) -> dict:
    try:
        access_token = generate_access_token(user_data)
        refresh_token = generate_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        
    except Exception as e:
        print(f"There was an error trying to generate user tokens: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate tokens"
        )
        

def decode_access_token(access_token: str) -> dict:
    try:
        decoded_token = jwt.decode(access_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        return decoded_token
        
    except Exception as e:
        print(f"There was an error trying to decode the token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to decode the toke provided, invalid"
        )
        

def refresh_token(refresh_token: str) -> dict:
    decoded_token = decode_access_token(refresh_token)
        
    if decoded_token["type"] != "refresh":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type was passed"
        )
            
    try:
        user_id = decoded_token["sub"]
        username = decoded_token["username"]
        
        new_tokens_data = {
            "sub": user_id,
            "username": username
        }
        
        new_access_token = generate_access_token(new_tokens_data)
        new_refresh_token = generate_refresh_token(new_tokens_data)
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
        
    except ExpiredSignatureError as e:
        print(f"Token expired: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired, refresh it"
        )
        
    except InvalidTokenError as e:
        print(f"Invalid token passed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token was passed"
        )
        
    except Exception as e:
        print(f"Unable to refresh the refresh token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to refresh the token"
        )
        

def get_current_user_handeler(access_token: str) -> dict:
    try:
        decoded_token = decode_access_token(access_token)
        
        user_id = decoded_token["sub"]
        username = decoded_token["username"]
        
        return {
            "user_id": user_id,
            "username": username
        }
        
    except Exception as e:
        print(f"Unable to get the current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to get the current user"
        )