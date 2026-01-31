from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

LOCATION_TEMPLATES = [
    "shopping mall",
    "street",
    "road",
    "college campus",
    "hospital",
    "apartment building",
    "pg hostel",
    "metro station",
    "market area",
    "residential area",
    "office building"
]

template_embeddings = model.encode(
    LOCATION_TEMPLATES, convert_to_tensor=True
)

def semantic_location(text: str):
    emb = model.encode(text, convert_to_tensor=True)
    scores = util.cos_sim(emb, template_embeddings)[0]

    best_idx = scores.argmax().item()
    best_score = scores[best_idx].item()

    if best_score > 0.55:
        return {
            "text": LOCATION_TEMPLATES[best_idx],
            "confidence": round(best_score, 2),
            "semantic": True
        }

    return None