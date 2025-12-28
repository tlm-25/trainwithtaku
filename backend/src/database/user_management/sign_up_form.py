from validators import email
import logging
import jwt 
import re
from pymongo.asynchronous.collection import AsyncCollection

from src.database.user_management.utils import check_if_email_already_in_use

# make sure email address is valid - email being used as username
def validate_email_format(email_address:str)->bool:
    '''
        Ensure email is a valid format

        Arg(s):
            email_adresss(str) - email address that the user attempts to use
        
        Returns:
            bool - Return true if email is in a valid format, otherwise returns false
    
    '''
    #check if email is in a valid format
    is_email_valid_format = email(email_address.strip())

    if is_email_valid_format:
        print("email is valid")
        logging.info("email is valid")
    else:
        print("email is invalid")
        logging.info("email is invalid")

    return is_email_valid_format


#TODO 

#check if email already exists


def validate_password_format(password:str)->bool:
    '''
        Ensure that the password is valid. 
        It must meet the following conditions:
           
             - A minimum of 8 characters
             - At least 1 numeric character
             - Contain capital letters and lower case letters
             - Contain at least 1 special character
        
        Arg(s):
            - password (str): user's input into the 'password' input field
        
        Return(s):
            - bool: Returns true if password format is valid
        
    '''
    #check if password is at least 8 characters
    password_minimum_8_characters = (len(password) >=8)

    #password contains at least 1 number
    password_contains_number = any(char.isdigit() for char in password)

    #password contains at least one capital letter
    password_contains_capital_letter = any(char.isupper() for char in password)

    #password contains at least one lower case letter
    password_contains_lowercase_letter = any(char.islower() for char in password)

    #check if password has least 1 special character
    password_contains_special_character = any(not char.isalnum() for char in password)

    #check that all conditions are met
    is_password_valid = password_minimum_8_characters and password_contains_number and password_contains_capital_letter and password_contains_special_character and password_contains_lowercase_letter

    return is_password_valid



def check_if_passwords_match(password:str,confirm_password:str)->bool:
    '''
        Ensure that the 'password' and 'confirm password' fields match

            :param password: user input in password field
            :type password: str
            :param confirm_password: user input in 'confirm password' field
            :type confirm_password: str
            :return: True or False - checking if passwords match
            :rtype: bool


    
    '''


    if password == confirm_password:
        logging.info("'password' and 'confirm password' fields match")
        print("'password' and 'confirm password' fields match")
        return True
    else:
        logging.info("'password' and 'confirm password' fields do not match")
        print("'password' and 'confirm password' fields do not match")
        return False




async def validate_input_form(email_input:str,password_input:str,confirm_password_input:str,collection:AsyncCollection)->tuple[bool,str]:
    #list to store any error messages relating to incorrect formatting of the input fields
    input_format_error_messages = []


    
    #check that email does not already exist

    #check that email is valid format
    is_email_valid_format = validate_email_format(email_address=email_input)

    if not is_email_valid_format:
        input_format_error_messages.append("Email format invalid")
    
    email_already_in_use = await check_if_email_already_in_use(email_input=email_input,collection=collection)
    
    if email_already_in_use:
        input_format_error_messages.append(f"The email address '{email_input}' is already in use. If it is your account, please sign in, or use a different email")
        

    

    #check that password is valid format
    is_password_valid_format = validate_password_format(password=password_input)

    if not is_password_valid_format:
        input_format_error_messages.append(f"Password is not valid format. It must contain:\n 1. lowercase and uppercase letters\n 2. At least 8 characters\n 3. at least one number\n 4. At least 1 special character")


    #check that password matches 
    password_fields_match_match = check_if_passwords_match(password=password_input,confirm_password=confirm_password_input)

    if not password_fields_match_match:
        input_format_error_messages.append(f"'Password' and 'Confirm Password' fields do not match")

    input_format_error_messages_string = " | ".join(input_format_error_messages)


    all_user_inputs_formats_valid = is_email_valid_format and (not email_already_in_use) and is_password_valid_format and password_fields_match_match

    if all_user_inputs_formats_valid:

        logging.info("Successfully added new user")

        return True, "Successfully added new user"
    
    else:
        logging.info(f"Failed to add new user: {input_format_error_messages_string}")
        return False, input_format_error_messages_string
    


#Check if user exists in database



#confirm user email with security code