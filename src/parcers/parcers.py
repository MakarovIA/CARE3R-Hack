import random
from dataclasses import dataclass

from bs4 import BeautifulSoup
import requests
from requests.structures import CaseInsensitiveDict
from newspaper import Article, ArticleException
import heapq

from config import MOCK

MOCK_MSG_DANGER = """Immediate Action Required

The Environment Agency has issued a flood warning for Southampton as water levels are rising rapidly after consistent heavy rainfall. This is expected to continue and poses significant flooding risks to the area.

Residents along the riverside near the River Itchen and River Test should be on high alert, especially in neighbourhoods such as St Denys, Northam, and Bitterne Park. Those in coastal regions near Southampton Water, including the docks and parts of Woolston and Sholing, are also at risk, as are those close to flood plains near smaller streams and brooks within the Southampton urban area.

You are strongly advised to evacuate if instructed by emergency services and to do so without delay. It is also crucial to avoid all travel; driving or walking through floodwaters is extremely dangerous. Take immediate steps to protect your property by moving valuable items to a higher level and using sandbags to block doorways if you have them.

Stay informed by keeping an eye on local news and weather updates, and make sure to monitor the official Environment Agency flood warning information. Prepare a flood kit with essential items like a torch, a fully charged mobile phone, warm clothing, and necessary medication.

Do check on neighbours, especially the vulnerable, to ensure they are aware of the flood warning and are taking necessary measures.

In case of life-threatening emergencies, call 999. For other assistance and information, you can reach out to the local council or contact the Environment Agency's Floodline. Details regarding temporary shelters for those displaced will be provided through local media and official communication channels.

Once the floodwaters have receded, do not return to your premises until it is declared safe by the authorities, and be cautious of residual risks such as contaminated water and damaged infrastructure.

Your safety is paramount. Adhere strictly to the guidelines provided by officials and emergency responders.

For ongoing updates, please refer to the official government website or follow our social media channels.
"""


MOCK_MSG_INIT = """Residents and authorities in Southampton are closely monitoring a concerning development as water levels in the city have started to rise. The increase in water levels is causing alarm among the local population and officials, as it poses potential risks to low-lying areas, infrastructure, and the overall safety of the community.
"""

MOCK_NEWS_CLOSE = """Breaking news: Itchen Toll Bridge is under water"""



def loc_and_msg_to_article(where, what):
    art = Article('')
    art.title = where + ' - government warning system'
    art.text = what
    return art

def get_alert_messages_ukgov():
    url = 'https://www.gov.uk/alerts/past-alerts'
    # Send a GET request to the webpage
    response = requests.get(url)
    
    # List to hold the extracted messages
    alert_messages = []

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all div elements with class 'alerts-icon__container alerts-icon__container--48'
        div_elements = soup.find_all('div', class_='alerts-icon__container alerts-icon__container--48')
        
        for div in div_elements:
            # Extract the text from each div element and add it to the list
            msg = div.get_text(separator='\n', strip=True)
            where = msg.split("\n")[1]
            what = '\n'.join(msg.split("\n")[2:])
            alert_messages.append(loc_and_msg_to_article(where, what))

    else:
        print(f"Failed to retrieve the webpage. Status Code: {response.status_code}")
    if MOCK:
        i = random.randint(0, len(alert_messages)//2-1)
        alert_messages.insert(i, loc_and_msg_to_article("Southampton", MOCK_MSG_INIT))
        i = random.randint(i+1, len(alert_messages)-2)
        alert_messages.insert(i, loc_and_msg_to_article("Southampton", MOCK_MSG_DANGER))
        i = random.randint(i+1, len(alert_messages)-1)
        alert_messages.insert(i, loc_and_msg_to_article("Southampton", MOCK_NEWS_CLOSE))
    return alert_messages


class BraveRetriever:
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, credentials_path=".creds/.credentials"):
        self.headers = self._initialize_headers(credentials_path)
        
    def _initialize_headers(self, credentials_path):
        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Accept-Encoding"] = "gzip"
        
        with open(credentials_path, "r") as f:
            headers["X-Subscription-Token"] = f.read()
            
        return headers

    def get_articles_from_urls(self, urls):
        articles = []
        exceptions_counter = 0
        for url in urls:
            article = Article(url)
            try:
                article.download()
                article.parse()
                articles.append(article)
            except ArticleException:
                exceptions_counter += 1
        out = {
            "articles": articles,
            "total_articles": len(urls),
            "exceptions_counter": exceptions_counter,
        }
        return out

    def retrieve_news(self, request, count=10):
        params = {
            "q": request,
            "count": count,
            "country": "GB",
            "search_lang": "en",
            "spellcheck": 1,
            "freshness": "pd"
        }
        response = requests.get(f"{self.BASE_URL}/news/search",
                                headers=self.headers, params=params) 
        return response.json()

    def parce_news(self, response):
        urls = [result["url"] for result in response["results"]]
        return self.get_articles_from_urls(urls)

    def search(self, request, count=10):
        params = {
            "q": request,
            "country": "ES",
            "count": count
        }
        response = requests.get(f"{self.BASE_URL}/web/search",
                                headers=self.headers, params=params)
        return self._parse_search_results(response.json())

    def _parse_search_results(self, data):
        short_results = []
        for result in data["web"]["results"]:
            content_type = result.get("content_type", "web_page")
            short_results.append((content_type, result["description"], result["url"]))
        return short_results

class ComparableWrapper:
    def __init__(self, priority, item):
        self.priority = priority
        self.item = item
    
    def __lt__(self, other):
        return self.priority < other.priority
    
    def __eq__(self, other):
        return self.priority == other.priority

    # You can also implement other comparison methods if needed (__le__, __gt__, __ge__, etc.)

class NewsHeap:
    def __init__(self, news_retreiver, warnings_retreiver) -> None:
        self.heap = []
        self.news_retreiver = news_retreiver
        self.warnings_retreiver = warnings_retreiver
    
    def parce_news(self, request="Natural disasters in Southhampton"):
        result = self.news_retreiver.retrieve_news(request, count=5)
        news = self.news_retreiver.parce_news(result)
        for art in news["articles"]:
            heapq.heappush(self.heap, ComparableWrapper(3, art))

    def parce_warnings(self, request=None):
        result = self.warnings_retreiver()
        for art in result:
            heapq.heappush(self.heap, ComparableWrapper(1, art))

    def heappop(self):
        return heapq.heappop(self.heap).item

# brave_retriever = parcers.BraveRetriever()
# news_heap = parcers.NewsHeap(brave_retriever, parcers.get_alert_messages_ukgov)
# news_heap.parce_news()