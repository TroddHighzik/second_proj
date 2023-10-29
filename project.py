from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from typing import Dict
import csv
import os
from typing import Optional, List

app = FastAPI()

# Global variable to keep track of the current logged-in user
current_user: Optional[str] = None


# CSV CHECK AND CREATION
if not os.path.exists('users.csv'):
    with open('users.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Id', 'Email', 'Name'])

if not os.path.exists('articles.csv'):
    with open('articles.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Id', 'Title', 'Body', 'UserId', 'CreatedAt'])


# USER LOGIN CHECK
def get_current_user(email: Optional[str] = None):
    if email and email == current_user:
        return email
    raise HTTPException(status_code=403, detail="You are authenticated")


#USER REGISTRATION
@app.post("/register/")
def register(email: str, name: str) -> Dict[str, str]:
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == email:
                raise HTTPException(status_code=400, detail="User with this email already exists.")
    
    user_id = str(len(list(csv.reader(open('users.csv')))) + 1)
    with open('users.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user_id, email, name])
    
    return {"message": "User registered successfully!"}


#USER LOGIN
@app.post("/login/")
def login(email: str) -> Dict[str, str]:
    global current_user
    with open('users.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == email:
                current_user = email
                return {"message": f"Logged in as {email}"}
    
    raise HTTPException(status_code=400, detail="This user ID does not exist!.")


#USER LOGOUT
@app.post("/logout/")
def logout() -> Dict[str, str]:
    global current_user
    current_user = None
    return {"message": "Successfully Logged-out."}


#CREATE ARTICLE
@app.post("/create_article/")
def create_article(title: str, body: str, user: str = Depends(get_current_user)) -> Dict[str, str]:
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    article_id = str(len(list(csv.reader(open('articles.csv')))) + 1)
    with open('articles.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([article_id, title, body, user, created_at])
    
    return {"message": "Article successfully Created!"}


#FETCH ARTICLE BY ID:
@app.get("/article/{article_id}/")
def get_article(article_id: int) -> Dict[str, str]:
    with open('articles.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if len(row) < 5:  # Assuming you expect 5 columns per row
                continue
            if int(row[0]) == article_id:
                return {"id": row[0], "user": row[1], "title": row[2], "body": row[3], "timestamp": row[4]}
    raise HTTPException(status_code=404, detail="Article does not exist.")


#EDIT ARTICLE
@app.put("/article/{article_id}/edit/")
def edit_article(article_id: int, title: str, body: str, user: str = Depends(get_current_user)) -> Dict[str, str]:
    articles = []
    edited = False
    
    with open('articles.csv', 'r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if int(row[0]) == article_id:
                if row[3].strip() != user.strip():
                    raise HTTPException(status_code=403, detail="You can only edit your own articles.")
                articles.append([row[0], row[1], title, body, row[4]])  # Update title and body
                edited = True
            else:
                articles.append(row)
    
    if not edited:
        raise HTTPException(status_code=404, detail="Article not found.")
    

    # SAVING UPDATED ARTICLE BACK TO ARTICLE.CSV
    with open('articles.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(articles)

    return {"message": "Article updated successfully!"}