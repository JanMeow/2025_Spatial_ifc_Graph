from sqlalchemy.orm import Session
from database.core import engine, text

session = Session(engine)
session.execute(text("INSERT INTO buildups (name, description) VALUES ('Test', 'Test')"))