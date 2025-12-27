import uvicorn
from fastapi import FastAPI


app = FastAPI(swagger_ui_parameters={"operationsSorter": "method"})


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000)