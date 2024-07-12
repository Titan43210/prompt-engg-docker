import os
import logging
from logging.handlers import RotatingFileHandler

if not os.path.exists("./logs"):
    os.makedirs("./logs")

rfh = RotatingFileHandler(
    filename="./logs/interview_bot.log",
    mode="a",
    maxBytes=10 * 1024 * 1024,
    backupCount=10,
    encoding=None,
    delay=False,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s :: %(levelname)s :: %(process)d :: %(threadName)s :: %("
    "pathname)s :: %("
    "funcName)s :: %(lineno)d :: %(message)s",
    handlers=[rfh],
)

openailogs = [
    logging.getLogger(name)
    for name in logging.root.manager.loggerDict
    if name.startswith("dotenv")
]
for openailog in openailogs:
    openailog.setLevel(logging.WARNING)

# Creating an logger object
logger = logging.getLogger()
