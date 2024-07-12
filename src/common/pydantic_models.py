from pydantic import BaseModel, Field, BaseSettings
from fastapi import UploadFile

class BaseError(BaseModel):
    status_code: int = Field(default=400, description="")
    has_error: bool = Field(default=True)
    error: str = Field()

class BaseResponse(BaseModel):
    status_code: int = Field(default=200, description="")
    has_error: bool = Field(default=False, )
    error: str = Field(default='')

class HealthStatusResponse(BaseResponse):
    message: str = Field(default='')

class Env(BaseSettings):
    openai_key: str
    origins: list
    redis_host: str
    redis_port: int

    class Config:
        env_file = ".env"

class ExtractQuesAnsRequest(BaseModel):
    file: UploadFile
    query: str = Field()

class ExtractQuesAnsResponse(BaseResponse):
    message: str = Field()
    answer: dict = Field()
    validation: dict = Field()
