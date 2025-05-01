from fastapi import FastAPI
import uvicorn

from api.routers import metroinfo, realtimes

app = FastAPI()

prefix = "/api/metro"

app.include_router(metroinfo.router, prefix = prefix)
app.include_router(realtimes.router, prefix = prefix)

@app.get("/api/metro")
async def metro():
    return {"description": "This is the API for metro data"}

if __name__ == "__main__":
    pass