# SVC_System
Subversion control system using IBM bluemix Cloudant and AWS MySQL RDS
Go to IBM bluemix create an account.
Start a cloudant instance and get the connection string and username and password to connect to Database.
Go to  def conn() in server.py in the project and paste your parameters in the corresponding varaibles to connect you project to cloudant NoSQl DB.
Go to AWS start a new account and start a new MySQL RDS instance.
Download SQL workbench to connect to you MySQL instance.
Create a new Database and a new table in your MySQL instance.
In the new table insert username and a password for authentication.
Go to def auth() in server.py in the project and paste your parameters in the corresponding varaibles to connect you project to the AWS MySQl RDS instance to authenticate users for login.
Once cloudant NoSQL DB and MySQL instance is initialized and connected to your project, just run the python.py file.
Go to localhost:8000/ you should see the login page.
Login with username and password you inserted into your MySQL table to login.
If you want to host the project online change the host in line 181 in server.py to 0.0.0.0.
