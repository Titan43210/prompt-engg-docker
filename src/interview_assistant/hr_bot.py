import random

import openai
import json

from src.interview_assistant.config import appreciation_messages, openai_key, welcome_message
from src.common.logger import logger
from src.interview_assistant.utils import replace_end_comma_newline

openai.api_key = openai_key


def get_topic_specific_message(topic, user_ans, predefined_ans, predefined_que):  # topic React-JS
    return [{"role": "system",
             "content": f"""Evaluate the user's answer based on the predefined answer for this question "{predefined_que}" as an "{topic}" expert. Provide ratings out of 5 for Clarity, Relevance and Completeness. Please explain all your ratings in normal text format.
                    
        Predefined Answer for "{predefined_que}": "{predefined_ans}"

        User's Explanation of "{predefined_que}": "{user_ans}"

        
        Ratings:
        - Clarity: [Provide a rating out of 5]
        - Clarity Explanation: [Explain the clarity of the user's explanation on {topic}, whether it's clear and understandable or needs improvement.]

        - Relevance: [Provide a rating out of 5]
        - Relevance Explanation: [Explain how relevant the information provided is to {topic} concepts.]

        - Completeness: [Provide a rating out of 5]
        - Completeness Explanation: [Discuss if the explanation covers all important aspects of {topic} comprehensively or if it lacks depth or examples.]

        Provide the ratings and explanations in valid JSON format."""}]


def evaluate_user_ans(topic, user_ans, predefined_ans, predefined_que):
    resp = {}
    logger.info("Entered into evaluate_user_ans module...")
    topic_specific_message = get_topic_specific_message(topic, user_ans, predefined_ans, predefined_que)
    logger.info(f"topic_specific_message: {topic_specific_message}")
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0613",

        messages=topic_specific_message,
        max_tokens=1000,
        temperature=0.1,
        n=1,
        stop=None
    )
    if response.choices:
        valid_json_content = replace_end_comma_newline(response.choices[0].message.content)
        resp = json.loads(valid_json_content)
    return resp


# def initialize_covered_items(topices_qa):
#     topices = list(topices_qa)
#     covered_items = {}
#     for topic in topices:
#         covered_items[topic] = {"is_cover": False, "evals": []}
#         qa = topices_qa[topic]
#         list_of_ques = list(qa)
#         for predefined_que, _ in qa.items():
#             covered_items[topic]["evals"].append(
#                 {"ques": predefined_que, "Clarity": 0, "Relevance": 0, "Completeness": 0,
#                  "need_to_ask": True, "is_ask": False, "is_pass": False})
#     return covered_items


def update_session_obj_ques_items(covered_items, topic, predefined_que, eval_res, need_to_ask, is_ask, is_pass):
    for i, eval in enumerate(covered_items[topic]['evals']):
        if predefined_que == eval['ques']:
            eval['Clarity'] = eval_res['Clarity']
            eval['Relevance'] = eval_res['Relevance']
            eval['Completeness'] = eval_res['Completeness']
            eval["need_to_ask"] = need_to_ask
            eval["is_ask"] = is_ask
            eval["is_pass"] = is_pass
            covered_items[topic]['evals'][i] = eval
    return covered_items


def update_cover_topic(covered_items, topic):
    if not covered_items[topic]['is_cover']:
        covered_items[topic]['is_cover'] = True
        for i, eval in enumerate(covered_items[topic]['evals']):
            if eval['need_to_ask']:
                covered_items[topic]['is_cover'] = False

    return covered_items


def get_other_predefined_ans_to_compare(topic, topices_qa, covered_items):
    ans_to_compare = {}
    qa = topices_qa[topic]
    for predefined_que, predefined_ans in qa.items():
        for i, eval in enumerate(covered_items[topic]['evals']):
            if predefined_que == eval['ques'] and eval["need_to_ask"]:
                ans_to_compare[predefined_que] = predefined_ans
    return ans_to_compare


