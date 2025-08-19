from sqlalchemy.orm import Session
from . import models, schemas

def get_item(db: Session, item_id: int):
    return db.query(models.Item).filter(models.Item.id == item_id).first()

def get_item_by_sku(db: Session, sku: str):
    return db.query(models.Item).filter(models.Item.sku == sku).first()

def list_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(sku=item.sku, name=item.name, quantity=item.quantity, location=item.location)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    obj = get_item(db, item_id)
    if obj:
        db.delete(obj)
        db.commit()
    return obj

def update_item(db: Session, item_id: int, data: schemas.ItemUpdate):
    obj = get_item(db, item_id)
    if not obj:
        return None
    if data.name is not None:
        obj.name = data.name
    if data.quantity is not None:
        obj.quantity = data.quantity
    if data.location is not None:
        obj.location = data.location
    db.commit()
    db.refresh(obj)
    return obj
