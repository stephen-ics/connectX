from pydantic import BaseModel, EmailStr
from pydantic.types import conint
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    profile_photo: str 
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPasswordReset(BaseModel):
    old_password: str
    new_password: str

class UserProfileResponse(BaseModel):
    first_name: str
    biography: str = None
    profile_photo: str 
    num_posts: int
    num_votes: int

class UserBiography(BaseModel):
    new_biography: str

class UserProfilePhoto(BaseModel):
    new_profile_photo: str
    
class PostBase(BaseModel):
    title: str
    content: str
    image: str = None
    published: bool = True #default value

class PostVotesResponse(BaseModel):
    found_vote: bool
    
class PostCreate(PostBase):
    pass

class PostUpdate(PostBase):
    published: bool

class PostResponseBase(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: UserResponse
    parent_id: int = None

    class Config:
        orm_mode = True
class PostResponse(BaseModel):
    Post: PostResponseBase
    votes: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
class LoginResponse(Token):
    user_id: int
    first_name: str
    last_name: str
class TokenData(BaseModel):
    id: Optional[str]

class Vote(BaseModel):
    post_id: int
    vote_dir: conint(le=1, ge=0) # less than or equal 1, greater than or equal to 0 (constrained to 0 and 1)