def generate_response(prompt, temperature=0.1):
    # Generate response using OpenAI
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "user",
                   "content": prompt, }],
        max_tokens=1000,
        temperature=temperature,
        n=1,
        stop=None
    )
    return response.choices[0].message.content


def get_follow_up_message(user_response):
    follow_up_prompt = f"""
        Topics: 'skip', 'rephrase', 'self-confidence', 'greetings', 'uncertainty'.
        
        Candidate: {user_response},

        Interviewer: Analyze the candidate's response and  if the candidate's response is related to one of the specified topics, classify candidate's response accordingly to the specified topics. If the candidate's response is not related/relevant to any of the specified topics, then classify it as 'out-of-topics' as an action_item.
    
        Interviewer: Analyze the candidate's response and provide appropriate acknowledgement as an interviewer. Ensure that interviewer's response does not include any additional questions or information and should maintain flow of the interview. 

        Please return the response in json format.
        
        Desired format:
        interviewer_acknowledgement: <appropriate acknowledgement as an interviewer>
        action_item: <appropriate classification of topics>"""
    return json.loads(generate_response(follow_up_prompt))


def is_answer(user_response, question, predefined_ans):
    # Use a generative approach to determine if the response is an attempt to answer
    prompt = f"""Please classify the candidate's Answer against prepredefined answer for this question and 
        respond with 'Yes' if the candidate's Answer is related to the main topic of the Question. 
        'No' if it's not related to the main topic of the Question or a normal conversation.

        Predefined Answer for question "{question}": "{predefined_ans}"

        Candidate's Explanation of question "{question}": "{user_response}"
        """

    # print("prompt:", prompt)
    response = generate_response(prompt)
    if response.lower().strip() == 'no':
        # If the response is "No", ask the model to provide a proper message
        return get_follow_up_message(user_response)
    else:
        return "Yes"


# def should_move_to_next_question(response):
#     # Function to determine if the user wants to move to the next question
#     # Placeholder implementation using a generative model
#     prompt = f"User response: {response}\nPlease analyze the user's response and determine whether user 'wish to proceed to the next question/topic or skip the current question/topic' or wants to continue on conversation. Return 'Yes' with explanation if user want to move to the next question/topic and/or skip the current question/topic, and return 'No' with explanation if user wants normal conversation.\n Yes/No with explanation in json format where value of should_skip is Yes/No."
#     ai_response = generate_response(prompt)
#     return ai_response


def want_to_rephrase_question(response):
    # Function to determine if the user wants to move to the next question
    # Placeholder implementation using a generative model
    prompt = f"User response: {response}\nAnalyze the user's response and determine if user are requesting for the question to be rephrased. Return 'Yes' if it seems the user is requesting a rephrased question, otherwise return 'No'."

    ai_response = generate_response(prompt)
    return ai_response


def do_rephrase_question(question):
    prompt = f"Original question: {question}\nRewrite the question in a different way."
    rephrased_question = generate_response(prompt)
    return rephrased_question


def do_evaluation(topic, user_ans, predefined_ans, predefined_que, covered_items, no_of_ques_passed, topics_qa):
    response = evaluate_user_ans(topic, user_ans, predefined_ans, predefined_que)
    logger.info(f"Evaluation results: {response}")
    # print(response)
    # print("response:", response['Clarity'], response['Relevance'], response['Completeness'])
    if response['Clarity'] > 3 and response['Relevance'] > 3 and response['Completeness'] > 3:
        covered_items = update_session_obj_ques_items(covered_items, topic, predefined_que, response, False,
                                                      True, True)
        no_of_ques_passed += 1
    else:
        covered_items = update_session_obj_ques_items(covered_items, topic, predefined_que, response, False,
                                                      True, False)

    # for predefined_ans in ans_to_compare:
    ans_to_compare = get_other_predefined_ans_to_compare(topic, topics_qa, covered_items)

    for predefined_que_, predefined_ans_ in ans_to_compare.items():
        # print("ans_to_compare:", predefined_que)
        logger.info(f"Answer to compare: {predefined_que_}")
        response = evaluate_user_ans(topic, user_ans, predefined_ans_, predefined_que_)
        logger.info(f"Answer to compare evaluation results: {response}")
        # print("response:", response['Clarity'], response['Relevance'], response['Completeness'])
        if response['Clarity'] > 3 and response['Relevance'] > 3 and response['Completeness'] > 3:
            covered_items = update_session_obj_ques_items(covered_items, topic, predefined_que_, response,
                                                          False, True, True)
            no_of_ques_passed += 1
    return covered_items, no_of_ques_passed


