
from google.appengine.ext import ndb

class Booking(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()
	no_of_people = ndb.IntegerProperty()
	time_from = ndb.DateTimeProperty()
	time_to = ndb.DateTimeProperty()
	room_id = ndb.IntegerProperty()
	created = ndb.DateTimeProperty(auto_now_add=True)

class Room(ndb.Model):
    number = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)