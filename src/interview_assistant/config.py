from src.common.pydantic_models import Env

env = Env()
openai_key = env.openai_key

appreciation_messages = [
    "Great job! Your response demonstrates a good understanding of the topic.",
    "Well done! It's clear that you're knowledgeable about the subject.",
    "Excellent! Your response shows a strong grasp of the topic.",
    "Fantastic! Thank you for your insightful response.",
    "Wonderful! It's evident that you've put thought into your answer.",
    "Amazing! Your response reflects a deep understanding of the topic."
]

welcome_message = ("Welcome to the HR interview chat! 🌟 I'm here to guide you through our interview process and learn "
                   "more about you. Let's get started by discussing your experience and skills...")

exit_message = ("Thank you for sharing your insights and experiences with us today! 🌟 We appreciate the "
                "opportunity to learn more about you and your potential fit for our team. If you have any "
                "additional questions or need further information, please don't hesitate to reach out. "
                "We'll be in touch regarding next steps in the hiring process. Best of luck, and we look "
                "forward to potentially welcoming you to our team in the future! 😊")

ques_set_expiry_time = 86400  # in seconds
