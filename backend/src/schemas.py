from pydantic import BaseModel

from typing import List, Optional

#data structure for user query - data structure expecting a string - data validation 
#could use plain dict, however losing that data validation aspect (if data missing, throws back 422 error)
class Message(BaseModel):
    message: str



class ClientForm(BaseModel):
    '''
        Client information
    '''
    email: str
    age: int
    gender: str
    current_bodyweight_kg: float
    goal_bodyweight_kg: Optional[float]=None
    injuries:str
    height_cm:int
    primary_fitness_goal:str
    current_activity_level:str
    equipment_available:str
    preferred_location:str
    current_occupation:str
    preferred_no_meals:int
    allergies:str
    dietary_restrictions:str
    preferred_foods: str
    food_dislikes:Optional[str]=None
    preferred_cultural_cuisines: Optional[str]=None
    days_available_to_train_per_week:int
    liked_exercises:Optional[str]=None
    disliked_exercises:Optional[str]=None
    
    




class ChatHistoryRequest(BaseModel):
    conversation_id:str 


class ClientNutritionRequirements(BaseModel):
    total_kcal: int   
    total_carbohydrates_grams: float
    total_protein_grams: float
    total_fat_grams: float
    min_fibre_grams: float
    max_saturated_fat_grams:float
    



class MealNutrients(BaseModel):
    '''
        Structure for displaying calories, macronutrients, and fibre in a meal
    '''

    total_kcal: int   
    total_carbohydrates_grams: float
    total_protein_grams: float
    total_fat_grams: float
    total_fibre_grams: float
    saturated_fat_grams:float

#standardised food fats for a food per 100 grams 
class FoodStats(BaseModel):
    kcal_per_100g: float
    carbs_g_per_100g:float
    protein_g_per_100g: float
    fat_g_per_100g: float
    saturated_fat_g_per_100g: float
    fibre_g_per_100g: float

    

class UserSignUpForm(BaseModel):
    email:str
    password:str
    user_type:str
    confirm_password:str

class UserLoginForm(BaseModel):
    email:str
    password:str

class ChatMessage(BaseModel):
    message:str
    type:str
    timestamp:str


class Conversation(BaseModel):
    conversation_id:str
    messages:list[ChatMessage]
    email:str

class ChatRequest(BaseModel):
    user_message:ChatMessage
    chat_history:list[ChatMessage]
    # client form
    client_form:ClientForm|None=None
    conversation_id:str

    
class UserEmail(BaseModel):
    email:str

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    email:str
    user_type:str
    disabled: bool | None = None



class UserInDB(User):
    '''
    Output schema when retrieving user info (excludes hashed password)
    '''
    password:str
    refresh_token: Optional[str] = None

class RefreshTokenREquest(BaseModel):
    refresh_token:str
