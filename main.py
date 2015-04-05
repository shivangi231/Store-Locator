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
		self.response.headers['Content-Type'] = 'text/html'
		self.render("registration.html", userid = "Enter a unique user id", username = "Enter your name")

	def post(self):
		register_status = 0 #If status = 0, so far success. If it goes -1, something's wrong
		error = ''
		self.response.headers['Content-Type'] = 'text/html'
		__fname = self.request.get('fname')
		_lname = self.request.get('lname')
		_email=self.request.get('email')
		_password = self.request.get('pwd')
		_c_password = self.request.get('crpwd')


		_fname,error = utils.verify_name(_fname)
		_lname,error = utils.verify_name(_lname)
		_email,error = utils.verify_email(_email)
		_password,error = utils.verify_passwords(_password,_c_password)
		
		if _fname != '-1' or _lname != '-1' or _email != '-1' or _password != '-1':
			register_status,error = datastore.Users.register(_fname,_lname,_email,_password)	#Now contains user key
			print register_status
		else: 
			self.render("registration.html", error = error, fname = _fname, lname = _lname, email = _email)


		print "Successfully Registered"
		self.response.headers.add_header('Set-cookie', 'user = %s' % register_status[0])
		self.redirect("/")		#Change to homepage.

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
		#Check for cookies. If exist. or if not!
		_user = self.request.cookies.get('user','guest')
		_user = datastore.Users.checkUser(_user)
		if _user != -1:
			#User exists.
			self.render("home.html", user = _user.fname)
		else:
			self.response.headers.add_header('Set-cookie','user =  guest')
			self.render("home.html")

	def post(self): 	
		_email = self.request.get('email')
		_password = self.request.get('password')

		_password = utils.encrypt(_password)
		_user = datastore.Users.login(_email,_password)
		if _user == -1:
		 	#Incorrect credentials
		 	self.render("home.html", error = "Please recheck your credentials and try again,", email = _email)
		else:
		 	print "User successfully logged in!"
		 	self.response.headers.add_header('Set-cookie','user = %s' % _user)
		 	self.redirect("/")

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
									('/getusers',PrintUsers),
									('/test',TestingServer),
									('/admin',PopulatingServer),
									], debug=True)




#TODO
	#Fetch links,number of products and name of category
	#Implement basic search of sub categories. How? Well its really simple.
		#What i want to do is to simply - fetch all the things that carry the entire text of what we want!
