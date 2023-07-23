# Backend Assignment

### Created a Loan Management System as per requirements.

***Note: I have used Windows-10 x64 system (I do not have Linux machine), some steps may vary, so, I attached the setup documentations that I followed during dev.***

## Creating the virtual environment

Clone this project and create a Virtual Environment & activate the venv in the project location.

```sh
virtualenv venv
```
If you're in windows:
```sh
venv/Scripts/activate
```  

If you're in Linux:
```sh
source venv/bin/activate
```  

## Install all required dependencies from requirements.txt file
```sh
pip3 install -r requirements.txt
```

Rename `.env-dev` file to `.env` and fill your database credentials.
  
## Install Redis 


Install Redis on your computer by below link:
```sh
https://redis.io/docs/getting-started/installation/
```

OR 

Follow the below documentation:
```sh
https://docs.servicestack.net/install-redis-windows
```

Now, on command promp or in shell type this to configure Redis:
```sh
redis-cli
```
Then, open the redis-server on the shell:
```sh
redis-server
```

Something link below will appear:
```sh
[5644] 21 Jul 11:07:32.876 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[5644] 21 Jul 11:07:32.877 # Redis version=5.0.14.1, bits=64, commit=ec77f72d, modified=0, pid=5644, just started
[5644] 21 Jul 11:07:32.878 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
                _._
           _.-``__ ''-._
      _.-``    `.  `_.  ''-._           Redis 5.0.14.1 (ec77f72d/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 5644
  `-._    `-._  `-./  _.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |           http://redis.io
  `-._    `-._`-.__.-'_.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |
  `-._    `-._`-.__.-'_.-'    _.-'
      `-._    `-.__.-'    _.-'
          `-._        _.-'
              `-.__.-'

[5644] 21 Jul 11:07:32.909 # Server initialized
[5644] 21 Jul 11:07:32.925 * DB loaded from disk: 0.012 seconds
[5644] 21 Jul 11:07:32.925 * Ready to accept connections
```

### Install MySQL Database

To Install MySQL Database, I have followed this documentation:
```sh
https://www.dataquest.io/blog/install-mysql-windows/
```

Create Database in your MySQL shell / or in CMD by:
```sh
mysql -u <mysql-user-name> -p
```

Run a CREATE DATABASE command to create a new database. 
```sh
CREATE DATABASE <mysql-database-name>; 
```
***For example: CREATE DATABASE assignment;***

## Initial Project setup
Open file backend_assignment/settings.py and change the MySQL Database settings such as: 
```sh
# MySQL Database Setup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USERNAME'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST':'localhost',
        'PORT':'3306',
    }
}
```
Now, change the values in `.env` to your own values, such as:

```sh
DATABASE_NAME = assignment
DATABASE_USERNAME = sample_username
DATABASE_PASSWORD = sample_password
```


## Creating and Setting up Models  

```sh
cd backend_assignment/
```
```sh
python3 manage.py makemigrations loan payments user
```
```sh
python3 manage.py migrate 
```
Run the Django Server:
```sh
python3 manage.py runserver
```
  
## Start Celery worker  
Inside your project dir and in the venv, type:
```sh
$ celery -A backend_assignment.celery worker --pool=solo -l INFO
```


#### ***File path for transactions_data.csv is backend_assignment/static/***

## API ENDPOINTS  

http://localhost:8000/ 
  
### Create User API 
[POST Request]
-  http://localhost:8000/api/register-user/
  
### Apply for Loan API
  
[POST req]  
  
-  http://localhost:8000/api/apply-loan/ 

### Make Payment API
[POST req] 
-  http://localhost:8000/api/make-payment/
  
### Get Transactions Statement API
[GET req]  
-  http://localhost:8000/api/get-statement/


## API Details:
For each API, attached the CURLs:

### Create User API
```sh
curl --location 'localhost:8000/api/register-user/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "aadhar_number": "1051ed87-1007-4d3b-8d11-b02ab008e2ea",
    "name": "Vivek Ghosh",
    "email": "vivek@email.com",
    "annual_income": 5000000
}'
```
- aadhar_number : User from transactions_data.csv file (Unique Identifier). {string}
- name: User Name {string}
- email: User Email address {string}
- annual_income: User Annual Income {Float}

### Create Loan API
```sh
curl --location 'localhost:8000/api/apply-loan/' \
--header 'Content-Type: application/json' \
--data '{
    "user_id": "f2eabb0d87cd4bb79bc879010437ad8e",
    "loan_type": "Car",
    "loan_amount": 700000,
    "interest_rate": 18,
    "term_period": 6,
    "disbursement_date": "2023-07-26"
}'
```
- user_id : User Unique UUID. {string}
- loan_type: Type of Loan {string} ['Car', 'Home', 'Personal', 'Education']
- loan_amount: Loan Amount {Float}
- interest_rate: Loan Interest Rate {Float}
- term_period: Loan Term Period (In Months*) {Integer}
- disbursement_dateL Disbursement Date ("YYYY-MM-DD") (Date)


### Make Payment API
```sh
curl --location 'localhost:8000/api/make-payment/' \
--header 'Content-Type: application/json' \
--data '{
    "loan_id": "ca6542d6-b911-4e20-a5d0-3ba395ccf636",
    "amount": 122868
}'
```
- loan_id : Loan ID (Unique UUID Identifier). {string}
- amount: Amount to be Paid for respective Loan {Float}

### get Transactions Statement API
```sh
curl --location 'localhost:8000/api/get-statement/' \
--header 'loan-id: ca6542d6-b911-4e20-a5d0-3ba395ccf639'
```
- loan_id : Loan ID (Unique UUID Identifier). {string}


## Some Useful Resources:

### Attached the postman collection inside the static folder

Open and import the file inside Postman:
***backend_assignments/static/backend_assignment.postman_collection.json***