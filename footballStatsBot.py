import praw
import datetime
from bs4 import BeautifulSoup
import urllib
import ConfigParser
config = ConfigParser.ConfigParser()
config.read("config.ini")


starttime = datetime.datetime.utcnow()
print("Start "+str(starttime))

print(config.get('Authentication', 'client_id'))

bot = praw.Reddit(
  user_agent='FootballPlayerStatsBot v0.1',
  client_id=config.get('Authentication', 'client_id'),
  client_secret=config.get('Authentication', 'client_secret'),
  username=config.get('Authentication', 'username'),
  password=config.get('Authentication', 'password'),
)

subreddit = bot.subreddit('kieryweery')

comments = subreddit.stream.comments()


for comment in comments:
    text = comment.body
    author = comment.author
    created = comment.created_utc

    if 'footballplayerstats' in text.lower() and datetime.datetime.utcfromtimestamp(created) > starttime:
        page = urllib.urlopen('https://www.statbunker.com/players/getPlayerStats?player_id=36682').read()
        soup = BeautifulSoup(page)
        print(soup.prettify())
        print(text)
        print(datetime.datetime.utcfromtimestamp(created))
        text = text.split(' ', 1)[1]
        print('You want to find stats for '+text)

        page = urllib.urlopen(
          'https://www.statbunker.com/players/GetHistoryStats?player_id=36682&comps_type=-1&dates=2016').read()
        soup = BeautifulSoup(page, "html.parser")
        statstables = soup.find("table", "table").find("tbody").find_all("tr")
        statstablesheaders = soup.find("table", "table").find("thead").find("tr").find_all("th")

        headers = []

        for header in statstablesheaders:
            if header.img:
                content = header.img['alt']
            else:
                content = header.contents

            headers.append(content)

        # print "headers", headers

        collatedstats = []

        for i, statstable in enumerate(statstables):
            stats = statstable.find_all("td")
            collatedstats.append([])
            # print("Stat Table!")
            for j, stat in enumerate(stats):
                # print "a", stat.a
                if stat.a:
                    # print "Some", "a", stat.a
                    content = stat.a.contents
                else:
                    # print "None", "a", stat.a
                    content = stat.contents
                    # print stat.contents
                # print headers[j], stat.contents
                collatedstats[i].append((headers[j], content[0]))

        reply = ""

        for comp in collatedstats:
            try:
                games = int(comp[2][1])
            except ValueError:
                games = 0

            try:
                goals = int(comp[11][1])
            except ValueError:
                goals = 0

            try:
                assists = int(comp[10][1])
            except ValueError:
                assists = 0

            reply += "In the {} for {}, {} played {} games scoring {} goals and had {} assists.\n\n".format(comp[0][1],
                                                                                                            comp[1][1],
                                                                                                            text,
                                                                                                            games,
                                                                                                            goals,
                                                                                                            assists)
        print reply
        comment.reply(reply)
