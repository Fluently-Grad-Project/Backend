###  To do:
>   - non Functional Requirements (security bas azon ma3mola ya3ny me7tagen nekhaby el secrets       masalan??, performance blalalalaa)
>   - Chatbot for user lvl and AI conversations with pronunciation analysis  yarab nekhlas ba2a
>   - users voice chat including The NLP for hate speech recognition
>   - 3ayzeen ne3adel el status code beta3 el exceptions
>   - Unit Tests
----

# For frontend team:
```bash
docker pull mennaa/fluently-app:latest 
docker run -p 8000:8000 mennaa/fluently-app:latest
```
# Things to be considered After Security🥱
> Ensure That reported users cannot login to the System, don't appear in the matchmaking,     Friend's list, etc.....   
> Hal el report_score byerga3 zero after lifting suspension 🤔??  
---
# Update Rating column to have a default value 
```sql
ALTER TABLE user_manager ALTER COLUMN rating SET DEFAULT 0.0;

-- Update any existing NULL values
UPDATE user_manager SET rating = 0.0 WHERE rating IS NULL;
```

# To-Be-DoneS-Later     >> after team-meeting probably??

## 📌📌📌📌
> A verify_recaptcha() function was added to call Google's API    
> The login route now requires a recaptcha_token in the request   
> If CAPTCHA validation fails, the login is blocked and logged

---

> localization and globalization    
> run SAST using sonarqube/bandit and inject it to the pipeline --> yes, using GitHub Actions [to-be-learned]    
> run DAST using OWASP ZAP or [Burp Suite]    
> on deployment:
>  - **Use Docker securely:**   
>     - Use non-root users   
>     - Use multi-stage builds   
>     - Scan Docker images (docker scan or Trivy)    
>  -  **Environment Hardening:**    
>     - Disable debug mode in production (uvicorn main:app --env=production)   
>     - Use HTTPS in production (TLS with certbot or Cloudflare)   
>     - Apply CIS Benchmarks for OS and container security   
>  - **Secure secrets in deployment**   
>     - Don’t store tokens or passwords in your GitHub   

----
> ### Password Strength:
>   - At least 8 characters
>   - At least 1 uppercase letter
>   - At least 1 lowercase letter
>   - At least 1 number
>   - At least 1 special character
----

> ### Report User Logic:
>  # user will be suspended when report_score reaches 20
>   - 30 days for users with 3+ critical reports
>   - 15 days for users with 1-2 critical reports
>   - 7 days for users with only low/medium priority reports
----

🚨🚨🚨 **INSTALL/UPGRADE PYTHON 3.6.12**
```bash
black app/ tests/
```
## 📌📌📌📌
# ***BEFORE COMMITTING***

## **Run this to solve the flake8 errors, *to autoformat*:**
```bash 
black . 
```   

```bash
flake8 . --exclude=env,.venv,venv --max-line-length=200 --ignore=E203,E262,W291,W503
```   

```bash
mypy app --exclude '(env|.venv|venv)' --explicit-package-bases
```   
then fix these issues

----

#  Backend Setup & API Documentation

## How to run things    

**To run tests:**
*NOT YET COMPLETED*
```bash
$env:PYTHONPATH = "."
pytest --cov=app tests/
```   

----  

```

## Update the models using these:

```bash
alembic revision --autogenerate -m "... Add ...COLUMN... column to ...TABLE... ..."
```
then:

```bash
alembic upgrade head
```

## 🚨🚨🚨 DB Update
```bash

alembic revision --autogenerate -m "add profile_pic"
alembic revision --autogenerate -m "add UserRating table"
alembic revision --autogenerate -m "blocked_user_ids list a mutable"
```
then:
```bash
alembic upgrade head
```


##  How to Run the Backend
>go to the project main directory and create virtual environment using the following command:
```bash
python -m venv env
#activate this environment using the following command:

# For Windows:
env\Scripts\activate
```

> create a database: fluently
- 🚨 *Ensure your username and password are both: **postgres*** 🚨

```bash
#install dependencies
pip install -r requirements.txt

