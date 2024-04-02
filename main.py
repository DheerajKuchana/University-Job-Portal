from datetime import datetime
import re
from flask import Flask, request, render_template, session, redirect
import pymysql as pymysql
from Mail import send_email
conn = pymysql.connect(host="localhost", user="root", password="Sharmi@2020", db="UniversityRecruitment")
cursor = conn.cursor()

import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = "UniversityRecruitment"

@app.route("/")
def head():
    return render_template("index.html")

@app.route("/recruiter_reg")
def recruiter_reg():
    return render_template("recruiter_reg.html")

@app.route("/recruiter_reg1",methods=['post'])
def recruiter_reg1():
    name = request.form.get("name")
    email = request.form.get("email")
    experience = request.form.get("experience")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    count = cursor.execute("select * from recruiter where email = '"+str(email)+"' or phone = '"+str(phone)+"'")
    if count == 0:
        cursor.execute("insert into recruiter(name,email,experience,phone,password,address,status) values('"+str(name)+"','"+str(email)+"','"+str(experience)+"','"+str(phone)+"', '"+str(password)+"' , '"+str(address)+"', 'Not Approved')")
        conn.commit()
        return render_template("message.html", message="Recruiter Registered Successfully")
    else:
        return render_template("message.html", message="Already Exists")

@app.route("/student_reg")
def student_reg():
    cursor.execute("select * from studies")
    studies = cursor.fetchall()
    cursor.execute("select * from degree")
    degrees = cursor.fetchall()
    return render_template("student_reg.html",degrees=degrees, studies=studies,get_studies_id=get_studies_id)

@app.route("/student_reg1",methods=['post'])
def student_reg1():
    name = request.form.get("name")
    email = request.form.get("email")
    date_of_birth = request.form.get("date_of_birth")
    gender = request.form.get("gender")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    degree_id = request.form.get("degree_id")
    resume = request.files.get("resume")
    path = APP_ROOT + "/static/images/" + resume.filename
    resume.save(path)
    count = cursor.execute("select * from student where email = '"+str(email)+"' or phone = '"+str(phone)+"'")
    if count == 0:
        cursor.execute("insert into student(name,email,phone,password,address,gender,resume,date_of_birth,degree_id) values('"+str(name)+"','"+str(email)+"','"+str(phone)+"', '"+str(password)+"' , '"+str(address)+"' , '"+str(gender)+"',  '"+str(resume.filename)+"' , '"+str(date_of_birth)+"', '"+str(degree_id)+"')")
        conn.commit()
        return render_template("message.html", message="Student Registered Successfully")
    else:
        return render_template("message.html", message="Already Exists")

@app.route("/university_log", methods=['post'])
def university_log():
    university_username = request.form.get("university_username")
    university_password = request.form.get("university_password")
    if university_username == "university" and university_password == "university":
        session['role'] = 'university'
        return redirect("university_home")
    else:
        return render_template("message.html", message="Invalid Login Details")

@app.route("/university_home")
def university_home():
    cursor.execute("select * from recruiter")
    recruiters = cursor.fetchall()
    recruiters_count = len(recruiters)
    cursor.execute("select * from skill")
    skills = cursor.fetchall()
    skills_count = len(skills)
    cursor.execute("select * from jobpost")
    jobposts = cursor.fetchall()
    jobpost_count = len(jobposts)
    cursor.execute("select * from application")
    applications = cursor.fetchall()
    applications_count = len(applications)
    return render_template("university_home.html", recruiters_count=recruiters_count, skills_count=skills_count, jobpost_count=jobpost_count, applications_count=applications_count)

@app.route("/recruiter_log", methods = ['post'])
def recruiter_log():
    recruiter_email = request.form.get("recruiter_email")
    recruiter_password = request.form.get("recruiter_password")
    count = cursor.execute("select * from recruiter where email = '"+str(recruiter_email)+"' and password = '"+str(recruiter_password)+"'")
    if count > 0:
        recruiter = cursor.fetchone()
        status = recruiter[7]
        if status == 'Approved':
            session['recruiter_id'] = recruiter[0]
            session['role'] = 'recruiter'
            return redirect("/recruiter_home")
        else:
            return render_template("message.html", message="Account Not Approved By University")
    else:
        return render_template("message.html", message="Invalid Login Details")

@app.route("/recruiter_home")
def recruiter_home():
    recruiter_id = session['recruiter_id']
    cursor.execute("select * from jobpost where recruiter_id = '"+str(recruiter_id)+"'")
    jobposts = cursor.fetchall()
    jobpost_count = len(jobposts)
    cursor.execute("select * from application")
    applications = cursor.fetchall()
    applications_count = len(applications)
    cursor.execute("select * from application where status = 'Selected'")
    applications = cursor.fetchall()
    select_applications_count = len(applications)
    cursor.execute("select * from application where status = 'Rejected'")
    applications = cursor.fetchall()
    reject_applications_count = len(applications)
    return render_template("recruiter_home.html", jobpost_count=jobpost_count,applications_count=applications_count,select_applications_count=select_applications_count,reject_applications_count=reject_applications_count)

