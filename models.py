from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Orders(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True)
    file_type = Column(String(50), primary_key=True)
    mail_date = Column(String(50), nullable=False)
