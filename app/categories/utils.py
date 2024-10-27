# TODO: Implement an override for the GOV.UK WTForms radio field to support divisors
def get_items_with_divisor(items):
    output = []
    for _ in items:
        output.append(dict())
    output[-2]["divider"] = "or"
    return output


# TODO: Implement an override for the GOV.UK WTForms radio field supporting passing in a pre-selected answer
def check_radio_field(question, answer, items):
    if not items:
        items = []
        for _ in items:
            items.append(dict())

    for question_num in range(len(question.choices)):
        if question.choices[question_num][0] == answer:
            items[question_num]["checked"] = True
    return items
