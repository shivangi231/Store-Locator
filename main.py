import os
import cgi
import datetime
import jinja2
import webapp2

import datastore		#Our databases
import utils			#Misc utility class

print "Server starting"
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

	def check_cookies(self, handler, logout = False):
		_user = handler.request.cookies.get('user')
		_session = handler.request.cookies.get('session')
		if logout:
			_user = datastore.Users.logout(_user,_session)
			self.response.headers.add_header('Set-cookie','user = %s'%str(""))
			self.response.headers.add_header('Set-cookie','session = %s'%str(""))
			self.response.delete_cookie('user')
			self.response.delete_cookie('session')
			return _user

		_user = datastore.Users.checkValidSession(_user,_session)
		print "CHECKCOOKIES User found", _user
		return _user

class Registration(Handler):
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		self.render("registration_customer.html", fname = "First Name", lname = "Last Name", email = "Email ID")

	def post(self):
		register_status = 0 #If status = 0, so far success. If it goes -1, something's wrong
		error = ''
		self.response.headers['Content-Type'] = 'text/html'
		_fname = self.request.get('fname')
		_lname = self.request.get('lname')
		_email=self.request.get('email')
		_password = self.request.get('pwd')
		_c_password = self.request.get('crpwd')


		_fname,error = utils.verify_name(_fname)
		_lname,error = utils.verify_name(_lname)
		_email,error = utils.verify_email(_email)
		_password,error = utils.verify_passwords(_password,_c_password)
		
		if _fname != '-1' and _lname != '-1' and _email != '-1' and _password != '-1':
			register_status,error = datastore.Users.register(_fname,_lname,_email,_password)	#Now contains user key
			print "/registration-post: ", register_status
		else: 
			print "/registration-post : INCORRECT DETECTED"
			self.render("registration_customer.html", error = error, fname = _fname, lname = _lname, email = _email)
			return

		print "/registration-post: Successfully Registered"
		#self.response.headers.add_header('Set-cookie', 'user = %s' % register_status[0])
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
		_user = self.check_cookies(self)
		if _user != -1:
			#User exists and cookie is correct.
			self.render("home.html", user = _user.fname)
		else:
			#self.response.headers.add_header('Set-cookie','user =  guest')
			print "NO COOKIE FOUND ON HOME PAGE"
			self.render("home.html")

	def post(self): 	
		_email = self.request.get('email')
		_password = self.request.get('password')

		_password = utils.encrypt(_password)
		_user = datastore.Users.login(_email,_password)

		if _user == -1:
		 	print "Incorrect credentials"
		 	self.render("home.html", error = "Please recheck your credentials and try again,", email = _email)
		else:
		 	print "User successfully logged in!", _user
		 	self.response.headers.add_header('Set-cookie','user = %s' % _user[1].key.id())
		 	self.response.headers.add_header('Set-cookie','session = %s' % _user[0])
		 	self.redirect("/loggedin")

class PrintUsers(Handler):
	def get(self):
		print "/getusers-get"
		queries = datastore.Users.getUserIDs()
		for query in queries:
			self.write("<p>%s</p>" % query)

class WelcomePage(Handler):
	def get(self):
		_user = self.check_cookies(self)
		if _user != -1:
			self.write(_user.fname)

class LogoutPage(Handler):
	def get(self):
		url =  self.request.get('url')
		print "INITIATING LOGOUT ", url
		self.check_cookies(self,logout = True)
		self.redirect(url)

