import requests
import urllib
from bs4 import BeautifulSoup
from requests_futures import sessions
import string
from better_profanity import profanity
from youtube_transcript_api import YouTubeTranscriptApi
import time

class YouTuber:

    def __init__(self, name):
        self.name = name
        self.main_channel_link = None
        self.main_channel_html = None
        self.subscribers = 0
        self.bad_words = 0
        self.session = sessions.FuturesSession(max_workers=10)

    """Takes in the url and returns the html file"""
    # str --> str
    def get_parsed_html(self, url):
        # handle and raise exceptions
        try:
            response = self.session.get(url)
            soup = BeautifulSoup(response.result().text, "html.parser")
            return soup
        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            print("Request timed out")
            raise requests.exceptions.Timeout
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            print("Error getting request, bad URL")
            raise requests.exceptions.TooManyRedirects
        except requests.exceptions.MissingSchema:
            print("Bad URL")
            raise requests.exceptions.MissingSchema
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            raise SystemExit(e)

    """Takes the parsed html file and returns all possible youtube links in a list"""
    # --> list(str)
    def get_youtube_links(self, parsed_html):
        all_a_tags = parsed_html.findAll("a")
        all_links = []
        link_count = 0
        for i in range(len(all_a_tags)):
            url = all_a_tags[i]["href"][1:4]
            if link_count < 5 and url == "url" and all_a_tags[i]["href"].find("youtube") != -1:
                index_of_and = all_a_tags[i]["href"].find("&")
                all_links.append(all_a_tags[i]["href"][7:index_of_and])
                link_count += 1
        return all_links

    """Takes in all youtube_links and returns the correct one with most subscribers"""
    # str --> (int, str)
    def find_correct_link(self, youtube_links):
        start = time.time()
        most_subs = 0
        link_with_most_subs = ""
        for i in range(len(youtube_links)):
            try:
                soup = self.get_parsed_html(youtube_links[i])
            except Exception as e:
                raise e
            subscriber_tag = soup.find("span", {
                "class": "yt-subscription-button-subscriber-count-branded-horizontal subscribed yt-uix-tooltip"})
            if subscriber_tag is not None:
                subscriber_count = subscriber_tag.text
                parsed_number = self.parse_number(subscriber_count)
                if parsed_number > most_subs:
                    most_subs = parsed_number
                    link_with_most_subs = youtube_links[i]

        self.main_channel_link = self.upload_page(link_with_most_subs)
        try:
            self.main_channel_html = self.get_parsed_html(self.main_channel_link)
        except Exception as e:
            raise e
        end = time.time()
        print("TIME FOR LINK: " + str(end - start))
        self.subscribers = most_subs

    """Takes in a number as a string with commas and returns a new number(int) with commas removed"""
    # str --> int
    def parse_number(self, number):
        final_number = ""
        multiplier = {"K": 1000, "M": 1000000}
        multiply = 1
        for i in number:
            if i in string.ascii_uppercase:
                multiply = multiplier[i] # integer
                break
            final_number += i
        # print(float(final_number) * multiply)
        return float(final_number) * multiply

    """Takes in the channel link and returns a link to the upload page"""
    # str --> str
    def upload_page(self, youtube_link):
        addition = "videos?view=0&flow=grid"
        find_channel = youtube_link.find("channel")
        new_index = find_channel + 8
        channel_seg = ""
        end = False
        user = youtube_link.find("user")
        if find_channel == -1:
            return youtube_link + "/" + addition
        if user > -1:
            start = user + 5
            username = ""
            for j in range(start, len(youtube_link)):
                username += youtube_link[j]
                if youtube_link[j] == "/":
                    break
                if j == len(youtube_link) - 1:
                    username += "/"
            return "https://m.youtube.com/user/" + username + addition
        for i in range(new_index, len(youtube_link)):
            channel_seg += youtube_link[i]
            if youtube_link[i] == "/":
                break
            if i == len(youtube_link) - 1:
                end = True
        if not end:
            return "https://youtube.com/channel/" + channel_seg + addition
        return "https://youtube.com/channel/" + channel_seg + "/" + addition

    """Takes in the upload page link and returns a list of the number of views on latest videos of YouTuber"""
    # str --> list(int)
    def get_views(self):
        list_of_views = []
        all_videos_views = self.main_channel_html.findAll("ul", {"class": "yt-lockup-meta-info"})
        strip = ""
        total = 0
        for i in range(len(all_videos_views)):
            if i == len(all_videos_views) - 1:
                time = all_videos_views[i].text.find("views")
                start = time + 5
                strip = all_videos_views[i].text[start:].split()
            number_of_views = self.parse_views(all_videos_views[i].text)
            list_of_views.append(number_of_views)
            total += number_of_views
        return list_of_views, strip, total

    """Takes in the views text and parses it to return number of views as an integer"""
    # str --> (int, int)
    def parse_views(self, views):
        new_views = ""
        for i in views:
            if i == " ":
                break
            if i != ",":
                new_views += i
        return int(new_views)

    """Takes in a list of the views and returns an integer representing the average number of views"""
    def views_average(self, sum_views, last_date):
        dict_days = {"days": 1, "weeks": 7, "month": 30, "months": 30, "year": 365, "years": 365}
        return sum_views / (int(last_date[0]) * dict_days[last_date[1]])

    def analyze_titles(self):
        start = time.time()
        all_video_titles = self.main_channel_html.findAll("h3", {"class": "yt-lockup-title"})
        video_titles = []
        for i in range(10):
            video_title = all_video_titles[i].text
            if profanity.contains_profanity(video_title):
                self.bad_words += 1
            video_titles.append(video_title)
            video_id = all_video_titles[i].findAll("a", href=True)
            try:
                transcript = YouTubeTranscriptApi.get_transcript(self.get_video_id(video_id[0]['href']))
                for j in range(len(transcript)):
                    if time.time() - start > 10:
                        break
                    if profanity.contains_profanity(transcript[j]["text"]):
                        self.bad_words += 1
            except Exception as e:
                print(e)
                continue

        end = time.time()
        print("TIME FOR TITLES : " + str(end - start))
        return video_titles


    def get_video_id(self, url):
        loc = url.find("=")
        return url[loc + 1:]