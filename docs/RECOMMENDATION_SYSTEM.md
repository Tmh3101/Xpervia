# Tài liệu Hệ thống Gợi ý - Xpervia LMS

## Tổng quan

Hệ thống gợi ý (Recommendation System) của Xpervia LMS là một hybrid recommender system kết hợp hai phương pháp chính:
- **Content-Based Filtering (CB)**: Dựa trên nội dung khóa học (TF-IDF)
- **Collaborative Filtering (CF)**: Dựa trên hành vi người dùng (User-based CF)

Hệ thống được thiết kế để hoạt động hiệu quả với dữ liệu lớn, tự động cập nhật khi có thay đổi, và cung cấp gợi ý cá nhân hóa cho từng người dùng.

---

## Kiến trúc Tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                    XPERVIA RECOMMENDATION SYSTEM                │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐      ┌──────────────────┐     ┌──────────────┐
│   DATABASE    │      │   ARTIFACT STORE │     │  CELERY TASKS│
│               │      │                  │     │              │
│ • Users       │◄────►│ • TF-IDF Matrix  │◄────│ • CF Update  │
│ • Courses     │      │ • CF Neighbors   │     │ • Periodic   │
│ • Enrollments │      │ • Metadata       │     │   Refresh    │
│ • Favorites   │      │ • Indices        │     │              │
└───────────────┘      └──────────────────┘     └──────────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────────┐  ┌──────────────────────┐
        │  CONTENT-BASED (CB)   │  │ COLLABORATIVE (CF)   │
        │                       │  │                      │
        │ • TF-IDF Vectorizer   │  │ • User-Item Matrix   │
        │ • Course Vectors      │  │ • User Similarity    │
        │ • User Profile Vector │  │ • Neighbor Items     │
        └───────────────────────┘  └──────────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    HYBRID BLENDING     │
                    │                        │
                    │ • Candidate Pool       │
                    │ • Weighted Combine     │
                    │ • Diversity Filter     │
                    │ • Final Ranking        │
                    └────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │    RECOMMENDATION      │
                    │        OUTPUT          │
                    └────────────────────────┘
```

---

## 1. Content-Based Filtering (CB)

### 1.1. Cơ chế hoạt động

Content-Based Filtering sử dụng **TF-IDF (Term Frequency - Inverse Document Frequency)** để biểu diễn nội dung khóa học dưới dạng vector số học.

#### Quy trình xây dựng TF-IDF Matrix:

```
[Khóa học mới được tạo/cập nhật]
            │
            ▼
┌───────────────────────────┐
│  1. Lấy dữ liệu khóa học  │
│     - Title               │
│     - Description         │
│     - Categories          │
└───────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  2. Tiền xử lý văn bản    │
│     - Tokenization        │
│     - Lowercase           │
│     - Remove stopwords    │
│     - Phrase mapping      │
└───────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  3. Xây dựng Document     │
│     doc = build_document_ │
│     text(title, desc,     │
│     categories)           │
└───────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  4. Tokenize bằng         │
│     vn_tokenize()         │
│     tokens = ["khóa",     │
│     "học", "python", ...] │
└───────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  5. TF-IDF Vectorization  │
│     - Ngram: (1,2)        │
│     - Min_df: 2           │
│     - Max_df: 0.95        │
│     - Max_features: 50k   │
└───────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  6. L2 Normalization      │
│     normalize(X, axis=1)  │
│     → Chuẩn hóa độ dài =1 │
└───────────────────────────┘
            │
            ▼
┌───────────────────────────┐
│  7. Lưu Artifacts         │
│     - tfidf_vectorizer    │
│     - tfidf_matrix.npz    │
│     - course_row_map.json │
└───────────────────────────┘
```

### 1.2. Cập nhật khi khóa học thay đổi

#### **Kịch bản 1: Khóa học mới được tạo**

```python
# File: cb/tfidf_builder.py → transform_single_course()

[Admin tạo khóa học mới]
            │
            ▼
┌─────────────────────────────────┐
│ 1. Load artifacts hiện tại:     │
│    - vec (TfidfVectorizer)      │
│    - X (TF-IDF matrix N×D)      │
│    - row_map {course_id: idx}   │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 2. Lấy dữ liệu khóa học từ DB   │
│    r = fetch_course_by_id(id)   │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 3. Xây dựng document text       │
│    doc = _course_to_text(r)     │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 4. Transform với vectorizer     │
│    v = vec.transform([doc])     │
│    → Vector 1×D (KHÔNG refit)   │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 5. L2 normalize                 │
│    v = normalize(v, axis=1)     │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 6. Thêm vào ma trận X           │
│    X = vstack([X, v])           │
│    row_map[course_id] = N       │
│    (N = số hàng mới)            │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 7. Lưu lại artifacts            │
│    save_artifacts(vec, X, map)  │
└─────────────────────────────────┘
```

**Lưu ý quan trọng:**
- **KHÔNG refit vectorizer**: Chỉ transform văn bản mới với vocabulary đã học
- Nếu khóa học có từ mới không có trong vocabulary → từ đó bị bỏ qua
- Ma trận X tăng thêm 1 hàng (vertical stack)

#### **Kịch bản 2: Khóa học bị cập nhật**

```python
[Admin sửa title/description/category]
            │
            ▼
