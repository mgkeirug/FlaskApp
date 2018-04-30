from __future__ import division
from flask import render_template, request, flash, redirect, url_for, abort
from FlaskApp import app, db
from flask_login import current_user, login_user, logout_user
from FlaskApp.models import User, Post
from FlaskApp.forms import LoginForm, RegistrationForm, EditProfileForm, StatsForm, UpdateForm
from werkzeug.urls import url_parse
from flask_login import login_required
from datetime import datetime
from FlaskApp.forms import ResetPasswordRequestForm, ResetPasswordForm
from FlaskApp.email import send_password_reset_email


@app.route('/')
def redir():
    return redirect(url_for('index'))
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = StatsForm()          #these variables hold the data inserted into the html form
    name = form.name.data
    if name is None:
        name = 'Visitor. Register a profile to save your stats'
    height_feet = form.height_feet.data
    height_inches = form.height_inches.data
    if height_feet is None:
        height_feet = 0
    if height_inches is None:
        height_inches = 0
    height = (height_feet * 12) + height_inches
    #height = form.height.data
    starting_weight = form.starting_weight.data
    current_weight = form.current_weight.data
    goal_weight = form.goal_weight.data
    starting_bf_percentage = form.starting_bf_percentage.data
    current_bf_percentage = form.current_bf_percentage.data
    goal_bf_percentage = form.goal_bf_percentage.data
    #input_stats = [starting_weight, current_weight, goal_weight, starting_bf_percentage, current_bf_percentage, goal_bf_percentage]
    if height is None:
       height = 0
    if starting_weight is None:
        starting_weight = 0
    if current_weight is None:
        current_weight = 0
    if goal_weight is None:
        goal_weight = 0
    if starting_bf_percentage is None:
        starting_bf_percentage = 0
    if current_bf_percentage is None:
        current_bf_percentage = 0
    if goal_bf_percentage is None:
        goal_bf_percentage = 0
    total_weight_lost = starting_weight - current_weight
    if total_weight_lost < 0:
        total_weight_lost = 0
    total_weight_gained = current_weight - starting_weight
    if total_weight_gained < 0:
        total_weight_gained = 0
    starting_fat_pounds = round((starting_weight * starting_bf_percentage) * .01, 2)
    current_fat_pounds = round((current_weight * current_bf_percentage) * .01, 2)
    goal_fat_pounds = round((goal_weight * goal_bf_percentage) * .01, 2)
    fat_lost = round((starting_fat_pounds - current_fat_pounds), 2)         #these need to be here for when nobody is logged in
    starting_lean_bodymass = round(starting_weight - starting_fat_pounds, 2)
    current_lean_bodymass = round(current_weight - current_fat_pounds, 2)
    goal_lean_bodymass = round(goal_weight - goal_fat_pounds, 2)
    goal_weight_auto = round((current_lean_bodymass / ((100 - goal_bf_percentage) * .01)), 2)
    goal_fat_loss_auto = round((current_weight - goal_weight_auto), 2)
    try:
        bmi = round((current_weight / height / height) * 703, 2)
    except ZeroDivisionError:
        bmi = 0
    nonfat_lost = round((starting_lean_bodymass - current_lean_bodymass), 2)
    goal_fat_loss = round((current_fat_pounds - goal_fat_pounds), 2)
    goal_muscle_gain = round(goal_weight - (current_weight - goal_fat_loss), 2)

    if current_user.is_authenticated:
        form = UpdateForm()
        username = current_user.username  #not sure if im going to need this here, already got user_id
        user_id = current_user.id   #this needs to be here so the user_id is inserted into Post table, see below
        current_weight = current_user.current_weight     #= used to be form.current_weight.data
        current_bf_percentage = current_user.current_bf_percentage  #idk if i need this
        name = current_user.name    #i used to think these needed to be here, not sure why(its so the current users values are loaded when they login instead of showing 0s
        height = current_user.height  #all these variables need to be redefined here bc half of them would be 0 since the whole form isnt being filled out...
        starting_weight = current_user.starting_weight
        goal_weight = current_user.goal_weight
        starting_bf_percentage = current_user.starting_bf_percentage
        goal_bf_percentage = current_user.goal_bf_percentage
        '''if height is None:
            height = 0
        if starting_weight is None:             #still testing, dont think i need
            starting_weight = 0
        if current_weight is None:
            current_weight = 0  #dont know about this
        if goal_weight is None:
            goal_weight = 0
        if starting_bf_percentage is None:
            starting_bf_percentage = 0 #dont know about this
        if current_bf_percentage is None:
            current_bf_percentage = 0
        if goal_bf_percentage is None:
            goal_bf_percentage = 0'''
        total_weight_lost = starting_weight - current_weight
        if total_weight_lost < 0:
            total_weight_lost = 0
        total_weight_gained = current_weight - starting_weight
        if total_weight_gained < 0:
            total_weight_gained = 0
        starting_fat_pounds = round((starting_weight * starting_bf_percentage) * .01, 2)
        current_fat_pounds = round((current_weight * current_bf_percentage) * .01, 2)  #i dont know why any of these need to be here but they do
        goal_fat_pounds = round((goal_weight * goal_bf_percentage) * .01, 2)
        fat_lost = round((starting_fat_pounds - current_fat_pounds), 2)
        starting_lean_bodymass = round(starting_weight - starting_fat_pounds, 2)
        current_lean_bodymass = round(current_weight - current_fat_pounds, 2)
        goal_lean_bodymass = round(goal_weight - goal_fat_pounds, 2)
        try:
            bmi = round((current_weight / height / height) * 703, 2)
        except ZeroDivisionError:
            bmi = 0
        nonfat_lost = round((starting_lean_bodymass - current_lean_bodymass), 2)
        goal_fat_loss = round((current_fat_pounds - goal_fat_pounds), 2)
        goal_weight_auto = round((current_lean_bodymass / ((100 - goal_bf_percentage) * .01)), 2)
        goal_fat_loss_auto = round((current_weight - goal_weight_auto), 2)
        goal_muscle_gain = round(goal_weight - (current_weight - goal_fat_loss), 2)
        if form.validate_on_submit():   #this will update the user profile(thats why current_user.height etc does) db AND add a user post the the post db if someone is logged in
            current_user.username = username
            current_user.id = user_id        #these need to be here to update the "user database", thats wwhat 'current_user.' does, without 'current_user.' is will only update the Post db
            current_user.current_weight = form.current_weight.data
            if current_user.current_weight is None:
                current_user.current_weight = current_weight
            current_user.current_bf_percentage = form.current_bf_percentage.data
            if current_user.current_bf_percentage is None:
                current_user.current_bf_percentage = current_bf_percentage
            current_user.name = name
            current_user.height = height
            current_user.starting_weight = starting_weight
            current_user.goal_weight = goal_weight
            current_user.starting_bf_percentage = starting_bf_percentage
            current_user.goal_bf_percentage = goal_bf_percentage

            current_user.total_weight_lost = current_user.starting_weight - current_user.current_weight
            if current_user.total_weight_lost < 0:
                current_user.total_weight_lost = 0
            current_user.total_weight_gained = current_user.current_weight - current_user.current_weight
            if current_user.total_weight_gained < 0:
                current_user.total_weight_gained = 0

            current_user.starting_fat_pounds = starting_fat_pounds      #dont think i need the starting or goal ones equations here, might be wrong tho..
            current_user.current_fat_pounds = round((current_user.current_weight * current_user.current_bf_percentage) * .01, 2)
            current_user.goal_fat_pounds = round((current_user.goal_weight * current_user.goal_bf_percentage) * .01, 2)
            current_user.fat_lost = round((current_user.starting_fat_pounds - current_user.current_fat_pounds), 2)
            current_user.starting_lean_bodymass = starting_lean_bodymass
            current_user.current_lean_bodymass = round(current_user.current_weight - current_user.current_fat_pounds, 2)
            current_user.goal_lean_bodymass = goal_lean_bodymass
            try:
                current_user.bmi = round((current_user.current_weight / current_user.height / current_user.height) * 703, 2)
            except ZeroDivisionError:
                current_user.bmi = 0
            current_user.nonfat_lost = round((current_user.starting_lean_bodymass - current_user.current_lean_bodymass), 2)
            current_user.goal_fat_loss = round((current_user.current_fat_pounds - current_user.goal_fat_pounds), 2)
            current_user.goal_weight_auto = round((current_user.current_lean_bodymass / ((100 - current_user.goal_bf_percentage) * .01)), 2)
            current_user.goal_fat_loss_auto = round((current_user.current_weight - current_user.goal_weight_auto), 2)
            current_user.goal_muscle_gain = round(current_user.goal_weight - (current_user.current_weight - current_user.goal_fat_loss), 2)
            post = Post(username=current_user.username, user_id=current_user.id, name=current_user.name, height=height,
                        starting_weight=starting_weight, current_weight=current_user.current_weight,
                        goal_weight=goal_weight, starting_bf_percentage=starting_bf_percentage,
                        current_bf_percentage=current_user.current_bf_percentage, goal_bf_percentage=goal_bf_percentage,
                        total_weight_lost=current_user.total_weight_lost, total_weight_gained=current_user.total_weight_gained,
                        starting_fat_pounds=current_user.starting_fat_pounds,
                        current_fat_pounds=current_user.current_fat_pounds, goal_fat_pounds=current_user.goal_fat_pounds,
                        fat_lost=current_user.fat_lost, starting_lean_bodymass=starting_lean_bodymass,
                        current_lean_bodymass=current_user.current_lean_bodymass,
                        goal_lean_bodymass=goal_lean_bodymass, bmi=current_user.bmi, nonfat_lost=current_user.nonfat_lost,
                        goal_fat_loss=goal_fat_loss, goal_weight_auto=current_user.goal_weight_auto,
                        goal_fat_loss_auto=current_user.goal_fat_loss_auto, goal_muscle_gain= current_user.goal_muscle_gain)  #use current_user.username...for username/id, user form.current_weight.data to take info from the form to post to db
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('index_user.html', title='Home', form=form, current_weight=current_weight,
                               current_bf_percentage=current_bf_percentage,  name=name, height=height,
                               starting_weight=starting_weight, goal_weight=goal_weight,
                               starting_bf_percentage=starting_bf_percentage, goal_bf_percentage=goal_bf_percentage,
                               fat_lost=fat_lost, starting_lean_bodymass=starting_lean_bodymass,
                               current_lean_bodymass=current_lean_bodymass, goal_lean_bodymass=goal_lean_bodymass,
                               bmi=bmi, nonfat_lost=nonfat_lost, goal_fat_loss=goal_fat_loss,
                               total_weight_lost=total_weight_lost, total_weight_gained=total_weight_gained,
                               current_fat_pounds=current_fat_pounds,
                               goal_fat_pounds=goal_fat_pounds, goal_weight_auto=goal_weight_auto,
                               goal_fat_loss_auto=goal_fat_loss_auto, goal_muscle_gain=goal_muscle_gain)
    return render_template('index.html', title='Home', form=form, name=name, height=height,
                           starting_weight=starting_weight, current_weight=current_weight, goal_weight=goal_weight,
                           starting_bf_percentage=starting_bf_percentage, current_bf_percentage=current_bf_percentage,
                           goal_bf_percentage=goal_bf_percentage, fat_lost=fat_lost,
                           starting_lean_bodymass=starting_lean_bodymass, current_lean_bodymass=current_lean_bodymass,
                           goal_lean_bodymass=goal_lean_bodymass, bmi=bmi, nonfat_lost=nonfat_lost,
                           goal_fat_loss=goal_fat_loss, total_weight_lost=total_weight_lost,
                           total_weight_gained=total_weight_gained,
                           current_fat_pounds=current_fat_pounds, goal_fat_pounds=goal_fat_pounds,
                           goal_weight_auto=goal_weight_auto, goal_fat_loss_auto=goal_fat_loss_auto,
                           goal_muscle_gain=goal_muscle_gain)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Congratulations, you are now a registered user!  Edit your stats to get started.')
        return redirect(url_for('edit_profile'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.order_by(Post.timestamp.desc()).filter_by(user_id=user.id)
    last_weight = db.session.query(Post.current_weight).order_by(Post.timestamp.desc()).filter_by(user_id=user.id).first()  #this takes the current_weight column, then puts in chrono order, then filters by current_user.user_id, and [1] gets the second to last entry
    entry_id = None
    if request.method == 'POST':
        entry_id = request.form['entry_id']     #delete entry button
        db.session.query(Post).filter(Post.id == entry_id).delete()
        db.session.commit()
    if username == current_user.username:
        return render_template('user.html', title='Profile', user=user, posts=posts, entry_id=entry_id)
    else:
        abort(404)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = StatsForm()  # these variables hold the data inserted into the html form
    name = form.name.data
    username = current_user.username
    user_id = current_user.id
    height_feet = form.height_feet.data
    height_inches = form.height_inches.data
    if height_feet is None:
        height_feet = 0
    if height_inches is None:
        height_inches = 0
    height = (height_feet * 12) + height_inches
    #height = form.height.data
    starting_weight = form.starting_weight.data
    current_weight = form.current_weight.data
    goal_weight = form.goal_weight.data
    starting_bf_percentage = form.starting_bf_percentage.data
    current_bf_percentage = form.current_bf_percentage.data
    goal_bf_percentage = form.goal_bf_percentage.data
    # input_stats = [starting_weight, current_weight, goal_weight, starting_bf_percentage, current_bf_percentage, goal_bf_percentage]
    if height == 0:
        height = current_user.height
    if starting_weight is None:
        starting_weight = current_user.starting_weight
    if current_weight is None:
        current_weight = current_user.current_weight
    if goal_weight is None:
        goal_weight = current_user.goal_weight
    if starting_bf_percentage is None:
        starting_bf_percentage = current_user.starting_bf_percentage
    if current_bf_percentage is None:
        current_bf_percentage = current_user.current_bf_percentage
    if goal_bf_percentage is None:
        goal_bf_percentage = current_user.goal_bf_percentage
    total_weight_lost = starting_weight - current_weight  # these variable perfom calcs based on data entered into the html form
    starting_fat_pounds = round((starting_weight * starting_bf_percentage) * .01, 2)
    current_fat_pounds = round((current_weight * current_bf_percentage) * .01, 2)
    goal_fat_pounds = round((goal_weight * goal_bf_percentage) * .01, 2)
    fat_lost = round((starting_fat_pounds - current_fat_pounds), 2)
    starting_lean_bodymass = round(starting_weight - starting_fat_pounds, 2)
    current_lean_bodymass = round(current_weight - current_fat_pounds, 2)
    goal_lean_bodymass = round(goal_weight - goal_fat_pounds, 2)
    try:
        bmi = round((current_weight / height / height) * 703, 2)
    except ZeroDivisionError:
        bmi = 0
    nonfat_lost = round((starting_lean_bodymass - current_lean_bodymass), 2)
    goal_fat_loss = round((current_fat_pounds - goal_fat_pounds), 2)
    if form.validate_on_submit():
        current_user.username = username
        current_user.id = user_id  # these need to be here to update the "user database", thats wwhat 'current_user.' does, without 'current_user.' is will only update the Post db
        current_user.name = name
        current_user.height = height
        current_user.starting_weight = starting_weight
        current_user.current_weight = current_weight
        current_user.goal_weight = goal_weight
        current_user.starting_bf_percentage = starting_bf_percentage
        current_user.current_bf_percentage = current_bf_percentage
        current_user.goal_bf_percentage = goal_bf_percentage
        current_user.total_weight_lost = total_weight_lost
        current_user.starting_fat_pounds = starting_fat_pounds
        current_user.current_fat_pounds = current_fat_pounds
        current_user.goal_fat_pounds = goal_fat_pounds
        current_user.fat_lost = fat_lost
        current_user.starting_lean_bodymass = starting_lean_bodymass
        current_user.current_lean_bodymass = current_lean_bodymass
        current_user.goal_lean_bodymass = goal_lean_bodymass
        current_user.bmi = bmi
        current_user.nonfat_lost = nonfat_lost
        current_user.goal_fat_loss = goal_fat_loss
        post = Post(username=current_user.username, user_id=current_user.id, name=current_user.name, height=height,
                    starting_weight=starting_weight, current_weight=current_weight, goal_weight=goal_weight,
                    starting_bf_percentage=starting_bf_percentage, current_bf_percentage=current_bf_percentage,
                    goal_bf_percentage=goal_bf_percentage, total_weight_lost=total_weight_lost,
                    starting_fat_pounds=starting_fat_pounds, current_fat_pounds=current_fat_pounds,
                    goal_fat_pounds=goal_fat_pounds, fat_lost=fat_lost, starting_lean_bodymass=starting_lean_bodymass,
                    current_lean_bodymass=current_lean_bodymass, goal_lean_bodymass=goal_lean_bodymass, bmi=bmi,
                    nonfat_lost=nonfat_lost,
                    goal_fat_loss=goal_fat_loss)  # use current_user.username...for username/id, user form.current_weight.data to take info from the form to post to db
        db.session.add(post)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('index'))
   # elif request.method == 'GET':
        #form.username.data = current_user.username #dont need these, might put something else in
        #form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
