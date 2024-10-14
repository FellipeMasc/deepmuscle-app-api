import sys
sys.path.append('C:/Users/felip/OneDrive/Área de Trabalho/ITA/CSI28/PROJECT/deepmuscle-app-api')
from fastapi import FastAPI
from api.main import api_router


app = FastAPI()

app.include_router(api_router)

