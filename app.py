#!flask/bin/python
import sys
sys.path.append('../')
from flask import Flask, Response, request, make_response, json,jsonify,url_for,g
from flask_httpauth import HTTPBasicAuth
# from Models.User import User
# from Models.Contact import Contact
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from passlib.apps import custom_app_context as pwd_context

from flask_sqlalchemy import SQLAlchemy
from DAOMysql.configuration import configuration
from sqlalchemy.dialects.mysql import BIGINT

config = configuration()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =  config.configString
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
db = SQLAlchemy(app)


class User(db.Model):

	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(32))
	password_hash = db.Column(db.String(128))

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def generate_auth_token(self, expiration = 600):
		s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
		return s.dumps({ 'id': self.id })

	@staticmethod
	def verify_auth_token(token):

		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None # valid token, but expired
		except BadSignature:
			return None # invalid token
		user = User.query.get(data['id'])
		return user

class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(256), index=True)
    mobile = db.Column(BIGINT(unsigned=True))
    userid = db.Column(db.Integer)

    userSearch = {}

    @property
    def serialize(self):
        return {
            'contact name': self.name,
            'contact email': self.email,
            'contact mobile': self.mobile,
        }


auth = HTTPBasicAuth()
user = User()
contact = Contact()

@app.route('/')
def index():
    return "Plivo Assignment"


@app.route('/api/users', methods = ['POST'])
def new_user():
	if request.data:
		username = request.json.get('username')
		password = request.json.get('password')

		if username is None or password is None:
			# missing arguments
			return make_response("username and password fields are mandatory for the account to get created \n", 400)
		try:
			if User.query.filter_by(username = username).first() is not None:
				# existing user
				return make_response("User Name Already Exists \n",400)
			user = User(username = username)
			user.hash_password(password)
			db.session.add(user)
			db.session.commit()

		except Exception as e:
			return make_response('Please try after some time',503)

		return jsonify({ 'username': user.username }), 200, {'Location': url_for('get_user', id = user.id, _external = True)}
	else:
		return make_response('Bad Input \n', 400)

@app.route('/api/users/<int:id>')
def get_user(id):
	user = User.query.get(id)
	if not user:
		return make_response("Please try registering after sometime\n",500)
	return jsonify({'username': user.username})


@auth.verify_password
def verify_password(username_or_token, password):
	# first try to authenticate by token
	user = User.verify_auth_token(username_or_token)
	if not user:
		# try to authenticate with username/password
		user = User.query.filter(User.username==username_or_token).first()
		if not user or not user.verify_password(password):
			return False
	g.user = user
	return True


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })



@app.route('/api/add',methods=['POST'])
@auth.login_required
def add():
	current_db_sessions_flag = False

	response_text = ''
	if request.data:
		data = request.data
		dataDict = json.loads(data)
		try:
			for key,value in dataDict.items():
				if value :
					if 'name' not in value or 'email' not in value or 'mobile' not in value :
						continue
					try:
						if Contact.query.filter_by(email=value['email'],userid=g.user.id).first() is not None:
							response_text = response_text + value['email']+' user already found \n'
							continue  # existing contact
						contact = Contact()
						contact.email = value['email']
						contact.mobile = value['mobile']
						contact.name = value['name']
						contact.userid = g.user.id

						try:
							current_db_sessions = db.session.object_session(contact)
							current_db_sessions.add(contact)
							current_db_sessions.commit()
						except Exception as e:
							db.session.add(contact)
							db.session.commit()

						current_db_sessions_flag = True

					except Exception as e:
						return make_response('Please try after some time',503)
				else:
					response_text = response_text + ' Values not given properly \n'
					continue
		except Exception as e:
			return make_response('Please try after some time',503)


		if response_text == '':
			response_text = 'Contacts Added \n'
		return make_response(response_text,200)

	else:
		response = make_response("\nBad Request - Input JSON is empty\n",400)
		return response