┌─────────────────────────────────┐
│ 1. Load artifacts hiện tại      │
└─────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│ 2. Kiểm tra course_id có trong  │
│    row_map không?               │
│    if course_id in row_map:     │
└─────────────────────────────────┘
         │           │
     Yes │           │ No
         ▼           ▼
    ┌────────┐  ┌─────────┐
    │ UPDATE │  │   ADD   │
    └────────┘  └─────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 3. Transform văn bản mới        │
│    v = vec.transform([doc])     │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 4. Cập nhật hàng tại vị trí i   │
│    i = row_map[course_id]       │
│    X_lil = X.tolil()            │
│    X_lil[i, :] = v              │
│    X = X_lil.tocsr()            │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ 5. Lưu lại artifacts            │
└─────────────────────────────────┘
```

#### **Kịch bản 3: Khóa học bị xóa**

```
[Admin xóa khóa học]
            │
            ▼
┌─────────────────────────────────┐
│ CHƯA ĐƯỢC IMPLEMENT             │
│                                 │
│ Giải pháp tạm thời:             │
│ - Để hàng đó trong ma trận X    │
│ - Bỏ qua khi tính toán          │
│                                 │
│ Giải pháp đầy đủ:               │
│ - Xóa hàng khỏi X               │
│ - Rebuild row_map               │
│ - Hoặc rebuild toàn bộ          │
└─────────────────────────────────┘
```

### 1.3. Xây dựng User Profile Vector

User profile vector là tổng trọng số của các khóa học mà user đã tương tác:

```python
# File: cb/user_profile.py → build_user_vector()

┌──────────────────────────────────────┐
│ 1. Lấy sự kiện tương tác của user    │
│    events = fetch_user_events(uid)   │
│    [                                 │
│      {course_id, type, days_ago},    │
│      ...                             │
│    ]                                 │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 2. Load TF-IDF Matrix                │
│    vec, X, row_map = load_tfidf()    │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 3. Với mỗi event:                    │
│    ┌──────────────────────────────┐  │
│    │ a) Lấy course vector         │  │
│    │    i = row_map[course_id]    │  │
│    │    v = X.getrow(i)  # 1×D    │  │
│    │                              │  │
│    │ b) Tính trọng số event       │  │
│    │    w = event_weight(         │  │
│    │      type,                   │  │
│    │      days_ago                │  │
│    │    )                         │  │
│    │                              │  │
│    │    Formula:                  │  │
│    │    w = base × exp(-days/τ)   │  │
│    │                              │  │
│    │    base_enroll = 1.0         │  │
│    │    base_favorite = 0.7       │  │
│    │    τ = 60 days               │  │
│    │                              │  │
│    │ c) Nhân trọng số             │  │
│    │    v_weighted = v × w        │  │
│    │                              │  │
│    │ d) Cộng dồn                  │  │
│    │    acc = acc + v_weighted    │  │
│    └──────────────────────────────┘  │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ 4. L2 Normalize tổng vector          │
│    user_vector = normalize(acc)      │
│    → Vector 1×D                      │
└──────────────────────────────────────┘
```

**Công thức trọng số:**

```
w_event = w_base × decay_factor

Trong đó:
- w_base:
  • enroll   = 1.0  (tham gia học)
  • favorite = 0.7  (yêu thích)

- decay_factor = exp(-days_ago / 60)
  • Sự kiện gần đây (days_ago = 0):  decay = 1.0
  • Sau 30 ngày:                     decay ≈ 0.606
  • Sau 60 ngày:                     decay ≈ 0.368
  • Sau 120 ngày:                    decay ≈ 0.135
```

### 1.4. Tính toán Similarity

```python
# File: cb/similarity.py

┌──────────────────────────────────────┐
│ Tìm khóa học tương tự cho user:      │
│                                      │
│ similarity = user_vec @ X.T          │
│                                      │
│ Vì cả user_vec và X đều L2-norm:     │
│ → similarity = cosine similarity     │
│                                      │
│ Result: array shape (1, N_courses)   │
│ scores[i] = độ tương tự với course i │
└──────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────┐
│ Top-K Selection:                     │
│ - Lấy K khóa học có score cao nhất   │
│ - Lọc theo threshold (min_sim=0.2)   │
│ - Loại bỏ khóa học đã tham gia       │
└──────────────────────────────────────┘
```

---

## 2. Collaborative Filtering (CF)

### 2.1. Cơ chế hoạt động

CF sử dụng **User-based Collaborative Filtering** với các bước:

1. Xây dựng ma trận User-Item (R)
2. Tính ma trận User-User similarity (U)
3. Tìm k láng giềng gần nhất cho mỗi user
4. Gợi ý items mà láng giềng đã tương tác

### 2.2. Xây dựng User-Item Matrix

```python
# File: cf/build_matrix.py → build_user_item_matrix()

