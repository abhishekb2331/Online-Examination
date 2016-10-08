# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

## create all tables needed by auth if not custom tables
#auth.settings.registration_requires_approval = True
auth.settings.extra_fields['auth_user']=[
		Field('profession','string',requires=IS_IN_SET(['Faculty','Student'])),
		Field('qualification','string'),
		Field('phonenumber','string'),
		Field('about_you','text'),
		Field('image','upload')]
auth.define_tables(username=True, signature=False)

db.auth_user.password.requires=IS_STRONG()
## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' or 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.create_user_groups=False
## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
db.define_table('course',
		Field('name','string',notnull=True))
db.define_table('facultycourse',
		Field('facultyid',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.username')),
		Field('courseid',db.course,requires=IS_IN_DB(db,'course.id','course.name')))
db.define_table('qptable',
		Field('facultyid',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.username')),
		Field('topic','string',notnull=True),
		Field('qpname','string',notnull=True),
		Field('no_of_question','integer',notnull=True),
		Field('comments','string'))
db.define_table('qtable',
		Field('qptableid',db.qptable,requires=IS_IN_DB(db,'qptable.id','qptable.qpname')),
		Field('qnumber','integer',notnull=True),
		Field('question','string',notnull=True),
		Field('marks_for_each_question','integer'),
		Field('negativemarks','integer'),
		Field('number_of_option','integer'))
		#Field('correct_option','string'))
db.define_table('qoptions',
		Field('qoptions','string'),
		Field('qoption_num','string'),
		Field('qname',db.qtable,requires=IS_IN_DB(db,'qtable.id','qtable.question')))
db.define_table('correctoptions',
		Field('qtable',db.qtable,requires=IS_IN_DB(db,'qtable.id','qtable.question')),
		Field('name','string'))
db.define_table('answer',
		Field('studentid',requires=IS_IN_DB(db(db.auth_user.profession.like('Student')),'auth_user.id','auth_user.username')),
		Field('qptableid',requires=IS_IN_DB(db,'qptable.id','qptable.qpname')),
		Field('qnum','string'),
		Field('optionselected','string'),
		Field('marks'))
db.define_table('marks',
		Field('studentid',requires=IS_IN_DB(db(db.auth_user.profession.like('Student')),'auth_user.id','auth_user.username')),
		Field('qptableid',requires=IS_IN_DB(db,'qptable.id','qptable.qpname')),
		Field('marks','string'))
db.define_table('sugesstion',
		Field('qptableid',db.qptable,requires=IS_IN_DB(db,'qptable.id','qptable.qpname')),
		Field('sender',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.username')),
		Field('reciever',db.auth_user,requires=IS_IN_DB(db,'auth_user.id','auth_user.username')))
