import os
import cgi
import re
import random
import string


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

def encrypt(strng):
	return strng

def generate_string(size = 10, chars =  string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

def time_difference(self,datetime_a,datetime_b):
	return True