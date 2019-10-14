#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import *
from models import Base, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


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
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_venues = db.session.query(Venue).order_by(Venue.state, Venue.city).all()
  data = []
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  location = ''
  for venue in all_venues:
    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
    venue_info = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(upcoming_shows)
    }
    if location == venue.city + venue.state:
      data[len(data) - 1]["venues"].append(venue_info)
    else:
      location = venue.city + venue.state
      data.append({
              "city": venue.city,
              "state": venue.state,
              "venues": [venue_info]
    })
  
  
  return render_template('pages/venues.html', areas=data)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  def my_venue(Venue):
        return {
            'id': Venue.id,
            'name': Venue.name,
        }
  venue_query = db.session.query(Venue).filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
  venue_list = list(map(my_venue, venue_query))
  response = {
      "count": len(venue_list),
      "data": venue_list
    }
 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  current_venue = db.session.query(Venue).get(venue_id)
  data = Venue.info(current_venue)
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  new_shows = db.session.query(Show).options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time > current_time).all()
  new_shows_list = list(map(Show.artist_info, new_shows))
  data["upcoming_shows"] = new_shows_list
  data["upcoming_shows_count"] = len(new_shows_list)
  past_shows = db.session.query(Show).options(db.joinedload(Show.Venue)).filter(Show.venue_id == venue_id).filter(Show.start_time <= current_time).all()
  past_shows_list = list(map(Show.artist_info, past_shows))
  data["past_shows"] = past_shows_list
  data["past_shows_count"] = len(past_shows_list)   
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  newVenue = {}
  try: 
      name = request.form.get('name', '')
      city = request.form.get('city', '')
      address = request.form.get('address', '')
      phone = request.form.get('phone', '')
      state = request.form.get('state', '')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link', '')
      venue = Venue(name=name, city=city, address=address, phone=phone, state=state, genres=genres, facebook_link=facebook_link)
      db.session.add(venue)
      db.session.commit()
      newVenue['name'] = venue.name
      newVenue['city'] = venue.city
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      abort(400)    
  else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try: 
        db.session.query(Venue).filter_by(id=venue_id).delete()
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
  # TODO: replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  def my_artist(Artist):
        return {
            'id': Artist.id,
            'name': Artist.name,
        }
  artist_query = db.session.query(Artist).filter(Artist.name.ilike('%' + request.form['search_term'] + '%'))
  artist_list = list(map(my_artist, artist_query))
  response = {
      "count": len(artist_list),
      "data": artist_list
    }
  return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  current_artist = db.session.query(Artist).get(artist_id)
  data = Artist.info(current_artist)
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  new_shows = db.session.query(Show).options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time > current_time).all()
  new_shows_list = list(map(Show.venue_info, new_shows))
  data["upcoming_shows"] = new_shows_list
  data["upcoming_shows_count"] = len(new_shows_list)
  past_shows = db.session.query(Show).options(db.joinedload(Show.Artist)).filter(Show.artist_id == artist_id).filter(Show.start_time <= current_time).all()
  past_shows_list = list(map(Show.venue_info, past_shows))
  data["past_shows"] = past_shows_list
  data["past_shows_count"] = len(past_shows_list)   
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  current_artist = db.session.query(Artist).get(artist_id)
  artist = Artist.info(current_artist)
  form.name.data = artist["name"]
  form.genres.data = artist["genres"]
  form.city.data = artist["city"]
  form.state.data = artist["state"]
  form.phone.data = artist["phone"]
  form.facebook_link.data = artist["facebook_link"]
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  current_artist = db.session.query(Artist).get(artist_id)
  setattr(current_artist, 'name', request.form['name'])
  setattr(current_artist, 'genres', request.form.getlist('genres'))
  setattr(current_artist, 'city', request.form['city'])
  setattr(current_artist, 'state', request.form['state'])
  setattr(current_artist, 'phone', request.form['phone'])
  setattr(current_artist, 'facebook_link', request.form['facebook_link'])
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  newArtist = {}
  try: 
      name = request.form.get('name', '')
      city = request.form.get('city', '')
      phone = request.form.get('phone', '')
      state = request.form.get('state', '')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link', '')
      artist = Artist(name=name, city=city, phone=phone, state=state, genres=genres, facebook_link=facebook_link)
      db.session.add(artist)
      db.session.commit()
      newArtist['name'] = artist.name
      newArtist['city'] = artist.city
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      abort(400)    
  else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = db.session.query(Show).all()

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  newShow = {}
  try: 
      artist_id = request.form.get('artist_id', '')
      venue_id = request.form.get('venue_id', '')
      start_time = request.form.get('start_time', '')
      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
      newShow['artist_id'] = show.artist_id
      newShow['venue_id'] = show.venue_id
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show ' + request.form['artist_id'] + ' could not be listed.')
      abort(400)    
  else:
      flash('Show ' + request.form['artist_id'] + ' was successfully listed!')
      return render_template('pages/home.html')
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

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
