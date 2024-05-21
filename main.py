import os
import requests

from fastapi import FastAPI, HTTPException, Form
from dotenv import load_dotenv
from models import Course, Discussion, Entry, Assignment
from typing import Optional

# /courses

load_dotenv()

app = FastAPI()

access_token = os.getenv("ACCESS_TOKEN")

base_url = "https://dixietech.instructure.com/api/v1"

headers: dict[str, str] = {
    "Authorization": f"Bearer {access_token}"
}

@app.get("/courses")
async def get_courses() -> list[Course]:
    response = requests.get(url=f"{base_url}/courses", headers=headers)
    r_json = response.json()

    courses: list[Course] = []
    for course_json in r_json:
        course = Course(id=course_json["id"], name=course_json["name"])
        courses.append(course)
    
    return courses

@app.get("/discussions")
async def get_discussions(course_id: int) -> list[Discussion]:
    response = requests.get(url=f"{base_url}/courses/{course_id}/discussion_topics", headers=headers)
    r_json = response.json()
    
    discussions: list[Discussion] = []
    for discussion_json in r_json:
        discussion = Discussion(id=discussion_json["id"], title=discussion_json["title"])
        discussions.append(discussion)
    
    return discussions

@app.post("/discussions/entries")
async def create_discussion_entry(course_id: int, topic_id: int, body: Entry):
    response = requests.post(url=f"{base_url}/courses/{course_id}/discussion_topics/{topic_id}/entries", headers=headers, data=body.model_dump())
    r_json = response.json()
    return 

@app.get("/courses/assignments")
async def get_assignments(course_id: int) -> list[Assignment]:
    
    try:
        response = requests.get(url=f"{base_url}/courses/{course_id}/assignments", headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"External API request failed: {e}")

    r_json = response.json()
    
    assignments: list[Assignment] = []
    for assignment_json in r_json:
        try:
            assignment = Assignment(
                id=assignment_json["id"],
                name=assignment_json["name"],
            )
            assignments.append(assignment)
        except KeyError as e:
            raise HTTPException(status_code=500, detail=f"Missing key in assignment data: {e}")
    
    return assignments

@app.post("/courses/assignments/submit")
async def submit_assignment(course_id: int,
    assignment_id: int,
    submission_type: str = Form(...),
    url: Optional[str] = Form(None)):
    
    response = requests.post(url=f"{base_url}/courses/{course_id}/assignments/{assignment_id}/submit", headers=headers)
    r_json = response.json()
    submission_data = {'submission_data': submission_type,
                       'url': url}
    
    if submission_type != 'online_url':
        raise HTTPException(status_code=400, detail='online_url required')
        
    try:
        response = requests.post(
            url=f"{base_url}/courses/{course_id}/assignments/{assignment_id}/submit",
            data=submission_data,
            headers=headers
        )
        response.raise_for_status() 
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"External API request failed: {e}")
    
    if response.content:
        
        try:
            r_json = response.json()
        except ValueError:
            raise HTTPException(status_code=500, detail="Invalid JSON response from external API")
    
    else:
        raise HTTPException(status_code=500, detail="Empty response from external API")
    
    if r_json.get("status") == "success":
        return {"message": "Assignment successfully submitted!"}
    
    else:
        raise HTTPException(status_code=400, detail="Failed to submit assignment")
        
    
    
    
        
    


    