@app.route("/student_log", methods = ['post'])
def student_log():
    student_email = request.form.get("student_email")
    student_password = request.form.get("student_password")
    count = cursor.execute("select * from student where email = '"+str(student_email)+"' and password = '"+str(student_password)+"'")
    if count > 0:
        student = cursor.fetchone()
        student_id = student[0]
        session['student_id'] = student[0]
        session['role'] = 'student'
        return redirect("/student_home")
    else:
        return render_template("message.html", message="Invalid Login Details")

@app.route("/student_home")
def student_home():
    student_id = session['student_id']
    cursor.execute("select * from jobpost")
    jobposts = cursor.fetchall()
    jobpost_count = len(jobposts)
    cursor.execute("select * from application where status = 'Selected' and student_id = '"+str(student_id)+"'")
    applications = cursor.fetchall()
    select_applications_count = len(applications)
    cursor.execute("select * from application where status = 'Rejected' and student_id = '"+str(student_id)+"'")
    applications = cursor.fetchall()
    reject_applications_count = len(applications)
    return render_template("student_home.html",jobpost_count=jobpost_count,select_applications_count=select_applications_count,reject_applications_count=reject_applications_count)

@app.route("/view_recruiters")
def view_recruiters():
    cursor.execute("select * from recruiter")
    recruiters = cursor.fetchall()
    return render_template("view_recruiters.html",recruiters=recruiters)

@app.route("/approve")
def approve():
    recruiter_id = request.args.get("recruiter_id")
    cursor.execute("update recruiter set status = 'Approved' where recruiter_id = '"+str(recruiter_id)+"' ")
    conn.commit()
    return render_template("umessage.html", umessage="Approved Successfully")

@app.route("/decline")
def decline():
    recruiter_id = request.args.get("recruiter_id")
    cursor.execute("update recruiter set status = 'Declined' where recruiter_id = '"+str(recruiter_id)+"' ")
    conn.commit()
    return render_template("umessage.html", umessage="Declined Successfully")

@app.route("/add_view_skills")
def add_view_skills():
    cursor.execute("select * from skill")
    conn.commit()
    skills = cursor.fetchall()
    return render_template("add_view_skills.html", skills=skills)

@app.route("/add_skill", methods = ['post'])
def add_skill():
    skill_name = request.form.get("skill_name")
    count = cursor.execute("select * from skill where skill_name = '"+str(skill_name)+"'")
    conn.commit()
    if count == 0:
        cursor.execute("insert into skill(skill_name) values('"+str(skill_name)+"')")
        conn.commit()
        return redirect("/add_view_skills")
    else:
        return render_template("umessage.html", umessage="Already Skill Name Exist")

@app.route("/add_view_studies")
def add_view_studies():
    cursor.execute("select * from studies")
    conn.commit()
    studies = cursor.fetchall()
    return render_template("add_view_studies.html", studies=studies)

@app.route("/add_studies", methods = ['post'])
def add_studies():
    study_name = request.form.get("study_name")
    count = cursor.execute("select * from studies where studies_name = '"+str(study_name)+"'")
    conn.commit()
    if count == 0:
        cursor.execute("insert into studies(studies_name) values('"+str(study_name)+"')")
        conn.commit()
        return redirect("/add_view_studies")
    else:
        return render_template("umessage.html", umessage="Already Study Name Exist")

@app.route("/add_view_degree")
def add_view_degree():
    cursor.execute("select * from studies")
    conn.commit()
    studies = cursor.fetchall()
    cursor.execute("select * from degree")
    conn.commit()
    degrees = cursor.fetchall()
    return render_template("add_view_degree.html", studies=studies, degrees=degrees,get_studies_id=get_studies_id)

@app.route("/add_degree", methods = ['post'])
def add_degree():
    studies_id = request.form.get("studies_id")
    degree_name = request.form.get("degree_name")
    course_name = request.form.get("course_name")
    cursor.execute("insert into degree(degree_name,course_name,studies_id) values('"+str(degree_name)+"', '"+str(course_name)+"' , '"+str(studies_id)+"')")
    conn.commit()
    return redirect("/add_view_degree")

def get_studies_id(studies_id):
    cursor.execute("select * from studies where studies_id = '" + str(studies_id) + "'")
    studies = cursor.fetchone()
    studies_name = studies[1]
    return studies_name

