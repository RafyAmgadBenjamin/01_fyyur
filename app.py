#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # migrations instantiation


# TODO-done: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,nullable=False,default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venue", lazy=True) 
    #Creating the one to many relation with the show class

    # TODO-done: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable=False,default=False)
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(120))
    #Creating the one to many relation with the show class
    shows = db.relationship("Show", backref="artist", lazy=True) 

    # TODO-done: implement any missing fields, as a database migration using Flask-Migrate

# TODO-done Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__='Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime(), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)




#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime



#----------------------------------------------------------------------------#
# Helper functions.
#----------------------------------------------------------------------------#

def get_upcomming_shows_no(venue):
  """
  This is a function to get the number of upcomming shows related to this venue
  """
  now = datetime.now()
  current_time = now.strftime("%Y:%M:%D")
  shows = [ show for show in venue.shows if show.start_time.strftime("%Y:%M:%D") >current_time]
  return len(shows)

def create_venue_format(venue):
  """
  This function is to return the venue in the desired format to be rendered in the view
  """
  venue_data = {}
  venue_data['id'] = venue.id
  venue_data['name']=venue.name
  venue_data['num_upcoming_shows'] = get_upcomming_shows_no(venue)
  return venue_data

def format_show_data_for_artist(show):
  """
  Format the show data to be in the desired format to be rendered in the show_artist page
  """
  data = {}
  data['venue_id']=show.venue_id
  data['venue_name']=show.venue.name
  data['venue_image_link']=show.venue.image_link
  data['start_time']=  str(show.start_time)
  return data

def format_show_data_for_venue(show):
  """
  Format the show data to be in the desired format to be rendered in the show_venue page
  """
  data = {}
  data['artist_id']=show.artist_id
  data['artist_name']=show.artist.name
  data['artist_image_link']=show.artist.image_link
  data['start_time']= str(show.start_time)
  return data
