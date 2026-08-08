from fastapi import FastAPI

app = FastAPI(title="ByteForger Interview Agent")


@app.get("/")
def root():
    return {
        "message": "ByteForger Interview Agent is running"
    }