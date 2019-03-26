import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from models import *
from funcs import *
from datetime import datetime, timedelta

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class BookingHandler(webapp2.RequestHandler):

    def __init__(self, request, response):
        self.initialize(request, response)
        checklogin(users.get_current_user(), self)

        self.room = ndb.Key(urlsafe=self.request.get('k')).get()

        self.query = Booking.query(ancestor=ndb.Key(Booking, 'Booking')).filter(Booking.room_id == self.room.key.id())

        self.template_values = {
            'room' : self.room,
            'has_bookings': self.has_bookings(),
            'url' : users.create_logout_url(self.request.uri),
            'url_string' : 'logout'
        }

    def get_bookings(self):

        return self.query.order(Booking.created).fetch()

    def has_bookings(self):

        return self.query.count(limit=1) > 0

    def delete_booking(self):

        booking = ndb.Key(urlsafe=self.request.get('d')).get()
        
        if booking and booking.room_id == self.room.key.id():
            booking.key.delete()

        self.redirect('booking?k=' + self.room.key.urlsafe())

    def delete_room(self):

        if not self.template_values['has_bookings']:
            self.room.key.delete()
            self.redirect('/')

        else:
            self.redirect('booking?k=' + self.room.key.urlsafe())

    def get(self):
        
        self.response.headers['Content-Type'] = 'text/html'  

        if self.request.get('d'):
            self.delete_booking()

        elif self.request.get('remove'):
            self.delete_room()

        elif self.request.get('deleteAll'):

            now = datetime.now().replace(microsecond=0)
            for b in self.query.fetch(projection=[Booking.time_to]):
                if b.time_to <= now:
                    b.key.delete()

            self.redirect('booking?k=' + self.room.key.urlsafe())         

        self.template_values.update({
            'booking': Booking(),
            'bookings': self.get_bookings()
        })

        template = JINJA_ENVIRONMENT.get_template('booking_form.html')
        self.response.write(template.render(self.template_values))

    def post(self):

        self.response.headers['Content-Type'] = 'text/html'

        button = self.request.get('button')

        error = ''

        if button == 'Book':

            booking = Booking(parent=ndb.Key(Booking, 'Booking'))
            booking.room_id = self.room.key.id()

            booking.name = self.request.get('name').strip()

            if not booking.name:
                error = "Please type in your full name"

            booking.email = self.request.get('email').strip()

            if not booking.email:
                error = "Please type in a correct email address"

            people = self.request.get('no_of_people')

            if not people or people == '0':
                error = "No of People must be greater than 1"
            else:
                booking.no_of_people = int(people)

            if self.request.get('from') and self.request.get('to'):

                booking.time_from = datetime.strptime(self.request.get('from'), '%Y-%m-%dT%H:%M')
                booking.time_to = datetime.strptime(self.request.get('to'), '%Y-%m-%dT%H:%M')

                if booking.time_to > booking.time_from and booking.time_from > datetime.now():

                    clash = False

                    for b in self.query.filter(Booking.time_to > booking.time_from).fetch(projection=[Booking.time_from]):

                        clash = b.time_from <= booking.time_to
                        if clash:
                            break

                    if not clash:
                        booking.put()
                        self.redirect('/booking?k=' + self.room.key.urlsafe())
                        
                    else:
                        error = "Choose a date that does not overlap with an existing booking"
                
                else:
                    error = "Select future dates and make sure To is later than From "

            else:
                error = "Select correct values for From and To"

            self.template_values.update({
                'booking': booking,
                'bookings': self.get_bookings(),
                'error' : error
            })

            template = JINJA_ENVIRONMENT.get_template('booking_form.html')
            self.response.write(template.render(self.template_values))

        else:
            self.redirect('/')
