import json

from interview_state import create_session, get_session
from interview_planner import create_interview_plan
from llm_client import generate_response


def start_interview(session_id, candidate):
    """
    Create a new interview session and generate the opening question.
    """

    interview_plan = create_interview_plan(candidate)

    state = create_session(
        session_id,
        candidate,
        interview_plan,
    )

    first_topic = interview_plan[0]

    prompt = f"""
You are ByteForger, a professional technical interviewer.

You are interviewing a candidate for the role:
{candidate["member"]["jobRole"]}

Candidate:
{candidate["member"]["name"]}

Start a realistic technical interview.

Your first question should assess this curriculum topic:

Day {first_topic["day"]}: {first_topic["title"]}

Domain:
{first_topic["domain"]}

The candidate's learning signal:
{first_topic["learning_signal"]}

Role relevance:
{first_topic["role_relevance"]}

Ask exactly ONE clear technical question.

Do not explain the answer.
Do not ask multiple questions.
Do not mention the internal priority or learning signal.
"""

    question = generate_response(prompt)

    state.add_question(
        question,
        first_topic["day"],
    )

    return question


def analyze_answer(state, latest_answer, current_topic, next_topic):
    """
    Use one LLM call to decide whether to follow up
    or move to the next curriculum topic, and generate
    the appropriate question.
    """

    follow_up_allowed = state.can_follow_up(current_topic["day"])

    prompt = f"""
You are ByteForger, a professional technical interviewer.

Candidate:
{state.candidate["member"]["name"]}

Role:
{state.candidate["member"]["jobRole"]}

CURRENT CURRICULUM TOPIC:
Day {current_topic["day"]}: {current_topic["title"]}
Domain: {current_topic["domain"]}
Role relevance: {current_topic["role_relevance"]}

NEXT CURRICULUM TOPIC:
Day {next_topic["day"]}: {next_topic["title"]}
Domain: {next_topic["domain"]}
Role relevance: {next_topic["role_relevance"]}

Candidate's latest answer:
{latest_answer}

Conversation history:
{state.get_history()}

Follow-up allowed on the current topic:
{follow_up_allowed}

Decide what should happen next.

Choose FOLLOW_UP when:
- the candidate made a technical claim worth exploring
- there is a weakness or missing detail worth probing
- the candidate mentioned a meaningful trade-off
- clarification would help assess understanding

Choose MOVE_ON when:
- the answer is sufficiently complete
- there is little useful information to probe
- another curriculum topic should be assessed
- follow-up is not allowed on the current topic

IMPORTANT:
If follow-up is not allowed, you MUST choose MOVE_ON.

If you choose FOLLOW_UP:
- ask about the CURRENT topic
- build directly on the candidate's latest answer

If you choose MOVE_ON:
- ask about the NEXT topic
- do not ask another question about the current topic

Return ONLY valid JSON:

{{
    "decision": "FOLLOW_UP",
    "question": "..."
}}

OR:

{{
    "decision": "MOVE_ON",
    "question": "..."
}}

Do not include markdown.
Do not include explanations outside the JSON.
"""

    response = generate_response(prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

def process_answer(session_id, message):
    """
    Process the candidate's latest answer and generate
    the next interview question.
    """

    state = get_session(session_id)

    if state is None:
        raise ValueError("Interview session not found")

    state.add_answer(message)

    # Finish once the minimum interview requirements
    # have been satisfied.
    if state.has_minimum_coverage():
        return generate_final_feedback(state)

    current_topic = state.current_topic

    if current_topic is None:
        raise ValueError("No current interview topic found")

    next_topic = get_next_topic(state)

    analysis = analyze_answer(
        state,
        message,
        current_topic,
        next_topic,
    )

    decision = analysis.get("decision")
    question = analysis.get("question")

    if not question:
        raise ValueError("LLM did not return a question")

    # Follow up on the same topic.
    if (
        decision == "FOLLOW_UP"
        and state.can_follow_up(current_topic["day"])
    ):
        state.record_follow_up(current_topic["day"])

        state.add_question(
            question,
            current_topic["day"],
        )

        return question

    # Otherwise move to the next curriculum topic.
    state.add_question(
        question,
        next_topic["day"],
    )

    return question


def get_next_topic(state):
    """
    Select the highest-priority curriculum day that
    has not yet been covered.
    """

    covered_days = state.days_covered

    for topic in state.interview_plan:
        if topic["day"] not in covered_days:
            return topic

    # Fallback if every planned topic has already been covered.
    return state.interview_plan[0]


def build_next_question_prompt(state, topic, latest_answer):
    """
    Build the prompt used to generate the next interview question.
    """

    history = state.get_history()

    return f"""
You are ByteForger, a professional technical interviewer.

Candidate role:
{state.candidate["member"]["jobRole"]}

Candidate:
{state.candidate["member"]["name"]}

You are conducting a conversational technical interview.

The candidate's latest answer was:

{latest_answer}

Previous conversation:

{history}

The next curriculum topic to assess is:

Day {topic["day"]}: {topic["title"]}

Domain:
{topic["domain"]}

Learning signal:
{topic["learning_signal"]}

Role relevance:
{topic["role_relevance"]}

Generate exactly ONE technical interview question.

The question should:
- be relevant to the candidate's role
- assess understanding rather than memorization
- naturally continue the interview
- not repeat a question already asked
- not mention internal priority, learning signal, or planning
- not contain multiple questions

Return only the question.
"""

def generate_final_feedback(state):
    """
    Generate structured feedback after the minimum interview
    coverage has been reached.
    """

    prompt = f"""
You are ByteForger, a professional technical interviewer.

Candidate:
{state.candidate["member"]["name"]}

Role:
{state.candidate["member"]["jobRole"]}

Interview conversation:
{state.get_history()}

Generate concise, actionable interview feedback based only on the
candidate's answers in the interview.

Return ONLY valid JSON in exactly this structure:

{{
    "summary": "A concise overall assessment of the candidate.",
    "strengths": [
        "Strength demonstrated by the candidate.",
        "Another strength demonstrated by the candidate."
    ],
    "gaps": [
        "Specific technical gap or weakness.",
        "Another area that could be improved."
    ],
    "next": [
        "Specific recommendation for improvement.",
        "Another concrete next step."
    ]
}}

Rules:
- Do not include markdown.
- Do not include any explanation outside the JSON.
- Keep the feedback concise and actionable.
- Base the feedback on the interview conversation.
- Do not invent skills or weaknesses that were not demonstrated.
"""

    response = generate_response(prompt)

    return json.loads(response)