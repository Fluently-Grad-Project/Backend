# To-Be-DoneS-Later     >> after team-meating probably??

## 📌📌📌📌
> A verify_recaptcha() function was added to call Google's API
> The login route now requires a recaptcha_token in the request
> If CAPTCHA validation fails, the login is blocked and logged

----
> ### Password Strength:
> at least 8 characters, one lowercase, one uppercase, one digit
----


#  Backend Setup & API Documentation

## Infrastructure security things

for the secrets needed in the app, to avoid being hardcoded:
> docker run --cap-add=IPC_LOCK -e VAULT_DEV_ROOT_TOKEN_ID=myroot -e VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200 -p 8200:8200 hashicorp/vault:1.19

access through: ``` http://localhost:8200/ui/vault/dashboard ```

## Update the models using these:

```bash
alembic revision --autogenerate -m "... Add ...COLUMN... column to ...TABLE... ..."
```
then:

```bash
alembic upgrade head
```
## To update The proficiency_level field in matchmaking table run the following commands but make sure that the Database is up-to-data
```bash

alembic revision --autogenerate -m "Add proficiency_level to matchmaking"
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
