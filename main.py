import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
from models import *
from handlers import *
import os

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class MainPage(webapp2.RequestHandler):

    def __init__(self, request, response):

        self.initialize(request, response)

        user = users.get_current_user()

        if user:
            url = users.create_logout_url(self.request.uri)
            url_string = 'logout'

        else:
            url = users.create_login_url(self.request.uri)
            url_string = 'login'

        self.template_values = {
            'url' : url,
            'url_string' : url_string,
            'user' : user
        }

        self.query = Room.query(ancestor=ndb.Key(Room, 'Room'))

    def get_rooms(self):

        return self.query.fetch(projection=[Room.number])

    def get(self):

        self.response.headers['Content-Type'] = 'text/html'

        if self.template_values['user']:

            self.template_values.update({'rooms' : self.get_rooms()})

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(self.template_values))

    def post(self):

        self.response.headers['Content-Type'] = 'text/html'

        if not self.template_values['user']:

            self.redirect('/')

        button = self.request.get('button')

        if button == 'Create':

            room_number = self.request.get('no')
            room_number = int(room_number) if room_number else 0
            error = ''
          
            if room_number > 0:

                if self.query.filter(Room.number == room_number).count() == 0:

                    Room(parent=ndb.Key(Room, 'Room'), number=room_number).put()
                    self.redirect('/')

                else:
                    error = "A room with the same room number already exists"

            else:
                error = "Please type in a room number greater than 1"

            self.template_values['error'] = error
            self.template_values['rooms'] = self.get_rooms()

        elif button == 'Filter':

            bookings = []
            date = self.request.get('date')

            if date:

                date = datetime.strptime(date, '%Y-%m-%d').date()

                for b in Booking.query(ancestor=ndb.Key(Booking, 'Booking')).fetch():
                    if b.time_from.date() <= date and b.time_to.date() >= date:
                        bookings.append(b)

            self.template_values.update({
                'bookings' : bookings,
                'filter' : date
            })

        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(self.template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/booking', BookingHandler)
], debug = True)