┌──────────────────────────────────────────┐
│ 1. Lấy toàn bộ interactions từ DB        │
│    events = fetch_all_interactions()     │
│    [                                     │
│      (user_id, course_id, type, ts),     │
│      ...                                 │
│    ]                                     │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 2. Tạo index mapping                     │
│    user_index: {user_id → row_idx}       │
│    item_index: {course_id → col_idx}     │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 3. Với mỗi event:                        │
│    ┌──────────────────────────────────┐  │
│    │ a) Map to indices                │  │
│    │    u = user_index[user_id]       │  │
│    │    i = item_index[course_id]     │  │
│    │                                  │  │
│    │ b) Tính trọng số                 │  │
│    │    days = (now - ts) / 86400     │  │
│    │    w = event_weight(type, days)  │  │
│    │                                  │  │
│    │ c) Tích lũy vào dict             │  │
│    │    accum[(u,i)] += w             │  │
│    │    (Cộng dồn nếu user có nhiều   │  │
│    │     tương tác với cùng course)   │  │
│    └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 4. Tạo Sparse Matrix                     │
│    R = csr_matrix(                       │
│      (data, (rows, cols)),               │
│      shape=(n_users, n_items)            │
│    )                                     │
│                                          │
│    Ma trận R:                            │
│         course₁  course₂  course₃  ...   │
│    user₁   1.0     0.7      0      ...   │
│    user₂    0      1.0     1.0     ...   │
│    user₃   0.5      0      0.7     ...   │
│    ...                                   │
└──────────────────────────────────────────┘
```

### 2.3. Tính User-User Similarity

```python
# File: cf/user_user.py → compute_user_user_cosine()

┌──────────────────────────────────────────┐
│ 1. L2 Normalize từng hàng của R          │
│    R_norm = normalize(R, axis=1)         │
│    → Mỗi user vector có độ dài = 1       │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 2. Tính ma trận cosine U                 │
│    U = R_norm @ R_norm.T                 │
│                                          │
│    Kết quả: U (n_users × n_users)        │
│         user₁  user₂  user₃  ...         │
│    user₁  1.0   0.82   0.15  ...         │
│    user₂  0.82  1.0    0.45  ...         │
│    user₃  0.15  0.45   1.0   ...         │
│    ...                                   │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 3. Zero diagonal (tự similarity = 0)     │
│    U.setdiag(0.0)                        │
└──────────────────────────────────────────┘
```

### 2.4. Shrinkage - Giảm nhiễu

Shrinkage giúp giảm ảnh hưởng của các cặp user có ít item chung:

```python
# File: cf/user_user.py → apply_shrinkage()

┌──────────────────────────────────────────┐
│ 1. Tính số item chung giữa mỗi cặp user  │
│    B = binarize(R)  # 0/1 matrix         │
│    C = B @ B.T      # common counts      │
│                                          │
│    C[i,j] = số course cả i và j tham gia │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 2. Áp dụng công thức shrinkage           │
│                                          │
│    sim'[i,j] = sim[i,j] × (              │
│      n_common[i,j]                       │
│      ──────────────────────              │
│      n_common[i,j] + β                   │
│    )                                     │
│                                          │
│    β = 50.0 (tham số điều chỉnh)         │
│                                          │
│    Ví dụ:                                │
│    • n_common = 5:  scale = 5/55 = 0.09  │
│    • n_common = 20: scale = 20/70 = 0.29 │
│    • n_common = 50: scale = 50/100 = 0.50│
│    • n_common = 100: scale = 100/150=0.67│
└──────────────────────────────────────────┘
```

**Tác dụng Shrinkage:**
- Cặp user ít course chung → similarity bị giảm mạnh
- Cặp user nhiều course chung → similarity được giữ lại
- Tránh false positive từ trùng hợp ngẫu nhiên

### 2.5. Tìm K Neighbors

```python
# File: cf/neighbors.py

