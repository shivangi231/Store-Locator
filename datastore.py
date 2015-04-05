from google.appengine.ext import ndb 
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError
import catalogue					#TO populate the Categories DB
from fuzzywuzzy import fuzz 		#For better search
import datetime
import random
import utils

#Categories DB
class Categories(ndb.Model):
	name = ndb.StringProperty(required = True)
	children = ndb.StringProperty(repeated = True)

	@classmethod
	def populate(self):
		products = catalogue.getCategories()
		for product in products:
			_name = product[0]			#The product name is supposed to be unique. ASSUMED!
			if len(product) > 1:
				_children = product[1]
				entity = Categories(name = _name, children = _children)
			else:
				entity = Categories(name = _name)
			entity.put()

	@classmethod
	def isLeaf(self,_category_key):
		category = _category_key.get()
		if len(category.children) > 0:
			return False
		return True

	@classmethod
	def getLeafs(self,_category_key):
		#To find all the leaf categories. (Which have no children)
		#Will return itself if it is the leaf.
		if self.isLeaf(_category_key):
			return _category_key.get()
		
		category = _category_key.get()
		children = self.getChildren(category)

		while True:
			all_leaves = True
			new_list = []
			for child in children:
				if not self.isLeaf(child.key):
					all_leaves = False
					new_list += self.getChildren(child)
				else:
					new_list.append(child)
			children = new_list
			if all_leaves:
				break

		return children

	@classmethod
	def search(self,_name,_getchild = True,_ease = 90):
		#Get a list of categories which have the argument string in it.
		#query = self.locate(_name,_getchild = True)

		results = []
		query = Categories.query().fetch()
		for q in query:
			similarity = fuzz.partial_ratio(_name.lower(), q.name.lower())
			if similarity >= _ease:
				results.append(q)
			if similarity == 100:
				results = [q]
				break

		if _getchild:
			for q in results:
				children += self.getChildren(q)

		return results

	@classmethod
	def getAll(self):
		query = self.query()
		categories = []
		for category in query: categories.append(category.name + " " +category.key.urlsafe())
		#print categories
		return categories

	@classmethod
	def getProducts(self,key = ''):
		query = Products.query(Products.category == key)
		return query.fetch()

	@classmethod 	#Obsolete method of dumb  but fast keyword finding. Use only for quick results
	def locate_primitive(self,_name,getchild = False):
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
	def locate(self,_name,_getchild = False, _ease = 85):
		results = []
		children = []
		query = ndb.gql("SELECT * FROM Categories")
		for q  in query:
			similarity = fuzz.ratio(_name.lower(),q.name.lower())
			if similarity == 100:
				results = [q]
				break
			if similarity >= _ease:
				results.append(q)

		if _getchild:
			for q in results:
				children += self.getChildren(q)
				
		return results + children

	@classmethod
	def getChildren(self,_cat):
		_cat_children = []
		for child in _cat.children:
			for cat in self.locate_primitive(child):
				_cat_children.append(cat)
		#print _cat_children
		return _cat_children


	@classmethod
	def getRoots(self):
		root=[]
		children=[]
		all1 = ndb.gql("SELECT * FROM Categories").fetch()
		#Made a copy of all categories
		root = all1[:]
		for q in all1:
			children = self.getChildren(q)
			for child in children:
				for r in root:
					if r.key == child.key:
						print "REMOVING", r.name
						root.remove(r)
		print len(all1), len(root)
		return root

	@classmethod
	def getAllLeaves(self):
		leaves = ndb.gql("SELECT * from Categories").fetch()
		for element in leaves:
			if not self.isLeaf(element.key):
				leaves.remove(element)
		return leaves
		

