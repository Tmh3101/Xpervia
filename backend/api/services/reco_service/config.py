ALPHA_CONTENT = 0.65           # hybrid: content weight
TOPK_HOME = 12
TOPK_SIMILAR = 12

# CB – TF-IDF
TFIDF_MIN_DF = 2
TFIDF_MAX_FEATURES = 50000
USE_CHAR_NGRAM = True
WORD_NGRAM = (1, 2)
CHAR_NGRAM = (3, 5)

# User profile
WEIGHT_ENROLL = 1.0
WEIGHT_FAVORITE = 0.7
TAU_DAYS = 60                  # time-decay

# CF
CF_NEIGHBORS_PER_ITEM = 200    # số hàng xóm lưu sẵn/ item (nếu precompute)
USE_BM25 = False               # bật khi dữ liệu đủ lớn

# Cache TTL
TTL_POPULAR = 600              # (nếu có) — ở đây bạn không dùng popularity nữa
TTL_SIMILAR = 600
TTL_USER_HOME = 120
