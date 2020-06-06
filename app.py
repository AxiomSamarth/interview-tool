# import the necessary modules
from flask import Flask, render_template, redirect, session, request, url_for, flash, jsonify
from helper.interview import analyze_results, shortlist
from helper.connect import get_db_connection
from hashlib import md5
import os

root_folder = os.getcwd()

# create the Flask object to manage the rest of the application
app = Flask(__name__)
app.secret_key = "Very secret key"

# route to landing page which displays the login page & restrict the request method to GET
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # collect the credentials
        username = str(request.form['username'])
        password = str(request.form['password'])
        password_hash = md5(password.encode())

        # logic to cross verify from the data in the database
        try:
            client = get_db_connection()
            database = client["InterviewTool"]
            users = database["Interviewers"].find_one({"username": username, "password": password_hash.hexdigest()})
            client.close()
            
            if users is not None:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                flash("Wrong credentials")
                return redirect(url_for('login'))
        except Exception:
            client.close()
            return redirect(url_for('error'))

    elif request.method == 'GET':
        return render_template('login.html')    
    else:
        return redirect(url_for('error'))

# this is the route to signup
@app.route('/signup', methods=["GET", "POST"])        
def signup():
    # if the method is GET then return the web page
    if request.method == 'GET':
        return render_template('signup.html')
    # if the method is POST then grab the POST data, get the database client connection
    elif request.method == 'POST':
        username = str(request.form['username'])
        password = str(request.form['password'])
        pass_hash = md5(password.encode())        

        # check if the user exists. If the user is new tthen sign him up. Or throw error prompting back to signup page 
        # with relevant message
        try:
            client = get_db_connection()
            database = client['InterviewTool']
            collection = database['Interviewers']
            username_exists = collection.find_one({'username': username})
            if username_exists is None:
                collection.insert_one({'username': username, 'password': pass_hash.hexdigest()})
                client.close()
                flash("Successfully signed up! Please login")
                return redirect(url_for('login'))
            else:
                flash("You are already signed up. Please login!")
                return redirect(url_for('signup'))
        except Exception:
            client.close()
            flash("Something went wrong! Login again!")
            return redirect(url_for('logout'))
    else:
        return redirect(url_for('error.html'))

# Landing page after the login
@app.route('/index', methods=['GET', 'POST'])
def index():
    # check for the request method to be GET and if the session of username is
    # set then return the index page which lists out
    # the college and gives a form to set the cut-off marks or else return error
    
    try:
        if request.method == 'GET' and session['username'] is not None:
            client = get_db_connection()
            database = client['InterviewTool']
            collection = database.Colleges
            colleges = collection.find({})
            colleges = [college['name'] for college in colleges]
            return render_template('index.html', colleges=colleges)
        elif request.method == 'POST' and session['username'] is not None:
            college = request.form['college']
            session['college'] = college
            return analyze_results(college, root_folder)
        else:
            return redirect(url_for('error'))
    except Exception:
        client.close()
        return redirect(url_for('error'))
    

# Here is where the list of shortlisted students, navigation to profile of the interviewee are displayed
@app.route('/enter_session', methods=['POST'])
def enter():
    # this is an imported function from a sibling module interview.py
    try:
        if request.method == 'POST':
            cutoff = request.form['cutoff']
            return shortlist(session['college'], cutoff)
    except Exception:
        return redirect(url_for('error'))


# This basically starts the interview session, asks the interviewer what round he wants to take 
# and makes the necessary changes to the queues of the shortlisted students
@app.route('/start', methods=["GET", "POST"])
def start_session():
    if request.method == "GET":
        return render_template('interview_panel.html')
    elif request.method == "POST":
        try:
            round_type = request.form['round_type']
            client = get_db_connection()
            database = client['InterviewTool']
            collection = database['InterviewSessions']
            college = dict(collection.find_one({'college': session['college']}))
            if round_type == 'tech':
                if len(college['tech_queue']):
                    student = college['tech_queue'][0]
                    college['tech_queue'].remove(student)
                    shortlisted_candidates = college['shortlisted_candidates']
                    for index, candidate in enumerate(shortlisted_candidates):
                        if candidate['email_id'] == student:
                            shortlisted_candidates[index]['current_round'] = round_type
                            session['current_round'] = round_type
                            session['current_student'] = student
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates, 'tech_queue': college['tech_queue']}})
                            student = candidate
                            break
                    client.close()            
                    return render_template('tech_panel.html', student=student)
                else:
                    client.close()
                    flash('Currently no one in the queue for Technical Round! Please check again after sometime.')
                    return redirect(url_for('start_session'))

            elif round_type == 'managerial':
                if len(college['managerial_queue']):
                    student = college['managerial_queue'][0]
                    college['managerial_queue'].remove(student)
                    shortlisted_candidates = college['shortlisted_candidates']
                    for index, candidate in enumerate(shortlisted_candidates):
                        if candidate['email_id'] == student:
                            shortlisted_candidates[index]['current_round'] = round_type
                            session['current_round'] = round_type
                            session['current_student'] = student
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates, 'managerial_queue': college['managerial_queue']}})
                            student = candidate
                            break
                    client.close()            
                    return render_template('managerial_panel.html', student=student)
                else:
                    client.close()
                    flash('Currently no one in the queue for managerial Round! Please check again after sometime.')
                    return redirect(url_for('start_session'))
            elif round_type == 'hr':
                if len(college['hr_queue']):
                    student = college['hr_queue'][0]
                    college['hr_queue'].remove(student)
                    shortlisted_candidates = college['shortlisted_candidates']
                    for index, candidate in enumerate(shortlisted_candidates):
                        if candidate['email_id'] == student:
                            shortlisted_candidates[index]['current_round'] = round_type
                            session['current_round'] = round_type
                            session['current_student'] = student
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates, 'hr_queue': college['hr_queue']}})
                            student = candidate
                            break
                    client.close()            
                    return render_template('hr_panel.html', student=student)
                else:
                    client.close()
                    flash('Currently no one in the queue for HR Round! Please check again after sometime.')
                    return redirect(url_for('start_session'))
            else:
                return redirect(url_for('error'))
        except Exception:
            client.close()
            return redirect(url_for('error'))


