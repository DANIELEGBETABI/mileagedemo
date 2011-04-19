import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Fillup(db.Model):
    user = db.UserProperty()
    miles = db.FloatProperty()
    gal = db.FloatProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MPG(db.Model):
    user = db.UserProperty()
    totalMiles = db.FloatProperty()
    totalGal = db.FloatProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        fillup_query = Fillup.all().order('-date').filter('user = ', users.get_current_user())
        fillups = fillup_query.fetch(10)
        totalMPG_query = MPG.all().order('-date').filter('user = ', users.get_current_user())    
        if not totalMPG_query.fetch(1):
            user_mpg_total = ""
        else:
            user_MPG = totalMPG_query.fetch(1)[0]
            user_mpg_total = "%.2f" % (user_MPG.totalMiles / user_MPG.totalGal)
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        template_values = {
            'user_mpg_total':user_mpg_total,
            'fillups': fillups,
            'url': url,
            'url_linktext': url_linktext,
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class NewFillup(webapp.RequestHandler):
    def post(self):
        fillup = Fillup()
        fillup.user = users.get_current_user()
        fillup.miles = float(self.request.get('miles'))
        fillup.gal = float(self.request.get('gal'))
        fillup.put()
        totalMPG_query = MPG.all().order('-date').filter('user = ', users.get_current_user())
        if not totalMPG_query.fetch(1):
            user_MPG = MPG()
            user_MPG.user = users.get_current_user()
            user_MPG.totalMiles = fillup.miles
            user_MPG.totalGal = fillup.gal 
            user_MPG.put()
        else:
            user_MPG = totalMPG_query.fetch(1)[0]
            user_MPG.totalMiles = user_MPG.totalMiles + fillup.miles
            user_MPG.totalGal = user_MPG.totalGal + fillup.gal  
            user_MPG.put()
        self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/newfillup', NewFillup)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()

