from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class EmailRequest(BaseModel):
    to: str
    code: str


@app.post("/api/send_email")
def send_email(request: EmailRequest):
    print(f"Sending email to {request.to} with code {request.code}")
    return {"message": "Email sent"}
