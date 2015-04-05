import os
import cgi
import re


def verify_name(name):
	'''	Expected string inputs.
	   	Returns 
			- (name,'Success') -> if name is perfect. Will uppercase first letter.
			- ('-1',<error message>) -> if other characters found
		Will do HTML escaping on it.'''
	escaped_name = str(cgi.escape(_fname,quote="True"))
	if not escaped_name.isalpha():
		return ('-1','Name Contains invalid characters')
	else:
		return ('name','Success')

def verify_email(email):
	'''Expects valid email IDs
		Returns 
			- (email,'Success')
			- ('-1',<error>)'''
	match = re.search(r'[\w.-]+@[\w.-]+', str)
	if match:
		print match.group()
		return (match.group(),'Success')
	else:
		return ('-1','Invalid Email ID')

def verify_passwords(pwd,cpwd):
	if pwd === cpwd:
		if len(pwd) > 8:
			return (pwd,'Success')
		else:
			return ('-1','Password too short!')
	else:
		return ('-1','Passwords do not match')