@app.route("/recruiter_view_skills")
def recruiter_view_skills():
    cursor.execute("select * from skill")
    conn.commit()
    skills = cursor.fetchall()
    count = len(skills)  # Calculate the count of skills
    return render_template("recruiter_view_skills.html", skills=skills , count=count)

@app.route("/add_job_posts")
def add_job_posts():
    cursor.execute("select * from skill")
    skills = cursor.fetchall()
    cursor.execute("select * from degree")
    degrees = cursor.fetchall()
    return render_template("add_job_posts.html",degrees=degrees , get_studies_id=get_studies_id , skills=skills)

@app.route("/add_job_post1", methods = ['post'])
def add_job_post1():
    company_name = request.form.get("company_name")
    experience_needed = request.form.get("experience_needed")
    end_date = request.form.get("end_date")
    skill_ids = request.form.getlist("skill_id")
    degree_ids = request.form.getlist("degree_id")
    job_title = request.form.get("job_title")
    no_of_vacancies = request.form.get("no_of_vacancies")
    description = request.form.get("description")
    job_type = request.form.get("job_type")
    posted_date = datetime.now().date()
    if session["role"] == 'university':
        degree_id = degree_ids[0] if degree_ids else None
        if degree_id:
            cursor.execute("insert into jobpost(company_name,job_type,job_title,description,experience_needed,posted_date,end_date,no_of_vacancies,status,degree_id) values('"+str(company_name)+"', '"+str(job_type)+"', '"+str(job_title)+"', '"+str(description)+"', '"+str(experience_needed)+"', '"+str(posted_date)+"', '"+str(end_date)+"', '"+str(no_of_vacancies)+"', 'Job Posted', '"+str(degree_id)+"')")
            conn.commit()
        jobpost_id = cursor.lastrowid
        for skill_id in skill_ids:
            cursor.execute("insert into recruiter_skills(skill_id,jobpost_id) values ('"+str(skill_id)+"', '"+str(jobpost_id)+"')")
            conn.commit()
        for degree_id in degree_ids:
            degree_id = degree_id
            cursor.execute("insert into jobpost_qualification_degrees(degree_id,jobpost_id) values ('" + str(degree_id) + "', '" + str(jobpost_id) + "')")
            conn.commit()
            cursor.execute("select * from student where degree_id = '" + str(degree_id) + "'")
            students = cursor.fetchall()
            for student in students:
                send_email("New Job Posted"," Hello " + str(student[1]) +  " New job opportunity available! Check it out now.", student[2])
        return render_template("umessage.html", umessage="Job Posted")
    elif session["role"] == 'recruiter':
        recruiter_id = session['recruiter_id']
        degree_id = degree_ids[0] if degree_ids else None
        if degree_id:
            cursor.execute("insert into jobpost(company_name,job_type,job_title,description,experience_needed,posted_date,end_date,no_of_vacancies,status,degree_id,recruiter_id) values('" + str(company_name) + "', '" + str(job_type) + "', '" + str(job_title) + "', '" + str( description) + "', '" + str(experience_needed) + "', '" + str(posted_date) + "', '" + str(end_date) + "', '" + str(no_of_vacancies) + "', 'Job Posted', '" + str(degree_id) + "', '" + str(recruiter_id) + "')")
            conn.commit()
        jobpost_id = cursor.lastrowid
        for skill_id in skill_ids:
            cursor.execute("insert into recruiter_skills(skill_id,jobpost_id,recruiter_id) values ('" + str(skill_id) + "', '" + str(jobpost_id) + "', '" + str(recruiter_id) + "')")
            conn.commit()
        for degree_id in degree_ids:
            cursor.execute("insert into jobpost_qualification_degrees(degree_id,jobpost_id,recruiter_id) values ('" + str(degree_id) + "', '" + str(jobpost_id) + "',  '" + str(recruiter_id) + "')")
            conn.commit()
            cursor.execute("select * from student where degree_id = '" + str(degree_id) + "'")
            students = cursor.fetchall()
            for student in students:
                send_email("New Job Posted"," Hello " + str(student[1]) + " New job opportunity available! Check it out now.", student[2])
        return render_template("rmessage.html", rmessage="Job Posted")

@app.route("/view_posts")
def view_posts():
    if session['role'] == 'university':
        cursor.execute("select * from jobpost")
        conn.commit()
    elif session['role'] == 'recruiter':
        recruiter_id = session['recruiter_id']
        cursor.execute("select * from jobpost where recruiter_id = '"+str(recruiter_id)+"'")
        conn.commit()
    jobposts = cursor.fetchall()
    return render_template("view_posts.html",jobposts=jobposts,get_jobpost_id_by_jobpost=get_jobpost_id_by_jobpost,get_recruiter_id_by_jobpost=get_recruiter_id_by_jobpost,get_degree_details=get_degree_details)

