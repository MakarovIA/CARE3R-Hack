from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import DeepLake
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dirs import DATA_PATH
from langchain.document_loaders import TextLoader
import os

from src.agents.rag import BaseRAG


class LocalDangerProcessorQA(BaseRAG):
    def _init_db(self, is_initialized=True):
        if not is_initialized:
            file_content_list = []
            for fname in os.listdir(DATA_PATH / 'knowledge_base'):
                file_content_list.append(
                    TextLoader(file_path=str(DATA_PATH / 'knowledge_base' / fname)).load()[0].page_content)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=30)
            docs = text_splitter.create_documents(file_content_list)

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        # create Deep Lake dataset
        my_activeloop_org_id = "nseverin14"
        my_activeloop_dataset_name = "danger-knowledge-embeddings"
        dataset_path = f"hub://{my_activeloop_org_id}/{my_activeloop_dataset_name}"
        db = DeepLake(dataset_path=dataset_path, embedding_function=embeddings, overwrite=False)

        if not is_initialized:
            db.add_documents(docs)

        return db