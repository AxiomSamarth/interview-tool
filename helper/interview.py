from flask import render_template, redirect, url_for, session
from .connect import get_db_connection
import pandas as pd
import numpy as np
import json

# This function will continuosly communicate with the database and
# fetch the latest changes and progress that is happening in the 
# hiring process 
def analyze_results(college, root_folder):
    results =  pd.read_csv(root_folder+'\\results\\'+college+'.csv')
    try:
        client = get_db_connection()
        database = client["InterviewTool"]
        collection = database['InterviewSessions']
        candidates = []
        for i in range(len(list(results['id']))):
            candidates.append({'id': list(results['id'])[i], 'name': list(results['name'])[i], 'email_id': list(results['email_id'])[i], 'score': list(results['score'])[i]})
        if collection.find_one({'college': college}) is None:
            collection.insert_one({'college': college, 'candidates': candidates})
            client.close()      
        
        scores = list(results['score'])
        recommended_cutoff = int(sum(scores)/len((scores)) + (0.02*(sum(scores)/len(scores))))
        return render_template('index.html', college=college, scores=scores, recommended_cutoff=recommended_cutoff)
    except Exception:
        client.close()
        return redirect(url_for('error'))


# This method shortlists the students from the chosen college based on the cutoff passed
# And formats the initial structure of the collection in the database like different rounds, different queues
# and sets few necessary sessions
def shortlist(college, cutoff):    
    try:
        client = get_db_connection()
        database = client["InterviewTool"]
        collection = database['InterviewSessions']
        college_session = dict(collection.find_one({'college': college}))
        
        if college_session is not None:
            candidates = list(college_session['candidates'])
            shortlisted_candidates = []
            for candidate in candidates:
                if int(candidate['score']) >= int(cutoff):
                    candidate['status'] = "in progress"
                    candidate['current_round'] = ""
                    candidate['tech_round'] = {'interviewer': '', 'strengths': '', 'weaknesses': '', 'other_comments': ''}
                    candidate['managerial_round'] = {'interviewer': '', 'strengths': '', 'weaknesses': '', 'other_comments': ''}
                    candidate['hr_round'] = {'interviewer': '', 'strengths': '', 'weaknesses': '', 'other_comments': ''}
                    shortlisted_candidates.append(candidate)

            college_session['shortlisted_candidates'] = shortlisted_candidates
            college_session['tech_queue'] = [candidate['email_id'] for candidate in shortlisted_candidates]
            college_session['managerial_queue'] = []
            college_session['hr_queue'] = []
            collection.find_one_and_replace({'college': college}, college_session)
            client.close()
            session['session_started'] = True
            return render_template('shortlist.html', college=college, shortlisted_candidates=shortlisted_candidates)
        else:
            return redirect(url_for('index'))
    except Exception:
        return redirect(url_for('error'))
    
    