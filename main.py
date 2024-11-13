from fastapi import FastAPI
from api.main import api_router
from langserve import add_routes
# from rag_conversation import chain as rag_chain

app = FastAPI()

app.include_router(api_router)
# add_routes(app, rag_chain, path='/rag_conversation')


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
    
# uvicorn main:app --reload --host 127.0.0.1 --port 8001