@app.route('/api/edit',methods=['PUT','POST'])
@auth.login_required
def edit():
	current_db_sessions = None
	response_text = ''
	if request.data:
		data = request.data
		dataDict = json.loads(data)
		try:
			for key,value in dataDict.items():
				if value :
					if 'email' not in value:
						response_text = response_text + 'email is mandatory field \n'
						continue
					try:
						contact = Contact.query.filter_by(email=value['email'],userid=g.user.id).first()
						if contact is None:
							response_text = response_text + value['email'] + ' user not found \n'
							continue  # Contact Does Not exist

						if 'mobile' in value:
							contact.mobile = value['mobile']
						if 'name' in value:
							contact.name = value['name']

						try:
							current_db_sessions = db.session.object_session(contact)
							current_db_sessions.add(contact)
							current_db_sessions.commit()
						except Exception as e:
							db.session.add(contact)
							db.session.commit()

					except Exception as e:
						print "1"
						print e.message
						return make_response('Please try after some time',503)
				else:
					response_text = response_text + 'Contacts not given properly \n'
					continue
		except Exception as e:
			print "2"
			print e.message
			return make_response('Please try after some time',503)

		# if current_db_sessions:
		# 	current_db_sessions.close()
		if response_text == '':
			response_text = 'Contacts Edited \n'
			return make_response(response_text, 200)
		elif 'exception' not in response_text:
			response_text = response_text + ' Remaining Contacts(if any) are edited \n'
			return make_response(response_text, 200)
		else:
			return make_response('Contacts not found in the user\'s contact book\n',400)
	else:
		response = make_response("\nBad Request - Input JSON is empty\n",400)
		return response




@app.route('/api/delete',methods=['DELETE','POST'])
@auth.login_required
def delete():
	current_db_sessions = None
	response_text = ''
	if request.data:
		data = request.data
		dataDict = json.loads(data)
		try:
			for key,value in dataDict.items():
				if value :
					if 'email' not in value:
						continue
					try:
						contact = Contact.query.filter_by(email=value['email'],userid=g.user.id).first()
						if contact is None:
							response_text = response_text + value['email'] +' not found in contact book \n'
							continue  # Contact Does Not exist

						current_db_sessions = db.session.object_session(contact)
						current_db_sessions.delete(contact)
						current_db_sessions.commit()

					except Exception as e:
						return make_response('Please try after some time',503)
				else:
					continue
		except Exception as e:
			return make_response('Please try after some time',503)

		if current_db_sessions:
			current_db_sessions.close()
			if response_text == '':
				response_text = 'Contacts Deleted \n'
			elif 'exception' not in response_text:
				response_text = response_text + ' Remaining Contacts(if any) are deleted \n'
			return make_response(response_text, 200)
		else:
			return make_response('Contacts not found in the user\'s contact book\n',400)
	else:
		response = make_response("\nBad Request - Input JSON is empty\n",400)
		return response




