# === CB (TFIDF) ===
# TFIDF
TFIDF_MIN_DF = 2
TFIDF_MAX_FEATURES = 50000
WORD_NGRAM = (1, 2)

# User profile
WEIGHT_ENROLL = 1.0
WEIGHT_FAVORITE = 0.7
TAU_DAYS = 60 # time-decay

# === CF (Collaborative Filtering) ===
# Cache TTL
TTL_POPULAR = 60 # (nếu có) — ở đây bạn không dùng popularity nữa
TTL_SIMILAR = 600
TTL_USER_HOME = 120

# === Hybrid & Post-process ===
# Cache
CACHE_TTL = 3600  # in seconds
ALPHA_HOME = 0.7
TOPK_CANDIDATES = 20
CF_K_NEIGHBORS = 10
CF_K_ITEM_PER_NEIGHBOR = 5
CB_USER_MAX_ITEMS = 10

# CB Similarity threshold
MIN_SIM_CB = 0.2

# CF Similarity threshold
MIN_SIM_CF = 0.02

# Filter rules
RULE_MAX_PER_TEACHER = 3
RULE_MAX_PER_CATEGORY = 5
RECENCY_MAX_BOOST = 0.2 # tối đa +20% điểm
MIN_SCORE_THRESHOLD = 0.01 # lọc điểm quá thấp
MIN_CANDIDATES = 10 # nếu lọc quá nhiều → hạ tiêu chuẩn
