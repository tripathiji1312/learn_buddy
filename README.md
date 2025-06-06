# Learn Buddy


Your workflow is simple:
1.  Start the backend with one command.
2.  Send requests to the API endpoints listed below.
3.  Receive JSON data back and use it to build a beautiful, responsive user experience.

## ✅ Prerequisites

You only need two pieces of software installed on your machine:
1.  **Docker**
2.  **Docker Compose**

(You do **not** need Python, PostgreSQL, or any other libraries installed on your host machine. Docker handles everything!)

## 🚀 One-Step Quick Start

This is the only command you need to run the entire backend system. Open your terminal in the project's root directory and run:

```bash
docker-compose up --build -d
```

**What this command does:**
*   `--build`: Builds the Docker container for the backend, installing all dependencies (it will be slow the very first time, then fast).
*   `-d`: Runs the containers in "detached" mode so they run in the background.

### How to Verify It's Working

After running the command, wait about 30 seconds for the server to start up. Then, you can check that everything is running correctly in two ways:

1.  **Check the Containers:** Run `docker-compose ps`. You should see two services, `learnbuddy-backend-1` and `learnbuddy-db-1`, both with a `STATUS` of `running` or `Up`.
2.  **Check the API Docs:** Open your web browser and go to **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**. If you see the FastAPI documentation page, the server is live and ready for requests.

## 🔧 Essential Developer Commands

You will use these commands frequently during development.

*   **Start everything:**
    ```bash
    docker-compose up --build -d
    ```
*   **See live logs (for debugging):**
    ```bash
    docker-compose logs -f backend
    ```
*   **Stop everything:**
    ```bash
    docker-compose down
    ```
*   **Reset the database to a clean state:**
    ```bash
    docker-compose exec backend python scripts/seed_db.py
    ```

## 🔑 The Authentication Flow

Our API is secure. Users must sign up and log in to access the learning features. Here is the flow you will need to build in the UI:

1.  **User Signs Up:** The user provides a username, email, and password. You send this to the `POST /signup` endpoint.
2.  **User Logs In:** The user provides their username and password. You send this to the `POST /token` endpoint.
3.  **Receive the Token:** The backend will send you back an `access_token` (a long string of characters).
4.  **Store the Token:** You must store this token somewhere in the frontend (e.g., `localStorage`, a state management library like Redux/Zustand).
5.  **Authorize Future Requests:** For every subsequent API call to a protected endpoint (like `/next_question`), you **must** include the token in the request headers like this:
    *   **Header Name:** `Authorization`
    *   **Header Value:** `Bearer <the_access_token_you_stored>`
    *   *Example:* `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

If the token is missing or invalid, the API will correctly send back a `401 Unauthorized` error.

## 🧠 The API Endpoints

This is your main reference guide. All requests and responses are in JSON format.

### Authentication Endpoints

These endpoints are for user management and are **not** protected.

---
#### **1. Create a New User**
*   **Endpoint:** `POST /signup`
*   **Description:** Registers a new user in the system.
*   **Request Body:**
    ```json
    {
      "username": "new_user",
      "email": "user@example.com",
      "password": "a_strong_password"
    }
    ```
*   **Success Response (201 Created):**
    ```json
    {
      "id": 2,
      "username": "new_user",
      "email": "user@example.com"
    }
    ```
*   **Failure Response (400 Bad Request):**
    ```json
    {
      "detail": "Username or email already registered."
    }
    ```

---
#### **2. User Login**
*   **Endpoint:** `POST /token`
*   **Description:** Authenticates a user and returns their access token.
*   **Request Body:** This endpoint expects `x-www-form-urlencoded` data (a standard login form), not JSON.
*   **Success Response (200 OK):**
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuZXdfdXNlciIsImV4cCI6MTcxNzcwNzAwOX0.some_long_string",
      "token_type": "bearer"
    }
    ```
*   **Failure Response (401 Unauthorized):**
    ```json
    {
      "detail": "Incorrect username or password"
    }
    ```

### Learning Endpoints

These endpoints are **protected**. They require the `Authorization: Bearer <token>` header.

---
#### **3. Get Next Question**
*   **Endpoint:** `POST /next_question`
*   **Description:** Asks the AI for the next best question for the authenticated user.
*   **Request Body:**
    ```json
    {
      "lesson_id": 1
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "difficulty_level": 1,
      "question_id": 3,
      "question_text": "What is ten minus the number three?"
    }
    ```
*   **Failure Response (404 Not Found):** Happens if the AI wants to give a harder question but we have no content for it.
    ```json
    {
      "detail": "No questions found for this difficulty."
    }
    ```

---
#### **4. Submit an Answer**
*   **Endpoint:** `POST /submit_answer`
*   **Description:** Submits a user's answer. The AI uses this to learn and update the user's XP.
*   **Request Body:**
    ```json
    {
      "lesson_id": 1,
      "question_id": 3,
      "difficulty_answered": 1,
      "user_answer": "I'm pretty sure it's 7"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
      "status": "Answer processed",
      "is_correct": true,
      "similarity_score": 0.95
    }
    ```

## 💡 Troubleshooting Guide

*   **Error: `permission denied` when running `docker-compose`**
    *   **Problem:** Your user account doesn't have permission to use Docker.
    *   **Fix (Linux):** Run `sudo usermod -aG docker ${USER}` once, then log out and log back in.

*   **Error: `Port is already allocated`**
    *   **Problem:** Another program is using port 8000 on your machine.
    *   **Fix:** Stop the other program, or open `docker-compose.yml` and change the `ports` mapping from `"8000:8000"` to `"8001:8000"`. You would then access the API at `http://127.0.0.1:8001`.

*   **Response: `{"detail": "Not authenticated"}`**
    *   **Problem:** You tried to access a protected endpoint without a valid token.
    *   **Fix:** Make sure you are attaching the `Authorization: Bearer <token>` header correctly to your request.

*   **Response: `422 Unprocessable Entity`**
    *   **Problem:** The JSON you sent in your request body is invalid.
    *   **Fix:** Check your JSON for mistakes like missing double quotes on keys or trailing commas.

---

Happy coding! Let me know if you have any questions.