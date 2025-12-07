# from jose import jwt, JWTError
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordBearer

# import models, database
# from core.config import settings
# from schemas import token_schema

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY = settings.secret_key
# ALGORITHM = settings.algorithm
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# def create_access_token(data: dict):
#     """
#     Create a JWT access token with expiration.
#     """
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def verify_access_token(token: str, credentials_exception):
#     """
#     Verify the JWT token and return TokenData.
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: int = payload.get("user_id")
#         if user_id is None:
#             raise credentials_exception
#         token_data = token_schema.TokenData(user_id=user_id)
#     except JWTError:
#         raise credentials_exception
#     return token_data


# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(database.get_db)
# ):
#     """
#     Get the currently authenticated user from the token.
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     token_data = verify_access_token(token, credentials_exception)
#     user = db.query(models.User).filter(models.User.user_id == token_data.user_id).first()
#     if not user:
#         raise credentials_exception
#     return user



# from jose import jwt, JWTError
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordBearer

# import models, database
# from core.config import settings
# from schemas import token_schema

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY = settings.secret_key
# ALGORITHM = settings.algorithm
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# def create_access_token(data: dict):
#     """
#     Create a JWT access token with expiration.
#     """
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


# def verify_access_token(token: str, credentials_exception):
#     """
#     Verify the JWT token and return TokenData.
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: int = payload.get("user_id")
#         if user_id is None:
#             raise credentials_exception
#         token_data = token_schema.TokenData(user_id=user_id)
#     except JWTError:
#         raise credentials_exception
#     return token_data


# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(database.get_db)
# ):
#     """
#     Get the currently authenticated user from the token.
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     token_data = verify_access_token(token, credentials_exception)
#     user = db.query(models.User).filter(models.User.user_id == token_data.user_id).first()
#     if not user:
#         raise credentials_exception
#     return user


# # ============================================
# # NEW FUNCTION FOR WEBSOCKET AUTHENTICATION
# # ============================================
# async def get_current_user_ws(token: str, db: Session):
#     """
#     Authenticate user from WebSocket token parameter.
#     Similar to get_current_user but for WebSocket connections.
    
#     Args:
#         token: JWT token from WebSocket query parameter
#         db: Database session
        
#     Returns:
#         User object if authentication successful
        
#     Raises:
#         HTTPException: If authentication fails
#     """
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         # Decode JWT token using your existing settings
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
#         # Extract user_id from payload (matches your existing code)
#         user_id: int = payload.get("user_id")
        
#         if user_id is None:
#             raise credentials_exception
        
#     except JWTError:
#         raise credentials_exception
    
#     # Get user from database
#     user = db.query(models.User).filter(models.User.user_id == user_id).first()
    
#     if user is None:
#         raise credentials_exception
    
#     return user



from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from fastapi.security import APIKeyHeader

import models, database
from core.config import settings
from schemas import token_schema

# ----------------------------------------
# REPLACED OAuth2PasswordBearer WITH APIKeyHeader
# ----------------------------------------
token_header = APIKeyHeader(name="Authorization", auto_error=False)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    """
    Create a JWT access token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    """
    Verify the JWT token and return TokenData.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = token_schema.TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(
    token: str = Depends(token_header),
    db: Session = Depends(database.get_db)
):
    """
    Get the currently authenticated user from the token (Bearer Token).
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    if not token:
        raise credentials_exception

    # Token format must be: Bearer <token>
    if not token.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use: Bearer <token>"
        )

    # Extract real token
    token = token.split(" ")[1]

    # Verify token
    token_data = verify_access_token(token, credentials_exception)

    # Get user from DB
    user = db.query(models.User).filter(models.User.user_id == token_data.user_id).first()
    if not user:
        raise credentials_exception

    return user


# ============================================
# NEW FUNCTION FOR WEBSOCKET AUTHENTICATION
# ============================================
async def get_current_user_ws(token: str, db: Session):
    """
    Authenticate user from WebSocket token parameter.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.user_id == user_id).first()

    if not user:
        raise credentials_exception

    return user
