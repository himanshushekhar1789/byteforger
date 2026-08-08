from data_loader import load_curriculum


# Curriculum domains based on the actual 31-day curriculum.
DOMAIN_DAYS = {
    "core_foundation": {1, 2},
    "data_retrieval": {4, 5, 6, 7, 8, 9, 10},
    "llm_prompting": {11, 12, 13, 14, 15},
    "backend_application": {3, 16, 17, 18, 19, 20},
    "agentic_ai": {21, 22, 23, 24},
    "production": {25, 26, 27, 28, 29, 30, 31},
}


# Which curriculum domains are most relevant to each role family.
ROLE_DOMAINS = {
    "data": {
        "data_retrieval": "HIGH",
        "backend_application": "MEDIUM",
        "llm_prompting": "MEDIUM",
        "production": "MEDIUM",
        "agentic_ai": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "backend": {
        "backend_application": "HIGH",
        "data_retrieval": "MEDIUM",
        "production": "MEDIUM",
        "agentic_ai": "MEDIUM",
        "llm_prompting": "LOW",
       "core_foundation": "VERY_LOW",
    },

    "ai": {
        "llm_prompting": "HIGH",
        "data_retrieval": "HIGH",
        "agentic_ai": "HIGH",
        "backend_application": "MEDIUM",
        "production": "MEDIUM",
        "core_foundation": "VERY_LOW",
    },

    "devops": {
        "production": "HIGH",
        "backend_application": "MEDIUM",
        "data_retrieval": "LOW",
        "agentic_ai": "LOW",
        "llm_prompting": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "mobile": {
        "backend_application": "HIGH",
        "llm_prompting": "MEDIUM",
        "production": "MEDIUM",
        "data_retrieval": "LOW",
        "agentic_ai": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "architect": {
        "backend_application": "HIGH",
        "data_retrieval": "HIGH",
        "llm_prompting": "HIGH",
        "agentic_ai": "HIGH",
        "production": "HIGH",
        "core_foundation": "VERY_LOW",
    },

    "developer": {
        "backend_application": "HIGH",
        "llm_prompting": "MEDIUM",
        "data_retrieval": "MEDIUM",
        "production": "MEDIUM",
        "agentic_ai": "MEDIUM",
        "core_foundation": "VERY_LOW",
    },

    "support": {
        "backend_application": "MEDIUM",
        "production": "HIGH",
        "data_retrieval": "MEDIUM",
        "agentic_ai": "LOW",
        "llm_prompting": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "business": {
        "llm_prompting": "HIGH",
        "backend_application": "MEDIUM",
        "production": "MEDIUM",
        "data_retrieval": "LOW",
        "agentic_ai": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "marketing": {
        "llm_prompting": "HIGH",
        "backend_application": "LOW",
        "data_retrieval": "LOW",
        "production": "LOW",
        "agentic_ai": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "hr": {
        "llm_prompting": "HIGH",
        "backend_application": "LOW",
        "data_retrieval": "LOW",
        "production": "LOW",
        "agentic_ai": "LOW",
        "core_foundation": "VERY_LOW",
    },

    "ux": {
        "backend_application": "HIGH",
        "llm_prompting": "MEDIUM",
        "production": "LOW",
        "data_retrieval": "LOW",
        "agentic_ai": "LOW",
        "core_foundation": "VERY_LOW",
    },
}


def get_learning_signal(mission):
    """
    Determine what the candidate's mission history tells us
    about their demonstrated understanding.
    """

    if mission.get("skipped", False):
        return "UNASSESSED"

    if not mission.get("passed", False):
        return "STRUGGLED"

    attempts = mission.get("attempts", 1)

    if attempts >= 4:
        return "DIFFICULT"

    if attempts >= 2:
        return "MODERATE"

    return "COMFORTABLE"


def get_role_family(job_role):
    """
    Map the supplied job role to a broader role family.
    """

    role = job_role.lower()

    if "data" in role:
        return "data"

    if "devops" in role:
        return "devops"

    if "ai" in role:
        return "ai"

    if "backend" in role:
        return "backend"

    if "mobile" in role:
        return "mobile"
    if "architect" in role:
        return "architect"

    if "engineer" in role:
        return "developer"

    if "developer" in role:
        return "developer"

    if "support" in role:
        return "support"

    if "business" in role:
        return "business"

    if "marketing" in role:
        return "marketing"

    if "hr" in role:
        return "hr"

    if "ux" in role:
        return "ux"

    return "developer"


def get_day_domain(day_number):
    """
    Determine which curriculum domain a day belongs to.
    """

    for domain, days in DOMAIN_DAYS.items():
        if day_number in days:
            return domain

    return None


def calculate_role_relevance(day_number, role_family):
    domain = get_day_domain(day_number)

    if domain is None:
        return "LOW"

    role_relevance = ROLE_DOMAINS.get(
        role_family,
        ROLE_DOMAINS["developer"],
    )

    return role_relevance.get(domain, "LOW")

def calculate_priority(learning_signal, role_relevance):
    # HIGH relevance topics should dominate the interview.
    if role_relevance == "HIGH":
        if learning_signal in ("STRUGGLED", "DIFFICULT", "MODERATE", "UNASSESSED"):
            return "HIGH"

        # Candidate already demonstrated comfort,
        # so verify it without over-focusing on it.
        return "MEDIUM"

    # MEDIUM relevance topics are secondary.
    if role_relevance == "MEDIUM":
        if learning_signal in ("STRUGGLED", "DIFFICULT"):
            return "HIGH"

        if learning_signal in ("MODERATE", "UNASSESSED"):
            return "MEDIUM"

        return "LOW"

    # LOW relevance topics should not dominate,
    # regardless of learning difficulty.
    if role_relevance == "LOW":
        return "LOW"

    # VERY_LOW topics are fallback topics only.
    return "VERY_LOW"


def create_interview_plan(candidate):
    """
    Create a ranked list of curriculum topics for the candidate.
    """

    curriculum = load_curriculum()["days"]

    curriculum_by_day = {
        day["day"]: day
        for day in curriculum
    }

    job_role = candidate["member"]["jobRole"]
    role_family = get_role_family(job_role)

    plan = []

    for mission in candidate["missions"]:
        day_number = mission["day"]

        if day_number not in curriculum_by_day:
            continue

        curriculum_day = curriculum_by_day[day_number]

        learning_signal = get_learning_signal(mission)

        role_relevance = calculate_role_relevance(
            day_number,
            role_family,
        )

        priority = calculate_priority(
            learning_signal,
            role_relevance,
        )

        plan.append(
            {
                "day": day_number,
                "title": curriculum_day["title"],
                "domain": get_day_domain(day_number),
                "learning_signal": learning_signal,
                "role_relevance": role_relevance,
                "priority": priority,
            }
        )

    priority_order = {
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
         "VERY_LOW": 0,
    }

    plan.sort(
        key=lambda item: priority_order[item["priority"]],
        reverse=True,
    )

    return plan