def get_jobpost_id_by_jobpost(jobpost_id):
    cursor.execute("select * from recruiter_skills where jobpost_id = '" + str(jobpost_id) + "'")
    conn.commit()
    recruiter_skills = cursor.fetchall()
    skill_names = []
    for recruiter_skill in recruiter_skills:
        skill_ids = str(recruiter_skill[1]).split(',')
        for skill_id in skill_ids:
            cursor.execute("select skill_name from skill where skill_id = '"+str(skill_id)+"'")
            skill_name = cursor.fetchone()[0]
            skill_names.append(skill_name)
    return skill_names

def get_recruiter_id_by_jobpost(jobpost_id):
    cursor.execute("select * from jobpost where jobpost_id = '" + str(jobpost_id) + "'")
    conn.commit()
    recruiter_skill = cursor.fetchone()
    recruiter_id = recruiter_skill[10]
    cursor.execute("select * from recruiter where recruiter_id= '"+str(recruiter_id)+"'")
    recruiter = cursor.fetchone()
    return recruiter

def get_degree_details(jobpost_id):
    cursor.execute("select * from jobpost_qualification_degrees where jobpost_id = '" + str(jobpost_id) + "'")
    conn.commit()
    jobpost_qualification_degrees = cursor.fetchall()
    degree_details = []
    for jobpost_qualification_degree in jobpost_qualification_degrees:
        degree_id = jobpost_qualification_degree[1]
        cursor.execute("SELECT * FROM degree WHERE degree_id = '"+str(degree_id)+"'")
        degree = cursor.fetchone()
        studies_id = degree[3]
        degree_name = degree[1]
        course_name = degree[2]
        cursor.execute("select * from studies where studies_id = '"+str(studies_id)+"'")
        studies = cursor.fetchone()
        studies_name = studies[1]
        degree_details.append((degree_name, course_name, studies_name))
    return degree_details


@app.route("/student_view_posts")
def student_view_posts():
    cursor.execute("select * from jobpost")
    conn.commit()
    jobposts = cursor.fetchall()
    return render_template("student_view_posts.html",jobposts=jobposts)

@app.route("/get_job_post")
def get_job_post():
    search_query = request.args.get('search_query', '').lower()
    if search_query:
        cursor.execute("""
                SELECT DISTINCT jp.* 
                FROM jobpost jp 
                JOIN jobpost_qualification_degrees jqd ON jp.jobpost_id = jqd.jobpost_id 
                JOIN degree d ON jqd.degree_id = d.degree_id 
                JOIN recruiter_skills rs ON jp.jobpost_id = rs.jobpost_id 
                JOIN skill s ON rs.skill_id = s.skill_id 
                WHERE LOWER(jp.job_title) LIKE %s 
                OR LOWER(jp.company_name) LIKE %s 
                OR LOWER(jp.experience_needed) LIKE %s 
                OR LOWER(d.course_name) LIKE %s
                OR LOWER(s.skill_name) LIKE %s
            """, (
            '%' + search_query + '%',
            '%' + search_query + '%',
            '%' + search_query + '%',
            '%' + search_query + '%',
            '%' + search_query + '%'
        ))
    else:
        cursor.execute("SELECT * FROM jobpost")
    jobposts = cursor.fetchall()
    return render_template("get_job_post.html",jobposts=jobposts,get_jobpost_id_by_jobpost=get_jobpost_id_by_jobpost,get_recruiter_id_by_jobpost=get_recruiter_id_by_jobpost,get_end_date=get_end_date,get_status_by_jobpost_id=get_status_by_jobpost_id,get_degree_details=get_degree_details)

def get_end_date(jobpost_id):
    cursor.execute("select * from jobpost where jobpost_id = '"+str(jobpost_id)+"'")
    jobpost = cursor.fetchone()
    end_date = datetime.strptime(jobpost[7], '%Y-%m-%d').date()
    current_date = datetime.now().date()
    if end_date < current_date:
        return False
    else:
        return True

@app.route("/apply_job")
def apply_job():
    jobpost_id = request.args.get("jobpost_id")
    application_date = datetime.now().date()
    student_id = session['student_id']
    cursor.execute("insert into application(application_date,status,student_id,jobpost_id) values('"+str(application_date)+"', 'Applied Job Application', '"+str(student_id)+"', '"+str(jobpost_id)+"')")
    conn.commit()
    return render_template("smessage.html", smessage="Applied Job Successfully")

def get_status_by_jobpost_id(jobpost_id):
    student_id = session['student_id']
    cursor.execute("select * from application where jobpost_id = '"+str(jobpost_id)+"' and student_id = '"+str(student_id)+"'")
    application = cursor.fetchone()
    return application