┌──────────────────────────────────────────┐
│ MODE 1: FULL (cho dataset nhỏ/vừa)       │
│                                          │
│ 1. Đã có ma trận U (n_users × n_users)   │
│                                          │
│ 2. Với mỗi user u:                       │
│    - Lấy hàng U[u, :]                    │
│    - Sắp xếp giảm dần                    │
│    - Chọn top-k                          │
│    - Lọc sim > min_sim                   │
│                                          │
│ 3. Lưu kết quả:                          │
│    {                                     │
│      "user1": [                          │
│        ["user5", 0.82],                  │
│        ["user12", 0.76],                 │
│        ...                               │
│      ],                                  │
│      ...                                 │
│    }                                     │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ MODE 2: STREAMING (cho dataset lớn)      │
│                                          │
│ 1. KHÔNG xây dựng full ma trận U         │
│                                          │
│ 2. Với mỗi user u:                       │
│    ┌──────────────────────────────────┐  │
│    │ a) Lấy hàng R[u, :]              │  │
│    │                                  │  │
│    │ b) Tính similarity với all:      │  │
│    │    R_norm = normalize(R)         │  │
│    │    u_vec = R_norm[u, :]          │  │
│    │    sims = u_vec @ R_norm.T       │  │
│    │                                  │  │
│    │ c) Apply shrinkage nếu có        │  │
│    │                                  │  │
│    │ d) Top-k selection               │  │
│    └──────────────────────────────────┘  │
│                                          │
│ 3. Tiết kiệm RAM: chỉ tính từng hàng     │
└──────────────────────────────────────────┘
```

### 2.6. Cập nhật khi có tương tác mới

```python
# File: tasks.py + startup.py

┌──────────────────────────────────────────┐
│ AUTOMATIC UPDATE FLOW                    │
│                                          │
│ 1. Celery Periodic Task (mỗi 10 phút)    │
│    @periodic_task(run_every=...)         │
│    update_cf_neighbors_task()            │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 2. Kiểm tra có sự kiện mới không?        │
│    latest_ts = MAX(                      │
│      enrollments.created_at,             │
│      favorites.created_at                │
│    )                                     │
│                                          │
│    last_build_ts = load từ cf_meta.json  │
│                                          │
│    if latest_ts > last_build_ts:         │
│        → CẦN REBUILD                     │
│    else:                                 │
│        → BỎ QUA                          │
└──────────────────────────────────────────┘
            │
            ▼ (Cần rebuild)
┌──────────────────────────────────────────┐
│ 3. File Lock (tránh race condition)      │
│    with file_lock(cf_build.lock):        │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 4. Rebuild CF Neighbors                  │
│    rebuild_user_neighbors_streaming(     │
│      mode="streaming",                   │
│      k_neighbors=10,                     │
│      shrink_beta=50.0,                   │
│      min_sim=0.02                        │
│    )                                     │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 5. Lưu artifacts                         │
│    - cf_user_neighbors.json              │
│    - cf_user_index.json                  │
│    - cf_item_index.json                  │
│    - cf_meta.json (timestamp)            │
└──────────────────────────────────────────┘
```

**Khi user mới enroll/favorite:**

```
[User enroll course hoặc favorite course]
            │
            ▼
┌──────────────────────────────────────────┐
│ 1. Ghi vào DB (enrollments/favorites)    │
│    updated_at = NOW()                    │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 2. Background process (không realtime)   │
│    Đợi Celery task chạy (10 phút/lần)    │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 3. CF neighbors được rebuild             │
│    Ma trận R mới bao gồm sự kiện mới     │
└──────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────┐
│ 4. Recommendations cập nhật              │
│    Lần tiếp user request sẽ dùng         │
│    neighbors mới                         │
└──────────────────────────────────────────┘
```

---

## 3. Hybrid Recommender

### 3.1. Luồng gợi ý trang Home

```python
# File: hybrid/service.py → hybrid_recommend_home()

