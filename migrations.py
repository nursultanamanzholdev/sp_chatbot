from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, User, Prompt, History
from database import SQLALCHEMY_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def migrate():
    with engine.connect() as connection:
        connection.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
        """))
        
        connection.execute(text("""
            ALTER TABLE prompts 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE;
        """))
        
        connection.execute(text("""
            ALTER TABLE history 
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        """))
        
        connection.commit()

if __name__ == "__main__":
    init_db()
    migrate()
    print("Database tables created and migration completed successfully!") 