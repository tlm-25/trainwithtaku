import bcrypt


def hash_password(password_string:str)->bytes:
    '''
    Docstring for hash_password
    
    :param password_string: user's password in raw string format
    :type password_string: str
    :return: hashed_password - byte string for hashed password
    :rtype: bytes
    '''

    password_bytes = password_string.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password_bytes,salt=salt)
    return hashed_password




def is_correct_password(password_string:str,hashed_password:bytes)->bool:
    '''
    Check if user entered correct password when logging in
    Can also be used to verify that a refresh token provided by user matches hashed refrehs token stored in a database (for token refresh or logout)
    
    :param password_string: Password entered by user when logging in
    :type password_string: str
    :param hash_value: Hashed password stored in database
    :type hash_value: bytes
    :return: True or false - whether the hashed user input matches the hashed value stored in the database
    :rtype: bool
    '''

    password_bytes = password_string.encode("utf-8")

    #check  if password is correct
    correct_password_input = bcrypt.checkpw(password=password_bytes,hashed_password=hashed_password)

    if correct_password_input:
        return True
    else:
        return False


