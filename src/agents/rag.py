from abc import abstractmethod, ABC
from langchain.chains import RetrievalQA

from src.agents.initializers import llm_0_temp


class BaseRAG(ABC):
    def __init__(self):
        self._db = self._init_db()
        self._retriever = self._db.as_retriever()
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm_0_temp,
            retriever=self._retriever,
            chain_type="stuff",
        )

    @abstractmethod
    def _init_db(self):
        pass

    def answer(self, query: str):
        return self.qa_chain.run(query)
