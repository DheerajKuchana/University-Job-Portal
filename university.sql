drop database UniversityRecruitment; 

create database UniversityRecruitment;
use UniversityRecruitment;

create table skill(
skill_id int auto_increment primary key,
skill_name varchar(255) not null
);

create table studies(
studies_id int auto_increment primary key,
studies_name varchar(255) not null
);

create table degree(
degree_id int auto_increment primary key,
degree_name varchar(255),
course_name varchar(255),
studies_id int ,
foreign key (studies_id) references studies(studies_id)
);

create table recruiter(
recruiter_id int auto_increment primary key,
name varchar(255) not null,
email  varchar(255) not null unique,
phone  varchar(255) not null unique,
password varchar(255) not null,
experience  varchar(255) not null ,
address  varchar(255) not null,
status  varchar(255) not null
);

create table jobpost(
jobpost_id int auto_increment primary key,
company_name varchar(255),
job_type varchar(255),
job_title varchar(255),
description varchar(255),
experience_needed varchar(255),
posted_date varchar(255),
end_date varchar(255),
no_of_vacancies varchar(255),
status varchar(255),
recruiter_id int ,
foreign key (recruiter_id) references recruiter(recruiter_id),
degree_id int ,
foreign key (degree_id) references degree(degree_id)
);

create table recruiter_skills(
recruiter_skills_id int auto_increment primary key,
skill_id int ,
foreign key (skill_id) references skill(skill_id),
jobpost_id int ,
foreign key (jobpost_id) references jobpost(jobpost_id),
recruiter_id int ,
foreign key (recruiter_id) references recruiter(recruiter_id)
);

create table jobpost_qualification_degrees(
jobpost_qualification_degrees_id int auto_increment primary key,
degree_id int ,
foreign key (degree_id) references degree(degree_id),
jobpost_id int ,
foreign key (jobpost_id) references jobpost(jobpost_id),
recruiter_id int ,
foreign key (recruiter_id) references recruiter(recruiter_id)
);

create table student(
student_id int auto_increment primary key,
name varchar(255),
email  varchar(255) unique,
phone  varchar(255) ,
password varchar(255) ,
date_of_birth  varchar(255) ,
gender  varchar(255) ,
address  varchar(255),
resume  varchar(255) ,
degree_id int ,
foreign key (degree_id) references degree(degree_id)
);

create table application(
application_id int auto_increment primary key,
application_date varchar(255),
status varchar(255),
student_id int ,
foreign key (student_id) references student(student_id),
jobpost_id int ,
foreign key (jobpost_id) references jobpost(jobpost_id)
);

create table student_skills(
student_skills_id int auto_increment primary key,
student_id int ,
foreign key (student_id) references student(student_id),
skill_id int ,
foreign key (skill_id) references skill(skill_id)
);

create table work_experience(
work_experience_id int auto_increment primary key,
company_name  varchar(255),
from_month_year  varchar(255),
to_month_year  varchar(255),
job_title  varchar(255),
no_work_experience varchar(255),
student_id int ,
foreign key (student_id) references student(student_id)
);


create table qualification(
qualification_id int auto_increment primary key,
qualification  varchar(255),
from_month_year  varchar(255),
to_month_year  varchar(255),
university_name  varchar(255),
student_id int ,
foreign key (student_id) references student(student_id)
);

create table interview_schedule(
interview_schedule_id int auto_increment primary key,
interview_date  varchar(255),
status  varchar(255),
description  varchar(255),
application_id int ,
foreign key (application_id) references application(application_id)
);