#run the development server
python -m uvicorn app.main:app --reload
```

---

##  Authentication Endpoints

### 1.  Register New User

* **Endpoint:** `POST /users/register`
* **URL:** [http://127.0.0.1:8000/users/register](http://127.0.0.1:8000/users/register)

####  Request Body

```json
{
  "first_name": "m",
  "last_name": "a",
  "email": "mennatallahahmed892@gmail.com",
  "password": "123",
  "gender": "FEMALE",
  "birth_date": "2003-06-18",
  "languages": ["English", "Turkish"],
  "proficiency_level": "Intermediate",
  "practice_frequency": "15",
  "interests": ["Reading", "Traveling"]
}
```

####  Response

```json
{
  "user": {
    "id": 3,
    "first_name": "m",
    "last_name": "a",
    "email": "mennatallahahmed892@gmail.com",
    "gender": "female",
    "is_verified": false
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "verification_link": "http://localhost:8000/auth/verify-email?email=mennatallahahmed892@gmail.com&code=87a833b165ecabc5935e7870213c23ba"
}
```

>  **Note:**
>
> * A verification email will be sent to the user.
> * Users **cannot log in** until their email is verified.

---

### 2.  Verify Email

* **Endpoint:** `GET /auth/verify-email?email={email}&code={verification_code}`

####  Response

```json
{
  "message": "Email verified successfully."
}
```

---

### 3.  Login

* **Endpoint:** `POST /auth/login`

####  Request Body

```json
{
  "email": "user@gmail.com",
  "password": "string"
}
```

####  Response

```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```

---

### 4.  Request Password Reset

* **Endpoint:** `POST http://127.0.0.1:8000/auth/request-password-reset`

####  Request Body

```json
{
  "email": "user@gmail.com"
}
```

####  Response

```json
{
  "message": "Password reset code generated successfully",
  "code": "string"
}
```

>  **Note:**
>
> * The reset code will be sent to the user's email.
> * Code expires in **15 minutes**.

---

### 5.  Reset Password

* **Endpoint:** `POST http://127.0.0.1:8000/auth/reset-password`

####  Request Body

```json
{
  "email": "user@gmail.com",
  "new_password": "string",
  "code": "string"
}
```

####  Response

```json
{
  "message": "Password reset successfully"
}
```

---   

### 6. Refresh Token    

---   

### 7. Upload or Update Profile Picture

* **Endpoint:** `POST /auth/upload-profile-picture`
* **Authorization:** Bearer Token

#### Request Body (form-data):

| Key  | Type |  Description             |
|------|------|--------------------------|
| file | File | Your profile image file (jpg/png/jpeg) |

#### Response:

```json
{
  "message": "Profile picture uploaded successfully",
  "image_path": "/uploads/profile_pics/xxxxxxxx.png"
}
```


--------------------------------------------  

## Freindship-related endpoints

###  **Precondition**: JWT Token Authentication

In **Postman**, under the `Authorization` tab:

* Type: `Bearer Token`
* Token: paste your JWT (from login endpoint)

---

##  1. **Send Friend Request**

* **Endpoint**:
  `POST http://localhost:8000/friends/request/{receiver_id}`
  Replace `{receiver_id}` with the target user’s ID (e.g. `2`)

* **Body**: None (Just authenticated user is the sender)

---

##  2. **Accept Friend Request**

* **Endpoint**:
  `POST http://localhost:8000/friends/accept/{sender_id}`
  Replace `{sender_id}` with the user who sent you the request.

* **Body**: None

* Authenticated user is the receiver.

---

##  3. **Reject Friend Request**

* **Endpoint**:
  `POST http://localhost:8000/friends/reject/{sender_id}`
  Replace `{sender_id}` with the user who sent you the request.

* **Body**: None

* Authenticated user is the receiver.

---

##  4. **Get Pending Friend Requests**

* **Endpoint**:
  `GET http://localhost:8000/friends/get-friend-requests`

* **Body**: None

* Response: List of pending friend requests sent to the authenticated user.

---

##  5. **Get Rejected Friend Requests**

* **Endpoint**:
  `GET http://localhost:8000/friends/get-rejected-requests`

* **Body**: None

* Response: List of rejected friend requests for authenticated user.

---

##  6. **Get Friend List**

* **Endpoint**:
  `GET http://localhost:8000/friends/get-friend-list`

* **Body**: None

* Response: List of friends for the authenticated user


---

##  Leaderboard Endpoints

### 1.  Get `All users` leaderboard

* **Endpoint:** `GET http://localhost:8000/leaderboard/all`

####  Request Body : None
####  Response: a list of top users based on number of hours in Activity Tracker

---

### 2.  Get `My friends` leaderboard

* **Endpoint:** `GET http://localhost:8000/leaderboard/friends?page=1&page_size=10`


####  Request Body : None
####  Response: a list of top users based on number of hours in Activity Tracker

>  **Note:**
>
> * *page={TO BE SENT FROM UI BASED ON THE PAGE THE USER IS IN}&page_size={TO BE SENT FROM UI BASED ON THE PAGE THE USER IS IN}*


---

##  Chat Endpoints

###  Message Status Lifecycle

| Status     | Meaning                                      |
|------------|----------------------------------------------|
| `sent`     | Message created by sender                   |
| `delivered`| Recipient was online and received the message |
| `read`     | Recipient viewed the message in the chat UI  |



### 1. **WebSocket: Real-time Messaging**

* **Endpoint:** `ws://localhost:8000/ws/chat?token=YOUR_JWT_TOKEN`

* **Type:** WebSocket

####  Description:

Establishes a WebSocket connection for real-time chatting between users

####  Send Message Format (JSON):

```json
{
  "receiver_id": 2,
  "message": "Hello!"
}
```

####  Message Received:

Messages are received in this format:

```
SenderName: Hello!
```

> **Note:**
>
> * You must pass a **valid JWT token** in the `token` query parameter

---

### 2. **Get Chat History with a Specific User**

* **Endpoint:** `GET http://localhost:8000/chat/history?receiver_id={receiver_id}`

* **Query Param:**

  * `receiver_id`: The ID of the user you chatted with

* **Headers:**

  * `Authorization: Bearer YOUR_JWT_TOKEN`

####  Response:

```json
[
  {
    "id": 1,
    "sender_id": 8,
    "receiver_id": 2,
    "message": "Hello!",
    "timestamp": "2025-06-10T14:00:00",
    "status": "delivered"  // "sent", "delivered", or "read"
  }
]
```

> Returns ***all messages*** exchanged between the authenticated user and the given `receiver_id`

---

### 3. **Get My Chat Contacts**

* **Endpoint:** `GET http://localhost:8000/chat/my-contacts`

* **Headers:**

  * `Authorization: Bearer YOUR_JWT_TOKEN`

####  Response:

```json
[
  {
    "id": 2,
    "first_name": "fname",
    "last_name": "lname",
    "email": "user@gmail.com"
  },
]
```

> Returns a list of users that the user has ever chatted with (sent or received a message)

---

### 4. **Mark Messages as Read**
**Endpoint:** POST /chat/mark-as-read/{sender_id}
Marks messages from the given sender as read for the user

**Headers:**

Authorization: Bearer YOUR_JWT_TOKEN

**Path Param:**
sender_id — ID of the user who sent you the messages

**Body: None**

Response:
```json
{
  "message": "Messages marked as read"
}
```
> ***This should be called from the frontend when the user opens the chat***

----


## User Rating Endpoints

### 1. **Rate a User**

* **Endpoint:**
  `POST http://127.0.0.1:8000/users/rate-user/{user_id}`
  *(Replace `{user_id}` with the ID of the user you want to rate)*

* **Authorization Required:** Bearer Token

#### Headers:

```http
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

#### Request Body:

```json
{
  "rating": 2.5
}
```

> 🟡 Allowed range is from **1** to **5**, floats are accepted (4.5)

#### Response:

```json
{
  "message": "Rating submitted successfully."
}
```

---

### 2. **Get Average Rating for a User**

* **Endpoint:**
  `GET http://127.0.0.1:8000/users/rating/{user_id}`
  *(Replace `{user_id}` with the rated user’s ID)*

* **Authorization Required:** None

#### Response:

```json
{
  "user_id": 2,
  "average_rating": 3.6,
  "count": 5
}
```

> ℹ️ `count` is the number of users who rated this user


----


## Block User (from another user) Endpoints

### 1. **Rate a User**

* **Endpoint:**
  `POST http://127.0.0.1:8000/users/block-user/{user_id_to_block}`
  *(Replace `{user_id}` with the ID of the user you want to block)*

* **Authorization Required:** Bearer Token

#### Headers:

```http
Authorization: Bearer YOUR_JWT_TOKEN
```

#### Request Body: none

> 🟡 Allowed range is from **1** to **5**, floats are accepted (4.5)

#### Response:

```json
{
    "message": "You blocked user {user_id_to_block} successfully"
}
```

---

### 2. **Get Blocked users for a user**

* **Endpoint:**
  `GET http://127.0.0.1:8000/users/blocked-users`

* **Authorization Required:** None

#### Response:

```json
{
    "blocked_user_ids": [
        id1,
    ]
}
```
## Matchmaking endpoint
**Endpoint:** `http://localhost:8000/matchmaking/get-matched-users?n_recommendations=5`
**Headers:**

Authorization: Bearer YOUR_JWT_TOKEN
####  Response Example
```json
[
    {
        "user_id": 2,
        "username": "m a",
        "interests": ["Reading","Traveling"],
        "rating": null,
        "age": 21,
        "gender": "female",
        "similarity_score": 1.0
    },
    {
        "user_id": 8,
        "username": "m a",
        "interests": [
            "Travel"
        ],
        "rating": null,
        "age": 21,
        "gender": "female",
        "similarity_score": 0.5773502691896258
    },
    {
        "user_id": 6,
        "username": "a b",
        "interests": [
            "Cars and automobiles",
            "Politics",
            "Travel"
        ],
        "rating": null,
        "age": 47,
        "gender": "female",
        "similarity_score": 0.0
    }
]
```


##  Report a user Endpoint
**Endpoint:** `http://127.0.0.1:8000/reports/`
**Headers:**

Authorization: Bearer YOUR_JWT_TOKEN
####  Request Body Example
```json
{
  "reported_user_id": 3,
  "priority": "CRITICAL",
  "reason": "anything"
}
```
