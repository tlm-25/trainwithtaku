import re


def check_valid_url_format(url: str) -> bool:
    '''
        Ensure web URL is in a valid format

        :param url: user input URL string
        :type url: str
        :return: True or False - checking if URL format is valid
        :rtype: bool
    '''
    #Regex expression for validating url format
    regex = ("((http|https)://)(www.)?" + 
             "[a-zA-Z0-9@:%._\\+~#?&//=]" + 
             "{2,256}\\.[a-z]" + 
             "{2,6}\\b([-a-zA-Z0-9@:%" + 
             "._\\+~#?&//=]*)")
    
    # Compile the regex pattern
    pattern = re.compile(regex)


    if (url is None):
        return False
    #if the format is correct, return true
    if(re.search(pattern, url)):
        return True
    else:
        return False

def check_valid_pdf_path_format(pdf_path: str) -> bool:
    '''
        Ensure pdf file path is in a valid format

        :param pdf_path: user input pdf file path string
        :type pdf_path: str
        :return: True or False - checking if pdf file path format is valid
        :rtype: bool
    '''
    pdf_lowercase = pdf_path.lower()
    if pdf_path is None:
        return False
     
    is_valid_pdf_extension = pdf_lowercase.endswith('.pdf')
    if  is_valid_pdf_extension:
        return True
    else:
        return False