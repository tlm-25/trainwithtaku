from src.database.vector_store import generate_documents
from src.database.document_source_validation import check_valid_url_format, check_valid_pdf_path_format
from langchain.schema import Document


def test_validate_document_source():
    '''
        Test for validating document source input
    '''
    valid_source_web = "https://www.google.com/"
    valid_source_pdf = "src/pdf_docs/document.pdf"
    invalid_source_web = "htps://www.google.com"
    invalid_source_pdf = "src/text_docs/document.txt"
    
    assert check_valid_url_format(url=valid_source_web)
    assert check_valid_pdf_path_format(pdf_path=valid_source_pdf)
    
    assert not check_valid_url_format(url=invalid_source_web)
    assert not check_valid_pdf_path_format(pdf_path=invalid_source_pdf)


    
# def test_success_generate_web_docs():
#     '''
#         Test for successful generation of documents from a web page
#     '''
#     url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
#     source = "web"
#     documents = generate_documents(source=source,url=url)
#     assert len(documents) > 0
#     assert isinstance(documents,list[Document])


