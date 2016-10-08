# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################


@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to Online Examination Portal!")
    k=db(db.auth_membership.user_id==auth.user.id).select(db.auth_membership.group_id)
    print k[0].group_id
    if k[0].group_id==1:
	    redirect(URL('faculty_home'))
    else:
	    redirect(URL('student_home'))
    return dict(message=T('Hello World'))
def faculty_home():
	return dict(message=T('Welcome faculty'))
def student_home():
	return dict(message=T('Welcome Student'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    auth.settings.register_onaccept=__add_user_membership
    return dict(form=auth())
def __add_user_membership(form):
	group=db(db.auth_group.role==form.vars.profession).select().first()
	print group,form.vars
	user_id=form.vars.id
	auth.add_membership(group.id,user_id)

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
def reg():
	form=SQLFORM(db.auth_user)
	if(form.accepts(request,session)):
		form.process()
		if(form.vars.profession=='Faculty'):
			auth.add_membership(1,form.vars.id)
		else:
			auth.add_membership(2,form.vars.id)
		response.flash='Form Accepted'
	elif(form.errors):
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
@auth.requires_login()
@auth.requires_membership('Faculty')
def make_paper():
	#if(db.auth_user.profession=='Students'):
		#redirect(URL('student_home'))
#	else:
	form=SQLFORM(db.qptable)
	#print form
	form.vars.facultyid=auth.user.id
	if(form.accepts(request,session)):
		#print 'lo1'
		form.process()
		session.k=int(form.vars.no_of_question)
		session.l=1
		session.q=form.vars.id
		print 'hi'
		redirect(URL(r=request,f='set_paper'))
	elif(form.errors):
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
def correctoptions():
	#print 'kt'
	#form=SQLFORM(db.correctoptions)
	#print 'loi'
	#print form
	session.option=db(db.qoptions.qname==session.q1).select(db.qoptions.qoptions)
	#print session.option.qoptions
	r=[]
	q=len(session.option)
	for i in range(q):
		r.append(session.option[i].qoptions)
	print r
	form=SQLFORM.factory(
			Field('qtable',db.qtable,requires=IS_IN_DB(db,'qtable.id','qtable.question')),
			Field('name','string',requires=IS_IN_SET(r,multiple=True),widget=SQLFORM.widgets.checkboxes.widget))
	form.vars.qtable=session.q1
	#print form
	#form.vars.name._requires=IS_IN_SET(range(1,(session.opt)+1),multiple=True)
	if(form.accepts(request,session)):
		#print 'it worked'
		#form.process()
		db.correctoptions.insert(qtable=form.vars.qtable,name=form.vars.name)
		#print 'it qorked'
		redirect(URL(r=request,f='set_paper'))
	elif(form.errors):
		response.Flash='Form Has Errors'
	else:
		response.Flash='Fill Correct Options'
	return dict(form=form)
def set_paper():
	print 'yoy'
	k=int(session.k)
	l=int(session.l)
	if(l<=k):
		q=session.q
		form=SQLFORM(db.qtable)
		form.vars.qnumber=l
		form.vars.qptableid=q
		if(form.accepts(request,session)):
			form.process()
			session.opt=form.vars.number_of_option
			session.op=1
			(session.l)+=1
			l=session.l
			print 'king'
			if(l<=k+1):
				print 'king2'
				session.r=1
				(session.q1)=form.vars.id
				session.j=int(form.vars.number_of_option)
				redirect(URL(r=request,f='set_option'))
			else:
				redirect(URL('faculty_home'))
		elif(form.errors):
			response.flash='Form Has Errors'
		else:
			response.flash='Fill Form'
		return dict(form=form)
	else:
		redirect(URL('faculty_home'))
def set_option():
	j=int(session.j)
	r=int(session.r)
	q1=session.q1
	k=int(session.k)
	l=int(session.l)
	q=session.q
	session.option=[]
	form=SQLFORM(db.qoptions)
	form.vars.qoption_num=r
	form.vars.qname=q1
	if(form.accepts(request,session)):
		form.process()
		#print form.vars.qoptions
		#(session.option).append(form.vars.qoptions)
		#print session.option
		session.r+=1
		r=session.r
		if(r<=j):
			redirect(URL(r=request,f='set_option'))
		else:
			redirect(URL(r=request,f='correctoptions'))
	elif(form.errors):
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
def search():
	form=SQLFORM.factory(
			Field('search','string',requires=IS_IN_SET(['Faculty','topic','both'])))
	if(form.accepts(request,session)):
			if(form.vars.search=='Faculty'):
				redirect(URL('search_faculty'))
			elif(form.vars.search=='topic'):
				redirect(URL('search_topic'))
			elif(form.vars.search=='both'):
				redirect(URL('search_both'))
	elif(form.errors):
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
def search_faculty():
	form=SQLFORM.factory(
			Field('faculty',db.auth_user,requires=IS_IN_DB(db(db.auth_user.profession.like('Faculty')),'auth_user.id','auth_user.username')))
	if(form.accepts(request,session)):
		session.searchfaculty=form.vars.faculty
		redirect(URL('show_paper_faculty'))
	elif(form.errors):
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
def search_both():
	form1=SQLFORM.factory(
			Field('faculty',db.auth_user,requires=IS_IN_DB(db(db.auth_user.profession.like('Faculty')),'auth_user.id','auth_user.username')))
	if(form1.accepts(request,session)):
		q=form1.vars.faculty
		r=db(db.qptable.facultyid==q).select(db.qptable.topic)
		session.l=[]
		for i in r:
			session.l.append(i.topic)
		redirect(URL('searchtopicfaculty'))
	#	form2=SQLFORM.factory(
	#			Field('topic',requires=IS_IN_SET(l)))
	#	iif(form2.accepts(request,session)):
	#		session.searchtopic=form.vars.topic
	#		redirect(URL('show_paper_topic'))
	#	elif form2.errors :
	#		response.flash='Form Has Errors'
	#	return dict(form2=form2)
	elif form1.errors :
		response.flash='Form Has Errors'
	return dict(form1=form1)
def searchtopicfaculty():
		form2=SQLFORM.factory(
				Field('topic',requires=IS_IN_SET(session.l)))
		if(form2.accepts(request,session)):
			session.searchtopic=form2.vars.topic
			redirect(URL('show_paper_topic'))
		elif form2.errors :
			response.flash='Form Has Errors'
		return dict(form2=form2)
def search_topic():
	r=db().select(db.qptable.topic)
	print 'rtrt'
	print r[1].topic
	l=len(r)
	p=[]
	for i in range(l):
		p.append(r[i].topic)

	p=set(p)
	form=SQLFORM.factory(
			Field('topic',db.qptable,requires=IS_IN_SET(p)))
	if(form.accepts(request,session)):
		session.searchtopic=form.vars.topic
		redirect(URL('show_paper_topic'))
	elif (form.errors):
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
def show_paper_topic():
	q=db(db.qptable.topic==session.searchtopic).select(db.qptable.qpname,db.qptable.id,db.qptable.no_of_question)
	return dict(q=q)
def show_paper_faculty():
	q=db(db.qptable.facultyid==session.searchfaculty).select(db.qptable.qpname,db.qptable.id,db.qptable.no_of_question)
	print q
	return dict(q=q)
session.cnt=0
def display():
	session.cnt=1
	print session.cnt
	q=request.args(0)
	session.i=(db(db.qtable.qptableid==q).select(db.qtable.ALL))
	session.no_of_question=len(session.i)
	#print session.i,len(session.i)
	redirect(URL(r=request,f='display_paper/%s' %session.cnt))
#def records_ans():
#	print 'i am here'
	#form=SQLFORM(db.answer)
	#form.vars.studentid=auth.user.id
	#form.vars.qptableid=(session.i[(session.cnt)-1]).qptableid
	#form.vars.qnum=(session.i[(session.cnt)-1].qnumber)
	#form.vars.optionselected=session.tmp
	#form.vars.marks=(session.i[session.cnt-1]).negativemarks
	#if(form.accepts(request,session)):
	#form.process()
#	print session.cnt,'lol'
#	db.answer.insert(studentid=auth.user.id,qptableid=(session.i[int(session.cnt)-1]).qptableid,qnum=session.i[int(session.cnt)-1].qnumber,optionselected=session.tmp,marks=session.i[int(session.cnt)-1].negativemarks)
#	l=int(session.cnt)
#	l+=1
#	print l,'i u '
#	redirect(URL('display_paper/%d' %(l)))
	#elif(form.errors):
	#	response.flash='hi'
	#return dict(form=form)
def display_paper():
	#session.cnt+=1
	#q=request.args(0)
	session.cnt=request.args(0)
	print 'uy1',session.cnt
	if(int(session.cnt)>int(session.no_of_question)):
		#redirect(URL('student_home'))
		redirect(URL(r=request,f='result/%s' %(int(session.i[0].qptableid))))
	k=session.i[int(session.cnt)-1]
	ans=db(db.qoptions.qname==k.id).select(db.qoptions.qoptions)
	r=[]
	l=len(ans)
	y=db((db.answer.studentid==auth.user.id)&(db.answer.qptableid==k.qptableid)).select(db.answer.qnum)
	lists=[]
	for i in y:
		lists.append(i.qnum)
	print lists,'i am i am'
	for i in range(l):
		r.append(ans[i].qoptions)
	print r
	form=SQLFORM.factory(
			Field('question','string',default=k.question,readable=True,writable=False),
			Field('option','string',requires=IS_IN_SET(r,multiple=True),widget=SQLFORM.widgets.checkboxes.widget)
			)
	print 'hjgj'
	if(form.accepts(request,session)):
		print 'gt1;'
		i=form.vars.option
		i='|'.join(i)
		i='|'+i+'|'
		session.tmp=i
		redirect(URL(r=request,f='records_ans/%s' %session.cnt))
	elif form.errors:
		response.flash='Form has errors'
	#print form.vars.option
	#submit=form.element('input',_type='submit')
	#submit['_style']='display:none;'
	if(int(session.cnt)<int(session.no_of_question)):
		form.add_button('next',URL('display_paper/%d' %(int(session.cnt)+1)))
	if(int(session.cnt)>=2):
		form.add_button('prev',URL('display_paper/%d' %(int(session.cnt)-1)))
	form.add_button('endexam',URL('result/%s' %(int(session.i[0].qptableid))))
	#form.add_button('submit1',URL('record_ans/%s' %(i)))
	#session.i=(db(db.qtable.qptableid==q).select(db.qtable.ALL))
	print 'ou'
	print session.i
	nofq=session.no_of_question
	return dict(form=form,nofq=nofq,lists=lists)
#def record_ans():
#	print 'i am here'
#	form=SQLFORM(db.answer)
#	form.vars.studentid=auth.user.id
#	form.vars.qptableid=(session.i[(session.cnt)-1]).qptableid
#	form.vars.qnum=(session.i[(session.cnt)-1].qnumber)
#	form.vars.optionselected=request.args(0)
#	form.vars.marks=(session.i[session.cnt-1]).negativemarks
#	if(form.accepts(request,session)):
#		form.process()
#		redirect(URL('display_paper/%d' %(session.cnt+1)))
#	elif(form.errors):
#		response.flash='hi'
#	return dict(form=form)
def result():
	l=request.args(0)
	r=db((db.answer.studentid==auth.user.id) & (db.answer.qptableid==l)).select(db.answer.marks)
	ans=0
	print r
	for i in r:
		ans=ans+ int(i.marks)
		print '#'
	print ans,'i did it'
	q=db((db.marks.studentid==auth.user.id)&(db.marks.qptableid==l)).select(db.marks.marks)
	if(len(q)==0):
		db.marks.insert(studentid=auth.user.id,qptableid=l,marks=ans)
	else:
		db((db.marks.studentid==auth.user.id)&(db.marks.qptableid==l)).update(marks=ans)
	return locals()
def records_ans():
	print 'i am here'
	#form=SQLFORM(db.answer)
	#form.vars.studentid=auth.user.id
	#form.vars.qptableid=(session.i[(session.cnt)-1]).qptableid
	#form.vars.qnum=(session.i[(session.cnt)-1].qnumber)
	#form.vars.optionselected=session.tmp
	#form.vars.marks=(session.i[session.cnt-1]).negativemarks
	#if(form.accepts(request,session)):
	#form.process()
	session.cnt=request.args(0)
	print session.cnt,'lol'
	#db(db.answer.studentid=auth.user.id & db.answer.qptableid=()).update()
	correct_ans=db(db.correctoptions.qtable==session.i[int(session.cnt)-1].id).select(db.correctoptions.name)
	print correct_ans
	l=(correct_ans[0]).name
	#l=l[:-1]
	print l,'oip'
	#session.tmp+='\n'
	if(l==session.tmp):
		marking=session.i[int(session.cnt)-1].marks_for_each_question
	else:
		marking=-int(session.i[int(session.cnt)-1].negativemarks)
	print correct_ans,marking,'iu'
	d=db((db.answer.studentid==auth.user.id )& (db.answer.qptableid==(session.i[int(session.cnt)-1]).qptableid )& (db.answer.qnum==session.i[int(session.cnt)-1].qnumber )& (db.answer.optionselected==session.tmp)).select(db.answer.marks)
	print 'hello',d,'yo'
	if(len(d)==0):
		db.answer.insert(studentid=auth.user.id,qptableid=(session.i[int(session.cnt)-1]).qptableid,qnum=session.i[int(session.cnt)-1].qnumber,optionselected=session.tmp,marks=marking)
	else:
		db((db.answer.studentid==auth.user.id )& (db.answer.qptableid==(session.i[int(session.cnt)-1]).qptableid )& (db.answer.qnum==session.i[int(session.cnt)-1].qnumber )& (db.answer.optionselected==session.tmp)).update(marks=marking)
	l=int(session.cnt)
	l+=1
	print l,'i u '
	redirect(URL('display_paper/%d' %(l)))
	#elif(form.errors):
	#	response.flash='hi'
	#return dict(form=form)
def suggest():
	#form=SQLFORM(db.sugesstion)
	form=SQLFORM.factory(
			Field('sender',readable=True,writable=False,default=auth.user.username),
			Field('qptableid',db.qptable,requires=IS_IN_DB(db,'qptable.id','qptable.qpname')),
			Field('reciever',db.auth_user,requires=IS_IN_DB(db(db.auth_user.profession.like('Student')),'auth_user.id','auth_user.username')))
	#form.vars.sender=auth.user.id
	if(form.accepts(request,session)):
		db.sugesstion.insert(sender=auth.user.id,qptableid=form.vars.qptableid,reciever=form.vars.reciever)
	elif form.errors:
		response.flash='Form Has Errors'
	else:
		response.flash='Fill Form'
	return dict(form=form)
def suggestions():
	r=db((db.sugesstion.reciever==auth.user.id)&(db.sugesstion.qptableid==db.qptable.id) &(db.sugesstion.sender==db.auth_user.id)).select(db.auth_user.username,db.auth_user.id,db.qptable.qpname,db.qptable.id)
	return dict(r=r)
def show_profile():
	q=request.args(0) or auth.user.id
	l=db(db.auth_user.id==q).select(db.auth_user.ALL).first()
	images=l.image
	return dict(images=images,l=l)
def download():
	return response.download(request,db)
def show_attempted_paper():
	completed=[]
	q=db((db.marks.studentid==auth.user.id)&(db.marks.qptableid==db.qptable.id)&(db.qptable.facultyid==db.auth_user.id)).select(db.marks.marks,db.qptable.topic,db.qptable.qpname,db.auth_user.username)
	return dict(q=q)
