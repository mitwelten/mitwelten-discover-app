import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from dashboard.app import app as dash_app

app = FastAPI()


@app.get("/index")
def index():
    return "Hello World"


app.mount("/", WSGIMiddleware(dash_app.server))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
