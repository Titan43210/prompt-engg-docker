import os
import shutil
import time
import json
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import redis
from fastapi.middleware.cors import CORSMiddleware
from src.common.pydantic_models import Env, HealthStatusResponse, ExtractQuesAnsRequest, ExtractQuesAnsResponse, BaseError
from src.common.logger import logger
from src.interview_assistant.question_answer_extractor import extract_ques_ans
# from src.interview_assistant.validation import validate_response

env = Env()



redis_obj = redis.Redis(host=env.redis_host, port=env.redis_port)

app = FastAPI()
headers = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Interview Assistant!"}

@app.get('/status')
async def health_check():
    return HealthStatusResponse(message="Running")

@app.get('/timeout_status')
async def timeout_check():
    print("timer started....")
    time.sleep(120)
    return HealthStatusResponse(message="ok")

@app.post('/extract-ques-ans', response_model=ExtractQuesAnsResponse)
async def upload_file(file: UploadFile, query: str = Form()):
    input_file_path = ''
    try:
        file_content = file.file.read()
        file_id = file.filename
        redis_obj.set(file_id, file_content)
        suffix = Path(file.filename.lower()).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(file_content)
            input_file_path = tmp.name
            response = extract_ques_ans(input_file_path, query)
            # validation_result = validate_response(query, response)

        return ExtractQuesAnsResponse(message="File uploaded and processed successfully", answer=response, validation="not yet implemented")
    except Exception as e:
        logger.error(f"General Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_file_path):
            os.remove(input_file_path)
            logger.info("Temporary file deleted...")


