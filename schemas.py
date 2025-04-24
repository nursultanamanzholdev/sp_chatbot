from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import List, Optional, Dict, Any
import re

# Регулярное выражение для казахстанского номера телефона
KZ_PHONE_REGEX = r'^\+7\s?\(?[0-9]{3}\)?\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}$'

def validate_kz_phone(phone: str) -> bool:
    return bool(re.match(KZ_PHONE_REGEX, phone))

class NoteBase(BaseModel):
    content: str
    child_name: str
    feedback: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    parent_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PromptBase(BaseModel):
    name: str
    prompt: str
    pdf_book_id: Optional[int] = None
    mode: Optional[str] = "chat"

class PromptCreate(PromptBase):
    pass

class PDFBookBase(BaseModel):
    book_reference: str

class PDFBookCreate(PDFBookBase):
    pass

class PDFBook(PDFBookBase):
    id: int
    filename: str
    user_id: int
    json_content: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Prompt(PromptBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    pdf_book: Optional['PDFBook'] = None

    class Config:
        from_attributes = True

class PromptUpdate(BaseModel):
    prompt: str
    mode: Optional[str] = None

class HistoryBase(BaseModel):
    prompt_id: int
    conversation: str

class HistoryCreate(HistoryBase):
    pass

class History(HistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 