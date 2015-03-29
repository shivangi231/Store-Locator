import os
import cgi
import datetime
import jinja2
import webapp2
from google.appengine.ext import ndb 

#Setup templating engine - Jinja2
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


#Setup Users DB. and its methods acting as wrappers
class Users(ndb.Model):
	userid = ndb.StringProperty()
	username = ndb.StringProperty()
	password = ndb.StringProperty()
	visits = ndb.IntegerProperty()

	@classmethod
	def getUserIDs(self):
		users = []
		query = self.query(projection=[Users.userid])
		for user in query: users.append(str(user.userid))
		print users
		return users

	@classmethod
	def register(self,_userid,_username,_password):
		print "Registering %s" %_username
		if not _userid in self.getUserIDs():
			user = Users(userid = _userid, username = _username, password = _password)
			user.put()
			return (0,'Success')
		else:
			return (-1,'Userid already exists. Please select a different one')			

class Registration(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.render("registration.html", userid = "Enter a unique userid", username = "Enter your name")

	def post(self):
		register_status = (0,'Not begun yet') #If status = 0, so far success. If it goes -1, something's wrong
		self.response.headers['Content-Type'] = 'text/html'
		_userid = self.request.get('userid')
		_username = self.request.get('username')
		_password = self.request.get('password')
		_c_password = self.request.get('c_password')

		_username = str(cgi.escape(_username,quote="True"))
		_userid = str(cgi.escape(_userid,quote="True"))

		#Encrypt the pwd

		#Fix the value of all inputs
		if _password != _c_password:
			register_status = (-1,'The passwords do not match!')

		#Attempt to register. Return value corresponding to success or failure
		if register_status[0] == 0:
			register_status = Users.register(_userid,_username,_password)
			print register_status
		

		if register_status[0] != 0:
			self.render("registration.html", error = register_status[1], userid = _userid, username = _username)
		else:
			self.redirect("/getusers/")		#Change to homepage.


class MainPage(Handler):
	def get(self):
		self.write("Welcome!")

class PrintUsers(Handler):
	def get(self):
		queries = Users.getUserIDs()
		for query in queries:
			self.write("<p>%s</p>" % query)

application = webapp2.WSGIApplication([
									('/',MainPage),
									('/registration',Registration),
									('/getusers/',PrintUsers)
									], debug=True)


