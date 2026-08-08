from data_loader import load_candidates
from interview_agent import start_interview, process_answer
from interview_state import get_session


candidate = load_candidates()[0]

session_id = "full-test-001"

print("=" * 60)
print("STARTING BYTEFORGER INTERVIEW")
print("=" * 60)

question = start_interview(session_id, candidate)

state = get_session(session_id)

print(f"\nQuestion 1 | Day {state.current_topic['day']}")
print(question)


test_answers = [
    "I would use batch and streaming pipelines to ingest data, transform it, generate embeddings, and update the retrieval index. I would also use caching to reduce latency.",

    "Batch processing would handle historical data while streaming would handle real-time changes. I would need to keep the vector index consistent with the source of truth and avoid stale embeddings.",

    "I would use versioning and event-driven updates so changes can propagate to the index. I would also monitor indexing lag and periodically reconcile the index with the source data.",

    "For scale, I would partition the data and distribute indexing across multiple workers. I would choose an index structure that provides a good balance between search accuracy, memory usage, and latency.",

    "For failures, I would make updates idempotent and use retries or a dead-letter mechanism. That would prevent individual failed events from leaving the index permanently inconsistent.",

    "I would monitor query latency, indexing latency, error rates, and freshness. These metrics would help identify whether the retrieval system is meeting its reliability and performance goals.",

    "For the retrieval layer, I would evaluate precision and recall along with latency. The right balance depends on the requirements of the product.",

    "I would also consider how the system behaves as the dataset grows. Capacity planning, partitioning, replication, and efficient storage would become increasingly important.",
    "I would use a vector database such as Milvus or another distributed vector store, partition the embeddings across nodes, and use replication for availability. I would also monitor storage growth and query latency as the dataset scales.",
]


for i, answer in enumerate(test_answers, start=2):

    question = process_answer(session_id, answer)

    state = get_session(session_id)

    print(f"\nQuestion {i} | Day {state.current_topic['day']}")
    print(question)

    print(
        f"Progress: "
        f"{state.questions_asked} questions, "
        f"{len(state.days_covered)} curriculum days"
    )

    if state.has_minimum_coverage():
        print("\nMinimum interview coverage reached.")
        break
    print("\n" + "=" * 60)
print("FINAL INTERVIEW PROGRESS")
print("=" * 60)

state = get_session(session_id)

print(f"Questions asked: {state.questions_asked}")
print(f"Curriculum days covered: {len(state.days_covered)}")
print(f"Days: {sorted(state.days_covered)}")
print(f"Follow-ups per day: {state.follow_ups_per_day}")

if state.has_minimum_coverage():
    print("Minimum requirements: PASSED")
else:
    print("Minimum requirements: NOT YET PASSED")

