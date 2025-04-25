from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from datetime import timedelta
from typing import Optional, List, Dict, Any
import models
import schemas
import auth
from database import engine, get_db
import os
import json
import tempfile
from pdf2json.gpt import process as pdf_to_json_process
from pdf2json.book2dial import process_json_data
from dotenv import load_dotenv
import time

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatbot-frontend-oeip.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/profile", response_model=schemas.User)
async def get_user_profile(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.put("/api/users/profile", response_model=schemas.User)
async def update_user_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.name:
        current_user.name = user_update.name
    if user_update.email:
        current_user.email = user_update.email
    if user_update.phone is not None:
        current_user.phone = user_update.phone
    db.commit()
    db.refresh(current_user)
    return current_user

@app.put("/api/users/change-password")
async def change_password(
    password_data: schemas.PasswordChange,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    if not auth.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    current_user.hashed_password = auth.get_password_hash(password_data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}

@app.get("/api/prompts", response_model=list[schemas.Prompt])
async def get_prompts(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Prompt).filter(
        models.Prompt.user_id == current_user.id
    ).options(
        joinedload(models.Prompt.pdf_book)
    ).all()

@app.post("/api/pdf-books", response_model=schemas.PDFBook)
async def upload_pdf_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    book_reference: str = Form(...),
    prompt_id: Optional[int] = Form(None),
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    temp_dir = os.path.join(os.getcwd(), "temp_uploads")
    os.makedirs(temp_dir, exist_ok=True)
    
    timestamp = int(time.time())
    unique_filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(temp_dir, unique_filename)
    
    print(f"[Upload] Received PDF upload: {file.filename}, saving as: {unique_filename}")
    
    file_content = await file.read()
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    print(f"[Upload] PDF file saved to: {file_path}")
    
    db_pdf = models.PDFBook(
        filename=file.filename,
        book_reference=book_reference,
        json_content={"status": "processing"},
        user_id=current_user.id
    )
    
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    
    print(f"[Upload] Created new PDF book record with ID: {db_pdf.id}")
    
    if prompt_id:
        prompt = db.query(models.Prompt).filter(
            models.Prompt.id == prompt_id,
            models.Prompt.user_id == current_user.id
        ).first()
        if prompt:
            prompt.pdf_book_id = db_pdf.id
            db.commit()
            print(f"[Upload] Associated PDF with prompt ID: {prompt_id}")
    
    background_tasks.add_task(
        process_pdf_to_json,
        file_path=file_path,
        db_pdf_id=db_pdf.id,
        user_id=current_user.id,
        db=db
    )
    
    print(f"[Upload] Started background task for processing PDF ID: {db_pdf.id}")
    
    return db_pdf

@app.get("/api/pdf-books", response_model=list[schemas.PDFBook])
async def get_pdf_books(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.PDFBook).filter(
        models.PDFBook.user_id == current_user.id
    ).all()

async def process_pdf_to_json(file_path: str, db_pdf_id: int, user_id: int, db: Session):
    try:
        filename = os.path.basename(file_path)
        folder = os.path.dirname(file_path)
        
        print(f"[PDF2JSON] Starting processing for PDF: {filename} (ID: {db_pdf_id})")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise Exception("OpenAI API key not found in environment variables")
        
        print(f"[PDF2JSON] Converting PDF to structured JSON")
        combined_json = pdf_to_json_process(
            filename=filename,
            folder=folder,
            api_key=api_key,
            verbose=True,
            cleanup=True
        )
        
        print(f"[PDF2JSON] Generating dialogs from structured JSON")
        dialogs = process_json_data(combined_json)
        
        print(f"[PDF2JSON] Dialog generation complete, saving to database")
        db_pdf = db.query(models.PDFBook).filter(
            models.PDFBook.id == db_pdf_id,
            models.PDFBook.user_id == user_id
        ).first()
        
        if db_pdf:
            db_pdf.json_content = dialogs
            db.commit()
            print(f"[PDF2JSON] Successfully updated database with dialogs for PDF ID {db_pdf_id}")
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"[PDF2JSON] Temporary PDF file removed: {file_path}")
            except Exception as file_error:
                print(f"[PDF2JSON] Warning: Could not remove temporary PDF file: {str(file_error)}")
            
    except Exception as e:
        print(f"[PDF2JSON] Error processing PDF: {str(e)}")
        db_pdf = db.query(models.PDFBook).filter(
            models.PDFBook.id == db_pdf_id,
            models.PDFBook.user_id == user_id
        ).first()
        
        if db_pdf:
            db_pdf.json_content = {"status": "error", "message": str(e)}
            db.commit()
            print(f"[PDF2JSON] Updated database with error status for PDF ID {db_pdf_id}")
        
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"[PDF2JSON] Temporary PDF file removed after error: {file_path}")
        except Exception as file_error:
            print(f"[PDF2JSON] Warning: Could not remove temporary PDF file: {str(file_error)}")

