#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from copy import error
import json
from xmlrpc.client import boolean
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

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
  return babel.dates.format_datetime(date, format, locale='en')

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
    venues = Venue.query.all()
    areas = dict()

    for venue in venues:
      key = f'{venue.state}+{venue.city}'

      if areas.get(key) is None:
        areas[key] = {
          "state": venue.state,
          "city": venue.city,
          "venues": [],
        }
      
      areas[key]["venues"].append(venue)
    areas = areas.values()

    return render_template ('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  form = request.form
  search_term=form.get('search_term')
  search = f'%{search_term}%'
  venues = Venue.query.filter(Venue.name.ilike(search)).all()
  
  response={
    "count": len(venues),
    "data": []
  }
  for venue in venues:
    venue_data = {
      "id": venue.id,
      "name": venue.name,
    }
    response['data'].append(venue_data)
  
  return render_template('pages/search_venues.html', results=response, search_term=form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    #form = ArtistForm()
  venue = Venue.query.get(venue_id)
  shows = Show.query.join(Artist).filter(Show.venue_id==venue_id).all()

  past_shows = []
  upcoming_shows = []

  for show in shows:
    artist_data = {
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.time))
    }
    if show.time > datetime.now():
      upcoming_shows.append(artist_data)
    else:
      past_shows.append(artist_data)

  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)
    error = False
    try:
      if form.validate():
        venue = Venue(
          name=form.name.data,
          city=form.city.data,
          phone=form.phone.data,
          state=form.state.data,
          address=form.address.data,
          genres=request.form.getlist('genres'),
          facebook_link=form.facebook_link.data,
          image_link=form.image_link.data,
          website_link=form.website_link.data,
          seeking_talent=boolean(request.form.get('seeking_talent', False)),
          seeking_description=form.seeking_description.data,
        )

        db.session.add(venue)
        db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  # on successful db insert, flash success
    if(error):
      flash('An error occurred. Venue ' + form.name.data + ' could not be listed.')
    else:
      flash('Venue ' + form.name.data + ' was successfully listed!')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
      Venue.query.filter_by(id=venue_id).delete()
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()

  # Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = []
  for artist in artists:
    artist_data={
      "id": artist.id,
      "name": artist.name,
    }
    data.append(artist_data)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  form = request.form
  search_term=form.get('search_term')
  search = f'%{search_term}%'
  artists = Artist.query.filter(Artist.name.ilike(search)).all()

  response={
    "count": len(artists),
    "data": []
  }
  for artist in artists:
    artist_data = {
      "id": artist.id,
      "name": artist.name,
    }
    response['data'].append(artist_data)

  return render_template('pages/search_artists.html', results=response, search_term=form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  shows = Show.query.join(Venue).filter(Show.artist_id==artist_id).all()   
  print(shows)
  past_shows = []
  upcoming_shows = []

  for show in shows:
    venue_data = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.time))
    }
    if show.time > datetime.now():
      upcoming_shows.append(venue_data)
    else:
      past_shows.append(venue_data)

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  print('form: ' + form.name.data)
  print(form.genres.data)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = request.form
  artist = Artist.query.get(artist_id)
  error = False
  try:
      artist.name = form.get('name')
      artist.genres = form.getlist('genres')
      artist.city = form.get('city')
      artist.state = form.get('state')
      artist.phone = form.get('phone')
      artist.facebook_link=form.get('facebook_link')
      artist.image_link=form.get('image_link')
      artist.website_link=form.get('website_link')
      artist.seeking_venue = boolean(form.get('seeking_venue'))
      artist.seeking_description = form.get('seeking_description')
      
      print(artist)
      db.session.commit()
  except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website_link.data = venue.website_link
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_venue
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = request.form
  venue = Venue.query.get(venue_id)
  error = False
  try:
      venue.name = form.get('name')
      venue.genres = form.getlist('genres')
      venue.address = form.get('address')
      venue.city = form.get('data')
      venue.state = form.get('state')
      venue.phone = form.get('phone')
      venue.facebook_link=form.get('facebook_link')
      venue.image_link=form.get('image_link')
      venue.website_link=form.get('website_link')
      venue.seeking_talent = boolean(form.get('seeking_talent'))
      venue.seeking_description = form.get('seeking_description')

      db.session.commit()

  except:
      error = True
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
  form = ArtistForm(request.form)
  error = False 
  try:
    if form.validate_on_submit():
      artist = Artist(
      name=form.name.data,
      city=form.city.data,
      phone=form.phone.data,
      state=form.state.data,
      genres=form.getlist('genres'),
      facebook_link=form.facebook_link.data,
      image_link=form.image_link.data,
      website_link=form.website_link.data,
      seeking_venue=boolean(request.form.get('seeking_venue', False)),
      seeking_description=form.seeking_description.data,
    )

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if (error):
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  else:
    flash('Artist ' + form.name.data + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  shows = Show.query.join(Artist).join(Venue)
  data = []
  for show in shows:
    print(show)
      show_data={
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.time))
    }
    data.append(show_data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    #if form.validate_on_submit():
    show = Show(
      artist_id=request.form.get('artist_id'),
      venue_id=request.form.get('venue_id'),
      time=request.form.get('start_time')
    )

    print(Show.artist_id)

    db.session.add(show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  # called to create new shows in the db, upon submitting new show listing form
  if (error):
    flash('An error occurred')
  # on successful db insert, flash success
  else:
    flash('Show was successfully listed!')
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