┌──────────────────────────────────────────────────┐
│ INPUT: user_id                                   │
└──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────┐
│ STEP 1: Build Candidate Pool                     │
│                                                  │
│ ┌────────────────────────────────────────────┐   │
│ │ CB Candidates (Content-Based):             │   │
│ │ ─────────────────────────────────          │   │
│ │ 1. Load user vector                        │   │
│ │ 2. Similarity = user_vec @ X.T             │   │
│ │ 3. Top-M courses (M=10)                    │   │
│ │ 4. Filter: sim > 0.2                       │   │
│ │                                            │   │
│ │ Output: {course_id: score_cb, ...}         │   │
│ └────────────────────────────────────────────┘   │
│                                                  │
│ ┌────────────────────────────────────────────┐   │
│ │ CF Candidates (Collaborative):             │   │
│ │ ─────────────────────────────────          │   │
│ │ 1. Load neighbors của user                 │   │
│ │    neighbors = [                           │   │
│ │      ["user_v", sim_v],                    │   │
│ │      ...                                   │   │
│ │    ]                                       │   │
│ │                                            │   │
│ │ 2. Với mỗi neighbor v (top-k=10):          │   │
│ │    - Lấy items mà v đã tương tác           │   │
│ │    - Sắp xếp theo weight giảm dần          │   │
│ │    - Chọn top-5 items/neighbor             │   │
│ │                                            │   │
│ │ 3. Union tất cả items                      │   │
│ │                                            │   │
│ │ Output: {course_id: weight_cf, ...}        │   │
│ └────────────────────────────────────────────┘   │
│                                                  │
│ ┌────────────────────────────────────────────┐   │
│ │ Popular Candidates (Backup):               │   │
│ │ ─────────────────────────────              │   │
│ │ - Các khóa học phổ biến                    │   │
│ │ - Dùng khi CB/CF không đủ                  │   │
│ │                                            │   │ 
│ │ Output: [course_id, ...]                   │   │
│ └────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────┐
│ STEP 2: Weighted Blending                        │
│                                                  │
│ Formula:                                         │
│ ────────                                         │
│ score_final[i] = α × score_cb[i]                 │
│                + (1-α) × score_cf[i]             │
│                                                  │
│ Với: α = 0.7 (ưu tiên CB hơn)                    │
│                                                  │
│ Ví dụ:                                           │
│ ───────                                          │
│ course_123:                                      │
│   CB score = 0.85                                │
│   CF score = 0.60                                │
│   Final = 0.7×0.85 + 0.3×0.60 = 0.775            │
│                                                  │
│ course_456:                                      │
│   CB score = 0.00 (không có trong CB)            │
│   CF score = 0.90                                │
│   Final = 0.7×0.00 + 0.3×0.90 = 0.270            │
└──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────┐
│ STEP 3: Filter & Rank                            │
│                                                  │
│ 1. Lọc khóa học đã tham gia:                     │
│    seen_ids = [courses user đã enroll]           │
│    if course_id in seen_ids:                     │
│        score = 0.0                               │
│                                                  │
│ 2. Sắp xếp theo score giảm dần                   │
│                                                  │
│ 3. Trả về danh sách:                             │
│    [                                             │
│      {"course_id": 123, "score": 0.775},         │
│      {"course_id": 456, "score": 0.690},         │
│      ...                                         │
│    ]                                             │
└──────────────────────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────────────────────┐
│ OUTPUT: Ranked Recommendations                   │
└──────────────────────────────────────────────────┘
```

### 3.2. Ví dụ cụ thể

**User A:**
- Đã học: Python cơ bản, Django basics
- Đã favorite: Machine Learning intro

**Bước 1: CB Candidates**
```
User vector A = weighted_sum([
  TF-IDF(Python cơ bản) × 1.0,
  TF-IDF(Django basics) × 0.9,
  TF-IDF(ML intro) × 0.7
])

Similarity với tất cả courses:
  - Advanced Python:     0.85
  - Django REST API:     0.78
  - Flask Web:           0.62
  - React JS:            0.15 (< 0.2, loại)
  - Deep Learning:       0.72
  ...

CB Candidates = {
  "Advanced Python": 0.85,
  "Django REST API": 0.78,
  "Deep Learning": 0.72,
  "Flask Web": 0.62
}
```

**Bước 2: CF Candidates**
```
Neighbors của User A:
  - User B: similarity 0.82
  - User C: similarity 0.75
  - User D: similarity 0.68

Items User B đã học (chưa overlap với A):
  - Node.js Backend: weight 1.0
  - PostgreSQL:      weight 0.9
  - Docker:          weight 0.7

Items User C đã học:
  - React Advanced:  weight 1.0
  - Django REST API: weight 0.95
  - AWS Basics:      weight 0.8

Items User D đã học:
  - TensorFlow:      weight 1.0
  - Deep Learning:   weight 0.9
  ...

CF Candidates = {
  "Node.js Backend": 0.82,
  "Django REST API": 0.75,
  "PostgreSQL": 0.74,
  "React Advanced": 0.75,
  "TensorFlow": 0.68,
  "Deep Learning": 0.68
}
```

**Bước 3: Blending (α = 0.7)**
```
All candidates = Union(CB, CF, Popular)

Final scores:
  - Advanced Python:  0.7×0.85 + 0.3×0    = 0.595
  - Django REST API:  0.7×0.78 + 0.3×0.75 = 0.771
  - Deep Learning:    0.7×0.72 + 0.3×0.68 = 0.708
  - Flask Web:        0.7×0.62 + 0.3×0    = 0.434
  - Node.js Backend:  0.7×0    + 0.3×0.82 = 0.246
  - TensorFlow:       0.7×0    + 0.3×0.68 = 0.204
```

**Bước 4: Final Ranking**
```
1. Django REST API    (0.771) ← CB + CF đều cao
2. Deep Learning      (0.708) ← CB + CF đều cao
3. Advanced Python    (0.595) ← CB cao, CF = 0
4. Flask Web          (0.434) ← CB trung bình
5. Node.js Backend    (0.246) ← Chỉ có CF
6. TensorFlow         (0.204) ← CF thấp
```

---

## 4. Cấu trúc Artifacts

### 4.1. Thư mục lưu trữ

```
api/var/reco/
├── tfidf_vectorizer.joblib    # Sklearn TfidfVectorizer
├── tfidf_matrix.npz            # Sparse matrix (N courses × D features)
├── course_row_map.json         # {course_id: row_index}
├── cf_user_neighbors.json      # {user_id: [[neighbor_id, sim], ...]}
├── cf_user_index.json          # {user_id: row_index}
├── cf_item_index.json          # {course_id: col_index}
├── cf_meta.json                # {last_build_ts, mode, params}
└── build.lock                  # File lock for concurrent safety
```

### 4.2. Chi tiết artifacts

#### `tfidf_matrix.npz`
```python
# Sparse CSR matrix: N × D
# N = số khóa học
# D = số features (max 50,000)
# Mỗi hàng = TF-IDF vector của 1 khóa học
# L2-normalized (||row|| = 1)

