"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash

##############Leejin Kim##############
from .models import get_user_email
from .settings import APP_FOLDER
from py4web.utils.url_signer import URLSigner
import os
url_signer = URLSigner(session)
import json
#############    end    ##############

@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    rows = db(db.pending.pending_inviter == get_user_email()).select()
    return dict(message=message, actions=actions, rows=rows, url_signer=url_signer)

@action('create_event')
@action.uses('create_event.html', url_signer)
def create_event():
    return dict(
        load_events_url = URL('load_events', signer=url_signer),
        add_event_url = URL('add_event', signer=url_signer),
        delete_event_url = URL('delete_event', signer=url_signer),
    )

@action('load_events')
@action.uses(url_signer.verify(), db)
def load_events():
    rows = db(db.event).select().as_list()
    return dict(rows=rows)
    
@action('add_event', method="POST")
@action.uses(url_signer.verify(), db)
def add_event():
    id = db.event.insert(
        event_title=request.json.get('event_title'),
        event_image=request.json.get('event_image'),
        event_location=request.json.get('event_location'),
        event_description=request.json.get('event_description'),
        event_attachment=request.json.get('event_attachment'),
        event_creator=get_user_email(),
    )
    mylist = request.json.get('event_pending_list'),
    for names in mylist:
        db.pending.insert(
            pending_inviter=get_user_email(),
            pending_invitee=names,
            event_pending=id,
        )
    return dict(id=id)


# @action('add', method=["GET", "POST"])
# @action.uses(url_signer, db, session, auth.user)
# def add():
#     # Insert form: no record= in it.
#     form = Form(db.event, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # We simply redirect; the insertion already happened.
#         redirect(URL('index'))
#     # Either this is a GET request, or this is a POST but not accepted = with errors.
#     return dict(form=form)

# @action('edit_event/<event_id:int>', method=["GET", "POST"])
# @action.uses('edit_event.html', url_signer, db, session, auth.user)
# def edit(event_id=None):
#     assert event_id is not None
#     e = db.event[event_id]
#     if e is None:
#         # Nothing found to be edited!
#         redirect(URL('index'))
#     # Edit form: it has record=
#     form = Form(db.event, record=b, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         # The update already happened!
#         redirect(URL('index'))
#     return dict(form=form)

@action('delete_event')
@action.uses(url_signer.verify(), db)
def delete_event():
    id = request.params.get('id')
    assert id is not None
    db(db.event.id == id).delete()

##############Leejin Kim##############

# @action('notifications/<event_id:int>', method=["GET", "POST"])
# @action.uses('notifications.html', url_signer, db, session, auth.user)
# def notifications(event_id=None):
#     assert event_id is not None
#     # user = auth.get_user()
#     p = db.event[event_id]
#     if p["user_email"] != get_user_email():
#         redirect(URL('index'))
#     if p is None:

#         redirect(URL('index'))
#     # s is the user_name
#     s = ""
#     # s = user


#     return dict( s = s)

# @action("notifications")
# @action.uses("notifications.html", auth, T)
# def index():
#     user = auth.get_user()
#     rows = db(db.event.user_email == get_user_email()).select()
#     s = user
#     return dict(rows=rows, url_signer=url_signer, s = s)
@action('notifications')
@action.uses(db, auth, 'notifications.html', url_signer,auth.user)
def index():
   
        # COMPLETE: return here any signed URLs you need.
        user = auth.get_user()
        rows = db(db.event.event_creator == get_user_email()).select()
        s = user
     
        return dict(
            all_url = URL('all', signer=url_signer),
            pending_url = URL('pending', signer=url_signer),
            accepted_url = URL('accepted', signer=url_signer),
            
            rows=rows, url_signer=url_signer, s = s)
    

@action('accepted',method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def accepted():
    eventid = request.params.get('eventid') 
    row = db((db.pending.event_pending == eventid) ).select().first()
    
    db((db.pending.event_pending == eventid)).update(
        # have to remove the request.json.get('accepted') from pending invitee
        pending_invitee = request.json.get('accepted')
    )
    return dict()

@action('all')
@action.uses(url_signer.verify(), db)
def all():
    rows = db(db.event).select().as_list()
    pending = []
    email = get_user_email() 
    print("email is ", email)
    for r in rows: 
        row =  db((db.pending.event_pending == r['id']) ).select().first()
        if(email in row.pending_invitee and r['event_creator'] != email ):
            pending.append(r)
            
    return dict(rows=pending)
    
#############    end    ##############

#############Robert Johansen###############
@action("splash_page")
@action.uses("splash_page.html", auth, db, session, T)
def splash_page():
    return dict()
#############    end    ##############

#############Michael Ekman###############
@action("event")
@action.uses("event.html", db, auth)
def edit_event():
    event = db(db.invite.invitee == get_user_email()).select().first()
    if(event is None):
        redirect("create_event")
    event = event.event_invited
    title = event.event_title
    icon = event.event_image
    location = event.event_location
    date = event.event_date
    attachment = event.event_attachment
    id = event.id

    return dict(title=title, 
                icon=icon, 
                location=location,
                date=date, 
                attachment=attachment, 
                id=id)

@action("edit_event")
@action.uses("edit_event.html", db, auth)
def edit_event():
    return dict()

    
@action("account_settings")
@action.uses("account_settings.html", db, auth)
def account_settings():
    return dict()