class SearchPageProduct(Handler):
	def get(self):
		self.write('''<form method = "post"> <input type = "input" name = "query"> </form>''')

	def post(self):
		query = self.request.get('query')
		#print query
		categories = []
		products = []
		products_category = []
		products_brand = []
		brands = []
		found_category = False		
		found_brand = False
		found_products = False
		done =  False

		#First try to locate category.
		#Here i am assuming that if we have found a match for category, then we don't need to investigate on this front further. Simply return a one tuple list in the function
		#Further, simply fetch products relevent to the category and proceed to render them.
		categories = datastore.Categories.locate(query)
		#print categories
		if utils.found_match(categories):
			found_category = True
			print "SEARCH : found category", categories
			categories = utils.return_match(categories)
			products_category +=  utils.add_similarity(datastore.Products.getProductsInCategory(categories[0][0]))		#Added dummy similarity only for the sake of further operations
			categories += datastore.Categories.getChildren(categories[0][0])
			#Categories now have children & we also have products to show.

		# Then we attempt a brand match
		brands = datastore.Products.searchBrand(query)
		if utils.found_match(brands):
			found_brand = True
			print "SEARCH : found brand!"
			brands = utils.return_match(brands)
			products_brand += utils.add_similarity(datastore.Products.getProductsInBrands(brands[0][0]))						#Added dummy similarity only for the sake of further operations
			#Now we have products of a brand to show!

		#print "Reached Here"
		#Then we proceed to find some relevent products
		products = utils.sort(datastore.Products.searchProduct(query,_ease = 70))		
		if utils.found_match(products):
			#We have found some products spot on. So now simply render these products along with some products from the brand and some from the categories. (If they were spot on too!)
			products = utils.return_upto(products,_ease = 85)
			found_products = True

		products = utils.join(products,products_brand,products_category,_distinct = True)
		print "SEARCH: product lenght: ", len(products)

		#Evaluate our current situation. 
		if not found_brand and not found_products and not found_products:
			#At this point, assuming we have neither products or brands or categories match or even products match!
			#We search for categories in a relaxed manner. And we search for products. Forget brand!
			categories = datastore.Categories.search(query,_ease = 70,_getchild = True)
			brands =  datastore.Products.searchBrand(query,_ease = 70)

			if len(categories) > 0:
				products_category +=  utils.add_similarity(datastore.Products.getProductsInCategories(utils.remove_similarity(categories)))
				if utils.found_match(categories,_ease = 80):
					found_category = True
			if len(brands) > 0:
				if utils.found_match(brands,_ease = 80):
					found_brand = True
				products_brand += utils.add_similarity(datastore.Products.getProductsInBrands(utils.remove_similarity(brands)))

			#We might not have any meaningful search but we have found some products.
			products = utils.join(products,products_brand,products_category,_distinct = True)
			if len(products) > 1:
				#Just simply render these products and categories and be done with it.
				done = True

		else:
			done = True

		####################### We are done finding products. Now second and easier part!####################
		if done:
			#We have two arrays to show.
				#Products
				#Categories

			#We also know that the products will contain the relevant products from the categories if there were any, in the first place!
			#But we don't know if we have enough categories to show. Or if categories match with the products required!
			if len(categories) < 5 and not found_category:
				categories += utils.add_similarity(datastore.Products.getCategoriesForProducts(utils.remove_similarity(products)))

			#Finally render the two arrays	
			self.render("search.html",products = utils.remove_similarity(products), categories = utils.remove_similarity(categories))

		else:
			#If we are still not done, it could mean only one thing that we have not found any match whatsoever!
			#Throw error message
			self.write("Sorry no product found. Please go back and try again")

class ShoppingListPage(Handler):
	def get(self):
		#Authenticate the user based on cookies. See get of mainpage on how to do so.

		return True
		#Fetch user's shopping list



		#Render the shopping list page. by simply sending the required data to frontend through self.render
			#See how i rendered data in search page

class ShoppingListAdd(Handler):
	def get(self):
		#Authenticate the user based on cookies. See get of mainpage on how to do so.

		return True
	

class ShoppingListRemove(Handler):
	def get(self):
		#Authenticate the user based on cookies. See get of mainpage on how to do so.

		return True
	


application = webapp2.WSGIApplication([
									('/',MainPage),
									('/products',ProductsPage),
									('/registration',Registration),
									('/getusers',PrintUsers),
									('/test',TestingServer),
									('/admin',PopulatingServer),
									('/loggedin',WelcomePage),
									('/logout',LogoutPage),
									('/search',SearchPageProduct),
									('/shoppinglist',ShoppingListPage),
									('/addshoppinglist',ShoppingListAdd),
									('/removeshoppinglist',ShoppingListRemove)
									], debug=True)