Shape: (247, 15832)  # Ví dụ: 247 courses, 15832 features
Non-zero elements: ~35,000
Density: ~0.9%
```

#### `course_row_map.json`
```json
{
  "1": 0,
  "2": 1,
  "3": 2,
  ...
  "247": 246
}
```

#### `cf_user_neighbors.json`
```json
{
  "user_uuid_1": [
    ["user_uuid_5", 0.8234],
    ["user_uuid_12", 0.7891],
    ["user_uuid_23", 0.7145],
    ...
  ],
  "user_uuid_2": [
    ["user_uuid_8", 0.9012],
    ...
  ]
}
```

#### `cf_meta.json`
```json
{
  "last_build_ts": "2025-11-29T10:30:45.123456Z",
  "mode": "streaming",
  "k_neighbors": 10,
  "use_bm25": false,
  "shrink_beta": 50.0,
  "min_sim": 0.02,
  "users_total": 1523
}
```

---

## 5. Tham số Cấu hình

### 5.1. Content-Based (CB)

```python
# File: config.py

# TF-IDF Parameters
TFIDF_MIN_DF = 2              # Từ phải xuất hiện >= 2 documents
TFIDF_MAX_FEATURES = 50000    # Giới hạn vocabulary size
WORD_NGRAM = (1, 2)           # Unigram + Bigram

# User Profile Weights
WEIGHT_ENROLL = 1.0           # Trọng số sự kiện "enroll"
WEIGHT_FAVORITE = 0.7         # Trọng số sự kiện "favorite"
TAU_DAYS = 60                 # Time decay constant (τ)

# CB Filtering
MIN_SIM_CB = 0.2              # Ngưỡng similarity tối thiểu
CB_USER_MAX_ITEMS = 10        # Số candidates CB tối đa
```

### 5.2. Collaborative Filtering (CF)

```python
# CF Parameters
CF_K_NEIGHBORS = 10           # Số láng giềng gần nhất
CF_K_ITEM_PER_NEIGHBOR = 5    # Items/neighbor để gợi ý
MIN_SIM_CF = 0.02             # Ngưỡng similarity tối thiểu

# BM25 (Optional)
USE_BM25 = False              # Có dùng BM25 weighting không
BM25_K1 = 1.2                 # Tham số k1
BM25_B = 0.75                 # Tham số b

# Shrinkage
SHRINK_BETA = 50.0            # Beta cho shrinkage formula
```

### 5.3. Hybrid Blending

```python
# Blending
ALPHA_HOME = 0.7              # Trọng số CB (CF = 1 - α)
TOPK_CANDIDATES = 20          # Số candidates tối đa xét

# Cache TTL (seconds)
CACHE_TTL = 3600              # 1 hour
TTL_SIMILAR = 600             # 10 minutes
TTL_USER_HOME = 120           # 2 minutes
```

---

## 6. Sơ đồ Tổng hợp

### 6.1. Data Flow Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE EVENTS                          │
├─────────────────────────────────────────────────────────────┤
│  • Course Created/Updated/Deleted                           │
│  • User Enrolls in Course                                   │
│  • User Favorites Course                                    │
└─────────────────────────────────────────────────────────────┘
        │                           │                    │
        │ Course Change             │ Interaction        │ Interaction
        │                           │ (Enroll)           │ (Favorite)
        ▼                           ▼                    ▼
┌──────────────────┐      ┌─────────────────────────────────┐
│   CB Pipeline    │      │        CF Pipeline              │
│                  │      │                                 │
│ 1. Transform     │      │ 1. Accumulate in R matrix       │
│    course text   │      │    R[user, course] += weight    │
│                  │      │                                 │
│ 2. Update/Add    │      │ 2. Celery periodic (10 min):    │
│    to X matrix   │      │    - Check new events           │
│                  │      │    - Rebuild neighbors          │
│ 3. Save          │      │    - Save cf_neighbors.json     │
│    artifacts     │      │                                 │
└──────────────────┘      └─────────────────────────────────┘
        │                           │
        │ Read                      │ Read
        ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     ARTIFACT STORAGE                        │
├─────────────────────────────────────────────────────────────┤
│  CB: tfidf_matrix.npz, vectorizer, course_row_map           │
│  CF: cf_user_neighbors.json, indices, metadata              │
└─────────────────────────────────────────────────────────────┘
        │                           │
        │                           │
        └────────────┬──────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │   Recommendation API   │
        │   Request comes in     │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Build Candidates:     │
        │  • CB: user_vec @ X.T  │
        │  • CF: neighbor items  │
        │  • Popular: backup     │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Blend & Rank:         │
        │  α×CB + (1-α)×CF       │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  Filter & Return       │
        │  Top-N Recommendations │
        └────────────────────────┘
```

