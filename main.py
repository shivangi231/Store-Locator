import os
import cgi
import datetime
import jinja2
import webapp2

import datastore		#Our databases



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


class Registration(Handler):
	def get(self):
		print "/registration-get"
		self.response.headers['Content-Type'] = 'text/html'
		self.render("registration.html", userid = "Enter a unique user id", username = "Enter your name")

	def post(self):
		print "/registration-post"
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
			register_status = datastore.Users.register(_userid,_username,_password)
			print register_status

		if register_status[0] != 0:
			self.render("registration.html", error = register_status[1], userid = _userid, username = _username)
		else:
			self.redirect("/getusers/")		#Change to homepage.

class ProductsPage(Handler):
	def get(self):
		#Categories.populate()
		#Products.populate()
		categories = Products.getAll()
		self.write("<ul>")
		for cat in categories:
			entry = "<li>"+ cat + "</li>"
			self.write(entry)
		self.render("testpage.html")

	def post(self):
		_query = self.request.get('query')
		_category = self.request.get('category')
		#categories = Products.searchProduct(_query)
		#for cat in categories:
		#	entry = "<li>" + cat[0].name + " URL: " + cat[0].key.urlsafe() + " BRAND: " + cat[0].brand + "</li>"
		#	self.write(entry)
		brands = datastore.Products.searchProductsInCategory(_query,_category)
		for b in brands:
			entry = "<li>" + b[0].name + " URL: " + b[0].key.urlsafe() + " BRAND: " + b[0].brand + "</li>"
			self.write(entry)

class TestingServer(Handler):
	def get(self):
		roots = datastore.Categories.getRoots()
		for root in roots:
			line = "<li>" + root.name + "</li>"
			self.write(line)

class PopulatingServer(Handler):
	def get(self):
		datastore.Categories.populate()
		self.write('<form method = "post"> <input type="submit"> </form>')
		
	def post(self):
		datastore.Products.populate()


class MainPage(Handler):
	def get(self):
		print "/-get"
		self.write("Welcome!")

class PrintUsers(Handler):
	def get(self):
		print "/getusers-get"
		queries = datastore.Users.getUserIDs()
		for query in queries:
			self.write("<p>%s</p>" % query)

application = webapp2.WSGIApplication([
									('/',MainPage),
									('/products',ProductsPage),
									('/registration',Registration),
									('/getusers/',PrintUsers),
									('/test/',TestingServer),
									('/admin/',PopulatingServer)
									], debug=True)




#TODO
	#Fetch links,number of products and name of category
	#Implement basic search of sub categories. How? Well its really simple.
		#What i want to do is to simply - fetch all the things that carry the entire text of what we want!
