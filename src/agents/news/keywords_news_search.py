from langchain import PromptTemplate, LLMChain
from langchain.output_parsers import CommaSeparatedListOutputParser

from src.agents.initializers import llm_0_temp


class KWGenerator:
    def __init__(self):
        self._prompt_template = \
        """Given the string of user location. Your task is to generate 5-10 keywords/phrases related to the location so that they include region, street, if they are stated. Also include neighboring regions not far away if it is a city. Include city only if the city is small, but include street if found
        {format_instructions}\n\nLocation: {location}"""

        self._parser = CommaSeparatedListOutputParser()
        self._prompt = PromptTemplate(
            template=self._prompt_template,
            input_variables=["location"],
            partial_variables={"format_instructions": self._parser.get_format_instructions()},
        )
        self.chain = LLMChain(llm=llm_0_temp, prompt=self._prompt)

    def generate(self, location):
        generated_str = location
        try:
            generated_str += ',' + self.chain.run(location)
        except:
            pass
        return [kw.strip() for kw in generated_str.split(',')]


key_words_generator = KWGenerator()