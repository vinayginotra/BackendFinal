from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import requests
import logging
import os

# FastAPI app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Contact Form Model
class ContactForm(BaseModel):
    name: str
    email: EmailStr
    company: str = ""
    message: str

class ContactResponse(BaseModel):
    status: str
    message: str

# Contact Form Route (Google Sheets)
@api_router.post("/contact", response_model=ContactResponse)
async def contact_form(form_data: ContactForm):
    try:
        google_sheets_url = "https://script.google.com/macros/s/AKfycbyT65djHFUaZiVA1Jj86BwIuVYrWdttp96KxRlcyb_JMCJN4OL1wP3eCGfL6Lqz7VS6IA/exec"
        
        payload = {
            "name": form_data.name,
            "email": form_data.email,
            "company": form_data.company,
            "message": form_data.message
        }

        response = requests.post(
            google_sheets_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )

        if response.status_code == 200:
            return ContactResponse(
                status="success",
                message="Thank you! I'll get back to you soon."
            )
        else:
            raise HTTPException(status_code=500, detail="Sheets API error")

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=500, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Root route
@api_router.get("/", response_class=HTMLResponse)
async def root():
    return "<h2>Backend running ✅</h2><p>Contact form is live.</p>"

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
