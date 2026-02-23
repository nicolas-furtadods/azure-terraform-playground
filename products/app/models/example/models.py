from pydantic import BaseModel

# Declare a model from the BaseModel class
class Item(BaseModel):
    id: int
    name: str
    tags: list[str] = []


# Create a new model that inherits from the Item model
# Reduce duplication:
# https://fastapi.tiangolo.com/tutorial/extra-models/#reduce-duplication
class ItemFull(Item):
    description: str | None = None
    price: float
    tax: float | None = None