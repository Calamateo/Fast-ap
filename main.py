#Python
from typing import Optional
from enum import Enum 

#Pydantic
from pydantic import BaseModel, EmailStr
from pydantic import Field 

#FastAPI
from fastapi import FastAPI, File, Form, Header, Path, Query, Cookie, UploadFile
from fastapi import Body, status
from fastapi import HTTPException

app = FastAPI()	

#Models

class HairColor(Enum):
    white = "white"
    brown = "brown"
    black = "black"
    blonde = "blonde"
    red = "red"

class Location(BaseModel):
    cit: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="Tlaquepaque"
    )
    state: str = Field(
        ..., 
        min_length=1,
        max_length=50,
        example="Jalisco"
        )
    country: str = Field(
        ..., 
        min_length=1,
        max_length=50,
        example="México"
        )

class PersonBase(BaseModel):
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        )
    age: int = Field(
        ...,
        gt=0,
        le=115,
        )
    hair_color: Optional[HairColor] = Field(default=None)
    is_married: Optional[bool] = Field(default=None)

    class Config:
        schema_extra = {
            "example": {
                "first_name": "Daniel",
                "last_name": "Calamateo",
                "age": 28,
                "hair_color": "black",
                "is_married": False,
                "password": "123456789"
            }
        }

class Person(PersonBase):
    password: str = Field(
        ...,
        min_length=8
        )

class PersonOut(PersonBase):
    pass

class LoginOut(BaseModel):
    username: str = Field(
        ...,
        max_length=20,
        example="Calamateo"
    )
    message: str = Field(
        default="Login Successfully"
    )

@app.get(
    path='/', 
    status_code=status.HTTP_200_OK,
    tags=["Home"]
    )
def home():
    return{"Hello": "world"}

# Request and Response body

@app.post(
    path='/person/new', 
    response_model=PersonOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Persons"],
    summary="Crate person in the app"
    )
def create_person(person: Person = Body(...)):
    """
    Crate Person
    
    This path operation creates a person in the app and save the information in the database

    Parameters:
    - Request body parameters:
        - **person: person** -> A person model with fist name, last name, age, hair color and marital status
        
    Returns a person model with the information fist name, last name, age, hair color and marital status
    """
    return person


#Validation query parameters

@app.get(
    path='/person/detail',
    status_code=status.HTTP_200_OK,
    tags=["Persons"],
    deprecated= True     
    )
def show_person(
    name: Optional[str] = Query(
        None,
        min_length = 1,
        max_length = 50,
        title="Person Name",
        description="this is the Person Name. It's between 1 and 50 characters",
        example="Gabriela"
        ),
    age: str = Query(
        ...,
        title="Person Age",
        description="This is the person age. It's requied",
        example="28",
        ) 
):
    return {name: age}

#VAlidation path parameters

persons = [1,2,3,4,5]

@app.get(
    path='/person/detail/{person_id}',
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
    )
def show_person(
    person_id: int = Path(
        ...,
        gt=0,
        title="Person Id",
        description="This is the person id. It's requied and is greater than 0",
        example=123
        )
):
    if person_id not in persons:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This person does not exist"
        )
    return {person_id: "It exists"}

#Validation Request body 

@app.put(
    path='/person/{person_id}',
    status_code=status.HTTP_200_OK,
    tags=["Persons"]
    )
def update_person(
    person_id: int = Path(
        ...,
        title="Person Id",
        description="This is the person id. It's requied and is greater than 0",
        gt=0,
        example=123
    ),
    person: Person = Body(...),
    location: Location = Body(...)
):
    results = person.dict()
    results.update(location.dict())
    return results

#Forms

@app.post(
    path='/login',
    response_model=LoginOut,
    status_code=status.HTTP_200_OK,
    tags=["Login"]
)    
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    return LoginOut(username=username)

#Cookies and headers parameters

@app.post(
    path='/contact',
    status_code=status.HTTP_200_OK,
    tags=["Contact"]
)
def contact(
    first_name: str = Form(
        ...,
        min_length=1,
        max_length=20,
        ),    
    last_name: str = Form(
        ...,
        min_length=1,
        max_length=20,
    ),
    email: EmailStr = Form(
        ...
    ),
    user_agent: Optional[str] = Header(default=None),
    ads: Optional[str] = Cookie(default=None)
):
    return user_agent


#Files

@app.post(
    path="/post-image",
    tags=["Files"]
)
def post_image(
    image: UploadFile = File(...)
):
    return {
        "Filename": image.filename,
        "Format": image.content_type,
        "Size(kb)": round(len(image.file.read())/1024, ndigits=2),
    }