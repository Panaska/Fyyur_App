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
  last_five_venues = db.session.query(Venue).order_by(Venue.id.desc()).limit(5)
  last_five_artists = db.session.query(Artist).order_by(Artist.id.desc()).limit(5)
  data_venues = []
  data_artists = []
  for venue in last_five_venues:
    venue_info = {
      "id": venue.id,
      "name": venue.name,
      "city": venue.city,
      "state": venue.state
    }
    data_venues.append(venue_info)
  for artist in last_five_artists:
    artist_info = {
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state
    }
    data_artists.append(artist_info)  

  return render_template('pages/home.html', venues = data_venues, artists = data_artists)


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

@app.route('/delete/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try: 
        bad_venue = db.session.query(Venue).filter(Venue.id==venue_id).first()
        name = bad_venue.name
        db.session.delete(bad_venue)
        db.session.commit()
        flash('Venue ' + name + ' deleted successfully!')
    except:
        db.session.rollback()
        flash('Venue ' + name + ' IS NOT deleted!')
    finally:
        db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect('/')

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


@app.route('/delete/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try: 
        bad_artist = db.session.query(Artist).filter_by(id=artist_id).first()
        name = bad_artist.name
        db.session.delete(bad_artist)
        db.session.commit()
        flash('Artist ' + name + ' deleted successfully!')
    except:
        db.session.rollback()
        flash('Artist ' + name + ' IS NOT deleted!')
    finally:
        db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return redirect('/')  

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
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      abort(400)    
  else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
      return render_template('pages/home.html')
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')  

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
  current_venue = db.session.query(Venue).get(venue_id)
  venue = Venue.info(current_venue)
  form.name.data = venue["name"]
  form.genres.data = venue["genres"]
  form.city.data = venue["city"]
  form.state.data = venue["state"]
  form.address.data = venue["address"]
  form.phone.data = venue["phone"]
  form.facebook_link.data = venue["facebook_link"]
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  current_venue = db.session.query(Venue).get(venue_id)
  setattr(current_venue, 'name', request.form['name'])
  setattr(current_venue, 'genres', request.form.getlist('genres'))
  setattr(current_venue, 'city', request.form['city'])
  setattr(current_venue, 'state', request.form['state'])
  setattr(current_venue, 'address', request.form['address'])
  setattr(current_venue, 'phone', request.form['phone'])
  setattr(current_venue, 'facebook_link', request.form['facebook_link'])
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Show).options(db.joinedload(Show.Venue), db.joinedload(Show.Artist)).all()
  data = list(map(Show.info, shows))

  
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
  try: 
      artist_id = request.form.get('artist_id', '')
      venue_id = request.form.get('venue_id', '')
      start_time = request.form.get('start_time', '')
      show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
      db.session.add(show)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
  finally:
      db.session.close()
  if error:
      flash('An error occurred. Show ' + request.form['artist_id'] + ' could not be listed.')
      abort(400)    
  else:
      flash('Show ' + request.form['start_time'] + ' was successfully listed!')
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