@app.route("/student_view_profile")
def student_view_profile():
    student_id = session['student_id']
    skill_names = []
    qualification_details = []
    work_experience_details = []

    cursor.execute("select * from student where student_id = '"+str(student_id)+"'")
    student = cursor.fetchone()

    cursor.execute("select * from student_skills where student_id = '"+str(student_id)+"'")
    student_skills = cursor.fetchall()
    for student_skill in student_skills:
        skill_ids = str(student_skill[2]).split(',')
        for skill_id in skill_ids:
            cursor.execute("select skill_name from skill where skill_id = '" + str(skill_id) + "'")
            skill_name = cursor.fetchone()[0]
            skill_names.append(skill_name)

    cursor.execute("select * from qualification where student_id = '"+str(student_id)+"'")
    student_qualifications = cursor.fetchall()
    for student_qualification in student_qualifications:
        qualification_ids = str(student_qualification[0]).split(',')
        for qualification_id in qualification_ids:
            cursor.execute("select * from qualification where qualification_id = '" + str(qualification_id) + "'")
            qualification = cursor.fetchone()
            qualification_details.append(qualification)

    cursor.execute("select * from work_experience where student_id = '"+str(student_id)+"'")
    work_experiences = cursor.fetchall()
    for work_experience in work_experiences:
        work_experience_ids = str(work_experience[0]).split(',')
        for work_experience_id in work_experience_ids:
            cursor.execute("select * from work_experience where work_experience_id = '" + str(work_experience_id) + "'")
            work_experience = cursor.fetchone()
            work_experience_details.append(work_experience)

    cursor.execute("select * from degree")
    degree = cursor.fetchone()
    studies_id = degree[3]
    cursor.execute("select * from studies where studies_id = '"+str(studies_id)+"'")
    studies = cursor.fetchone()
    return render_template("student_view_profile.html",student=student,skill_names=skill_names,qualification_details=qualification_details,work_experience_details=work_experience_details,degree=degree,studies=studies)


@app.route("/update_profile")
def update_profile():
    student_id = request.args.get("student_id")
    skill_names = []
    qualification_details = []
    work_experience_details = []

    cursor.execute("select * from student where student_id = '"+str(student_id)+"'")
    student = cursor.fetchone()

    cursor.execute("select * from student_skills")
    student_skills = cursor.fetchall()
    for student_skill in student_skills:
        skill_ids = str(student_skill[2]).split(',')
        for skill_id in skill_ids:
            cursor.execute("select skill_name from skill where skill_id = '" + str(skill_id) + "'")
            skill_name = cursor.fetchone()[0]
            skill_names.append(skill_name)

    cursor.execute("select * from qualification")
    student_qualifications = cursor.fetchall()
    for student_qualification in student_qualifications:
        qualification_ids = str(student_qualification[0]).split(',')
        for qualification_id in qualification_ids:
            cursor.execute("select * from qualification where qualification_id = '" + str(qualification_id) + "'")
            qualification = cursor.fetchone()
            qualification_details.append(qualification)

    cursor.execute("select * from work_experience")
    work_experiences = cursor.fetchall()
    for work_experience in work_experiences:
        work_experience_ids = str(work_experience[0]).split(',')
        for work_experience_id in work_experience_ids:
            cursor.execute("select * from work_experience where work_experience_id = '" + str(work_experience_id) + "'")
            work_experience = cursor.fetchone()
            work_experience_details.append(work_experience)
    return render_template("update_profile.html", student=student,skill_names=skill_names,qualification_details=qualification_details,work_experience_details=work_experience_details)

@app.route("/update_student_profile")
def update_student_profile():
    return render_template("update_student_profile.html")

@app.route("/update_student_profile1", methods = ['post'])
def update_student_profile1():
    student_id = request.form.get("student_id")
    name = request.form.get("name")
    email = request.form.get("email")
    date_of_birth = request.form.get("date_of_birth")
    gender = request.form.get("gender")
    phone = request.form.get("phone")
    password = request.form.get("password")
    address = request.form.get("address")
    resume = request.files.get("resume")
    if resume:
        path = APP_ROOT + "/static/images/" + resume.filename
        resume.save(path)
        resume_filename = resume.filename
    else:
        resume_filename = request.form.get("resume_filename")
    cursor.execute("update student set name = '"+str(name)+"', email = '"+str(email)+"', date_of_birth = '"+str(date_of_birth)+"', gender = '"+str(gender)+"', phone = '"+str(phone)+"', password = '"+str(password)+"', address = '"+str(address)+"', resume = '"+str(resume_filename)+"' where student_id = '"+str(student_id)+"'")
    conn.commit()
    return render_template("smessage.html", smessage="Student Profile Updated Successfully")

