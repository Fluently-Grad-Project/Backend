go to:  https://ffmpeg.org/download.html    
choose windows, and choose: Windows builds by BtbN    
install:    
```ffmpeg-master-latest-win64-gpl.zip```      
extract files and take the .exe and put it in:  
```bash
C:\Users\<user>\AppData\Local\Programs\Python\Python312\Scripts
```        


## Backend Sample
![alt text](image.png)

![alt text](image-1.png)

![alt text](image-2.png)

navigate to http://127.0.0.1:8000/docs  and u will find all the endpoints 
![alt text](image-3.png)

----

### For running any new translations for localization:    
> go to: 
```bash
/app/core
```   
> then run:
```bash
pybabel compile -d translations
```

###  To do:
>   - non Functional Requirements (security bas azon ma3mola ya3ny me7tagen nekhaby el secrets       masalan??, performance blalalalaa)
>   - Chatbot for user lvl and AI conversations with pronunciation analysis  yarab nekhlas ba2a
>   - users voice chat including The NLP for hate speech recognition
>   - 3ayzeen ne3adel el status code beta3 el exceptions
>   - Unit Tests
----

# Things to be considered After Security🥱
> Ensure That reported users cannot login to the System, don't appear in the matchmaking,     Friend's list, etc.....   
> Hal el report_score byerga3 zero after lifting suspension 🤔??  
---
# Update Rating column to have a default value 
```sql
ALTER TABLE user_manager ALTER COLUMN rating SET DEFAULT 0.0;

-- Update any existing NULL values
UPDATE user_manager SET rating = 0.0 WHERE rating IS NULL;
-- Update the activty tracker Table with this --
ALTER TABLE activity_tracker ADD COLUMN last_practiced_date TIMESTAMP WITH TIME ZONE;
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
  "password": "Asdqwe123*",
  "gender": "FEMALE",
  "birth_date": "2003-06-18",
  "languages": ["English", "Turkish"],
  "proficiency_level": "INTERMEDIATE",
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

* **Endpoint:** `POST http://127.0.0.1:8000/auth/refresh-token?refresh-token=the_refresh_token_stored_from_user_login`
* **Rate Limit:** 2 requests per minute

#### Request: 

```http
refresh_token=your_refresh_token_here
```

#### Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```   
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
---   

### 8. Update Profile

* **Endpoint:** `PATCH http://127.0.0.1:8000/users/update-profile`
* **Authorization:** Bearer Token

#### Request Body 
```json
{
  "first_name": "s",
  "last_name": "a",
  "gender": "FEMALE",
  "interests": [
    "Science"
  ],
  "proficiency_level": "INTERMEDIATE"
}
```
#### Response:

```json
{
    "id": 2,
    "first_name": "s",
    "last_name": "a",
    "gender": "female",
    "interests": [
        "Science"
    ],
    "proficiency_level": "Intermediate",
    "message": "Profile updated successfully"
}
```
---   

### 9. Logout

* **Endpoint:** `POST http://127.0.0.1:8000/users/logout`
* **Authorization:** Bearer Token

#### Response:

```json
{
    "message": "Successfully logged out"
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


---




### 5. **Send Call Request**

**Endpoint:** `WebSocket /ws/send_call_request?token=YOUR_JWT_TOKEN`
Used for initiating and handling signaling between users for a voice call (offer/answer style).

**Authentication:**
Token must be passed as a query parameter:

```
/ws/send_call_request?token=YOUR_JWT_TOKEN
```

**Headers:**
None (token is in URL)

**Sent Events (Client → Server):**

```json
{
  "event": "call_user",
  "callee_id": 12
}
```

Initiates a call to another user by ID.

```json
{
  "event": "call_response",
  "accepted": true,
  "room_id": "e4a1cb12-9f55-4ef6-8cf7-a6d8a1eec5b3"
}
```

Response to an incoming call with `accepted: true` or `false`.

**Received Events (Server → Client):**

```json
{
  "event": "incoming_call",
  "from_user": { "id": 10, "name": "Alice" },
  "room_id": "e4a1cb12-9f55-4ef6-8cf7-a6d8a1eec5b3"
}
```

Notifies the callee of an incoming call.

```json
{
  "event": "call_accepted",
  "room_id": "e4a1cb12-9f55-4ef6-8cf7-a6d8a1eec5b3"
}
```

The callee accepted — start voice chat.

```json
{
  "event": "call_rejected",
  "room_id": "e4a1cb12-9f55-4ef6-8cf7-a6d8a1eec5b3"
}
```

The callee rejected the call.

> ℹ️ This socket remains open to manage multiple call events per session.

---

### 6. **Start Voice Chat**

**Endpoint:** `WebSocket /ws/start_voice_chat/{roomId}?token=YOUR_JWT_TOKEN`
Starts a real-time audio streaming session for a 1-on-1 voice call.

**Authentication:**
Token must be passed as a query parameter:

```
/ws/start_voice_chat/{roomId}?token=YOUR_JWT_TOKEN
```

**Headers:**
None

**Body:**
Sends raw binary audio data (e.g., `Float32Array`) over WebSocket in real time.

**Special Control Message (to end call):**
The string `"END_CALL"` must be sent as binary to indicate call termination.

**Received Messages:**

* Binary audio data from the other user (as `ArrayBuffer`)
* Control message:

  ```text
  "END_CALL"
  ```

  Indicates the other user ended the call.

> ⚠️ If a user sends `"END_CALL"`, the backend notifies and disconnects both peers.
>
> ℹ️ Only users who are part of the `active_calls` session can access this WebSocket.

----



### 7. **Analyze Audio**

**Endpoint:** `POST http://localhost:8001/analyze-audio` 
Used for uploading an audio file to transcribe speech and detect hate speech content.

**Authentication:**
Token must be passed in the `Authorization` header as a Bearer token

```
Authorization: Bearer YOUR_JWT_TOKEN
```

**Headers:**

* `Content-Type: multipart/form-data` (for file upload)
* `Authorization: Bearer YOUR_JWT_TOKEN`

**Request Body (multipart/form-data):**

| Field | Type | Description           |
| ----- | ---- | --------------------- |
| file  | File | Audio file to analyze |

**Response (application/json):**

```json
{
  "transcript": "Transcribed text from audio",
  "label": "hate_speech" | "normal" | "offensive" | ...
}
```

* `transcript`: Text transcribed from the audio.
* `label`: Classification result indicating hate speech or other categories.

**Behavior:**

* Converts uploaded audio to 16kHz mono WAV internally before processing.
* If `label` is `"hate_speech"`, a notification is sent internally to `/notify-hate-speech` with the transcript and label, including the Authorization header if provided.
* Temporary files are cleaned up automatically.

**Error Responses:**

* `400 Bad Request` if audio conversion fails or invalid file is provided.
* Other HTTP errors may occur if internal notification fails.

---


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
**Endpoint:** `GET http://localhost:8000/matchmaking/get-matched-users?n_recommendations=5`
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
**Endpoint:** `POST http://127.0.0.1:8000/reports/`
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
##  Update Practice Hours Endpoint
**Endpoint:** `PATCH http://localhost:8000/activity/update_hours` 
**Headers:**

Authorization: Bearer YOUR_JWT_TOKEN
####  Request Body Example
```json
{
  "hours_to_add": 1
}
```
```json
####  Response
{
    "streaks": 0,
    "user_id": 7,
    "id": 5,
    "number_of_hours": 1
}
```