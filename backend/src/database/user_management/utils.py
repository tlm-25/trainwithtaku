from pymongo.asynchronous.collection import AsyncCollection
async def check_if_email_already_in_use(email_input:str,collection:AsyncCollection)->bool:
    '''
    Check if an email is alreadu in use check_if_email_already_in_use
    
    :param email_input: Email input value
    :type email_input: str
    :param collection: Description
    :type collection: AsyncCollection
    :return: True/False
    :rtype: bool
    '''
    #check if email already in use - only return value the default "_id" field, not the other fields (save memory) 
    is_email_already_in_use = await collection.find_one(filter={"email":email_input},projection={"_id":True})
    #if email is already in 
    if is_email_already_in_use:
        return True
    else:
        return False
