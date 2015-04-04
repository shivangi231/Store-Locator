import webapp2
import os
import jinja2
import cgi
from google.appengine.ext import ndb 

#Custom imports
import catalogue		#TO populate the DB

from fuzzywuzzy import fuzz

#Setup templating engine
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

#Categories DB
class Categories(ndb.Expando):
	name = ndb.StringProperty(required = True)
	children = ndb.StringProperty(repeated = True)

	@classmethod
	def populate(self):
		products = catalogue.getProducts()
		print "PRODUCTS -", products
		for product in products:
			_name = product[0]			#The product name is supposed to be unique. ASSUMED!
			if len(product) > 1:
				_children = product[1]
				entity = Categories(name = _name, children = _children)
			else:
				entity = Categories(name = _name)
			entity.put()

	@classmethod
	def search(self,_name):
		#Get a list of categories which have the argument string in it.
		query = self.locate(_name,getchild = True)
		if len(query) > 1:
			#print query[1]
			return query

		results = []
		query = Categories.query().fetch()
		for q in query:
			if _name in q.name.split():
				results.append(q)
		return results

	@classmethod
	def getAll(self):
		query = self.query()
		categories = []
		for category in query: categories.append(category.name + " " +category.key.urlsafe())
		print categories
		return categories

	@classmethod
	def getProducts(self,key = ''):
		query = Products.query(Products.category == key)
		return query.fetch()

	@classmethod
	def locate(self,_name,getchild = False):
		#simply does a strict string match search. MAY RETURN MORE THAN ONE RESULT!
		query = Categories.query(Categories.name == _name).fetch()
		children = []
		if getchild:
			for q in query:
				child = self.getChildren(q)
				for c in child:
					children.append(c)
		query += children
		return query

	@classmethod
	def getChildren(self,_cat):
		_cat_children = []
		for child in _cat.children:
			for cat in self.locate(child):
				_cat_children.append(cat)
		print _cat_children
		return _cat_children

	
#Products DB
class Products(ndb.Model):
	name = ndb.StringProperty(required = True)
	description = ndb.TextProperty()
	popularity = ndb.IntegerProperty()
	category = ndb.KeyProperty(kind = Categories)
	brand = ndb.StringProperty()
	#shopkeeper = ndb.KeyProperty(kind = Shopkeepers)

	@classmethod
	def searchBrand(self, _name,_ease = 90):
		#The scope of this 
		brand = ''		#The name of the brand. args may have a name similar but not equal. Hence this precaution.
		query = ndb.gql("SELECT DISTINCT brand from Products").fetch()
		#Try printing?
		probable_brands = []
		for q in query:
			#First try looking for ratio match.
			similarity = fuzz.ratio(_name,q.brand)
			if similarity >= _ease:
				probable_brands = (q.brand,similarity)
				if similarity == 100:
					probable_brands = [(q.brand,100)]
					break

		#Probable brand now contains either the perfect match or some matches or NONE!.
		#If perfect match or just one match, then that is the brand we are looking for and fetch all products for this brand.
		#if len(probable_brands) == 1:

			 






#Basic
class MainPage(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		visits = self.request.cookies.get('visits','0')
		userid = self.request.cookies.get('userid','guest')
		if visits.isdigit():
			visits = int(visits) + 1
		else:
			visits = 0
		self.render("login.html", visits = visits)
		self.response.headers.add_header('Set-cookie', 'visits = %s' % visits)
		self.response.headers.add_header('Set-cookie', 'userid = %s' % str(userid))

	def post(self):

		#Fetch the username, from the form and from the cookie.
		self.response.headers['Content-Type'] = 'text/html'
		userid_from_cookies = self.request.cookies.get('userid','guest')
		userid_from_form = self.request.get('username')
		visits = self.request.cookies.get('visits','0')

		#Print out the number of visits
		if visits.isdigit():
			visits = int(visits) + 1
		else:
			visits = 0

		#If the names don't match, then simply welcome the new user differently.
		if userid_from_form != userid_from_cookies:
			self.write("Welcome Mr. %s" % userid_from_form)
			visits = 0
		
		#Set cookies
		self.response.headers.add_header('Set-cookie', 'visits = %s' % visits)
		self.response.headers.add_header('Set-cookie', 'userid = %s' % str(userid_from_form))

		#Render the form
		self.render("welcome.html", visits = visits)	


class ProductsPage(Handler):
	def get(self):
		#Categories.populate()
		categories = Categories.getAll()
		self.write("<ul>")
		for cat in categories:
			entry = "<li>"+ cat + "</li>"
			self.write(entry)
		self.render("testpage.html")

	def post(self):
		_query = self.request.get('query')
		categories = Categories.search(_query)
		for cat in categories:
			entry = "<li>" + cat.name + " " + cat.key.urlsafe() + "</li>"
			self.write(entry)



application = webapp2.WSGIApplication([
									('/',MainPage),
									('/products',ProductsPage)
									], debug=True)




#TODO
	#Fetch links,number of products and name of category
	#Implement basic search of sub categories. How? Well its really simple.
		#What i want to do is to simply - fetch all the things that carry the entire text of what we want!