def format_data_for_search(search_element):
  """
    Format the data to be in the desired format to be rendered in the search 
  """
  data = {}
  data['id']= search_element.id
  data['name']=search_element.name
  data['num_upcoming_shows']= len(search_element.shows)
  return data
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO-done: replace with real venues data.
  # TODO-done: num_shows should be aggregated based on number of upcoming shows per venue.
 
  venues = Venue.query.all()
  all_areas = [(venue.city,venue.state) for venue in venues ] 
  #get unique areas
  city_index = 0
  state_index = 1
  areas = list(set(all_areas))
  data = []
  for area in areas:
    tmp = {}
    tmp['city']=area[city_index]
    tmp['state']=area[state_index]
    tmp['venues'] = [create_venue_format(venue) for venue in venues if venue.city == tmp['city'] and 
    venue.state == tmp['state']]
    data.append(tmp)

  return render_template('pages/venues.html', areas=data)



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO-done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')
  search_term=search_term.strip()  #removing the spaces form the beginning and the end
  search_query = '%{0}%'.format(search_term) # prepare the query 
  results = Venue.query.filter(Venue.name.ilike(search_query)).all()
  venue_data= [format_data_for_search(venue) for venue in results]
  #Format the data to be in the desired format
  response = {}
  response['count']= len(results)
  response['data'] = venue_data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO-done: replace with real venue data from the venues table, using venue_id
  
  venue = Venue.query.get(venue_id)
  #splitting the genres in order to loop on them in the front-end
  tmp_genres = venue.genres.split(',')
  venue.genres = tmp_genres
  data = vars(venue) #changin(casting) venue object to dictionary 
  past_shows = [format_show_data_for_venue(show) for show in venue.shows if show.start_time < datetime.today()] 
  upcomming_shows = [format_show_data_for_venue(show) for show in venue.shows if show.start_time >= datetime.today()] 
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcomming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcomming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO-Done: insert form data as a new Venue record in the db, instead
  #flag to show if an error happened or not
  is_error =False
  venue_id = None
  try:
    venue = Venue()
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link= request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    tmp_genres= request.form.getlist('genres')
    #Joining genres together in one string to be stored in DB 
    venue.genres = ','.join(tmp_genres)
    venue.website = request.form['website']
    venue.seeking_talent = True if request.form.get('seeking_talent') and request.form.get('seeking_talent') == 'y' else False
    venue.seeking_description = request.form['seeking_description']
    db.session.add(venue)
    db.session.commit()
    venue_id = venue.id
  except:
    db.session.rollback()
    is_error =True
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO-Done: modify data to be the data object returned from db insertion
  try:
    venue_data = Venue.query.get(venue_id)
  except:
    print("Something wrong happened during retrieving the data from database")
  if is_error:
    # TODO-Done: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue_data.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO-done: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    #TODO: i have to make it using cascading
    Show.query.filter_by(venue_id =venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO-done: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO-done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term=request.form.get('search_term', '')
  search_term=search_term.strip()  #removing the spaces form the beginning and the end
  search_query = '%{0}%'.format(search_term) # prepare the query 
  results = Artist.query.filter(Artist.name.ilike(search_query)).all()
  artist_data= [format_data_for_search(artist) for artist in results]
  #Format the data to be in the desired format
  response = {}
  response['count']= len(results)
  response['data'] = artist_data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO-done: replace with real venue data from the venues table, using venue_id
  
  artist = Artist.query.get(artist_id)
  #splitting the genres in order to loop on them in the front-end
  tmp_genres = artist.genres.split(',')
  artist.genres = tmp_genres
  data = vars(artist) #changin(casting) artist object to dictionary 
  now = datetime.now()
  current_time = now.strftime("%Y:%M:%D")
  past_shows = [format_show_data_for_artist(show) for show in artist.shows if show.start_time < datetime.today()] 
  upcomming_shows = [format_show_data_for_artist(show) for show in artist.shows if show.start_time >= datetime.today()] 
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcomming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcomming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO-done: populate form with fields from artist with ID <artist_id>
  #Populating fields in the front-end
  artist = Artist.query.get(artist_id)
  form.seeking_description.data = artist.seeking_description
  form.seeking_venue.data = artist.seeking_venue
  form.genres.data = artist.genres
  form.state.data= artist.state
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO-done: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    # mapping data from the request to the artist object
    artist = Artist.query.get(artist_id)
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    tmp_genres= request.form.getlist('genres') 
    artist.genres= ','.join(tmp_genres) 
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.seeking_venue=True if request.form.get('seeking_venue') and (request.form.get('seeking_venue') == 'y' or request.form.get('seeking_venue') == 'on') else False
    artist.website=request.form['website']
    artist.seeking_description=request.form['seeking_description']

    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  # TODO-done: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  form.seeking_description.data = venue.seeking_description
  form.seeking_talent.data = venue.seeking_talent
  form.genres.data = venue.genres
  form.state.data= venue.state
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO-done: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  try:
    venue.name = request.form['name']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.address = request.form['address']
    venue.phone = request.form['phone']
    venue.image_link= request.form['image_link']
    venue.facebook_link = request.form['facebook_link']
    tmp_genres= request.form.getlist('genres') 
    venue.genres = ','.join(tmp_genres)
    venue.website = request.form['website']
    venue.seeking_talent = True if request.form.get('seeking_talent') and (request.form.get('seeking_talent') == 'y' or  request.form.get('seeking_venue') == 'on') else False
    venue.seeking_description = request.form['seeking_description']
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO-Done: insert form data as a new Venue record in the db, instead 
  artist_id = None
  #flag to show if an error happened or not
  is_error =False
  try:
    # mapping data from the request to the artist object
    artist = Artist()
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    tmp_genres= request.form.getlist('genres') 
    #Joining genres together in one string to be stored in DB
    artist.genres = ','.join(tmp_genres)
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.seeking_venue=True if request.form.get('seeking_venue') and request.form.get('seeking_venue') == 'y' else False
    artist.website=request.form['website']
    artist.seeking_description=request.form['seeking_description']

    db.session.add(artist)
    db.session.commit()
    artist_id = artist.id
  except:
    db.session.rollback()
    is_error =True
    print(sys.exc_info())
  finally:
    db.session.close()

  # TODO-done: modify data to be the data object returned from db insertion
  try:
    artist_data = Artist.query.get(artist_id)
  except:
    print("Something wrong happened during retrieving the data from database")
    

  if  is_error:
    # TODO-done: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + artist_data.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO-done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  shows = Show.query.all()
  data = []
  for show in shows:
    tmp_show = {}
    tmp_show['venue_id'] = show.venue.id
    tmp_show['venue_name'] = show.venue.name
    tmp_show['artist_id'] = show.artist.id
    tmp_show['artist_name'] = show.artist.name
    tmp_show['artist_image_link'] = show.artist.image_link
    tmp_show['start_time'] = show.start_time.isoformat()
    data.append(tmp_show)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO-done: insert form data as a new Show record in the db, instead
  is_error = False
  show_id = None
  try:
    show = Show()
    show.artist_id = request.form['artist_id']
    show.venue_id = request.form['venue_id']
    show.start_time= request.form['start_time']
    db.session.add(show)
    db.session.commit()
    show_id = show.id
  except:
    db.session.rollback()
    is_error=True
    print(sys.exc_info())
  finally:
    db.session.close()
  try:
    show_data = Show.query.get(show_id)
  except:
    print("Something wrong happened during retrieving the data from database")
  
  # TODO-done: on unsuccessful db insert, flash an error instead.
  if is_error:
    flash('An error occurred. Show could not be listed.')  # on successful db insert, flash success
  else:
    flash('Show was successfully listed!')

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
