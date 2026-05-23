from fastapi import FastAPI
from database import db
from models import Category
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db

app = FastAPI()


@app.post("/categories")
def create_category(data: dict, db: Session = Depends(get_db)):
    category = Category(
        name=data["name"],
        parent_id=data.get("parent_id")
    )

    db.add(category)
    db.commit()

    return {"message": "Category created"}


@app.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()

    return categories