### 6.2. Request Flow - User Home Page

```
[User visits Home Page]
            │
            ▼
┌──────────────────────────────────┐
│ API: GET /recommendations/home   │
└──────────────────────────────────┘
            │
            ▼
┌──────────────────────────────────┐
│ hybrid_recommend_home(user_id)   │
└──────────────────────────────────┘
            │
            ├─────────────────┬─────────────────┐
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌──────────┐
    │ CB Branch   │   │ CF Branch   │   │ Popular  │
    │             │   │             │   │          │
    │ • Load      │   │ • Load      │   │ • Query  │
    │   X matrix  │   │   neighbors │   │   DB     │
    │             │   │             │   │          │
    │ • Build     │   │ • Collect   │   │ • Top    │
    │   user_vec  │   │   neighbor  │   │   viewed │
    │             │   │   items     │   │          │
    │ • Compute   │   │             │   │          │
    │   similarity│   │ • Weight    │   │          │
    │             │   │   scoring   │   │          │
    │ • Top-K     │   │             │   │          │
    └─────────────┘   └─────────────┘   └──────────┘
            │                 │                 │
            └─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Blend Scores    │
                    │  α=0.7           │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Filter Seen     │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Sort by Score   │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Return JSON     │
                    └──────────────────┘
```

---

## 7. Performance & Optimization

### 7.1. Độ phức tạp tính toán

#### Content-Based
```
Build TF-IDF Matrix:
  Time: O(N × M × log(M))
    N = số courses
    M = avg words per course

Transform single course:
  Time: O(M × log(V))
    V = vocabulary size

User vector similarity:
  Time: O(D × N)
    D = feature dimensions
    N = số courses

→ CB scoring rất nhanh với sparse matrix
```

#### Collaborative Filtering
```
Build R matrix:
  Time: O(E)
    E = số interactions

Compute U (full):
  Time: O(U² × I)
    U = số users
    I = số items
  Space: O(U²)

Compute U (streaming):
  Time: O(U × I × U)
    Nhưng không lưu full U
  Space: O(U × k)
    k = số neighbors

→ Streaming mode tiết kiệm RAM đáng kể
```

### 7.2. Caching Strategy

```python
# 3 layers of caching:

1. Artifact Cache (Disk)
   - TF-IDF matrix: Load once at startup
   - CF neighbors: Reload khi có update
   - TTL: Unlimited (manual rebuild)

2. Result Cache (Redis/Memory)
   - User home recommendations: 2 minutes
   - Similar courses: 10 minutes
   - Popular courses: 1 hour

3. Database Connection Pool
   - Reuse connections
   - Batch queries when possible
```

### 7.3. Scalability

**Current Capacity:**
- Courses: ~250-1000 ✓
- Users: ~1000-5000 ✓
- Daily interactions: ~5000-10000 ✓

**Scale to Medium (10K users, 5K courses):**
- Use streaming mode for CF ✓
- Increase CF update interval (15-30 min) ✓
- Cache more aggressively ✓

**Scale to Large (100K+ users):**
- Consider item-based CF instead of user-based
- Implement incremental updates
- Distribute computation (Spark/Dask)
- Use approximate algorithms (LSH, ANNOY)

---

## 8. Monitoring & Debugging

### 8.1. Health Checks

```python
# Check CB artifacts
def check_cb_health():
    try:
        vec, X, row_map = load_tfidf()
        course_count = _course_count()
        return {
            "status": "OK",
            "n_courses": X.shape[0],
            "n_features": X.shape[1],
            "db_courses": course_count,
            "in_sync": X.shape[0] == course_count
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

# Check CF artifacts
def check_cf_health():
    try:
        neighbors = load_user_neighbors_json()
        meta = load_cf_meta()
        return {
            "status": "OK",
            "users_with_neighbors": len(neighbors),
            "last_build": meta.get("last_build_ts"),
            "mode": meta.get("mode")
        }
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}
```

### 8.2. Common Issues

#### Issue 1: CB recommendations all same
```
Symptom: Mọi user đều được gợi ý giống nhau

Root cause:
  - User vector quá sparse (ít tương tác)
  - Hoặc vocabulary không đủ diverse

Solution:
  - Giảm MIN_SIM_CB
  - Tăng CB_USER_MAX_ITEMS
  - Kết hợp nhiều CF hơn (giảm ALPHA)
```

