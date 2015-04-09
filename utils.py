import os
import cgi
import re
import random
import string
import datetime


def verify_name(name):
	'''	Expected string inputs.
	   	Returns 
			- (name,'Success') -> if name is perfect. Will uppercase first letter.
			- ('-1',<error message>) -> if other characters found
		Will do HTML escaping on it.'''
	escaped_name = str(cgi.escape(name,quote="True"))
	if not escaped_name.isalpha():
		return ('-1','Name Contains invalid characters')
	else:
		return (name,'Success')

def verify_email(email):
	'''Expects valid email IDs
		Returns 
			- (email,'Success')
			- ('-1',<error>)'''
	match = re.search(r'[\w.-]+@[\w.-]+', email)
	if match:
		print match.group()
		return (str(match.group()),'Success')
	else:
		return ('-1','Invalid Email ID')

def verify_passwords(pwd,cpwd):
	if pwd == cpwd:
		if len(pwd) > 8:
			return (pwd,'Success')
		else:
			return ('-1','Password too short!')
	else:
		return ('-1','Passwords do not match')

def verify_mobile(mobile):
	#expects string
	print "utils: verify_mobile: ", mobile
	return (int(mobile),'Success')

def verify_text(text):
	return (text,'Success')

def verify_location(latitiude,longitude):
	try:
		latitiude = float(latitiude)
		longitude = float(longitude)
	except:
		print latitiude, longitude

	if latitiude.__class__ == 12.43.__class__ and longitude.__class__ == 12.3.__class__:
		return latitiude, longitude
	else:
		return 'error','error'

def encrypt(strng):
	return strng

def generate_string(size = 10, chars =  string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def time_difference(datetime_a,datetime_b,duration):
	date1 = datetime.datetime.strptime(datetime_a, '%Y-%m-%d %H:%M:%S.%f')
	date2 = datetime.datetime.strptime(datetime_b, '%Y-%m-%d %H:%M:%S.%f')
	days=abs((date2 - date1).days)
	
	if days<= duration:
		return True
	else :
		return False

def sort(_list):
	#Expected a list of tuples (entity, similarity index). Will sort and return all minus the index
	return sorted(_list, key=lambda tup: tup[1])		

def found_match(_list,_ease = 90):
	#Expected a list of tuples where irrespective of first item, we look into the second item and see if we found anything moore than 90% close
	for item in _list:
		if item[1] > _ease:
			return True
	return False

def return_match(_list,_ease = 90):
	#Assumes that the list contains atleast one match. Else god knows what may happen
	return [sort(_list)[0]]

def find_in_tuple_list(_tuple,_list):
	for _item in _list:
		a = _item[0].key.urlsafe
		b = _tuple[0].key.urlsafe
		if a == b:
			return True
	return False

def join(_list1 = [],_list2 = [],_list3 = [],_distinct = False):
	if not _list1:
		_list1 = []
	if not _list2:
		_list2 = []
	if not _list3:
		_list3 = []		

	_list =  _list1 + _list2 + _list3
	if not len(_list) > 0:
		return []
	if _distinct:
		_list_unique = [_list[0]]
		for _item in _list:
			#print "UTILS: ", _item #surely item is a tuple
			if not find_in_tuple_list(_item,_list_unique):
				_list_unique.append(_item)
		return _list_unique
	return _list

def remove_similarity(_list):
	items = []
	for item in _list:
		if check_if_tuple(item):
			items.append(item[0])
		else:	
			items.append(item)
	return items

def check_if_tuple(_item):
	t = (1,2)
	return t.__class__ == _item.__class__

def add_similarity(_list):
	results = []
	for item in _list:
		results.append((item,0))
	return results

def return_upto(_list,_ease):
	results = []
	for item in _list:
		if item[1] >= _ease:
			results.append(item)
	return results