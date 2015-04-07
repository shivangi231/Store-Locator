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
		_shop = handler.request.cookies.get('shop')
		_session = handler.request.cookies.get('session_shop')
		self.response.delete_cookie('user')
		self.response.delete_cookie('session')
		print "check_cookies: ", _shop, _session
		if logout:
			_shop = datastore.Shops.logout(_shop,_session)
			self.response.headers.add_header('Set-cookie','shop = %s'%str(""))
			self.response.headers.add_header('Set-cookie','session = %s'%str(""))
			self.response.delete_cookie('shop')
			self.response.delete_cookie('session')
			return _shop

		_shop = datastore.Shops.checkValidSession(_shop,_session)
		print "check_cookies User found", _shop
		return _shop

class RegistrationPage(Handler):
	def get(self):
		self.response.headers['Content-Type']='text/html'
		self.render("shop_reg.html",fname = 'First Name', lname = 'Last Name', email = 'Email Address', mobile = 'Mobile Number', shop_name = 'Shop Name', shop_add = 'Shop Address')

	def post(self):
		register_status = 0
		error = ''
		_fname=self.request.get('fname')
		_lname=self.request.get('lname')
		_email=self.request.get('email')
		_password=self.request.get('pwd')
		_c_password=self.request.get('crpwd')
		_mobile=self.request.get('mobile')
		_shop_name=self.request.get('shop_name')
		_shop_address=self.request.get('shop_add')
	
		_fname,error = utils.verify_name(_fname)
		_lname,error = utils.verify_name(_lname)
		_email,error = utils.verify_email(_email)
		_password,error = utils.verify_passwords(_password,_c_password)
		_mobile,error = utils.verify_mobile(_mobile)
		_shop_name,error = utils.verify_name(_shop_name)
		_shop_address,error = utils.verify_text(_shop_address)

		print "/registration-post: fname", _fname
		print "/registration-post: lname", _lname
		print "/registration-post: email", _email
		print "/registration-post: mobile", _mobile
		print "/registration-post: shopname", _shop_name
		print "/registration-post: shopaddress", _shop_address
		print "/registration-post: password", _password

		if _fname != '-1' and _lname != '-1' and _email != '-1' and _password != '-1' and _mobile != '-1' and _shop_address != '-1' and _shop_name != '-1':
			register_status,error = datastore.Shops.register(_email,_fname,_lname,_password,_mobile,_shop_name,_shop_address)
			print "/registration-post: ", register_status
		else:
			print "/registration-post: incorrect inputs"
			print "/registration-post: fname", _fname
			print "/registration-post: lname", _lname
			print "/registration-post: email", _email
			print "/registration-post: mobile", _mobile
			print "/registration-post: shopname", _shop_name
			print "/registration-post: shopaddress", _shop_address
			print "/registration-post: password", _password
			self.render("shop_reg.html", error = error, fname = _fname, lname = _lname, email = _email, mobile = _mobile, shop_name = _shop_name, shop_add = _shop_address)
			return
		
		print "/registration-post: successfully registered"
		self.redirect("/shop/")

class MainPage(Handler):
	def get(self):
		_shop =  self.check_cookies(self)
		if _shop != -1:
			print "mainpage-get: found shop", _shop
			self.redirect("/shop/profile")
		else:
			print "mainpage-get: no shop found in cookies"
			self.render("shop_home.html")

	def post(self):
		#LOGIN Feature
		_email = self.request.get('email')
		_password = self.request.get('password')

		print "mainpage-post: ", _email, _password
		_password = utils.encrypt(_password)
		_shop = datastore.Shops.login(_email,_password)

		if _shop == -1:
			print "mainpage-post: incorrect credentials"
			self.render("shop_home.html", error = "Invalid username or password", email = _email)
		else:
			print "mainpage-post: shop logged in", _shop
			self.response.headers.add_header('Set-cookie','shop = %s' % _shop[1].key.id())
			self.response.headers.add_header('Set-cookie','session_shop = %s' % _shop[0])
			self.redirect("/shop/profile")			

class ProfilePage(Handler):
	def get(self):
		_shop = self.check_cookies(self)
		if _shop != -1:
			print "profile-get: found shop", _shop
			self.render("shop_profile.html", shopname = _shop.shop_name)
		else:
			print "profile-get: no shop found in cookies"
			self.redirect("/shop/")

class LocationPage(Handler):
	def get(self):
		_shop =  self.check_cookies(self)
		if _shop != -1:
			#Authenticated
			print "location-page: found shop", shop_name
			self.render("map.html")
		else:
			self.redirect("/shop/")
	def post(self):
		_lat=self.request.get('lat')
		_log=self.request.get('long')


application = webapp2.WSGIApplication([('/shop/',MainPage),
									 ('/shop/register',RegistrationPage),
									 ('/shop/profile',ProfilePage),
									 ('/shop/getlocation',LocationPage)
									 ], debug=True)