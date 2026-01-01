import uvicorn
from fastapi import FastAPI

from src.app.admin.routes import router as admin_router

app = FastAPI(swagger_ui_parameters={"operationsSorter": "method"})

app.include_router(router=admin_router, prefix="/admin")

if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000)
