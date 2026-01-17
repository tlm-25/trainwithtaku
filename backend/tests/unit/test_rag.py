


 
from  src.retrieval import format_documents_for_prompt

from langchain.schema import Document






def test_format_documents_for_prompt():
    '''
    Test formatting documents to insert into a prompt
    '''

    documents = [
        Document(page_content="Document 1 content."),
        Document(page_content="Document 2 content."),
        Document(page_content="Document 3 content.")
    ]

    formatted_string = format_documents_for_prompt(documents=documents)

    assert isinstance(formatted_string,str)

    