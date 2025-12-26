from src.database.user_management.password import hash_password, is_correct_password






def test_correct_password():
    '''
        Test scenario for correct password 
    '''



    #dummy password representing a password stored in the user collection
    account_password_string = "Password1!"

    #dummy password representing the string that the user enters when trying to log in
    password_login_input = "Password1!"

    account_hashed_password = hash_password(password_string=account_password_string)

    check_password_bool = is_correct_password(password_string=password_login_input,hashed_password=account_hashed_password)

    assert check_password_bool


def test_incorrect_password():
    '''
        Test scenario for incorrect password 
    '''



    #dummy password representing a password stored in the user collection
    account_password_string = "Password1!"

    #dummy password representing the string that the user enters when trying to log in
    password_login_input = "Password2!"

    account_hashed_password = hash_password(password_string=account_password_string)

    check_password_bool = is_correct_password(password_string=password_login_input,hashed_password=account_hashed_password)

    assert not check_password_bool

