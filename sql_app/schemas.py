from pydantic import BaseModel, ConfigDict


class RepairBase(BaseModel):
    manufacturer: str
    model: str
    kind: str
    description: str

class RepairCreate(RepairBase):
    pass


class Repair(RepairBase):
    id: int
    mechanic_id: int | None
    model_config = ConfigDict(from_attributes=True)



class MechanicBase(BaseModel):
    login: str
    first_name: str
    last_name: str

class MechanicCreate(MechanicBase):
    password: str
    is_admin: bool | None

class Mechanic(MechanicBase):
    id: int
    repairs: list[Repair] = []
    model_config = ConfigDict(from_attributes=True)
