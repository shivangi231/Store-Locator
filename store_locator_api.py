import endpoints
from protorpc import messages
from protorpc import message_types
from protorpc import remote
from datastore import Users

package = 'StoreLocator'

class LoginResponseType(messages.Enum):
  NONE = 0
  LOGIN = 1
  NOT_FOUND = 2
  WRONG_PASSWORD = 3

class UserRequestAuthentication(messages.Message):
  email = messages.StringField(1, required=True)
  password = messages.StringField(2, required=True)

class UserField(messages.Message):
  fname = messages.StringField(1)
  lname = messages.StringField(2)
  email = messages.StringField(3)
  id = messages.IntegerField(4)
  phone = messages.StringField(5)

class UserResponseAuthentication(messages.Message):
  status = messages.EnumField(LoginResponseType, 1)
  userInformation = messages.MessageField(UserField, 2)

class UserReponseRegistration(messages.Message):
  status = messages.BooleanField(1)

@endpoints.api(name='storelocator', version='v1')
class StoreLocatorAPI(remote.Service):

  @endpoints.method(UserRequestAuthentication, UserResponseAuthentication,
                    path="login", http_method='POST',
                    name='greetings.userAuthentication')
  def check_user_authentication(self, request):
    try:
      statusMessage = LoginResponseType.NONE
      query = Users.query(Users.email == request.email).fetch() 
      if len(query) == 0:
        statusMessage = LoginResponseType.NOT_FOUND
      elif query[0].password != request.password:
        statusMessage = LoginResponseType.WRONG_PASSWORD
      else:
        statusMessage = LoginResponseType.LOGIN
        userField = UserField(fname = query[0].fname,
                              lname = query[0].lname,
                              id = query[0].key.id(),
                              #TODO: add phone field in datastore
                              # phone = query[0].phone
                              email = query[0].email)
        return UserResponseAuthentication(status = statusMessage, userInformation = userField)
      return UserResponseAuthentication(status=statusMessage)
    except(TypeError):
      raise endpoints.NotFoundException('Error in the input format')

  @endpoints.method(UserRequestAuthentication, UserReponseRegistration,
                    path="register", http_method='PUT',
                    name='greetings.register')
  def register_user(self, request):
      if len(Users.query(Users.email == request.email).fetch()) == 0:
        Users(email=request.email, password=request.password).put()
        return UserReponseRegistration(status=True)
      else:
        return UserReponseRegistration(status=False)

APPLICATION = endpoints.api_server([StoreLocatorAPI])