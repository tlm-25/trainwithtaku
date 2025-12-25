from validators import email
import logging
import jwt 
import re



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

        Arg(s):

            password (str) - user input in password field
            confirm_password (str) - user input in 'confirm password' field
    
    '''


    if password == confirm_password:
        logging.info("'password' and 'confirm password' fields match")
        print("'password' and 'confirm password' fields match")
        return True
    else:
        logging.info("'password' and 'confirm password' fields do not match")
        print("'password' and 'confirm password' fields do not match")
        return False




#Check if user exists in database



#handle 'forgot your password' - send user an email



#confirm user email with security code