# def agent_controller(covered_items):
#     bot_response_message = ""
#     print(
#         "Welcome to the HR interview chat! 🌟 I'm here to guide you through our interview process and learn more about you. Let's get started by discussing your experience and skills...")
#     for topic in topices:
#         if covered_items[topic]['is_cover']:
#             continue
#         print(f"\nLet's discuss on {topic}...\n")
#         qa = topices_qa[topic]
#         no_of_ques_asked = 0
#         no_of_ques_passed = 0
#         no_of_ques = len(list(qa))
#         for predefined_que, predefined_ans in qa.items():
#             for i, eval in enumerate(covered_items[topic]['evals']):
#                 if predefined_que == eval['ques'] and eval["need_to_ask"]:
#                     print(f"Question=>", predefined_que)
#                     bot_response_message = f"Question=> {predefined_que}"
#                     no_of_ques_asked += 1
#                     # print("Answer:", predefined_ans)
#
#                     user_ans = input("Candidate response: ")
#                     # print("Your answer:", user_ans)
#                     is_answer_res = is_answer(user_ans, predefined_que)
#                     # print("is_answer_res====>", is_answer_res)
#                     if is_answer_res == 'Yes':
#                         print("Interviewer response: ", random.choice(appreciation_messages))
#                         # print("\nWe are evaluating your answer...")
#                         covered_items, no_of_ques_passed = do_evaluation(
#                             topic, user_ans, predefined_ans, predefined_que, covered_items, no_of_ques_passed)
#
#                     else:
#                         # print(is_answer_res)
#                         if is_answer_res['action_item'] == 'out-of-topics':
#                             print(f"Interviewer response: Thanks for sharing. Let's stay focused on {topic} for now.")
#                             covered_items = update_cover_ques_items(covered_items, topic, predefined_que, response,
#                                                                     False,
#                                                                     True, False)
#                             continue
#                         else:
#                             print("Interviewer response: ", is_answer_res['interviewer_acknowledgement'])
#
#                         if is_answer_res['action_item'] == "rephrase" or want_to_rephrase_question(user_ans) == "Yes":
#                         # if want_to_rephrase_question(user_ans) == "Yes":
#                             rephrased_question = do_rephrase_question(predefined_que)
#                             return("Rephrased question:", rephrased_question)
#                             user_ans = input("Candidate response: ")
#                             # print("Your answer:", user_ans)
#                             is_answer_res = is_answer(user_ans, predefined_que)
#                             # print("is_answer_res====>", is_answer_res)
#                             if is_answer_res == 'Yes':
#                                 print("Interviewer response: ", random.choice(appreciation_messages))
#                                 covered_items, no_of_ques_passed = do_evaluation(
#                                     topic, user_ans, predefined_ans, predefined_que, covered_items, no_of_ques_passed)
#                             else:
#                                 return("Interviewer response: Lets move to the next question...")
#                         elif is_answer_res['action_item'] in ["skip", "uncertainty"]:
#                             continue
#                         else:
#
#                             while True:
#                                 user_response = input("Your response: ")
#                                 # print(user_response)
#                                 if user_response == "exit":
#                                     break
#                                 follow_up_response = get_follow_up_message(user_response)
#
#                                 if follow_up_response['action_item'] in ['skip', 'rephrase', 'uncertainty']:
#                                     return("Interviewer response: ", follow_up_response['interviewer_acknowledgement'])
#                                     break
#                                 elif is_answer_res['action_item'] == 'out-of-topics':
#                                     return(f"Interviewer response: Thanks for sharing. Let's stay focused on {topic} for now.")
#                                     break
#                                 else:
#                                     return("Interviewer response: ", follow_up_response['interviewer_acknowledgement'])
#
#             if no_of_ques_asked / no_of_ques >= 0.6 and no_of_ques_passed / no_of_ques_asked < 0.5:
#                 break
#         covered_items = update_cover_topic(covered_items, topic)
#     return("Interviewer response: Thank you for sharing your insights and experiences with us today! 🌟 We appreciate the opportunity to learn more about you and your potential fit for our team. If you have any additional questions or need further information, please don't hesitate to reach out. We'll be in touch regarding next steps in the hiring process. Best of luck, and we look forward to potentially welcoming you to our team in the future! 😊")


