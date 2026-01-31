from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

INTENT_TEMPLATES = {
    "ambulance": [
        "person is injured",
        "someone is bleeding",
        "accident happened",
        "person collapsed",
        "not breathing"
    ],
    "police": [
        "crime happened",
        "someone attacked",
        "theft occurred",
        "person murdered",
        "assault took place"
    ],
    "fire": [
        "fire broke out",
        "building is burning",
        "smoke everywhere"
    ]
}

template_embeddings = {
    k: model.encode(v, convert_to_tensor=True)
    for k, v in INTENT_TEMPLATES.items()
}

def semantic_classify(text: str):
    emb = model.encode(text, convert_to_tensor=True)

    best = ("unknown", 0.0)

    for intent, t_emb in template_embeddings.items():
        score = util.cos_sim(emb, t_emb).max().item()
        if score > best[1]:
            best = (intent, score)

    return best