@app.route("/add_student_skills")
def add_student_skills():
    student_id = request.args.get("student_id")
    cursor.execute("select * from skill")
    skills = cursor.fetchall()
    return render_template("add_student_skills.html",student_id=student_id,skills=skills)

@app.route("/add_student_skills_1", methods = ['post'])
def add_student_skills_1():
    student_id = request.form.get("student_id")
    skill_ids = request.form.get("skill_id").split(',')
    for skill_id in skill_ids:
        cursor.execute("select * from student_skills where student_id = '" + str(student_id) + "' and skill_id = '" + str(skill_id) + "'")
        existing_skill = cursor.fetchone()
        if not existing_skill:
            cursor.execute("insert into student_skills(student_id,skill_id) values('"+str(student_id)+"', '"+str(skill_id)+"' )")
            conn.commit()
        else:
            return render_template("smessage.html", smessage="Already Skill Existed")
    return redirect("/student_view_profile")

@app.route("/add_student_qualification")
def add_student_qualification():
    student_id = session['student_id']
    cursor.execute("select * from qualification where student_id = '"+str(student_id)+"'")
    conn.commit()
    qualifications = cursor.fetchall()
    return render_template("add_student_qualification.html",qualifications=qualifications)

@app.route("/add_student_qualification1", methods = ['post'])
def add_student_qualification1():
    student_id = session['student_id']
    qualification = request.form.get("qualification")
    from_month_year = request.form.get("from_month_year")
    university_name = request.form.get("university_name")
    to_month_year = request.form.get("to_month_year")
    count = cursor.execute("select * from qualification where qualification = '"+str(qualification)+"' and student_id = '"+str(student_id)+"'")
    conn.commit()
    if count == 0 :
        cursor.execute("insert into qualification(qualification,from_month_year,to_month_year,university_name,student_id) values('"+str(qualification)+"', '"+str(from_month_year)+"' , '"+str(to_month_year)+"' , '"+str(university_name)+"', '"+str(student_id)+"')")
        conn.commit()
        return redirect("/add_student_qualification")
    else:
        return render_template("smessage.html", smessage="Already Qualification Existed")


@app.route("/delete_student_qualification")
def delete_student_qualification():
    qualification_id = request.args.get("qualification_id")
    cursor.execute("DELETE FROM qualification WHERE qualification_id = '" + str(qualification_id) + "'")
    conn.commit()
    return redirect("/add_student_qualification")

@app.route("/add_student_experience")
def add_student_experience():
    student_id = session['student_id']
    cursor.execute("select * from work_experience where student_id = '" + str(student_id) + "'")
    conn.commit()
    work_experiences = cursor.fetchall()
    return render_template("add_student_experience.html",work_experiences=work_experiences)

@app.route("/add_student_experience1", methods = ['post'])
def add_student_experience1():
    student_id = session['student_id']
    job_title = request.form.get("job_title")
    from_month_year = request.form.get("from_month_year")
    company_name = request.form.get("company_name")
    to_month_year = request.form.get("to_month_year")
    present = request.form.get("present")
    no_work_experience = request.form.get("no_work_experience")

    if present == "on":
        # If "Present" checkbox is checked, set to_month_year to current month and year
        to_month_year = datetime.now().strftime("%Y-%m")
    else:
        to_month_year = request.form.get("to_month_year")

    count = cursor.execute("select * from work_experience where company_name = '"+str(company_name)+"'")
    conn.commit()
    if count == 0 :
        if no_work_experience == "on":
            cursor.execute("insert into work_experience(company_name,from_month_year,to_month_year,job_title,student_id,no_work_experience) values('"+str(company_name)+"', '"+str(from_month_year)+"' , '"+str(to_month_year)+"' , '"+str(job_title)+"', '"+str(student_id)+"', 'No Work Experience' )")
            conn.commit()
            return redirect("/add_student_experience")
        else:
            cursor.execute("insert into work_experience(company_name,from_month_year,to_month_year,job_title,student_id,no_work_experience) values('" + str(company_name) + "', '" + str(from_month_year) + "' , '" + str(to_month_year) + "' , '" + str(job_title) + "', '" + str(student_id) + "', ' ' )")
            conn.commit()
            return redirect("/add_student_experience")
    else:
        return render_template("smessage.html", smessage="Already Work Experience With This Company Existed")


@app.route("/delete_student_experience")
def delete_student_experience():
    work_experience_id = request.args.get("work_experience_id")
    cursor.execute("DELETE FROM work_experience WHERE work_experience_id = '" + str(work_experience_id) + "'")
    conn.commit()
    return redirect("/add_student_experience")

