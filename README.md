# InterviewTool
## What does this software do? 

This is a software tool that makes the process of campus recruitment seamless. It executes it the following way -

* Gives performance snapshots and performance summary of the college where the campus hiring is going to happen.
* Shortlists the candidates there and maps them to technical round queues, managerial round queues and HR round queues.
* Each interviewer will land in a page where he will get to see the resume of the candidate and a form to provide his opinions about the candidates in regard to his strengths, weaknesses and any other comments if any. 
* He can then choose to recommend him for further rounds or abort the recruitment processs for him.

## Prerequisites

* Python 3.x (after installing Python, run `pip install -r requirements.txt` which will install all the necessary Python modules)
* MongoDB (It is good if you also install **MongoDB Compass Community** for a GUI to have a visual of the database contents)

## Usage

Follow the below steps - 
- Install the prerequisites and clone the repository.
- Start the MongoDB using `mongod` command at localhost and port 27017 or change `helper.connect.py` file with the values of the host and port number.
- Run the flask app as `python app.py` which by default runs at [http://localhost:5000](http://localhost:5000) and the GUI will be up and running over there. 
- Sign up, login and hire!

## What is coming up in the next version and release?

Next release will be more of addition of some feature enhancements and smooth operational features along with bug fixes like -
- Generation of session logs.
- Separate view for placement cell; just like a Campus Hiring Dashboard to monitor and track the progress of the candidates' interview process.
- Consolidation of final results and acknowledgement report of the same for both company and college.
- Acknowledging the rejected candidates with the feedback and reviews via emails so that they can work on their weaknesses and improve themselves for their future opportunities.

## Contributing 

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
