from fastapi import FastAPI

# Create an instance of the FastAPI application
app = FastAPI()

# Define a "root" endpoint for basic testing
@app.get("/")
def read_root():
    return {"Hello": "from LearnBuddy Backend!"}

# This is the endpoint for user registration.
# It directly matches the API spec you created on Day 1.
@app.post("/users/register")
def register_user():
    # For now, we are not doing anything.
    # We are just returning a fake message.
    # In Phase 2, you will add the real logic here.
    return {"message": "User registration endpoint is working!"}