@app.route("/view_applications")
def view_applications():
    type = request.args.get('type')
    if session["role"] == 'student':
        if type == 'application':
            student_id = session['student_id']
            cursor.execute("select * from application where student_id = '" + str(student_id) + "' and (status = 'Applied Job Application' OR status = 'Accepted Application' OR status = 'Interview Scheduled' OR status = 'Student Accepted Interview Schedule')")
        elif type == 'history':
            student_id = session['student_id']
            cursor.execute("select * from application where student_id = '" + str(student_id) + "' and (status = 'Rejected Application' OR status = 'Student Rejected Interview Schedule' OR status = 'Selected' OR status = 'Rejected')")
    elif session["role"] == 'recruiter':
        if type == 'application':
            recruiter_id = session['recruiter_id']
            cursor.execute("select * from jobpost where recruiter_id = '"+str(recruiter_id)+"'")
            jobpost = cursor.fetchone()
            jobpost_id = jobpost[0]
            cursor.execute("select * from application where jobpost_id = '"+str(jobpost_id)+"' and (status = 'Applied Job Application' OR status = 'Accepted Application' OR status = 'Interview Scheduled' OR status = 'Student Accepted Interview Schedule')")
        elif type == 'history':
            recruiter_id = session['recruiter_id']
            cursor.execute("select * from jobpost where recruiter_id = '"+str(recruiter_id)+"'")
            jobpost = cursor.fetchone()
            jobpost_id = jobpost[0]
            cursor.execute("select * from application where jobpost_id = '"+str(jobpost_id)+"' and (status = 'Rejected Application' OR status = 'Student Rejected Interview Schedule' OR status = 'Selected' OR status = 'Rejected')")
    elif session["role"] == 'university':
        if type == 'application':
            cursor.execute("select * from application where (status = 'Applied Job Application' OR status = 'Accepted Application' OR status = 'Interview Scheduled' OR status = 'Student Accepted Interview Schedule')")
        elif type == 'history':
            cursor.execute("select * from application where (status = 'Rejected Application' OR status = 'Student Rejected Interview Schedule' OR status = 'Selected' OR status = 'Rejected')")

    applications = cursor.fetchall()
    cursor.execute("select * from degree")
    degree = cursor.fetchone()
    studies_id = degree[3]
    cursor.execute("select * from studies where studies_id = '" + str(studies_id) + "'")
    studies = cursor.fetchone()
    return render_template("view_applications.html",applications=applications,degree=degree,studies=studies,get_jobpost_id=get_jobpost_id,get_student_details=get_student_details,get_skills=get_skills,get_student_qualification=get_student_qualification,get_student_work_experience=get_student_work_experience,get_interview_date=get_interview_date,get_end_date=get_end_date,get_recruiter_id_byjobpost_id=get_recruiter_id_byjobpost_id)

def get_jobpost_id(jobpost_id):
    cursor.execute("select * from jobpost where jobpost_id = '"+str(jobpost_id)+"'")
    jobpost = cursor.fetchone()
    return jobpost

def get_recruiter_id_byjobpost_id(jobpost_id):
    cursor.execute("select * from jobpost where jobpost_id = '"+str(jobpost_id)+"'")
    jobpost = cursor.fetchone()
    recruiter_id = jobpost[10]
    return recruiter_id

@app.route("/view_jobpost_details")
def view_jobpost_details():
    jobpost_id = request.args.get("jobpost_id")
    cursor.execute("select * from jobpost where jobpost_id = '"+str(jobpost_id)+"'")
    jobpost = cursor.fetchone()
    return render_template("view_jobpost_details.html",jobpost=jobpost,get_degree_details=get_degree_details,get_jobpost_id_by_jobpost=get_jobpost_id_by_jobpost,get_recruiter_id_by_jobpost=get_recruiter_id_by_jobpost)

def get_student_details(student_id):
    cursor.execute("select * from student where student_id= '"+str(student_id)+"'")
    student = cursor.fetchone()
    return student

@app.route("/accept_application")
def accept_application():
    application_id = request.args.get("application_id")
    return redirect("/add_schedule?application_id=" + str(application_id))

@app.route("/add_schedule")
def add_schedule():
    application_id = request.args.get("application_id")
    return render_template("add_schedule.html",application_id=application_id)

@app.route("/add_schedule1", methods = ['post'])
def add_schedule1():
    application_id = request.form.get("application_id")
    description = request.form.get("description")
    interview_date = request.form.get("interview_date")
    cursor.execute("update application set status = 'Interview Scheduled' where application_id = '"+str(application_id)+"'")
    conn.commit()
    cursor.execute("insert into interview_schedule(interview_date,status,description,application_id) values('"+str(interview_date)+"', 'Interview Scheduled', '"+str(description)+"' , '"+str(application_id)+"')")
    conn.commit()
    return render_template("rmessage.html", rmessage="Interview Scheduled Successfully")

