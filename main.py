import uvicorn
from fastapi import FastAPI

from src.app.api.v1 import router as api_router

app = FastAPI(swagger_ui_parameters={"operationsSorter": "method"})

app.include_router(router=api_router, prefix="/api/v1")


@app.get(path="/health", summary="Health check")
async def health_check() -> dict[str, str]:
    """
    Return service health status.

    :return: health status payload
    """
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000)
