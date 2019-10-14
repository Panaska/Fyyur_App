from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import backref, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(Base):
    __tablename__ = 'Venue'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    genres = Column(String(120))
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    address = Column(String(120), nullable=False)
    phone = Column(String(120))
    image_link = Column(String(500), default="..\..\static\img\default_venue.jpg")
    website = Column(String(120))
    facebook_link = Column(String(120))
    seeking_talent = Column(Boolean, default=False)
    seeking_description = Column(String(500))
    shows = relationship('Show', backref = 'Venue', lazy='dynamic')

    def info(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.strip("{}").split(","),
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(Base):
    __tablename__ = 'Artist'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    phone = Column(String(120))
    genres = Column(String(120))
    image_link = Column(String(500), default="..\..\static\img\default_artist.jpg")
    website = Column(String(120))
    facebook_link = Column(String(120))
    seeking_venue = Column(Boolean, default=False)
    seeking_description = Column(String(500))
    shows = relationship('Show', backref = 'Artist', lazy='dynamic')

    def info(self):
        return {
            'id': self.id,
            'name': self.name,
            'genres': self.genres.strip("{}").split(","),
            'city': self.city,
            'state': self.state,
            'phone': self.phone,
            'website': self.website,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'image_link': self.image_link,
        }


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(Base):
    __tablename__ = 'Show'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime, nullable=False)
    artist_id = Column(Integer, ForeignKey('Artist.id'), nullable=False)
    venue_id = Column(Integer, ForeignKey('Venue.id'), nullable=False) 

    def details(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def artist_info(self):
        return {
            'artist_id': self.artist_id,
            'artist_name': self.Artist.name,
            'artist_image_link': self.Artist.image_link,
            'start_time': self.start_time
        }

    def venue_info(self):
        return {
            'venue_id': self.venue_id,
            'venue_name': self.Venue.name,
            'venue_image_link': self.Venue.image_link,
            'start_time': self.start_time
        }
