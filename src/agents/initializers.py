from dotenv import load_dotenv
from langchain.chat_models import ChatAnthropic
from langchain.utilities import SerpAPIWrapper, BraveSearchWrapper
import os

from dirs import ENV_FILE

load_dotenv(str(ENV_FILE))

llm_0_temp = ChatAnthropic(api_key=os.environ['ANTHROPIC_API_KEY'], temperature=0)
brave_search = BraveSearchWrapper(api_key=os.environ['BRAVE_API_KEY'])
