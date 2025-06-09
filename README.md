#  Backend Setup & API Documentation

## Update the models using these:

```bash
alembic revision --autogenerate -m "... Add ...COLUMN... column to ...TABLE... ..."
```
then:

```bash
alembic upgrade head
```


##  How to Run the Backend

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
  "email": "user@example.com",
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