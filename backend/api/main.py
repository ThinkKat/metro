from fastapi import FastAPI

from .routers import metroinfo, realtimes

app = FastAPI()

prefix = "/api/metro"

app.include_router(metroinfo.router, prefix = prefix)
app.include_router(realtimes.router, prefix = prefix)

@app.get("/api/metro")
async def metro():
    return {"description": "This is the API for metro data"}