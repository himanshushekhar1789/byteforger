class InterviewState:
    def __init__(self, session_id, candidate, interview_plan):
        self.session_id = session_id
        self.candidate = candidate
        self.interview_plan = interview_plan

        self.conversation_history = []

        self.questions_asked = 0
        self.days_covered = set()

        self.answers = []
        self.current_topic = None

        self.follow_ups_per_day = {}

    def add_question(self, question, day):
        self.questions_asked += 1
        self.days_covered.add(day)

        self.current_topic = next(
            (
                topic
                for topic in self.interview_plan
                if topic["day"] == day
            ),
            None,
        )

        self.conversation_history.append(
            {
                "role": "assistant",
                "content": question,
                "day": day,
            }
        )

    def add_answer(self, answer):
        self.answers.append(answer)

        self.conversation_history.append(
            {
                "role": "user",
                "content": answer,
            }
        )

    def has_minimum_coverage(self):
        return (
            self.questions_asked >= 8
            and len(self.days_covered) >= 4
        )

    def can_follow_up(self, day, max_follow_ups=2):
        return self.follow_ups_per_day.get(day, 0) < max_follow_ups

    def record_follow_up(self, day):
        self.follow_ups_per_day[day] = (
            self.follow_ups_per_day.get(day, 0) + 1
        )

    def get_history(self):
        return self.conversation_history

    def get_current_progress(self):
        return {
            "questions_asked": self.questions_asked,
            "days_covered": len(self.days_covered),
            "answers": len(self.answers),
        }


# In-memory storage for active interview sessions.

sessions = {}


def create_session(session_id, candidate, interview_plan):
    state = InterviewState(
        session_id,
        candidate,
        interview_plan,
    )

    sessions[session_id] = state

    return state


def get_session(session_id):
    return sessions.get(session_id)


def delete_session(session_id):
    sessions.pop(session_id, None)