#Products DB
class Products(ndb.Model):
	name = ndb.StringProperty(required = True)
	description = ndb.TextProperty()
	popularity = ndb.IntegerProperty()
	category = ndb.KeyProperty(kind = Categories)
	brand = ndb.StringProperty()
	#shopkeeper = ndb.KeyProperty(kind = Shopkeepers)

	@classmethod
	def populate(self):
		products = catalogue.getProducts()
		for product in products:
			#print product
			_name = product[0]
			_brand = product[1]
			_category = Categories.locate_primitive(product[2])[0].key #The numeric key.
			entity = Products(name = _name, brand = _brand, category = _category)
			entity.put()

	@classmethod
	def searchProduct(self,_name,_ease = 70):
		#just find products equal or similar to this
		query = Products.query()

		if _ease > 100:
			_ease = 100

		results = []
		for q in query:
			similarity = fuzz.partial_ratio(q.name,_name)
			if similarity >= _ease:
				results.append((q,similarity))

		return results

	@classmethod
	def searchBrand(self, _name,_ease = 90):
		brand = ''		#The name of the brand. args may have a name similar but not equal. Hence this precaution.
		query = ndb.gql("SELECT DISTINCT brand from Products").fetch()
		#Try printing?
		#print query
		probable_brands = []

		if _ease > 100:
			_ease = 100

		for q in query:
			#First try looking for ratio match.
			similarity = fuzz.partial_ratio(_name.lower(),q.brand.lower())
			#print similarity,_name,q.brand
			if similarity == 100:
				probable_brands = [(q.brand,100)]
				break
			if similarity >= _ease:
				probable_brands.append((q.brand,similarity))

		return probable_brands

	@classmethod
	def searchProductsInCategory(self,_name, _category, _ease = 60):
		#Expects category's name
		_category = Categories.locate(_category,_ease = 60)
		if len(_category) > 0:
			_category = _category[0]
		else:
			return
		

		if not Categories.isLeaf(_category.key):
			return self.searchProductInCategories(_name, Categories.getLeafs(_category.key))

		#Category found in case of leaf, almost perfectly.
		query = Products.query(Products.category == _category.key).fetch()
		
		if _ease > 100:
			_ease = 100

		results = []
		for q in query:
			similarity = fuzz.partial_ratio(q.name,_name)
			if similarity >= _ease:
				results.append((q,similarity))

		#print results
		return results

	@classmethod
	def searchProductInCategories(self,_name,_categories,_ease = 70):
		#Expects categories entity
		_categories_key = []
		for x in _categories: _categories_key.append(x.key)
		query = Products.query(Products.category.IN(_categories_key)).fetch()
		
		if _ease > 100:
			_ease = 100

		results = []
		for q in query:
			similarity = fuzz.token_set_ratio(q.name,_name)
			if similarity >= _ease:
				results.append((q,similarity))

		return results

	@classmethod
	def searchProductInBrand(self,_name,_brand,_ease = 70):
		#Expects consise brand to be known!
		query = Products.query(Products.brand == _brand).fetch()
		
		if _ease > 100:
			_ease = 100

		results = []
		for q in query:
			similarity = fuzz.token_set_ratio(q.name,_name)
			if similarity >= _ease:
				results.append((q,similarity))

		return results		

	@classmethod
	def searchProductInBrands(self,_name,_brands,_ease = 70):
		#Expects brand name to be actual
		query = Products.query(Products.brand.IN(_brands)).fetch()
		
		if _ease > 100:
			_ease = 100

		results = []
		for q in query:
			similarity = fuzz.token_set_ratio(q.name,_name)
			if similarity >= _ease:
				results.append((q,similarity))

		return results		


	@classmethod
	def getAll(self):
		query = self.query().fetch()
		products = []
		for q in query: products.append(q.name + ' B: ' + q.brand + ' C: ' + q.category.urlsafe() + ' K: ' + q.key.urlsafe())
		return products

	@classmethod
	def getProductsInBrand(self,_brand,_ease = 80):
		_brands = self.assure(self.searchBrand(_brand,_ease = 60))
		if len(_brands) > 0:
			_brand = _brands[0]
		else:
			return []
		return Products.query(Products.brand == _brand[0]).fetch()

	@classmethod
	def assure(self,_list):
		#Expected a list of tuples (entity, similarity index). Will sort and return all minus the index
		return sorted(_list, key=lambda tup: tup[1])		


#Setup Users DB. and its methods acting as wrappers
class Users(ndb.Model):
	fname = ndb.StringProperty()
	lname = ndb.StringProperty()
	email = ndb.StringProperty()
	password = ndb.StringProperty()
	active_sessions = ndb.PickleProperty(repeated = True)

	@classmethod
	def getUserIDs(self):
		users = []
		query = self.query(projection=[Users.userid])
		for user in query: users.append(str(user.userid))
		print users
		return users
		
	@classmethod
	def register(self,_fname,_lname,_email,_password):
		#print "Registering %s" %_username
		query = Users.query(Users.email == _email).fetch()
		if len(query) > 0:
			return (-1,'There already exists an account with this email ID.')			
		else:
			user = Users(fname = _fname, lname = _lname, email=_email, password = _password)
			key = user.put()
			return (key.urlsafe(),'Registered Successfully.')

	@classmethod
	def checkValidSession(self,_user,_session):
		#Forst check for the user
		print "Checking for user based on userid", _user
		users = Users.query()
		user = None
		for u in users:
			if str(u.key.id()) == _user:
				user = u
				break

		print user
		result = -1
		if not user:
			return result

		for session in user.active_sessions:
			print session[0], _session
			if session[0] == _session:
				if utils.time_difference(session[1],str(datetime.datetime.now()),7) :
					result = user
		return result

	@classmethod
	def createSessionID(self,_user):
		#Expects real user entity
		time = str(datetime.datetime.now())
		string = utils.encrypt(utils.generate_string())
		_user.active_sessions = _user.active_sessions + [(string,time)]
		_user.put()
		#print "Users-createSessionID: Created new ID for ", _user.email
		return (string,time)
			
	@classmethod
	def login(self,_email,_password):
		session = (-1,'Does not exist')
		_user = -1
		query = Users.query(Users.email == _email).fetch()
		for q in query:
			if q.password == _password:
				_user = q
				session = self.createSessionID(q)

		print "LOGIN FOUND USER: ",_user

		if not _user == -1:
			return (session[0],_user)
		else:
			print "Users-login UNSUCCESSFUL"
			return (-1,-1)

	@classmethod
	def logout(self,_user,_session):
		print "Checking for user based on userid", _user
		users = Users.query()
		user = None
		for u in users:
			if str(u.key.id()) == _user:
				user = u
				break

		print user
		result = -1
		if not user:
			return result

		for session in user.active_sessions[:]:
			print session[0], _session
			if session[0] == _session:
				remaining_session  = []
				for s in user.active_sessions:
					if not s == session:
						remaining_session.append(s)
				user.active_sessions = remaining_session
				user.put()
				result = user
				break
				
		return result

