


 
from  src.search.retrieval import format_documents_for_prompt
import logging
from langchain.schema import Document






def test_format_documents_for_prompt():
    '''
    Test formatting documents to insert into a prompt
    '''

    documents = [
        Document(page_content="Document 1 content.",metadata={"source": "https://example.com"}),
        Document(page_content="Document 2 content.",metadata={"source": "https://example2.com"}),
        Document(page_content="Document 3 content.",metadata={"source": "https://example3.com"})
    ]

    formatted_string = format_documents_for_prompt(documents=documents)
    logging.info(formatted_string)

    assert isinstance(formatted_string,str)

    