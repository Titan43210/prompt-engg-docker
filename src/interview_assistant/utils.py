def replace_end_comma_newline(input_string):
    # Check if the string ends with ",\n}"
    if input_string.endswith(",\n}"):
        # Replace ",\n}" with "\n}" at the end of the string
        input_string = input_string[:-3] + "\n}"
    return input_string


def get_evaluation_results(session_object, topics):
    evaluation = {}
    for topic in topics:
        evals = session_object[topic]['evals']
        # print(evals)
        evals = [{k: v for k, v in d.items() if k not in ['need_to_ask', 'is_ask', 'is_pass']} for d in evals]
        evaluation[topic] = evals
    return evaluation