def initialize_session_object(topics_qa):
    topics = list(topics_qa)
    session_object = {'prompt_question': True, 'has_question_prompted': False, 'is_ques_eval_required': False,
                      'current_ques': "", 'is_show_yes_answer_message': False, 'is_show_out_of_topics_message': False,
                      'is_rephrase_asked': False, 'is_interview_over': False, 'show_welcome_message': True,
                      'no_of_ques_asked': -1, 'no_of_ques_passed': 0, 'no_of_ques': 0}
    for topic_no, topic in enumerate(topics):
        if topic_no == 0:
            session_object[topic] = {"is_cover": False, "evals": [], "is_current_topic": True,
                                     "is_show_now_in_response": True}
            session_object['current_topic'] = topic
            qa = topics_qa[topic]
            session_object['no_of_ques'] = len(list(qa))
        else:
            session_object[topic] = {"is_cover": False, "evals": [], "is_current_topic": False,
                                     "is_show_now_in_response": False}
        qa = topics_qa[topic]
        list_of_ques = list(qa)
        for predefined_que, _ in qa.items():
            session_object[topic]["evals"].append(
                {"ques": predefined_que, "Clarity": 0, "Relevance": 0, "Completeness": 0,
                 "need_to_ask": True, "is_ask": False, "is_pass": False})
    return session_object


def get_response_message(session_object, topics_qa):
    bot_response_message = []
    if session_object['show_welcome_message']:
        bot_response_message.append('START')
        bot_response_message.append(welcome_message)
        session_object['show_welcome_message'] = False

    current_topic = session_object['current_topic']
    if session_object[current_topic]['is_show_now_in_response']:
        bot_response_message.append(f"Let's discuss on {current_topic}...")
        session_object[current_topic]['is_show_now_in_response'] = False

    qa = topics_qa[current_topic]
    # no_of_ques_asked = 0
    # no_of_ques_passed = 0
    # no_of_ques = len(list(qa))
    if session_object['is_show_yes_answer_message']:
        bot_response_message.append(random.choice(appreciation_messages))
        session_object['is_show_yes_answer_message'] = False

    if session_object['is_show_out_of_topics_message']:
        bot_response_message.append(f"Thanks for sharing. Let's stay focused on {current_topic} for now.")
        session_object['is_show_out_of_topics_message'] = False

    # print("covered_items['is_rephrase_asked']=====>", session_object['is_rephrase_asked'])
    if session_object['is_rephrase_asked']:
        bot_response_message.append("Lets move to the next question...")

    # print("covered_items['prompt_question']:", covered_items['prompt_question'])
    prompt_question = False
    for predefined_que, predefined_ans in qa.items():
        for i, eval in enumerate(session_object[current_topic]['evals']):
            if predefined_que == eval['ques'] and eval["need_to_ask"] and session_object['prompt_question']:
                # print(f"Question=>", predefined_que)
                bot_response_message.append(f"Question=> {predefined_que}")
                session_object['current_ques'] = predefined_que
                session_object['current_ans'] = predefined_ans
                session_object[current_topic]['evals'][i]['need_to_ask'] = False
                session_object['is_ques_eval_required'] = True
                prompt_question = True
                session_object['no_of_ques_asked'] += 1
                # covered_items['prompt_question'] = False
                # covered_items['has_question_prompted'] = True
                break
        if prompt_question:
            break

    return bot_response_message, session_object


