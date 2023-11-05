from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dirs import DATA_PATH
from langchain.document_loaders import PyPDFLoader

from src.agents.rag import BaseRAG


class PostDangerProcessorQA(BaseRAG):
    def _init_db(self, is_initialized=True):
        if not is_initialized:
            document_loader = PyPDFLoader(file_path=str(DATA_PATH / 'Spain_recovery.pdf'))
            pages = document_loader.load_and_split()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
            docs = text_splitter.create_documents([page.page_content for page in pages])

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        # create Deep Lake dataset
        my_activeloop_org_id = "nseverin14"
        my_activeloop_dataset_name = "es-book-embeddings-new"
        dataset_path = f"hub://{my_activeloop_org_id}/{my_activeloop_dataset_name}"
        db = DeepLake(dataset_path=dataset_path, embedding_function=embeddings, overwrite=False)

        if not is_initialized:
            db.add_documents(docs)

        return db
