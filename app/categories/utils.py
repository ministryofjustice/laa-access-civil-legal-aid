def get_items_with_divisor(items):
    output = []
    for _ in items:
        output.append(dict())
    output[-2]["divider"] = "or"
    return output


def check_radio_field(question, answer, items):
    for question_num in range(len(question.choices)):
        if question.choices[question_num][0] == answer:
            items[question_num]["checked"] = True
    return items
