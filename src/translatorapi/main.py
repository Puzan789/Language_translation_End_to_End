from fastapi import FastAPI

app=FastAPI()



@app.get("/query")
async def querydata():
    return {"message": "query"}