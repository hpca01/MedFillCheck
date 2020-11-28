# MedFillCheck
REST Api made for an android app I am designing to make a virtual refill list based on automated dispensing system report.



### Project is no longer active

<br>

Project uses
- Flask
- Flask Marshmallow(for serialization)
- Flask JWT(for identity management and authentication)
- SQLAlchemy for database
- Blueprint for managing the individual resources
- passlib for hashing passwords

<br>
<br>
<br>

For the front-end(still to be implemented in Native Android), here are the designs:
<br>
![nav drawer](images/nav%20drawer.jpg)
<br>
<br>
Macro view of the devices in the hospital:
<br>
![high level view](images/Main%20Refill%20Board.jpg)
<br>
<br>
Device level view (includes medications)
<br>
![device level view](images/Device%20Detail.jpg)
<br>
<br>
Technician pulling medication to refill(via scanning or picking):
<br>
![tech pulls meds](images/Device%20Detail-1.jpg)
<br>
<br>
Pharmacist checking view(via scanning or picking):
<br>
![checking view](images/Checking%20Activity.jpg)
<br>
<br>
Widget for checking devices that need refills:
<br>
![widget](images/widget.jpg)

