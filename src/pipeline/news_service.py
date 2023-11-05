from config import DEFAULT_USER
from dirs import DATA_PATH
from src.agents.news.keywords_news_search import key_words_generator

from src.agents.news.news_classifier import NewsDangerClassifier, DangerStatus
from src.agents.process_global_danger import process_danger
from src.geo.rounting import get_map, start, end, planner, update_m
from src.parcers import parcers
from src.utils.io import read_json
from flashtext import KeywordProcessor
import newspaper

from src.utils.db import user_to_global_status, UserGlobalStatus
from src.utils.utils import are_eps_equal


class DisasterKWNewsDetector:
    def __init__(self):
        self.disaster_kw_detector = self._build_kw_detector()

    def _build_kw_detector(self):
        disaster_kw_detector = KeywordProcessor()
        disaster_kws = read_json(DATA_PATH / 'disaster_keywords.json')
        disaster_kw_detector.add_keywords_from_list(disaster_kws)
        return disaster_kw_detector

    def contains_disaster_kw(self, user_location: str, title: str, text: str):
        location_kw_detector = KeywordProcessor()
        location_kws = key_words_generator.generate(user_location)
        location_kw_detector.add_keywords_from_list(location_kws)
        text_to_search = title + ' || ' + text
        return (len(self.disaster_kw_detector.extract_keywords(text_to_search)) > 0 and
                len(location_kw_detector.extract_keywords(text_to_search)) > 0)


class DisasterNewsDetector:
    def __init__(self):
        self.disaster_kw_detector = DisasterKWNewsDetector()
        self.news_danger_classifier = NewsDangerClassifier()

    def get_news_danger_status(self, user_location, news_article: newspaper.Article):
        if not self.disaster_kw_detector.contains_disaster_kw(user_location, news_article.title, news_article.text):
            return DangerStatus.GREEN_LEVEL
        return self.news_danger_classifier.get_danger_status(user_location, news_article.title, news_article.text)


danger_status_to_global ={
    DangerStatus.YELLOW_LEVEL: UserGlobalStatus.PRE_DISASTER,
    DangerStatus.RED_LEVEL: UserGlobalStatus.IN_DISASTER
}

class NewsProcessor:
    def __init__(self):
        self.disaster_news_detector = DisasterNewsDetector()

    def process_in_ok_pre(self, user, news_article: newspaper.Article):
        news_danger_status = self.disaster_news_detector.get_news_danger_status(user_to_global_status[user]['location'],
                                                                                news_article)
        response = None
        if news_danger_status != DangerStatus.GREEN_LEVEL:
            user_to_global_status[user]['status'] = danger_status_to_global[news_danger_status]
            response = process_danger(user, news_article.title, news_article.text, news_danger_status)
        return response

    def process_in_disaster(self, user, news_article: newspaper.Article):
        if 'Itchen Toll Bridge is under water' not in news_article.text:
            return None
        _, old_route_stats = get_map(start, end, return_summary=True)
        planner.add_avoid_area((-1.380651, 50.896138), scale_hundred_m=1)
        route = planner.get_route(start, end)
        update_m(planner, route)
        _, new_route_stats = get_map(start, end, return_summary=True)
        if are_eps_equal(old_route_stats['distance'], new_route_stats['distance'], 0.1) and \
                old_route_stats['segments_num'] == new_route_stats['segments_num']:
            return None
        return 'Attention! There Itchen Toll Bridge is closed, since it got under water'
        # planner.add_avoid_area((-1.378108, 50.893093), scale_hundred_m=0.5)
        # route = planner.get_route(start, end)
        # m = planner.create_map(route, start, end)

    def process_news(self, user, news_article: newspaper.Article):
        user_status = user_to_global_status[user]['status']
        response = None
        if user_status in [UserGlobalStatus.OK, UserGlobalStatus.PRE_DISASTER]:
            response = self.process_in_ok_pre(user, news_article)
        elif user_status == UserGlobalStatus.IN_DISASTER:
            # response = process_danger(user, news_article.title, news_article.text, DangerStatus.RED_LEVEL)
            response = self.process_in_disaster(user, news_article)
        elif user_status == UserGlobalStatus.POST_DISASTER:
            pass
        return response


news_processor = NewsProcessor()

def get_news_and_warnings() -> parcers.NewsHeap:
    brave_retriever = parcers.BraveRetriever()
    news_heap = parcers.NewsHeap(brave_retriever, parcers.get_alert_messages_ukgov)
    news_heap.parce_news()
    news_heap.parce_warnings()
    return news_heap


def get_news_in_cycle():
    while True:
        news_heap = get_news_and_warnings()
        for _ in range(len(news_heap.heap)):
            news_article = news_heap.heappop()
            news_processor.process_news(DEFAULT_USER, news_article)