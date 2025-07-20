
# **Fluently – Your Language Practice companion**  
### *Real-time conversations with peer matching & pronunciation feedback*  

---

## **🌍 Overview**  
Fluently helps language learners practice speaking through **live conversations** with peers and AI. Unlike traditional apps that focus on vocabulary drills, Fluently bridges the gap between learning and real-world usage by:  
- **Matching learners** based on proficiency, interests, and goals  
- **Providing AI-powered feedback** on pronunciation and fluency  
- **Detecting hate speech** in real-time to ensure a safe community  

---

## **🚀 Quick Start**  

### **1. Prerequisites**  
- [FFmpeg](https://ffmpeg.org/download.html) (Windows users: [see installation notes](#ffmpeg-installation))
- Python 3.12+
- PostgreSQL 14+

### **2. Setup**  
```bash
git clone https://github.com/Fluently-Grad-Project/Backend
cd Application
python -m venv venv
.\venv\Scripts\activate   #windows

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

then:    
```bash
cd Word_of_the_day
python -m venv venv
.\venv\Scripts\activate   #windows

pip install -r requirements.txt
alembic upgrade head
python -m app.main

```

then:    
```bash
cd "Hate Detection Service"
python -m venv venv
.\venv\Scripts\activate   #windows

pip install -r requirements.txt
alembic upgrade head
python -m app.main

```

**API Docs**: http://localhost:8000/docs  

<details id="ffmpeg-installation">
<summary><h3>FFmpeg Installation (Windows)</h3></summary>

1. Download `ffmpeg-master-latest-win64-gpl.zip` from [FFmpeg](https://ffmpeg.org/download.html)  
2. Extract and place `ffmpeg.exe` in:  
   ```bash
   C:\Users\<user>\AppData\Local\Programs\Python\Python312\Scripts
   ```
</details>

---

## **📡 API Endpoints**

## Authentication Endpoints

<details>
<summary><strong> 1. Register New User </strong></summary>

* **Endpoint:** `POST /users/register`  
* **URL:** [http://127.0.0.1:8000/users/register](http://127.0.0.1:8000/users/register)

#### Request Body
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
````

#### Response

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
  "access_token": "...",
  "verification_link": "http://localhost:8000/auth/verify-email?email=...&code=..."
}
```

> **Note:**
>
> * A verification email will be sent to the user.
> * Users **cannot log in** until their email is verified.

</details>

<details>
<summary><strong> 2. Verify Email </strong></summary>

* **Endpoint:** `GET /auth/verify-email?email={email}&code={verification_code}`

#### Response

```json
{
  "message": "Email verified successfully."
}
```

</details>

<details>
<summary><strong> 3. Login </strong></summary>

* **Endpoint:** `POST /auth/login`

#### Request Body

```json
{
  "email": "user@gmail.com",
  "password": "string"
}
```

#### Response

```json
{
  "access_token": "string",
  "refresh_token": "string"
}
```

</details>

<details>
<summary><strong> 4. Request Password Reset</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/auth/request-password-reset`

#### Request Body

```json
{
  "email": "user@gmail.com"
}
```

#### Response

```json
{
  "message": "Password reset code generated successfully",
  "code": "string"
}
```

> **Note:**
>
> * The reset code will be sent to the user's email.
> * Code expires in **15 minutes**.

</details>

<details>
<summary><strong> 5. Reset Password</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/auth/reset-password`

#### Request Body

```json
{
  "email": "user@gmail.com",
  "new_password": "string",
  "code": "string"
}
```

#### Response

```json
{
  "message": "Password reset successfully"
}
```

</details>

<details>
<summary><strong> 6. Refresh Token</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/auth/refresh-token?refresh-token=the_refresh_token_stored_from_user_login`
* **Rate Limit:** 2 requests per minute

#### Request

```http
refresh_token=your_refresh_token_here
```

#### Response

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer"
}
```

</details>

<details>
<summary><strong> 7. Upload or Update Profile Picture</strong></summary>

* **Endpoint:** `POST /auth/upload-profile-picture`
* **Authorization:** Bearer Token

#### Request Body (form-data)

| Key  | Type | Description                            |
| ---- | ---- | -------------------------------------- |
| file | File | Your profile image file (jpg/png/jpeg) |

#### Response

```json
{
  "message": "Profile picture uploaded successfully",
  "image_path": "/uploads/profile_pics/xxxxxxxx.png"
}
```

</details>

<details>
<summary><strong> 8. Update Profile</strong></summary>

* **Endpoint:** `PATCH http://127.0.0.1:8000/users/update-profile`
* **Authorization:** Bearer Token

#### Request Body

```json
{
  "first_name": "s",
  "last_name": "a",
  "gender": "FEMALE",
  "interests": ["Science"],
  "proficiency_level": "INTERMEDIATE"
}
```

#### Response

```json
{
  "id": 2,
  "first_name": "s",
  "last_name": "a",
  "gender": "female",
  "interests": ["Science"],
  "proficiency_level": "Intermediate",
  "message": "Profile updated successfully"
}
```

</details>

<details>
<summary><strong> 9. Logout</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/users/logout`
* **Authorization:** Bearer Token

#### Response

```json
{
  "message": "Successfully logged out"
}
```

</details>

---

## Friendship-related Endpoints

<details>
<summary><strong> 1. Send Friend Request</strong></summary>

* **Endpoint:** `POST http://localhost:8000/friends/request/{receiver_id}`
* **Body:** None

</details>

<details>
<summary><strong> 2. Accept Friend Request</strong></summary>

* **Endpoint:** `POST http://localhost:8000/friends/accept/{sender_id}`
* **Body:** None

</details>

<details>
<summary><strong> 3. Reject Friend Request</strong></summary>

* **Endpoint:** `POST http://localhost:8000/friends/reject/{sender_id}`
* **Body:** None

</details>

<details>
<summary><strong> 4. Get Pending Friend Requests</strong></summary>

* **Endpoint:** `GET http://localhost:8000/friends/get-friend-requests`

</details>

<details>
<summary><strong> 5. Get Rejected Friend Requests</strong></summary>

* **Endpoint:** `GET http://localhost:8000/friends/get-rejected-requests`

</details>

<details>
<summary><strong> 6. Get Friend List</strong></summary>

* **Endpoint:** `GET http://localhost:8000/friends/get-friend-list`

</details>

---

## Leaderboard Endpoints

<details>
<summary><strong> 1. Get All Users Leaderboard</strong></summary>

* **Endpoint:** `GET http://localhost:8000/leaderboard/all`

</details>

<details>
<summary><strong> 2. Get Friends Leaderboard</strong></summary>

* **Endpoint:** `GET http://localhost:8000/leaderboard/friends?page=1&page_size=10`

</details>

---

## Chat Endpoints

<details>
<summary><strong> 1. WebSocket: Real-time Messaging</summary>

* **Endpoint:** `ws://localhost:8000/ws/chat?token=YOUR_JWT_TOKEN`

#### Send Message

```json
{
  "receiver_id": 2,
  "message": "Hello!"
}
```

</details>

<details>
<summary><strong> 2. Get Chat History with a Specific User</strong></summary>

* **Endpoint:** `GET http://localhost:8000/chat/history?receiver_id={receiver_id}`

#### Response

```json
[
  {
    "id": 1,
    "sender_id": 8,
    "receiver_id": 2,
    "message": "Hello!",
    "timestamp": "2025-06-10T14:00:00",
    "status": "delivered"
  }
]
```

</details>

<details>
<summary><strong> 3. Get My Chat Contacts</strong></summary>

* **Endpoint:** `GET http://localhost:8000/chat/my-contacts`

</details>

<details>
<summary><strong> 4. Mark Messages as Read</strong></summary>

* **Endpoint:** `POST /chat/mark-as-read/{sender_id}`

#### Response

```json
{
  "message": "Messages marked as read"
}
```

</details>

<details>
<summary><strong> 5. Send Call Request</strong></summary>

* **WebSocket Endpoint:** `/ws/send_call_request?token=YOUR_JWT_TOKEN`

#### Sent Events

```json
{
  "event": "call_user",
  "callee_id": 12
}
```

</details>

<details>
<summary><strong> 6. Start Voice Chat</strong></summary>

* **WebSocket Endpoint:** `/ws/start_voice_chat/{roomId}?token=YOUR_JWT_TOKEN`

</details>

<details>
<summary><strong> 7. Analyze Audio</strong></summary>

* **POST:** `http://localhost:8001/analyze-audio`
* **Header:** Bearer token
* **Body:** Audio file

#### Response

```json
{
  "transcript": "Transcribed text from audio",
  "label": "hate_speech"
}
```

</details>

---

## User Rating Endpoints

<details>
<summary><strong> 1. Rate a User</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/users/rate-user/{user_id}`

#### Request

```json
{
  "rating": 2.5
}
```

</details>

<details>
<summary><strong> 2. Get Average Rating for a User</strong></summary>

* **Endpoint:** `GET http://127.0.0.1:8000/users/rating/{user_id}`

#### Response

```json
{
  "user_id": 2,
  "average_rating": 3.6,
  "count": 5
}
```

</details>

---

## Block User Endpoints

<details>
<summary><strong> 1. Block a User</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/users/block-user/{user_id_to_block}`

#### Response

```json
{
  "message": "You blocked user {user_id_to_block} successfully"
}
```

</details>

<details>
<summary><strong> 2. Get Blocked Users</strong></summary>

* **Endpoint:** `GET http://127.0.0.1:8000/users/blocked-users`

#### Response

```json
{
  "blocked_user_ids": [id1]
}
```

</details>

---

## Matchmaking Endpoint

<details>
<summary><strong> Matchmaking</strong></summary>

* **Endpoint:** `GET http://localhost:8000/matchmaking/get-matched-users?n_recommendations=5`

#### Response

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
  }
]
```

</details>

---

## Report a User Endpoint

<details>
<summary><strong> Report a User</strong></summary>

* **Endpoint:** `POST http://127.0.0.1:8000/reports/`

