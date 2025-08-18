from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from . import models, schemas, crud

app = FastAPI(title="Inventory API", version="1.0.0")

# Auto-create tables (demo; use Alembic in prod)
Base.metadata.create_all(bind=engine)

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/items", response_model=list[schemas.ItemRead])
def list_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_items(db, skip, limit)

@app.post("/items", response_model=schemas.ItemRead, status_code=201)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    existing = crud.get_item_by_sku(db, item.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")
    return crud.create_item(db, item)

@app.get("/items/{item_id}", response_model=schemas.ItemRead)
def get_item(item_id: int, db: Session = Depends(get_db)):
    obj = crud.get_item(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj

@app.put("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(item_id: int, data: schemas.ItemUpdate, db: Session = Depends(get_db)):
    obj = crud.update_item(db, item_id, data)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return obj

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    obj = crud.delete_item(db, item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return None
