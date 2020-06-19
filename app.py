from flask import Flask, render_template, request, url_for, flash, redirect
from youtuber import *
import time

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['SECRET_KEY'] = '\x88\xc3;$\x0b\xfd\xd0\xfb\xb5\x93\x89\x14'


@app.route('/')


@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/info', methods=['POST'])
def info():
    youtuber_name = request.form['name']
    start = time.time()

    if youtuber_name == "":
        flash('This YouTuber does not exist, try another one.')
        return redirect(url_for('index'))

    youtuber = YouTuber(youtuber_name)
    try:
        parsed_html = youtuber.get_parsed_html("https://www.google.com/search?q={0} {1}".format(youtuber.name, "youtube"))
        youtube_links = youtuber.get_youtube_links(parsed_html)
        try:
            youtuber.find_correct_link(youtube_links)
        except Exception as e:
            print(e)
            flash('This YouTuber does not exist, try another one.')
            return redirect(url_for('index'))
        youtuber.analyze_titles()
        views = youtuber.get_views()
        last_vid_type = [views[1][0], views[1][1]]
        sum_views = sum(views[0])
        views_average = youtuber.views_average(sum_views, last_vid_type)
    except Exception as e:
        print(e)
        flash('This YouTuber does not exist, try another one.')
        return redirect(url_for('index'))

    end = time.time()
    print("END TIME: " + str(end - start))
    return render_template('info.html', n=youtuber_name, views=views_average, main_channel=youtuber.main_channel_link, subs=youtuber.subscribers)


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
