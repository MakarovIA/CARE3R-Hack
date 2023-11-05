from enum import Enum

from langchain import PromptTemplate, LLMChain

from src.agents.initializers import llm_0_temp


class DangerStatus(Enum):
    GREEN_LEVEL = 'GREEN_LEVEL'
    YELLOW_LEVEL = 'YELLOW_LEVEL'
    RED_LEVEL = 'RED_LEVEL'


class NewsDangerClassifier:
    def __init__(self):
        self._prompt_template = """Given the piece of news (title, text) that may be related to some kind of disaster. Based on the news and person location, your task is to classify the news into 3 classes:
        * GREEN_LEVEL - there is no real disaster in the news piece or the disaster is far away and can't affect the person;
        * YELLOW_LEVEL - the disaster may affect person, but it is still very unclear, but it's better for the person to start preparing;
        * RED_LEVEL - emergency, the disaster is very likely to affect the person, he/she needs to do something serious.

        Person location: {location}
        News title: {title}
        News text: {text}

        Answer ONLY with the class of the news"""
        self._prompt = PromptTemplate(
            template=self._prompt_template,
            input_variables=["location", "title", "text"],
        )
        self.chain = LLMChain(llm=llm_0_temp, prompt=self._prompt)

    def get_danger_status(self, user_location, title, text):
        status_str = self.chain.run(location=user_location, title=title, text=text).strip()
        if status_str == DangerStatus.RED_LEVEL:
            return DangerStatus.RED_LEVEL
        if status_str == DangerStatus.YELLOW_LEVEL:
            return DangerStatus.YELLOW_LEVEL
        return DangerStatus.GREEN_LEVEL