# This little jewel below updates the database with the reviews for the candidate from that current round and 
# makes necessary tweaks to the queues based on whether the candidate was promoted or rejected
# And finally, changing the hiring status to 'Hired' or 'Rejected' post HR round
@app.route('/update', methods=['POST'])   
def update():
    if request.method == "POST":
        try:
            strengths = request.form['strengths']
            weaknesses = request.form['weaknesses']
            other_comments =  request.form['other_comments']
            review = request.form['review']
            client = get_db_connection()
            database = client['InterviewTool']
            collection = database['InterviewSessions']
            college = dict(collection.find_one({'college': session['college']}))

            if session['current_round'] == 'tech':
                shortlisted_candidates = college['shortlisted_candidates']
                for index, candidate in enumerate(shortlisted_candidates):
                    if candidate['email_id'] == session['current_student']:
                        shortlisted_candidates[index]['tech_round']['interviewer'] = session['username']
                        shortlisted_candidates[index]['tech_round']['strengths'] = strengths
                        shortlisted_candidates[index]['tech_round']['weaknesses'] = weaknesses
                        shortlisted_candidates[index]['tech_round']['other_comments'] = other_comments
                        if review == 'promote':
                            college['managerial_queue'].append(session['current_student'])
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates, 'managerial_queue': college['managerial_queue']}})
                        elif review == 'reject':
                            shortlisted_candidates[index]['status'] = 'Rejected'
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates}})
                        else:
                            return redirect(url_for('error'))
                        break
                client.close()
                return redirect(url_for('start_session'))

            elif session['current_round'] == 'managerial':
                shortlisted_candidates = college['shortlisted_candidates']
                for index, candidate in enumerate(shortlisted_candidates):
                    if candidate['email_id'] == session['current_student']:
                        shortlisted_candidates[index]['managerial_round']['interviewer'] = session['username']
                        shortlisted_candidates[index]['managerial_round']['strengths'] = strengths
                        shortlisted_candidates[index]['managerial_round']['weaknesses'] = weaknesses
                        shortlisted_candidates[index]['managerial_round']['other_comments'] = other_comments
                        if review == 'promote':
                            college['hr_queue'].append(session['current_student'])
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates, 'hr_queue': college['hr_queue']}})
                        elif review == 'reject':
                            shortlisted_candidates[index]['status'] = 'Rejected'
                            collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates}})
                        break
                client.close()
                return redirect(url_for('start_session'))

            elif session['current_round'] == 'hr':
                shortlisted_candidates = college['shortlisted_candidates']
                for index, candidate in enumerate(shortlisted_candidates):
                    if candidate['email_id'] == session['current_student']:                    
                        shortlisted_candidates[index]['current_round'] = 'Complete'
                        shortlisted_candidates[index]['hr_round']['interviewer'] = session['username']
                        shortlisted_candidates[index]['hr_round']['strengths'] = strengths
                        shortlisted_candidates[index]['hr_round']['weaknesses'] = weaknesses
                        shortlisted_candidates[index]['hr_round']['other_comments'] = other_comments
                        if review == 'promote':
                            shortlisted_candidates[index]['status'] = 'Hired'
                        elif review == 'reject':
                            shortlisted_candidates[index]['status'] = 'Rejected'
                        collection.find_one_and_update({'college': session['college']}, {'$set': {'shortlisted_candidates': shortlisted_candidates}})
                        break
                client.close()
                return redirect(url_for('start_session'))

        except Exception:
            client.close()
            return redirect(url_for('error'))


# This is the url endpoint which will be hit whenever other functions encounter errors, make a provision to 
# display flash messages in the error page
@app.route('/error', methods=['GET'])
def error():
    return render_template('error.html')


# Logout the users and delete all the sessions
@app.route('/logout', methods=['GET'])    
def logout():
    if session['username']:
        session['username'] = None
    return redirect(url_for('login'))


# chick chick boom, run the application to ease the process of recruitment 
if __name__ == '__main__':
    app.run(debug=True)