@app.route('/api/search',methods=['GET','POST'])
@auth.login_required
def search():
	contact = None
	if request.data:
		data = request.data
		dataDict = json.loads(data)
		try:

			if dataDict :
				if 'email' not in dataDict and 'name' not in dataDict:
					return make_response("Search is allowed either by name or email \n",400)
				per_page = 10
				if 'per_page' in dataDict:
					per_page = dataDict['per_page']
					if per_page<10:
						per_page = 10
				try:
					if 'email' in dataDict:
						email = '%'+dataDict['email']+'%'

						contact = Contact.query.filter(Contact.email.like(email)).filter(Contact.userid==g.user.id).all()
						if contact is None or len(contact) == 0:
							msg = dataDict['email'] + ' Contact is not present'
							return make_response(msg,400)
						total_pages = len(contact)
						if total_pages <= per_page:
							pageCount = 1
						else:
							if total_pages%per_page == 0:
								pageCount = total_pages%per_page
							else:
								pageCount = 1 + total_pages/per_page


						if Contact.userSearch and str(g.user.id) in Contact.userSearch\
								and 'email' in Contact.userSearch[str(g.user.id)] and dataDict['email'] in  Contact.userSearch[str(g.user.id)]['email']:
							pass
						else:
							if str(g.user.id) not in Contact.userSearch:
								Contact.userSearch[str(g.user.id)] = {}
							if 'email' not in Contact.userSearch[str(g.user.id)]:
								Contact.userSearch[str(g.user.id)]['email'] = {}
							if dataDict['email'] not in Contact.userSearch[str(g.user.id)]['email']:
								Contact.userSearch[str(g.user.id)]['email'][dataDict['email']] = {}
							if 'pageCount' not in Contact.userSearch[str(g.user.id)]['email'][dataDict['email']]:
								Contact.userSearch[str(g.user.id)]['email'][dataDict['email']]['pageCount'] = 1
						#print Contact.userSearch
						p = Contact.userSearch[str(g.user.id)]['email'][dataDict['email']]['pageCount']

						contact1 = Contact.query.filter(Contact.email.like(email)).filter(Contact.userid == g.user.id).paginate(page=p, per_page=per_page)
						contacts = [i.serialize for i in contact1.items]
						if pageCount > 1:
							if Contact.userSearch[str(g.user.id)]['email'][dataDict['email']]['pageCount']  < pageCount:
								Contact.userSearch[str(g.user.id)]['email'][dataDict['email']]['pageCount']  += 1
							else:
								Contact.userSearch[str(g.user.id)]['email'][dataDict['email']]['pageCount'] = 1
						return jsonify(contacts = contacts)

					if 'name' in dataDict:
						name = '%'+dataDict['name']+'%'

						contact = Contact.query.filter(Contact.name.like(name)).filter(Contact.userid==g.user.id).all()

						if contact is None or len(contact) == 0:
							msg = dataDict['name'] + ' Contact is not present'
							return make_response(msg,400)
						total_pages = len(contact)
						if total_pages <= per_page:
							pageCount = 1
						else:
							if total_pages%per_page == 0:
								pageCount = total_pages%per_page
							else:
								pageCount = 1 + total_pages/per_page


						if Contact.userSearch and str(g.user.id) in Contact.userSearch\
								and 'name' in Contact.userSearch[str(g.user.id)] and dataDict['name'] in  Contact.userSearch[str(g.user.id)]['name']:
							pass
						else:
							if str(g.user.id) not in Contact.userSearch:
								Contact.userSearch[str(g.user.id)] = {}
							if 'name' not in Contact.userSearch[str(g.user.id)]:
								Contact.userSearch[str(g.user.id)]['name'] = {}
							if dataDict['name'] not in Contact.userSearch[str(g.user.id)]['name']:
								Contact.userSearch[str(g.user.id)]['name'][dataDict['name']] = {}
							if 'pageCount' not in Contact.userSearch[str(g.user.id)]['name'][dataDict['name']]:
								Contact.userSearch[str(g.user.id)]['name'][dataDict['name']]['pageCount'] = 1
						#print Contact.userSearch
						p = Contact.userSearch[str(g.user.id)]['name'][dataDict['name']]['pageCount']

						contact1 = Contact.query.filter(Contact.name.like(name)).filter(Contact.userid == g.user.id).paginate(page=p, per_page=per_page)
						contacts = [i.serialize for i in contact1.items]
						if pageCount > 1:
							if Contact.userSearch[str(g.user.id)]['name'][dataDict['name']]['pageCount']  < pageCount:
								Contact.userSearch[str(g.user.id)]['name'][dataDict['name']]['pageCount']  += 1
							else:
								Contact.userSearch[str(g.user.id)]['name'][dataDict['name']]['pageCount'] = 1
						return jsonify(contacts = contacts)

				except Exception as e:
					return make_response('Please try after some time',503)
			else:
				return make_response("Bad Input \n", 400)
		except Exception as e:
			return make_response('Please try after some time',503)

	else:
		response = make_response("\nBad Request - Input JSON is empty\n",400)
		return response

if __name__ == '__main__':
     app.run(debug=True)
	# app.run(threaded=True)