#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, url_for
import json

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://aa4213:chasjoag@34.73.21.127/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)
#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def loginPage():
	return render_template('login.html')
@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT * FROM Actor;")
  names = []
  for result in cursor:
    names.append(result)  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/get_media_details', methods=['POST'])
def get_media_details():
  res = awards = g.conn.execute("SELECT * FROM media WHERE mediaid = {} ".format(request.form['media']))
  if res:
    for x in res:
      r = x
      break

  info = dict(r)
  print("Started here")
  info['awards'] = []
  awards = g.conn.execute("SELECT * FROM award_given WHERE mediaid = {} ".format(r['mediaid']))
  if awards:
    for a in awards:
      award_details = g.conn.execute("SELECT * FROM award WHERE awardid = {} ".format(a['awardid']))
      if award_details:
        for ad in award_details:
          info['awards'].append({
            'name': ad['name'],
            'year': a['year']
          })
          break

  info['actors'] = []
  actors = g.conn.execute("SELECT * FROM acts_in WHERE mediaid = {} ".format(r['mediaid']))
  if actors:
    for a in actors:
      actor_details = g.conn.execute("SELECT * FROM actor WHERE actorid = {} ".format(a['actorid']))
      if actor_details:
        for ad in actor_details:
          info['actors'].append({
            'name': ad['name']
          })
          break

  info['reviews'] = []
  reviews = g.conn.execute("SELECT * FROM reviews WHERE mediaid = {} ".format(r['mediaid']))
  if reviews:
    for a in reviews:
      info['reviews'].append({
        'text': a['text'],
        'rating': a['rating']
      })

  info['number_reviews'] = len(info['reviews'])
  if len(info['reviews']) > 0:
    info['average_rating'] = sum([f['rating'] for f in info['reviews']]) / len(info['reviews'])
  else:
    info['average_rating'] = 0

  if(info['type']=='series'):
    seriesinfo = g.conn.execute("SELECT * FROM series WHERE mediaid = {} ".format(r['mediaid']))
    if seriesinfo:
      for sinf in seriesinfo:
        info['numseasons']= sinf['numberofseasons']
        info['numepisodes']= sinf['numberofepisodes']
  elif(info['type']=='movie'):
    movieinfo = g.conn.execute("SELECT * FROM movie WHERE movieid = {} ".format(r['mediaid']))
    if movieinfo:
      for minf in movieinfo:
        info['duration']= minf['duration']
  context = dict(data = info)
  return render_template("displayMediaInfo.html",**context)

@app.route('/search_media_for_review', methods=['POST'])
def search_media_for_review():
  result = g.conn.execute("SELECT * FROM media WHERE LOWER(name) LIKE LOWER('%%{}%%') ".format(request.form['media_name']))
  output = []
  if result:
    for r in result:
      output.append({
        'id': r['mediaid'],
        'name': r['name']
      })

    context = dict(data = output)      
    return render_template('select_review_item.html', **context)
  return render_template('review.html')


@app.route('/get_actor_details', methods=['POST'])
def get_actor_details():
  res = g.conn.execute("SELECT * FROM actor WHERE actorid = {} ".format(request.form['actor']))
  if res:
    for x in res:
      r = x
      break
  info = dict(r)

  info['medias'] = []
  medias = g.conn.execute("SELECT * FROM acts_in WHERE actorid = {} ".format(r['actorid']))
  if medias:
    for a in medias:
      media_details = g.conn.execute("SELECT * FROM media WHERE mediaid = {} ".format(a['mediaid']))
      if media_details:
        for ad in media_details:
          info['medias'].append({
            'name': ad['name'],
            'year': ad['yearofrelease'],
            'genre': ad['genre'],
            'language': ad['language'],
            'type': ad['type']
          })
          break

  context = dict(data = info)
  return render_template("displayActorInfo.html",**context)


@app.route('/review')
def review():
  return render_template("review.html")

@app.route('/search')
def search():
  return render_template("search.html")

@app.route('/search_actor', methods=["POST"])
def search_query():
  # if request.form['search_type'] == 'media':
  #   result = g.conn.execute("SELECT * FROM media WHERE name = '{}' ".format(request.form['query']))
  #   if result:
  #     for r in result:
  #       return get_media_details(r)
  #     return render_template('search.html')   
  # else:
  result = g.conn.execute("SELECT * FROM actor WHERE LOWER(name) LIKE LOWER('%%{}%%') ".format(request.form['query']))
  output = []
  if result:
    for r in result:
      output.append({
        'name': r['name'],
        'id': r['actorid']
      })
    context = dict(data = output)
    return render_template("displayactor.html",**context)
  return render_template('search.html')  

@app.route('/actor')
def actor():
  return render_template('actor.html')

@app.route('/media')
def media():
  return render_template('media.html')

@app.route('/media_search')
def media_search():
  return render_template('media_search.html')

@app.route('/search_media', methods= ['POST'])
def search_media():
  result = g.conn.execute("SELECT * FROM media WHERE LOWER(name) LIKE LOWER('%%{}%%') ".format(request.form['query']))
  output = []
  if result:
    for r in result:
      output.append({
        'name': r['name'],
        'id': r['mediaid']
      })
    context = dict(data = output)
    return render_template("displaymedialist.html",**context)
  return render_template('search.html')  

