import mechanize, cookielib, re, datetime
import sqlite3

#Constructor:
br = mechanize.Browser()
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)
br.set_handle_robots(False)
br.addheaders = [('User-agent', 'Mozilla/5.0')]
months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
subreddits = ["funny", "askscience", "TodayILearned", "gonewild", "firstworldanarchists", "buildapc", "dataisbeautiful", "calvinandhobbes", "sixwordstories", "ExplainLikeIAmA"]
url = "http://www.reddit.com/r/"

#Start SQL, create database if necessary
db = sqlite3.connect("results.db")
c = db.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data
                  (hour integer,
                  datetime text, 
                  funny_total integer, 
                  funny_online integer, 
                  askscience_total integer, 
                  askscience_online integer, 
                  TodayILearned_total integer, 
                  TodayILearned_online integer, 
                  gonewild_total integer, 
                  gonewild_online integer, 
                  firstworldanarchists_total integer, 
                  firstworldanarchists_online integer, 
                  buildapc_total integer, 
                  buildapc_online integer, 
                  dataisbeautiful_total integer, 
                  dataisbeautiful_online integer, 
                  calvinandhobbes_total integer, 
                  calvinandhobbes_online integer, 
                  sixworldstories_total integer, 
                  sixworldstories_online integer, 
                  ExplainLikeIAmA_total integer,
                  ExplainLikeIAmA_online integer)''')

#Log into Reddit
br.open("https://ssl.reddit.com/login")
br.select_form(nr = 1)

br.form['user'] = "counteraccount"
br.form['passwd'] = "*********"

if "counteraccount" in br.submit().read():
      print "Logged in"
else:
      print "Failed to log in"


#TABLE: 	Current Hour, Current Date/Time, {Total Users, Online Users} * len(subreddits)
#subreddits:	/r/funny, /r/askscience, /r/TodayILearned, /r/gonewild, /r/firstworldanarchists, /r/buildapc, /r/dataisbeautiful, /r/calvinandhobbes, /r/sixworldstories, ExplainLikeIAmA

def Quantify(string):
      nonnumerics = [",", "~"]
      for character in nonnumerics:
            while character in string:
                  string = string[:string.index(character)] + string[string.index(character)+1:]
      return int(string)

class Subreddit(object):
      def __init__(self, name):
            self.name = name
            self.total_users = 0
            self.online_users = 0
      def retrieve_users(self):
            #html = opener.open(url+self.name).read()
            #Retry 5 times in the event of failure:
            for i in range(5):
                  try:
                        html = br.open(url+self.name).read()
                        results = re.findall("<span class='number'>[\d,~]+</span>", html)
                        self.total_users = int(Quantify(results[0][21:-7]))
                        self.online_users = int(Quantify(results[1][21:-7]))
                  except:
                        print "Failed to Retrieve"
                        pass
                  else:
                        print "Retrieval Successful"
                        break
      def output_object(self):
            print "Subreddit: /r/" + self.name
            print "\tTotal:", self.total_users
            print "\tOnline:", self.online_users
      def get_Total(self):
            return self.total_users
      def get_Online(self):
            return self.online_users

now = datetime.datetime.now()
date = str(now.month) + "/" + str(now.day) + " " + str(now.hour) + ":" + str(now.minute)
hour = (sum(months[:now.month-1]) + (now.day-1))*24 + now.hour

data = [hour, date]

for i in range(len(subreddits)):
      subreddits[i] = Subreddit(subreddits[i])
      subreddits[i].retrieve_users()
      data.append(subreddits[i].get_Total())
      data.append(subreddits[i].get_Online())
      subreddits[i].output_object()

print data

c.executemany('INSERT INTO data VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', [data])

#for row in c.execute('SELECT * FROM data ORDER BY hour'): print row

db.commit()
db.close()