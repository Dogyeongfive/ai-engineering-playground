from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str

class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