#### Issue 2: CF neighbors not updating
```
Symptom: Celery task chạy nhưng neighbors không đổi

Root cause:
  - File lock bị stuck
  - last_build_ts không được update

Solution:
  - Xóa cf_build.lock
  - Rebuild manual: ensure_cf_artifacts(force=True)
  - Check Celery logs
```

#### Issue 3: Slow recommendations
```
Symptom: API response > 1s

Root cause:
  - TF-IDF matrix quá lớn
  - Không cache results

Solution:
  - Giảm MAX_FEATURES
  - Cache recommendations
  - Pre-compute popular users
```

---

## 9. Future Enhancements

### 9.1. Short-term (1-3 months)

1. **Real-time CF updates**
   - Stream processing với Kafka/Redis
   - Incremental neighbor updates
   - Không cần rebuild full

2. **Better cold start**
   - Explicit user preferences
   - Onboarding questionnaire
   - Popular by category

3. **A/B Testing framework**
   - Test different α values
   - Track click-through rates
   - Optimize parameters

### 9.2. Medium-term (3-6 months)

1. **Deep Learning models**
   - Neural Collaborative Filtering
   - Sequence models (RNN/Transformer)
   - Multi-task learning

2. **Context-aware recommendations**
   - Time of day
   - Device type
   - Learning path

3. **Explainability**
   - "Because you learned X"
   - "Students like you also took Y"
   - Show similarity reasons

### 9.3. Long-term (6-12 months)

1. **Multi-modal learning**
   - Course videos/images
   - Instructor profiles
   - Student demographics

2. **Reinforcement Learning**
   - Multi-armed bandits
   - Exploration vs exploitation
   - Online learning

3. **Federated Learning**
   - Privacy-preserving
   - Cross-platform data
   - Decentralized training

---

## 10. API Documentation

### 10.1. Endpoints

#### GET `/recommendations/home`
```json
Request:
  Headers: Authorization: Bearer <token>

Response:
  {
    "recommendations": [
      {
        "course_id": 123,
        "score": 0.775,
        "reason": "hybrid"
      },
      ...
    ],
    "total": 20
  }
```

#### GET `/recommendations/similar/{course_id}`
```json
Request:
  Path: course_id (int)
  Query: limit=10

Response:
  {
    "similar_courses": [
      {
        "course_id": 456,
        "similarity": 0.85,
        "method": "content-based"
      },
      ...
    ]
  }
```

### 10.2. Admin Commands

```bash
# Rebuild CB artifacts (TF-IDF)
python manage.py reco_init --mode=cb --force

# Rebuild CF artifacts (Neighbors)
python manage.py reco_init --mode=cf --force --streaming

# Check system health
python manage.py reco_health

# Manual trigger CF update
python manage.py reco_cf_update
```

---

## 11. References

### 11.1. Papers & Books

1. **Collaborative Filtering:**
   - "Collaborative Filtering Recommender Systems" - Ricci et al.
   - "Item-Based Collaborative Filtering" - Sarwar et al., 2001

2. **Content-Based:**
   - "Content-Based Recommendation Systems" - Pazzani & Billsus, 2007
   - TF-IDF: "A Statistical Interpretation of Term Specificity" - Sparck Jones, 1972

3. **Hybrid Systems:**
   - "Hybrid Recommender Systems: Survey and Experiments" - Burke, 2002
   - "The Netflix Prize" - Bennett & Lanning, 2007

### 11.2. Libraries Used

- **scikit-learn**: TF-IDF, normalization
- **scipy**: Sparse matrices
- **numpy**: Numerical computations
- **Django**: Web framework
- **Celery**: Async task queue
- **Redis**: Caching

---

## Tóm tắt

Hệ thống gợi ý của Xpervia LMS là một **hybrid recommender** kết hợp:

1. **Content-Based (CB)**: TF-IDF vectors của khóa học, user profile từ lịch sử tương tác
2. **Collaborative Filtering (CF)**: User-based CF với shrinkage và streaming mode
3. **Hybrid Blending**: Weighted combination (α=0.7 cho CB)

**Ưu điểm:**
- ✅ Scalable với streaming CF
- ✅ Tự động cập nhật (Celery tasks)
- ✅ Cold start handling (Popular fallback)
- ✅ Fast inference với sparse matrices
- ✅ Thread-safe với file locking

**Giới hạn hiện tại:**
- ⚠️ CF rebuild không real-time (10 phút)
- ⚠️ Cold start users có ít recommendations
- ⚠️ Chưa exploit temporal patterns
- ⚠️ Chưa có explainability

**Khuyến nghị:**
- Theo dõi CF update frequency
- A/B test α parameter
- Collect implicit feedback (clicks, time spent)
- Implement diversity metrics

---

**Tài liệu được tạo:** 29/11/2025  
**Phiên bản:** 1.0  
**Tác giả:** Xpervia Development Team
