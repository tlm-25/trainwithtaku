from src.database.user_management.sign_up_form import validate_email_format, validate_password_format

#test for identifying valid emails
def test_valid_email_format():
    valid_email_1 = "user1@gmail.com"
    valid_email_2 = "firstname.surname@org.gov.uk"
    valid_email_3 = "firstname.surname@org.com"
    is_email1_valid = validate_email_format(valid_email_1)
    is_email2_valid = validate_email_format(valid_email_2)
    is_email3_valid = validate_email_format(valid_email_3)
    assert is_email1_valid
    assert is_email2_valid
    assert is_email3_valid


#test for identifying invalid emails
def test_invalid_email_format():
    invalid_email_1 = "user@@gmail.com"
    invalid_email_2 = "plainaddress"
    invalid_email_3 = "email.example.com"
    invalid_email_4 = "email..email@example.com"
    invalid_email_5 = "email@-example.com"

    is_email1_valid = validate_email_format(invalid_email_1)
    is_email2_valid = validate_email_format(invalid_email_2)
    is_email3_valid = validate_email_format(invalid_email_3)
    is_email4_valid = validate_email_format(invalid_email_4)
    is_email5_valid = validate_email_format(invalid_email_5)

    assert not is_email1_valid
    assert not is_email2_valid
    assert not is_email3_valid
    assert not is_email4_valid
    assert not is_email5_valid

def test_valid_password_format():
    '''
        Test for identifying valid email formats
    
    '''

    valid_password_1 = "Validpassword1!"
    valid_password_2 = "ValidPassword2$"
    valid_password_3 = "valid_Password3"
    valid_password_4 = "VALID_PASSWORd4"

    is_password1_valid = validate_password_format(valid_password_1)
    is_password2_valid = validate_password_format(valid_password_2)
    is_password3_valid = validate_password_format(valid_password_3)
    is_password4_valid = validate_password_format(valid_password_4)

    assert is_password1_valid
    assert is_password2_valid
    assert is_password3_valid
    assert is_password4_valid

def test_invalid_password_format():

    '''
        Test for identifying invalid email formats
    
    '''

    invalid_password_1 = "invalidpassword1" # no capital letters or special characters
    invalid_password_2 = "invalidpassword!" # no numbers or capital letters
    invalid_password_3 = "INVALID_PASSWORD3!" # No lower case letters
    invalid_password_4 = "INVALID_PASSWORD4" # No lower case letters or special characters
    invalid_password_5 = "Invalidpassword5" # No special characters
    invalid_password_6 = "pass6" # less than 8 characters

    #assess the validity of all the password
    is_password1_valid = validate_password_format(invalid_password_1)
    is_password2_valid = validate_password_format(invalid_password_2)
    is_password3_valid = validate_password_format(invalid_password_3)
    is_password4_valid = validate_password_format(invalid_password_4)
    is_password5_valid = validate_password_format(invalid_password_5)
    is_password6_valid = validate_password_format(invalid_password_6)

    #ensure that the validate_password_format function correctly identifies that the passwords are invalid
    assert not is_password1_valid
    assert not is_password2_valid
    assert not is_password3_valid
    assert not is_password4_valid
    assert not is_password5_valid
    assert not is_password6_valid

