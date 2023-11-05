# from src.parcers import parcers
# from src.geo import rounting
#
# start = [-1.4071556, 50.9000224] # Leonardo Royal Hotel (30063400)
# end = [-1.3536545, 50.9129596] # April House
# planner = rounting.RoutePlanner(".creds\.osmcredentials")
#
# def get_news_and_warnings() -> parcers.NewsHeap:
#     brave_retriever = parcers.BraveRetriever()
#     news_heap = parcers.NewsHeap(brave_retriever, parcers.get_alert_messages_ukgov)
#     news_heap.parce_news()
#     news_heap.parce_warnings()
#     return news_heap
#
#
# # m = rounting.get_map(planner, start, end, avoid_area_extension_point=None)
# # (-1.4043260, 50.8964265), (-1.3847171, 50.8988538), (-1.3892514, 50.9058438) avoid
#

from flask import Flask

from src.geo.rounting import planner

app = Flask(__name__)

@app.route('/send_message_in_disaster')
def process_message_global_disaster(message: str):
    return

@app.route('/send_message_post_disaster')
def process_message_post_disaster(message: str):
    return


@app.route('/send_message')
def process_message_global(message: str):
    return


@app.route('/')
def init_connections():
    planner.avoid_areas.clear()




if __name__ == '__main__':
    app.run()
