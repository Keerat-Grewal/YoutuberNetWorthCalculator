import unittest
from youtuber import *


class TestList(unittest.TestCase):

    def test_basic_hash_01(self):
        youtubers = ["Logan Paul", "Jake Paul", "Nelk", "SteveWillDoIt", "KSI", "PewDiePie", "MrBeast", "Dude Perfect"]
        file = open("video_titles.txt", "w")
        for item in youtubers:
            youtuber = YouTuber(item)
            try:
                parsed_html = youtuber.get_parsed_html(
                    "https://www.google.com/search?q={0} {1}".format(youtuber.name, "youtube"))
                youtube_links = youtuber.get_youtube_links(parsed_html)
                try:
                    youtuber.find_correct_link(youtube_links)
                except Exception as e:
                    print(e)
                youtuber.analyze_titles()
                file.write("BAD WORDS FOR: " + youtuber.name + " -> " + str(youtuber.bad_words) + "\n")
                views = youtuber.get_views()
                last_vid_type = [views[1][0], views[1][1]]
                sum_views = sum(views[0])
                views_average = youtuber.views_average(sum_views, last_vid_type)
            except Exception as e:
                print(e)
        file.close()


if __name__ == '__main__':
    unittest.main()
