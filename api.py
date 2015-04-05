'''The class only to expose our datastore through an API to Meteor App'''


import os
import cgi
import datetime
import jinja2
import webapp2

import datastore

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.write(*a,**kw)

	def render_Str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_Str(template, **kw))

	def authenticate(self):
		return True

class FrontPage(Handler):
	def get(self):
		if not authenticate():
			self.redirect("/unauth")
		self.write()


application = webapp2.WSGIApplication([
									('/home',FrontPage),
									('/products',Inventory),
									('/registration',Registration),
									('/getusers',PrintUsers),
									('/test',TestingServer),
									('/admin',PopulatingServer),
									('/unauth',UnAuthorized)
									], debug=True)
