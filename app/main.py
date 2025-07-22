from fastapi import FastAPI
from app.core.middleware import LoggingMiddleware, RequestIDMiddleware

app = FastAPI()

app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)


@app.get("/")
def read_root():
    return {"Hello": "World"}
