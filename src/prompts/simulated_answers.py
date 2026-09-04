SIMULATED_ANSWERS_DB = {
    "location": "The address is 100 Main Street, Building B.",
    "address": "It's located at our Camden St campus, 3rd floor.",
    "contact": "You can reach the site manager at 555-0199.",
    "leak": "It's water leaking from the HVAC vent.",
    "trade": "It's a plumbing issue, water is pooling.",
    "urgent": "It's extremely urgent, water is getting near the electrical panels.",
    "access": "We are open from 9 AM to 5 PM today.",
    "default": "Yes, I can confirm that. Please send someone as soon as possible.",
}


def get_simulated_answer(question_text: str, target_field: str) -> str:
    """Returns a diverse simulated answer based on keywords in the question or target field."""
    q_lower = question_text.lower()
    t_lower = target_field.lower()

    for key, answer in SIMULATED_ANSWERS_DB.items():
        if key in q_lower or key in t_lower:
            return answer

    return SIMULATED_ANSWERS_DB["default"]