@app.get("/api/pdf-books/{pdf_id}/status", response_model=dict)
async def get_pdf_book_status(
    pdf_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_pdf = db.query(models.PDFBook).filter(
        models.PDFBook.id == pdf_id,
        models.PDFBook.user_id == current_user.id
    ).first()

    if not db_pdf:
        raise HTTPException(status_code=404, detail="PDF book not found")
    
    if not db_pdf.json_content:
        return {"status": "unknown"}
    
    if isinstance(db_pdf.json_content, dict) and "status" in db_pdf.json_content:
        return {"status": db_pdf.json_content["status"], "message": db_pdf.json_content.get("message", "")}
    
    return {"status": "complete"}

@app.delete("/api/pdf-books/{pdf_id}")
async def delete_pdf_book(
    pdf_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_pdf = db.query(models.PDFBook).filter(
        models.PDFBook.id == pdf_id,
        models.PDFBook.user_id == current_user.id
    ).first()

    if not db_pdf:
        raise HTTPException(status_code=404, detail="PDF book not found")

    prompts = db.query(models.Prompt).filter(models.Prompt.pdf_book_id == pdf_id).all()
    for prompt in prompts:
        prompt.pdf_book_id = None

    db.delete(db_pdf)
    db.commit()

    return {"message": "PDF book deleted successfully"}

@app.post("/api/prompts", response_model=schemas.Prompt)
async def create_prompt(
    prompt: schemas.PromptCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_prompt = models.Prompt(
        name=prompt.name,
        prompt=prompt.prompt,
        user_id=current_user.id,
        pdf_book_id=prompt.pdf_book_id,
        mode=prompt.mode
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@app.put("/api/prompts/{prompt_id}", response_model=schemas.Prompt)
async def update_prompt(
    prompt_id: int,
    prompt_update: schemas.PromptUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_prompt = db.query(models.Prompt).filter(
        models.Prompt.id == prompt_id,
        models.Prompt.user_id == current_user.id
    ).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db_prompt.prompt = prompt_update.prompt
    if prompt_update.mode is not None:
        db_prompt.mode = prompt_update.mode
    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@app.delete("/api/prompts/{prompt_id}")
async def delete_prompt(
    prompt_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_prompt = db.query(models.Prompt).filter(
        models.Prompt.id == prompt_id,
        models.Prompt.user_id == current_user.id
    ).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(db_prompt)
    db.commit()
    return {"message": "Prompt deleted successfully"}

@app.get("/api/history", response_model=list[schemas.History])
async def get_history(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.History).filter(models.History.user_id == current_user.id).all()

@app.post("/notes/", response_model=schemas.Note)
async def create_note(
    note: schemas.NoteCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    db_note = models.Note(
        content=note.content,
        child_name=note.child_name,
        parent_id=current_user.id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/notes/", response_model=list[schemas.Note])
async def read_notes(
    skip: int = 0,
    limit: int = 100,
    child_name: str | None = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(models.Note).filter(models.Note.parent_id == current_user.id)
    if child_name:
        query = query.filter(models.Note.child_name == child_name)
    return query.offset(skip).limit(limit).all()

@app.get("/api/get-json-dialogs")
async def get_json_dialogs(db: Session = Depends(get_db)):
    result = db.query(
        models.Prompt.id.label("prompt_id"),
        models.Prompt.name.label("prompt_name"),
        models.Prompt.prompt.label("prompt_text"),
        models.Prompt.mode.label("prompt_mode"),
        models.PDFBook.id.label("pdf_id"),
        models.PDFBook.book_reference.label("book_reference"),
        models.PDFBook.json_content.label("json_content")
    ).join(
        models.PDFBook, 
        models.Prompt.pdf_book_id == models.PDFBook.id, 
        isouter=True
    ).all()
    
    formatted_data = []
    for row in result:
        item = {
            "prompt": {
                "id": row.prompt_id,
                "name": row.prompt_name,
                "text": row.prompt_text,
                "mode": row.prompt_mode or "chat"
            },
            "pdf_book": None
        }
        
        if row.pdf_id is not None:
            item["pdf_book"] = {
                "id": row.pdf_id,
                "book_reference": row.book_reference,
                "dialogs": row.json_content
            }
        
        formatted_data.append(item)
    
    return {"dialogs": formatted_data} 