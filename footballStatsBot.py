# imports
import praw
import datetime
from bs4 import BeautifulSoup
import urllib
import ConfigParser

# Load config file
config = ConfigParser.ConfigParser()
config.read("config.ini")

# Get bot start time for new comment check
starttime = datetime.datetime.utcnow()
print("Start "+str(starttime))

# searchpage = urllib.urlopen('https://www.statbunker.com/usual/search?action=Find&search=ryan+christie').read()
# soup = BeautifulSoup(searchpage, "html.parser")
# player = soup.find("table", "players").find("tbody").find_all("tr")[0].find_all("td")[0].a['href'].split('=')[1]

# print player

# Connect to Reddit
bot = praw.Reddit(
  user_agent='FootballPlayerStatsBot v0.1',
  client_id=config.get('Authentication', 'client_id'),
  client_secret=config.get('Authentication', 'client_secret'),
  username=config.get('Authentication', 'username'),
  password=config.get('Authentication', 'password')
)

# Connect to subreddit
subreddit = bot.subreddit('kieryweery')

# Fetch comment stream
comments = subreddit.stream.comments()

# Loop through comments in stream
for comment in comments:
    # Extract information from the comment
    text = comment.body
    author = comment.author
    created = comment.created_utc

    # If the comment mentioned the keyword 'footballplayerstats'
    if 'footballplayerstats' in text.lower() and datetime.datetime.utcfromtimestamp(created) > starttime:
        # Split requested name up
        requestedname = text.split(' ', 1)[1].split(' ')

        # Create search url
        searchurl = 'https://www.statbunker.com/usual/search?action=Find&search='
        for index, word in enumerate(requestedname):
            searchurl += word
            if len(requestedname)> index + 1:
                   searchurl += '+'

        print(searchurl)

        # Search for player
        searchpage = urllib.urlopen(searchurl).read()
        soup = BeautifulSoup(searchpage, "html.parser")
        # Get player id from returned html page
        player = soup.find("table", "players").find("tbody").find_all("tr")[0].find_all("td")[0].a['href'].split('=')[1]

        print "player", player

        # Extract whole player name
        text = text.split(' ', 1)[1]
        print('You want to find stats for '+text)


        # Use fethched player id to request player stats
        page = urllib.urlopen(
          'https://www.statbunker.com/players/GetHistoryStats?player_id='+player+'&comps_type=-1&dates=2016').read()
        soup = BeautifulSoup(page, "html.parser")
        # Get stats tables
        statstables = soup.find("table", "table").find("tbody").find_all("tr")
        # Get stats tables headers
        statstablesheaders = soup.find("table", "table").find("thead").find("tr").find_all("th")

        headers = []

        # Extract header names
        for header in statstablesheaders:
            if header.img:
                content = header.img['alt']
            else:
                content = header.contents

            headers.append(content)

        # print "headers", headers

        collatedstats = []

        # Extract table stats
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

        # Output stats for each competition
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
        # Reply to comment with stats
        comment.reply(reply)
