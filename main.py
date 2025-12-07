
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routers import auth, user, resume, jobs, websocket, admin
from fastapi.openapi.utils import get_openapi

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HireSense API",
    version="1.0.0",
    description="AI-powered Resume Analyzer & Job Match Engine"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)


app.include_router(auth.router, prefix="/auth")
app.include_router(user.router, prefix="/users")
app.include_router(resume.router, prefix="/resumes")
app.include_router(jobs.router, prefix="/jobs")
app.include_router(websocket.router, prefix="/ws")
app.include_router(admin.router, prefix="/admin")

# redis 
@app.get("/")
async def read_root():
    return {"Hello": "Hire Sense"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="HireSense API",
        version="1.0.0",
        description="AI-powered Resume Analyzer & Job Match Engine",
        routes=app.routes,
    )

    # Add Bearer Token header
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **Bearer &lt;your_token&gt;**"
        }
    }

    # Apply BearerAuth globally to all endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["get", "post", "put", "delete", "patch"]:
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
