from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .database import Base

class Mechanic(Base):
    __tablename__ = "mechanics"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, unique = True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)

    repairs = relationship("Repair", back_populates="mechanic")


class Repair(Base):
    __tablename__ = "repairs"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String)
    model = Column(String)
    kind = Column(String)
    description = Column(String)
    mechanic_id = Column(Integer, ForeignKey("mechanics.id"))


    mechanic = relationship("Mechanic", back_populates="repairs")