#### Request Body

```json
{
  "reported_user_id": 3,
  "priority": "CRITICAL",
  "reason": "anything"
}
```

</details>

---

## Update Practice Hours Endpoint

<details>
<summary><strong> Update Practice Hours</strong></summary>

* **Endpoint:** `PATCH http://localhost:8000/activity/update_hours`

#### Request Body

```json
{
  "hours_to_add": 1
}
```

#### Response

```json
{
  "streaks": 0,
  "user_id": 7,
  "id": 5,
  "number_of_hours": 1
}
```

</details>

---

## **🛠 Tech Stack**  
- **Backend**: Python (FastAPI)    
- **Database**: PostgreSQL  
- **Auth**: JWT  
- **Real-Time**: WebSocket, WebRTC  
- **AI**: Gemini API, Whisper, BERT  

---

## **🧭 System Diagrams**

- *User Application Service*      
   <img width="7509" height="3644" alt="class diagram v1-Application (2)" src="https://github.com/user-attachments/assets/a1913c47-c38a-4ca7-8c7d-e9cdffcb8741" />      
<br><br><br>      
- *Word of the day Service*
  <img width="1721" height="901" alt="class diagram v1-wordOfTheDay drawio" src="https://github.com/user-attachments/assets/c8dfa2e5-d9d7-492d-a364-9e3d4e45bc0b" />      

<br><br><br>      
-  *Hate detection Service*
  <img width="1035" height="515" alt="class diagram v1-HateDetection drawio" src="https://github.com/user-attachments/assets/76dda8e4-d8e5-4796-b683-9194102909fa" />