def bot_agent(session_object, topics, topics_qa, user_ans=''):
    topic = session_object['current_topic']
    # covered_items['prompt_question'] = True
    bot_response_message, session_object = get_response_message(session_object, topics_qa)

    # covered_items['has_question_prompted'] = True

    # print(session_object['current_ans'])
    predefined_ans = session_object['current_ans']
    predefined_que = session_object['current_ques']
    if session_object['has_question_prompted']:
        # user_ans = input("Candidate response: ")
        # print("Your answer:", user_ans)
        is_answer_res = is_answer(user_ans, predefined_que, predefined_ans)
        # print("is_answer_res:", is_answer_res)
        if is_answer_res == 'Yes':
            logger.info("Relevant answer found...")
            session_object['is_show_yes_answer_message'] = True
            session_object['has_question_prompted'] = False
            session_object['is_ques_eval_required'] = False
            session_object['prompt_question'] = True
            session_object['is_rephrase_asked'] = False
            logger.info("Started doing evaluation...")
            session_object, session_object['no_of_ques_passed'] = do_evaluation(
                topic, user_ans, predefined_ans, predefined_que, session_object, session_object['no_of_ques_passed'],
                topics_qa)
            bot_response_message, session_object = get_response_message(session_object, topics_qa)
            # session_object['is_ques_eval_required'] = False
            # print("session_object['prompt_question']:", session_object['prompt_question'])
            # print("bot_YES_response_message:", bot_response_message)
            logger.info("Evaluation done...")
        elif is_answer_res['action_item'] == 'out-of-topics':
            session_object['is_show_out_of_topics_message'] = True
            session_object['has_question_prompted'] = False
            session_object['prompt_question'] = True
            session_object['is_ques_eval_required'] = False
            bot_response_message, session_object = get_response_message(session_object, topics_qa)
            # print("bot_out-of-topics-response_message:", bot_response_message)
            eval_res = {}
            eval_res['Clarity'] = 0
            eval_res['Relevance'] = 0
            eval_res['Completeness'] = 0
            session_object = update_session_obj_ques_items(session_object, topic, predefined_que, eval_res,
                                                           False,
                                                           True, False)

            # print("---covered_items['prompt_question']:", covered_items['prompt_question'])
        elif is_answer_res['action_item'] in ["skip", "uncertainty"]:
            tmp_bot_response_message = is_answer_res['interviewer_acknowledgement']
            session_object['has_question_prompted'] = False
            session_object['prompt_question'] = True
            session_object['is_ques_eval_required'] = False
            session_object['is_rephrase_asked'] = False

            eval_res = {}
            eval_res['Clarity'] = 0
            eval_res['Relevance'] = 0
            eval_res['Completeness'] = 0
            session_object = update_session_obj_ques_items(session_object, topic, predefined_que, eval_res,
                                                           False,
                                                           True, False)
            bot_response_message, session_object = get_response_message(session_object, topics_qa)
            bot_response_message.insert(0, tmp_bot_response_message)

        elif is_answer_res['action_item'] == "rephrase" or want_to_rephrase_question(user_ans) == "Yes":
            # print("covered_items['is_rephrase_asked']:", covered_items['is_rephrase_asked'])
            if session_object['is_rephrase_asked']:
                session_object['has_question_prompted'] = False
                session_object['prompt_question'] = True
                session_object['is_ques_eval_required'] = False

                eval_res = {}
                eval_res['Clarity'] = 0
                eval_res['Relevance'] = 0
                eval_res['Completeness'] = 0
                session_object = update_session_obj_ques_items(session_object, topic, predefined_que, eval_res,
                                                               False,
                                                               True, False)
                bot_response_message, session_object = get_response_message(session_object, topics_qa)
                session_object['is_rephrase_asked'] = False

            else:
                bot_response_message.append(is_answer_res['interviewer_acknowledgement'])
                rephrased_question = do_rephrase_question(predefined_que)
                session_object['prompt_question'] = False
                session_object['is_rephrase_asked'] = True
                # print("covered_items['is_rephrase_asked']:::::", session_object['is_rephrase_asked'])
                bot_response_message.append("Rephrased question:" + rephrased_question)
        else:
            bot_response_message.append(get_follow_up_message(user_ans)['interviewer_acknowledgement'])

    if session_object['prompt_question'] and session_object['is_ques_eval_required']:
        # print("********************")
        session_object['prompt_question'] = False
        session_object['has_question_prompted'] = True

    current_topic = session_object['current_topic']

    # print("session_object['no_of_ques_passed']:", session_object['no_of_ques_passed'])
    # print("session_object['no_of_ques']:", session_object['no_of_ques'], session_object['is_ques_eval_required'])
    min_gap_between_ques_asked_passed = round(session_object['no_of_ques'] * 0.6)
    # print("min_gap_between_ques_asked_passed:", min_gap_between_ques_asked_passed)
    if ((session_object['no_of_ques_asked'] / session_object['no_of_ques'] >= 0.6 and
            session_object['no_of_ques_asked'] - session_object['no_of_ques_passed'] >=
         min_gap_between_ques_asked_passed) or
            (session_object['no_of_ques_passed'] / session_object['no_of_ques'] >= 0.6)):
        session_object[current_topic]['is_cover'] = True
        session_object['is_ques_eval_required'] = False
        # print("session_object[current_topic]['is_cover']::::", session_object[current_topic]['is_cover'])

    if not session_object['is_ques_eval_required']:
        update_cover_topic(session_object, current_topic)
        # print("session_object[current_topic]['is_cover']:", session_object[current_topic]['is_cover'])
        if session_object[current_topic]['is_cover']:
            for topic_no, topic_ in enumerate(topics):
                if not session_object[topic_]['is_cover']:
                    # current_topic = topic
                    session_object[current_topic]['is_current_topic'] = False
                    session_object[current_topic]['is_show_now_in_response'] = False

                    session_object[topic_]['is_current_topic'] = True
                    session_object[topic_]['is_show_now_in_response'] = True
                    session_object['current_topic'] = topic_

                    session_object['prompt_question'] = True
                    session_object['has_question_prompted'] = False
                    session_object['is_ques_eval_required'] = False
                    qa = topics_qa[topic]
                    session_object['no_of_ques'] = len(list(qa))
                    session_object['no_of_ques_asked'] = -1
                    session_object['no_of_ques_passed'] = 0
                    break
            bot_response_message, session_object = get_response_message(session_object, topics_qa)
            if session_object['prompt_question'] and session_object['is_ques_eval_required']:
                session_object['prompt_question'] = False
                session_object['has_question_prompted'] = True

    return bot_response_message, session_object


def is_interview_over(session_object, topics):
    is_interview_cover = True
    for topic_no, topic_ in enumerate(topics):
        if not session_object[topic_]['is_cover']:
            is_interview_cover = False
    return is_interview_cover

# topices_qa = {"React-JS": qa_React, "Node-JS": qa_nodejs}
# topices = list(topices_qa)
# covered_items = initialize_covered_items(topices_qa)
# agent_controller(covered_items)
# print("covered_items:", covered_items)