@app.route('/write_review', methods=['POST'])
def write_review():
  result = g.conn.execute("SELECT * FROM media WHERE mediaid = {} ".format(request.form['media_name']))
  if result:
    for r in result:
      print(r)
      print(r['mediaid'])
      check = g.conn.execute("SELECT * FROM reviews WHERE personid = '{}' AND mediaid = '{}' ".format(session['userid'], r['mediaid']))

      if check:
        for c in check:
          print("here here")
          return render_template('already_reviewed.html')

      return render_template('write_review.html', mediaid = r['mediaid'], name = r['name'])
    return render_template('review.html')

@app.route('/submit_review', methods=["POST","GET"])
def submit_review():
  userid = session['userid']
  rating = request.form['rating']
  review = request.form['review']
  mediaid = request.form['mediaid']
  g.conn.execute("INSERT INTO reviews(text,rating,personid,mediaid) VALUES ('{}',{},{},{})".format(review,rating,userid,mediaid))
  # result = g.conn.execute("SELECT * FROM media WHERE name = '{}' ".format(request.form['media_name']))  
  # print(request.args['messages'])
  return render_template('thanks.html')

@app.route('/media_view', methods=['GET'])
def media_view():
  res = g.conn.execute('SELECT * from media')
  genres = []
  language = []
  years = []
  if res:
    for x in res:
      genres.append(x['genre'])
      language.append(x['language'])
      years.append(x['yearofrelease'])
  genres = list(set(genres))
  language = list(set(language))
  years = list(set(years))
  years.sort()
  years = ["All"] + years 
  genres = ["All"] + genres
  language = ["All"] + language
  actors = [("All","All")]
  type_ = ["All","series", "movie"]
  res = g.conn.execute('SELECT name, actorid from actor order by name')
  if res:
    for x in res:
      actors.append((x['name'], x['actorid']))
  data = {}
  data['genre'] = genres
  data['language'] = language
  data['actor'] = actors
  data['year'] = years
  data['type'] = type_
  context = dict(data = data)
  return render_template('media_view.html',**context)  

@app.route('/filter_view_media',methods = ['POST'])
def filter_view_media():
  query = "SELECT DISTINCT(m.mediaid), name, genre, language, yearofrelease, type FROM media m INNER JOIN acts_in a1 ON m.mediaid = a1.mediaid INNER JOIN acts_in a2 ON m.mediaid = a2.mediaid"
   
  conditions = " WHERE a2.actorid != a1.actorid"
  if request.form['actor1'] != "All":
    print(request.form['actor1'])
    conditions += " AND a1.actorid = {}".format(request.form['actor1'])
    print(conditions)
  if request.form['actor2'] != "All":
    conditions += " AND a2.actorid = {}".format(request.form['actor2'])

  if request.form['type'] != 'All':
    if conditions != "":
      conditions += " AND type = '{}'".format(request.form['type']) 
    else:
      conditions += "type = '{}'".format(request.form['type']) 

  if request.form['language'] != 'All':
    if conditions != "":
      conditions += " AND language = '{}'".format(request.form['language']) 
    else:
      conditions += "language = '{}'".format(request.form['language']) 

  if request.form['genre'] != 'All':
    if conditions != "":
      conditions += " AND genre = '{}'".format(request.form['genre']) 
    else:
      conditions += "genre = '{}'".format(request.form['genre']) 

  if request.form['year'] != 'All':
    if conditions != "":
      conditions += " AND yearofrelease = {}".format(request.form['year']) 
    else:
      conditions += "year = {}".format(request.form['year']) 

  # if conditions != "":
  query += conditions
  print(query)
  res = g.conn.execute(query)
  output = []
  if res:
    for x in res:
      output.append({
        'name': x['name'],
        'year': x['yearofrelease'],
        'language': x['language'],
        'genre': x['genre'],
        'type': x['type']
      })
    context = dict(data=output)
    return render_template('display_media_filter_list.html', **context)


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/index')


@app.route('/login', methods=['POST'])
def login():
  logins = g.conn.execute('SELECT * FROM PERSON;')
  login = []
  ids = []
  for result in logins:
    appendList = [result['username'], result['password']]
    login.append(appendList)
    ids.append(result['personid'])
  username = request.form['username']
  password = request.form['password']

  if ([username,password] in login):
    session['userid'] = ids[login.index([username,password])]
    return render_template("user.html")
  else:
    return redirect('/')

@app.route('/create_user', methods=['POST'])
def create_user():
  result = g.conn.execute("SELECT * FROM person WHERE username = '{}'".format(request.form['username']))
  if result:
    for r in result:
      return render_template("user_exists.html")
    
    g.conn.execute("INSERT INTO person(username, name, password) VALUES ('{}','{}','{}')".format(request.form['username'], request.form['name'], request.form['password']))
    return render_template('login.html')

@app.route('/user')
def user():
  return render_template("user.html")

@app.route('/signup')
def signup():
  return render_template("signup.html")


if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.secret_key = "sampe"
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)
  run()
