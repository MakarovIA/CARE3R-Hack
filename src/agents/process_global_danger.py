from typing import Type, Optional

from langchain.agents import initialize_agent, AgentType
from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.prompts import PromptTemplate
from langchain.tools import Tool, BaseTool
from pydantic import Field, BaseModel

from src.agents.initializers import llm_0_temp
from src.agents.news.news_classifier import DangerStatus

from langchain_experimental.smart_llm import SmartLLMChain
from langchain.memory import ConversationBufferMemory
from src.utils.db import user_to_global_status, UserGlobalStatus

global_status_to_danger ={
    UserGlobalStatus.PRE_DISASTER: DangerStatus.YELLOW_LEVEL,
    UserGlobalStatus.IN_DISASTER: DangerStatus.RED_LEVEL,
    UserGlobalStatus.OK: DangerStatus.GREEN_LEVEL,
}


def build_first_decision_tool():
    prompt_template = \
        """
        You are an assistant in YELLOW_LEVEL and RED_LEVEL (these are informal levels based on some estimations) emergency situations. The user location will be given to you, so assume it is known. Your task is:
        1. Explain the situation to a person without causing panic as the person hears about it for the first time. Be clear and supportive.
        2.1. If the level of danger is YELLOW_LEVEL, you need to tell person how to prepare as best as they can, but without causing panic. 
        2.2. If the level of danger is RED_LEVEL, you need to make plan for person how to act to save their lives (probably, they just need to stay at the same place or go to some shelter). If you suggest evacuation, you should say where to go, if there are some suggestions in the text
        You will be given:
        - history of chat with user regarding to the disaster (if there is any history)
        - the news with information about the disaster and location of the person. Your recommendations must be clear, remember people's lives may be at stake.

        CURRENT SITUATION:
        {human_input}

        Your response should be human-like, but don't imagine anything.
        """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["chat_history", "human_input"],
    )
    chain = SmartLLMChain(llm=llm_0_temp, prompt=prompt, n_ideas=1, verbose=True)
    return Tool.from_function(
            func=chain.run,
            name="Plan",
            description="useful for planning what to do during disaster for the first time",
        )


def build_change_react_decision_tool():
    prompt_template = \
        """
        You are an assistant in serious emergency situations. The user location will be given to you, so assume it is known. Your task is:
        1. Make decision what to do next, based on incoming information. Possibly, the person have to be evacuated. But in this case you should suggest location, if your sources or input say something about it.
        You are given:
        - history of chat with user regarding to the disaster (if there is any history)
        - the news with information about the disaster and location of the person. Your recommendations must be clear, remember people's lives may be at stake.

        CURRENT SITUATION:
        {human_input}

        Your response should be human-like, but don't imagine anything.
        """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["chat_history", "human_input"],
    )
    chain = SmartLLMChain(llm=llm_0_temp, prompt=prompt, n_ideas=1, verbose=True)
    return Tool.from_function(
            func=chain.run,
            name="Plan_Consideration",
            description="useful for reconsidering plan based on new observation of news",
        )

class DangerProcessor:
    def __init__(self):
        self._tools = [build_first_decision_tool(), build_change_react_decision_tool()]
        memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = initialize_agent(tools=self._tools, llm=llm_0_temp, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                      verbose=True, memory=memory)

    def generate_response(self, user_location, title, text, danger_level):
        human_input = \
            """Person current location: {location}
            News title: {title}
            News text: {text}
            Level of danger: {danger_level}
            What should I (person) do?""".format(location=user_location, title=title, text=text,
                                                      danger_level=danger_level)
        return self.agent.run(human_input)


user_to_danger_processor = {}


def process_danger(user, title, text, news_danger_status: Optional[DangerStatus] = None):
    if news_danger_status is None:
        news_danger_status = global_status_to_danger[user_to_global_status[user]]
    if user not in user_to_danger_processor:
        user_to_danger_processor[user] = DangerProcessor()
    response_desc_with_plan = \
        user_to_danger_processor[user](user_to_global_status[user]['location'], title, text, news_danger_status.value)
    return response_desc_with_plan