@app.route("/reject_application")
def reject_application():
    application_id = request.args.get("application_id")
    cursor.execute("update application set status = 'Rejected Application' where application_id = '"+str(application_id)+"'")
    conn.commit()
    return render_template("rmessage.html", rmessage="Rejected Application Successfully")

def get_skills(student_id):
    skill_names = []
    cursor.execute("select * from student_skills where student_id = '" + str(student_id) + "'")
    student_skills = cursor.fetchall()
    for student_skill in student_skills:
        skill_ids = str(student_skill[2]).split(',')
        for skill_id in skill_ids:
            cursor.execute("select skill_name from skill where skill_id = '" + str(skill_id) + "'")
            skill_name = cursor.fetchone()[0]
            skill_names.append(skill_name)
    return skill_names

def get_student_qualification(student_id):
    qualification_details = []
    cursor.execute("select * from qualification where student_id = '" + str(student_id) + "'")
    student_qualifications = cursor.fetchall()
    for student_qualification in student_qualifications:
        qualification_ids = str(student_qualification[0]).split(',')
        for qualification_id in qualification_ids:
            cursor.execute("select * from qualification where qualification_id = '" + str(qualification_id) + "'")
            qualification = cursor.fetchone()
            qualification_details.append(qualification)
    return qualification_details

def get_student_work_experience(student_id):
    work_experience_details = []
    cursor.execute("select * from work_experience where student_id = '" + str(student_id) + "'")
    work_experiences = cursor.fetchall()
    for work_experience in work_experiences:
        work_experience_ids = str(work_experience[0]).split(',')
        for work_experience_id in work_experience_ids:
            cursor.execute("select * from work_experience where work_experience_id = '" + str(work_experience_id) + "'")
            work_experience = cursor.fetchone()
            work_experience_details.append(work_experience)
    return work_experience_details

def get_interview_date(application_id):
    cursor.execute("select * from interview_schedule where application_id = '"+str(application_id)+"'")
    interview_schedule = cursor.fetchone()
    if interview_schedule is not None:
        interview_date = datetime.fromisoformat(interview_schedule[1])
        interview_date1 = datetime.strftime(interview_date, '%Y-%m-%d %I:%M %p')
        return interview_schedule, interview_date1
    else:
        return None, None

@app.route("/student_accept_interview_schedule")
def student_accept_interview_schedule():
    application_id = request.args.get("application_id")
    cursor.execute("update application set status = 'Student Accepted Interview Schedule' where application_id = '"+str(application_id)+"'")
    conn.commit()
    cursor.execute("update interview_schedule set status = 'Student Accepted Interview Schedule' where application_id = '"+str(application_id)+"'")
    conn.commit()
    return render_template("smessage.html", smessage="Accepted Interview Schedule Successfully")

@app.route("/student_reject_interview_schedule")
def student_reject_interview_schedule():
    application_id = request.args.get("application_id")
    cursor.execute("update application set status = 'Student Rejected Interview Schedule' where application_id = '"+str(application_id)+"'")
    conn.commit()
    cursor.execute("update interview_schedule set status = 'Student Rejected Interview Schedule' where application_id = '"+str(application_id)+"'")
    conn.commit()
    return render_template("smessage.html", smessage="Rejected Interview Schedule Successfully")

@app.route("/selected_application")
def selected_application():
    application_id = request.args.get("application_id")
    cursor.execute("update application set status = 'Selected' where application_id = '"+str(application_id)+"'")
    conn.commit()
    cursor.execute("update interview_schedule set status = 'Selected' where application_id = '"+str(application_id)+"'")
    conn.commit()

    cursor.execute("select * from application where application_id = '"+str(application_id)+"' and status = 'Selected' ")
    application = cursor.fetchone()
    jobpost_id = application[4]
    cursor.execute("select * from jobpost where jobpost_id = '"+str(jobpost_id)+"'")
    jobpost = cursor.fetchone()
    no_of_vacancies = jobpost[8]
    no_of_vacancies1 = int(no_of_vacancies) - 1
    cursor.execute("update jobpost set no_of_vacancies = '"+str(no_of_vacancies1)+"' where jobpost_id = '" + str(jobpost_id) + "'")
    conn.commit()
    cursor.execute("select * from jobpost where jobpost_id = '"+str(jobpost_id)+"'")

    return render_template("rmessage.html", rmessage="Selected Student")

@app.route("/rejected_application")
def rejected_application():
    application_id = request.args.get("application_id")
    cursor.execute("update application set status = 'Rejected' where application_id = '"+str(application_id)+"'")
    conn.commit()
    cursor.execute("update interview_schedule set status = 'Rejected' where application_id = '"+str(application_id)+"'")
    conn.commit()
    return render_template("rmessage.html", rmessage="Rejected Student")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)