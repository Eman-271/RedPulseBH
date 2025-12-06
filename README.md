# RedPulseBH
RedPulseBH – Blood Donation Web Platform

RedPulseBH is a full-stack web application designed to streamline the blood donation process in Bahrain.
The system connects hospitals with registered blood donors, enabling hospitals to post urgent blood requests and donors to respond quickly and efficiently.

The project was developed using Django, MongoDB, and Bootstrap, following a complete Model-View-Template architecture and fully integrating NoSQL database operations (CRUD).

1. Project Overview

RedPulseBH serves as a centralized digital platform to help hospitals communicate their blood needs to eligible donors.
The system provides:

Hospital registration and authentication

Donor registration and authentication

A dashboard for hospitals to submit and manage blood requests

A donor interface to view all active requests and respond

A Django Admin portal for full data management

A MongoDB backend optimized with indexes for performance

The platform aims to reduce delays in communication, increase donor engagement, and improve emergency medical response times.

2. Key Features
Hospital Features

Create, edit, update, and delete blood requests

Manage request status (Open / Closed)

View donor responses

Hospital profile editing

Secure login system

Donor Features

Donor signup and login

View all active blood requests

Respond to requests (Accept / Reject)

Donor profile editing

View donation request history

System Features

MongoDB NoSQL database

Automatic index creation (email, hospital licence number)

Django Admin site for centralized control

Fully responsive Bootstrap user interface

3. Technologies Used

Backend Framework: Django

Database: MongoDB (with Djongo connector)

Frontend: HTML, CSS, Bootstrap

Version Control: GitHub

Environment Management: Anaconda Virtual Environment

Templating Engine: Django Templates

4. Installation and Setup Instructions

Follow the steps below to run the project on any machine:

Step 1: Clone the GitHub Repository
git clone https://github.com/Eman-271/RedPulseBH.git

Step 2: Navigate to the Project Folder
cd RedPulseBH

Step 3: Install Required Packages

Make sure Python and pip are installed. Then run:

pip install -r requirements.txt

Step 4: Run the Development Server
python manage.py runserver

Step 5: Open the Project in Browser

Open:

http://127.0.0.1:8000/

5. Project Structure
RedPulseBH/
│── hospitals/          (Main Django App)
│── templates/          (HTML Templates)
│── static/             
│── manage.py           (Django Management File)
│── requirements.txt    (Installed Packages)
│── db.json / MongoDB   (NoSQL Database)
│── README.md           (Documentation)

6. Database Overview (MongoDB)

The system uses four main MongoDB collections:

hospitals_hospital – Hospital accounts

hospitals_donor – Donor accounts

hospitals_bloodrequest – Blood request posts

donor_request_responses – Donor acceptance/rejection records

Indexes Used

email – unique index

licence_number – unique index for hospitals

_id – default MongoDB index

Indexes improve query speed and ensure no duplicate records.

7. Version Control (GitHub)

GitHub was used extensively to manage code updates and organize development.

Repository Includes:

Django backend files

HTML templates

Bootstrap assets

MongoDB models and migrations

Documentation files

Branches Used:

main – final stable code

Additional branches for testing and development (if needed)

Commit Messages Include:

Added features

Updated templates

Bug fixes

CRUD operations

Database updates

8. Extra Challenging Work Completed

This project required additional research and debugging beyond typical assignments, including:

Integrating Django with MongoDB using Djongo, which is not officially supported by Django

Solving schema conflicts and migration errors

Designing dynamic hospital and donor dashboards

Implementing CRUD operations using NoSQL documents instead of traditional SQL tables

Creating unique index validations inside MongoDB

Managing database updates and model relations manually

Ensuring compatibility across multiple devices with Bootstrap

This effort resulted in a polished, scalable system built from scratch.

9. Developer Information

Eman Khamdan

Bahrain Polytechnic

Student ID: 202200542

10. Conclusion

RedPulseBH successfully demonstrates the development of a complete, database-driven web application using Django and MongoDB.
The platform supports real-time communication between hospitals and donors, offers a clean user interface, and incorporates strong backend logic for data management.
The application fulfills all academic requirements and showcases advanced practical skills in web development, NoSQL databases, and version control.
