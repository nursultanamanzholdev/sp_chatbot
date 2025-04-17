from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)
    phone = Column(String)  # Добавляем поле для телефона
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    notes = relationship("Note", back_populates="parent")

    prompts = relationship("Prompt", back_populates="user")
    history = relationship("History", back_populates="user")
    pdf_books = relationship("PDFBook", back_populates="user")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    child_name = Column(String)
    parent_id = Column(Integer, ForeignKey("users.id"))
    parent = relationship("User", back_populates="notes")

class Prompt(Base):
    __tablename__ = "prompts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    prompt = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    pdf_book_id = Column(Integer, ForeignKey("pdf_books.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="prompts")
    pdf_book = relationship("PDFBook", back_populates="prompts")

class PDFBook(Base):
    __tablename__ = "pdf_books"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    book_reference = Column(String)
    json_content = Column(JSON)  # Changed from file_content to json_content
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="pdf_books")
    prompts = relationship("Prompt", back_populates="pdf_book")

class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt_id = Column(Integer, ForeignKey("prompts.id"))
    conversation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="history") 