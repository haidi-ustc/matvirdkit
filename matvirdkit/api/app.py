from fastapi import FastAPI
from pydantic import BaseModel,Field
from auth_jwt import identify,ErrorResponseModel

class QueryParams(BaseModel):
    id: str = Field(...)
    api_key: str = Field(...)

app = FastAPI()

@app.get("/rest/v1/materials")
async def get_data_by_id(params:QueryParams):
    if identify(params.api_key):
        return ""
    return ErrorResponseModel("An error occurred.", 403, "invalid api key")