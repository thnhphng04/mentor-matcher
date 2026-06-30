"""Bilingual (English / Tiếng Việt) UI strings for the Streamlit app.

`t(key, **kwargs)` returns the string for the current language (st.session_state.lang,
default "en"), formatting in any kwargs. Missing keys fall back to English, then the
key itself — so the app never crashes on a missing translation.
"""
from __future__ import annotations

import streamlit as st

LANGS = {"en": "English", "vi": "Tiếng Việt"}

STRINGS = {
    "en": {
        # --- app shell ---
        "title": "🎯 TeenCare Mentor–Student Matcher",
        "subtitle": "Rule-driven, tunable matching · each question (Q1–Q4) runs its own method on **Run**",
        "language": "🌐 Language",
        "page": "📑 Page",
        "page_matcher": "Matcher",
        "page_instruction": "📖 Instruction",
        "page_description": "📋 Description",
        # --- overrides ---
        "overrides": "✍️ Overrides",
        "overrides_help": "Search by name to add pairs. Applied when you click Run on any question.",
        "force_pairs": "Force pairs (pin a student→mentor)",
        "block_pairs": "Block pairs (forbid a student→mentor)",
        "student": "Student",
        "mentor": "Mentor",
        "add_pair": "➕ Add pair",
        "skip_students": "Skip students",
        "skip_mentors": "Skip mentors",
        "kind_student": "student",
        "kind_mentor": "mentor",
        # --- tabs ---
        "tab_data": "📁 Data & Enrichment",
        "tab_enrichment": "🤖 Enrichment",
        "raw_data": "Raw data",
        "enriched_tags": "Enriched tags",
        "auto_enriching": "Enriching {kind}… {d}/{n}",
        "auto_enriched_done": "Uploaded & auto-enriched — saved to {backend}.",
        "upload_no_key_warn": "Data uploaded but not enriched (no OPENAI_API_KEY). "
                              "Set the key and re-upload.",
        "auto_enrich_on": "✓ New uploads are auto-enriched and saved to {backend}.",
        "auto_enrich_off": "⚠️ No OPENAI_API_KEY — uploads will load unenriched (Q2/Q3 score 0).",
        "tab_q1": "1️⃣ Q1 · Feasible",
        "tab_q2": "2️⃣ Q2 · Parent expectations",
        "tab_q3": "3️⃣ Q3 · Two-way fit",
        "tab_q4": "4️⃣ Q4 · Rejection & re-match",
        # --- data tab ---
        "m_students": "Students",
        "m_mentors": "Mentors",
        "m_active": "Active dataset",
        "upload_reset": "⬆️ Upload / reset dataset",
        "upload_help": "Upload replacement CSVs (same columns). Leave one empty to keep the current one.",
        "students_csv": "Students CSV",
        "mentors_csv": "Mentors CSV",
        "required": "Required: {cols}",
        "load_uploaded": "📥 Load uploaded data",
        "missing_cols": "Missing columns → {cols}",
        "loaded_where": "{ns} students × {nm} mentors {where}. Re-run the questions.",
        "where_supabase": "replaced in Supabase",
        "where_session": "loaded (session only — no Supabase)",
        "parse_error": "Could not parse: {err}",
        "reset_default": "♻️ Reset to default data",
        "enrich_cache": "🧠 Enrichment cache",
        "backend_line": "Backend: **{backend}** · students: {sc} · mentors: {mc}",
        "save_tags": "💾 Save tags to cache",
        "saved": "Saved.",
        "dl_students_json": "⬇ students_enriched.json",
        "dl_mentors_json": "⬇ mentors_enriched.json",
        "current_data": "👀 Current data",
        "students_n": "Students ({n})",
        "mentors_n": "Mentors ({n})",
        # --- enrichment tab ---
        "enrich_title": "🤖 LLM enrichment (OpenAI)",
        "enrich_help": "Turns the messy VI/EN text into structured tags used by Q2 and Q3. "
                       "Q1 does not need it. Tags persist to the active backend.",
        "key_loaded": "🔑 OpenAI key loaded from environment.",
        "key_missing": "No OPENAI_API_KEY found. Q1 still runs; Q2/Q3 need enrichment.",
        "backend_persist": "Persistence backend: **{backend}**",
        "model": "Model",
        "target": "Target",
        "sample_rows": "Sample rows",
        "enrich_all": "Enrich ALL {n} {kind} (slower / costlier)",
        "run_enrichment": "▶ Run enrichment",
        "calling_openai": "Calling OpenAI…",
        "enriched_progress": "Enriched {d}/{t}",
        "enriched_done": "Enriched {n} {kind} rows — saved to {backend}.",
        "enriched_failed": " ({n} stayed unenriched after retries.)",
        "rerun_q23": " Re-run Q2/Q3 to use the new tags.",
        "tags_by_source": "Tags by source — students: {sc} · mentors: {mc}",
        # --- Q1 ---
        "q1_title": "Q1 · Feasible matching (hard constraints only)",
        "q1_caption": "Assign each student to one mentor satisfying **gender + time + capacity**. "
                      "No preference scoring here.",
        "session_len": "Session length (min)",
        "max_cap": "Max students per mentor",
        "enforce_gender": "Enforce requested gender (hard)",
        "engine": "Engine",
        "run_q1": "▶ Run Q1",
        "q1_info": "Click **Run Q1** to compute the feasible matching.",
        "assignments": "✅ Assignments",
        "unassigned_why": "🚫 Unassigned (why)",
        # --- Q2 ---
        "q2_title": "Q2 · Parent / student expectations",
        "q2_caption": "Among feasible pairs, prefer mentors whose focus areas and traits match what "
                      "the parent/student asked for. Weights below serve **Q2**.",
        "q2_focus_w": "Q2 · focus-overlap weight",
        "q2_trait_w": "Q2 · trait-match weight",
        "min_acc": "Min acceptable score (metric)",
        "run_q2": "▶ Run Q2",
        "q2_info": "Click **Run Q2**. (Run enrichment first for non-zero scores.)",
        # --- Q3 ---
        "q3_title": "Q3 · Two-way fit (mentor preferences + student symptoms)",
        "q3_caption": "Extends Q2: also weighs the student's symptom needs and the mentor's own "
                      "preferred-student profile. Weights below serve **Q3** and build on Q2's weights.",
        "q3_symptom_w": "Q3 · symptom-fit weight",
        "q3_pref_w": "Q3 · mentor-preference weight",
        "poor_fit": "Poor-fit threshold (review queue)",
        "q3_inherits": "Inherits Q2 weights — focus: {focus}, trait: {trait} (set in the Q2 tab).",
        "run_q3": "▶ Run Q3",
        "review_queue": "⚠️ Review queue (poor fits)",
        "q3_info": "Click **Run Q3**. (Run enrichment first for non-zero scores.)",
        # --- Q4 ---
        "q4_title": "Q4 · Rejection & re-matching",
        "q4_caption": "Take the Q3 match, simulate students rejecting their mentor, then re-match the "
                      "rejected ones (barred from their old mentor). Parameters below serve **Q4**.",
        "reject_prob": "Rejection probability",
        "seed": "Random seed",
        "run_q4": "▶ Run Q4",
        "rejected": "Rejected",
        "mean_before": "Mean score before",
        "mean_after": "Mean score after",
        "coverage_after": "Coverage after",
        "q4_info": "Click **Run Q4**. (It uses the Q3 weights; run Q3/enrichment first.)",
        # --- metrics / tables ---
        "matched": "Matched",
        "coverage_delta": "{pct}% coverage",
        "mean_score": "Mean score",
        "vs_random": "{d} vs random",
        "median_score": "Median score",
        "pct_above": "% above acceptable",
        "review_size": "Review queue",
        "dl_assignments": "⬇ assignments.csv",
        "everyone_matched": "Everyone matched.",
        "reason": "reason",
        "count": "count",
    },
    "vi": {
        # --- app shell ---
        "title": "🎯 TeenCare · Ghép cặp Mentor–Học sinh",
        "subtitle": "Ghép cặp theo quy tắc, có thể tinh chỉnh · mỗi câu hỏi (Q1–Q4) chạy phương pháp riêng khi bấm **Run**",
        "language": "🌐 Ngôn ngữ",
        "page": "📑 Trang",
        "page_matcher": "Ghép cặp",
        "page_instruction": "📖 Hướng dẫn",
        "page_description": "📋 Mô tả",
        # --- overrides ---
        "overrides": "✍️ Ghi đè thủ công",
        "overrides_help": "Tìm theo tên để thêm cặp. Áp dụng khi bạn bấm Run ở bất kỳ câu hỏi nào.",
        "force_pairs": "Cặp bắt buộc (ghim học sinh→mentor)",
        "block_pairs": "Cặp cấm (cấm học sinh→mentor)",
        "student": "Học sinh",
        "mentor": "Mentor",
        "add_pair": "➕ Thêm cặp",
        "skip_students": "Bỏ qua học sinh",
        "skip_mentors": "Bỏ qua mentor",
        "kind_student": "học sinh",
        "kind_mentor": "mentor",
        # --- tabs ---
        "tab_data": "📁 Dữ liệu & Làm giàu",
        "tab_enrichment": "🤖 Làm giàu (LLM)",
        "raw_data": "Dữ liệu gốc",
        "enriched_tags": "Nhãn đã làm giàu",
        "auto_enriching": "Đang làm giàu {kind}… {d}/{n}",
        "auto_enriched_done": "Đã tải lên & tự động làm giàu — lưu vào {backend}.",
        "upload_no_key_warn": "Đã tải dữ liệu nhưng chưa làm giàu (thiếu OPENAI_API_KEY). "
                              "Hãy đặt khóa và tải lại.",
        "auto_enrich_on": "✓ Dữ liệu tải lên sẽ được tự động làm giàu và lưu vào {backend}.",
        "auto_enrich_off": "⚠️ Thiếu OPENAI_API_KEY — dữ liệu tải lên chưa được làm giàu (Q2/Q3 = 0 điểm).",
        "tab_q1": "1️⃣ Q1 · Khả thi",
        "tab_q2": "2️⃣ Q2 · Kỳ vọng phụ huynh",
        "tab_q3": "3️⃣ Q3 · Phù hợp hai chiều",
        "tab_q4": "4️⃣ Q4 · Từ chối & ghép lại",
        # --- data tab ---
        "m_students": "Học sinh",
        "m_mentors": "Mentor",
        "m_active": "Bộ dữ liệu hiện tại",
        "upload_reset": "⬆️ Tải lên / đặt lại dữ liệu",
        "upload_help": "Tải lên CSV thay thế (cùng cột). Để trống một ô để giữ dữ liệu hiện tại.",
        "students_csv": "CSV học sinh",
        "mentors_csv": "CSV mentor",
        "required": "Bắt buộc: {cols}",
        "load_uploaded": "📥 Tải dữ liệu đã chọn",
        "missing_cols": "Thiếu cột → {cols}",
        "loaded_where": "{ns} học sinh × {nm} mentor {where}. Hãy chạy lại các câu hỏi.",
        "where_supabase": "đã thay thế trong Supabase",
        "where_session": "đã tải (chỉ trong phiên — không có Supabase)",
        "parse_error": "Không đọc được dữ liệu: {err}",
        "reset_default": "♻️ Đặt lại dữ liệu mặc định",
        "enrich_cache": "🧠 Bộ nhớ làm giàu",
        "backend_line": "Lưu trữ: **{backend}** · học sinh: {sc} · mentor: {mc}",
        "save_tags": "💾 Lưu nhãn vào bộ nhớ",
        "saved": "Đã lưu.",
        "dl_students_json": "⬇ students_enriched.json",
        "dl_mentors_json": "⬇ mentors_enriched.json",
        "current_data": "👀 Dữ liệu hiện tại",
        "students_n": "Học sinh ({n})",
        "mentors_n": "Mentor ({n})",
        # --- enrichment tab ---
        "enrich_title": "🤖 Làm giàu bằng LLM (OpenAI)",
        "enrich_help": "Chuyển văn bản lộn xộn (Việt/Anh) thành nhãn có cấu trúc dùng cho Q2 và Q3. "
                       "Q1 không cần. Nhãn được lưu vào kho lưu trữ.",
        "key_loaded": "🔑 Đã nạp khóa OpenAI từ môi trường.",
        "key_missing": "Không tìm thấy OPENAI_API_KEY. Q1 vẫn chạy; Q2/Q3 cần làm giàu.",
        "backend_persist": "Nơi lưu trữ: **{backend}**",
        "model": "Mô hình",
        "target": "Đối tượng",
        "sample_rows": "Số dòng mẫu",
        "enrich_all": "Làm giàu TẤT CẢ {n} {kind} (chậm / tốn hơn)",
        "run_enrichment": "▶ Chạy làm giàu",
        "calling_openai": "Đang gọi OpenAI…",
        "enriched_progress": "Đã làm giàu {d}/{t}",
        "enriched_done": "Đã làm giàu {n} dòng {kind} — lưu vào {backend}.",
        "enriched_failed": " ({n} dòng vẫn chưa làm giàu sau khi thử lại.)",
        "rerun_q23": " Chạy lại Q2/Q3 để dùng nhãn mới.",
        "tags_by_source": "Nhãn theo nguồn — học sinh: {sc} · mentor: {mc}",
        # --- Q1 ---
        "q1_title": "Q1 · Ghép cặp khả thi (chỉ ràng buộc cứng)",
        "q1_caption": "Gán mỗi học sinh cho một mentor thỏa **giới tính + thời gian + sức chứa**. "
                      "Chưa chấm điểm ưu tiên ở đây.",
        "session_len": "Thời lượng buổi (phút)",
        "max_cap": "Số học sinh tối đa mỗi mentor",
        "enforce_gender": "Bắt buộc đúng giới tính yêu cầu (cứng)",
        "engine": "Thuật toán",
        "run_q1": "▶ Chạy Q1",
        "q1_info": "Bấm **Run Q1** để tính ghép cặp khả thi.",
        "assignments": "✅ Kết quả ghép",
        "unassigned_why": "🚫 Chưa ghép (lý do)",
        # --- Q2 ---
        "q2_title": "Q2 · Kỳ vọng phụ huynh / học sinh",
        "q2_caption": "Trong các cặp khả thi, ưu tiên mentor có lĩnh vực và tính cách khớp với mong muốn "
                      "của phụ huynh/học sinh. Các trọng số bên dưới phục vụ **Q2**.",
        "q2_focus_w": "Q2 · trọng số trùng lĩnh vực",
        "q2_trait_w": "Q2 · trọng số khớp tính cách",
        "min_acc": "Điểm tối thiểu chấp nhận (chỉ số)",
        "run_q2": "▶ Chạy Q2",
        "q2_info": "Bấm **Run Q2**. (Hãy làm giàu trước để có điểm khác 0.)",
        # --- Q3 ---
        "q3_title": "Q3 · Phù hợp hai chiều (mong muốn mentor + triệu chứng học sinh)",
        "q3_caption": "Mở rộng Q2: cân nhắc thêm nhu cầu theo triệu chứng của học sinh và hồ sơ học sinh "
                      "mà mentor mong muốn. Trọng số bên dưới phục vụ **Q3** và cộng dồn với trọng số Q2.",
        "q3_symptom_w": "Q3 · trọng số phù hợp triệu chứng",
        "q3_pref_w": "Q3 · trọng số mong muốn của mentor",
        "poor_fit": "Ngưỡng kém phù hợp (hàng chờ duyệt)",
        "q3_inherits": "Kế thừa trọng số Q2 — lĩnh vực: {focus}, tính cách: {trait} (đặt ở tab Q2).",
        "run_q3": "▶ Chạy Q3",
        "review_queue": "⚠️ Hàng chờ duyệt (kém phù hợp)",
        "q3_info": "Bấm **Run Q3**. (Hãy làm giàu trước để có điểm khác 0.)",
        # --- Q4 ---
        "q4_title": "Q4 · Từ chối & ghép lại",
        "q4_caption": "Lấy kết quả Q3, mô phỏng học sinh từ chối mentor, rồi ghép lại những em bị từ chối "
                      "(cấm ghép lại mentor cũ). Tham số bên dưới phục vụ **Q4**.",
        "reject_prob": "Xác suất từ chối",
        "seed": "Hạt ngẫu nhiên",
        "run_q4": "▶ Chạy Q4",
        "rejected": "Bị từ chối",
        "mean_before": "Điểm TB trước",
        "mean_after": "Điểm TB sau",
        "coverage_after": "Độ phủ sau",
        "q4_info": "Bấm **Run Q4**. (Dùng trọng số Q3; hãy chạy Q3/làm giàu trước.)",
        # --- metrics / tables ---
        "matched": "Đã ghép",
        "coverage_delta": "{pct}% độ phủ",
        "mean_score": "Điểm trung bình",
        "vs_random": "{d} so với ngẫu nhiên",
        "median_score": "Điểm trung vị",
        "pct_above": "% trên mức chấp nhận",
        "review_size": "Hàng chờ duyệt",
        "dl_assignments": "⬇ assignments.csv",
        "everyone_matched": "Tất cả đã được ghép.",
        "reason": "lý do",
        "count": "số lượng",
    },
}

# --------------------------------------------------------------------------
# Long-form pages (Markdown) — Instruction & Description.
# --------------------------------------------------------------------------
INSTRUCTION = {
    "en": """
## 📖 How to use this app

The app matches **students to mentors**. Work top-to-bottom; each question (Q1–Q4) runs only when you press its **Run** button.

### 1. Prepare data — 📁 Data tab
- View the current students/mentors tables and counts.
- Optionally **upload** replacement CSVs (same columns) — this replaces the dataset (and saves it to Supabase if connected). **Reset** reverts to the bundled data.

### 2. Enrich the text — 🤖 Enrichment tab
- This calls OpenAI to turn the messy Vietnamese/English notes into structured **tags** used by Q2 and Q3 (**Q1 does not need it**).
- Pick a **sample size** (start small to test) or **Enrich ALL**, then **Run enrichment**. Tags are saved automatically.

### 3. Run the questions — tabs Q1 → Q4
Each tab has its own controls and a **Run** button:
- **Q1 — Feasible:** set session length, capacity, gender, engine → match on hard constraints. See who's unassigned and **why**.
- **Q2 — Parent expectations:** set focus/trait weights → score by what the parent/student asked for, compared to a random baseline.
- **Q3 — Two-way fit:** set symptom/mentor-preference weights (builds on Q2) → two-sided score + a **review queue** of weak matches.
- **Q4 — Rejection & re-match:** set rejection probability → simulate ~20% rejecting and re-match; see score before/after.

### 4. Manual overrides — left sidebar
- **Force pair:** pin a student to a mentor. **Block pair:** forbid a pairing. **Skip:** remove someone from the pool.
- Pick people **by name** (searchable), click **Add pair**. Overrides apply on the next **Run**.

### Tip
Run **Enrichment** before Q2/Q3, otherwise their scores are 0 (Q1 still works without it).
""",
    "vi": """
## 📖 Cách sử dụng ứng dụng

Ứng dụng ghép **học sinh với mentor**. Làm theo thứ tự từ trên xuống; mỗi câu hỏi (Q1–Q4) chỉ chạy khi bạn bấm nút **Run** của nó.

### 1. Chuẩn bị dữ liệu — tab 📁 Dữ liệu
- Xem bảng học sinh/mentor và số lượng hiện tại.
- Có thể **tải lên** CSV thay thế (cùng cột) — thao tác này thay thế bộ dữ liệu (và lưu vào Supabase nếu đã kết nối). **Đặt lại** để quay về dữ liệu mặc định.

### 2. Làm giàu văn bản — tab 🤖 Làm giàu
- Bước này gọi OpenAI để chuyển các ghi chú lộn xộn (Việt/Anh) thành **nhãn** có cấu trúc dùng cho Q2 và Q3 (**Q1 không cần**).
- Chọn **số dòng mẫu** (nên thử ít trước) hoặc **Làm giàu TẤT CẢ**, rồi bấm **Chạy làm giàu**. Nhãn được lưu tự động.

### 3. Chạy các câu hỏi — tab Q1 → Q4
Mỗi tab có điều khiển riêng và một nút **Run**:
- **Q1 — Khả thi:** đặt thời lượng buổi, sức chứa, giới tính, thuật toán → ghép theo ràng buộc cứng. Xem ai chưa được ghép và **lý do**.
- **Q2 — Kỳ vọng phụ huynh:** đặt trọng số lĩnh vực/tính cách → chấm điểm theo mong muốn của phụ huynh/học sinh, so với mốc ngẫu nhiên.
- **Q3 — Phù hợp hai chiều:** đặt trọng số triệu chứng/mong muốn của mentor (cộng dồn Q2) → điểm hai chiều + **hàng chờ duyệt** các cặp kém phù hợp.
- **Q4 — Từ chối & ghép lại:** đặt xác suất từ chối → mô phỏng ~20% từ chối và ghép lại; xem điểm trước/sau.

### 4. Ghi đè thủ công — thanh bên trái
- **Cặp bắt buộc:** ghim một học sinh với một mentor. **Cặp cấm:** cấm một cặp. **Bỏ qua:** loại một người khỏi danh sách.
- Chọn người **theo tên** (tìm kiếm được), bấm **Thêm cặp**. Ghi đè áp dụng ở lần **Run** kế tiếp.

### Lưu ý
Hãy chạy **Làm giàu** trước Q2/Q3, nếu không điểm của chúng sẽ bằng 0 (Q1 vẫn chạy được mà không cần).
""",
}

DESCRIPTION = {
    "en": """
## 📋 How it works — the layers

### Layer 1 · Data upload
The mentor and student CSVs are parsed: the JSON schedule columns (`capacity`, `learning_slot`) become structured time windows/slots. Uploaded data replaces the dataset and (if Supabase is connected) persists in a `dataset_rows` table.

### Layer 2 · LLM enrichment
The free-text fields are mixed Vietnamese/English. A one-time **OpenAI** pass (Structured Outputs) converts them into a **closed set of tags**:
- **Student:** requested mentor gender, desired focus areas, desired traits, symptom category.
- **Mentor:** personality tags, offered focus areas, preferred-student profile.

Tags are cached (Supabase or local). The matching then runs **deterministically** on these tags — the LLM is a preparation step, not part of the live matching loop. Rows not yet enriched stay "unenriched" (empty tags) and score 0 until you enrich them.

### Layer 3 · Algorithms inside the question tabs
All four questions share two engines that decide *who matches whom* among feasible pairs:
- **Greedy** — assigns one student at a time, best-available first. Fast; the explainable baseline.
- **Optimal** — a min-cost max-flow that solves all assignments together: maximize how many are matched, then total score. The recommended default.

Each question builds on the previous one:

| Question | Method |
|---|---|
| **Q1 · Feasible** | Hard constraints only: **gender** (parent's requested mentor gender) + **time** (a student slot fits a mentor window) + **capacity** (non-overlapping session blocks, capped). Reports unassigned + reasons. |
| **Q2 · Parent expectations** | Scores each feasible pair by overlap of the student's **desired focus/traits** with the mentor's offered focus/personality. Compared to a random baseline. |
| **Q3 · Two-way fit** | Adds the student's **symptom needs** and the mentor's **preferred-student** profile → a two-sided score. Weak pairs go to a **review queue**. |
| **Q4 · Rejection & re-match** | Simulate ~20% of students rejecting their mentor (seeded). Kept students are pinned; rejected ones are barred from their old mentor and re-matched. Reports quality before/after. |

### Manual overrides (human-in-the-loop)
Force / block / skip let a person pin a known-good pairing, forbid a bad one, or remove someone — applied before the engine runs.
""",
    "vi": """
## 📋 Cách hoạt động — các tầng

### Tầng 1 · Tải dữ liệu
CSV mentor và học sinh được phân tích: các cột lịch dạng JSON (`capacity`, `learning_slot`) trở thành khung giờ/khe giờ có cấu trúc. Dữ liệu tải lên thay thế bộ dữ liệu và (nếu kết nối Supabase) được lưu trong bảng `dataset_rows`.

### Tầng 2 · Làm giàu bằng LLM
Các trường văn bản tự do trộn lẫn tiếng Việt/Anh. Một lượt **OpenAI** (Structured Outputs) chuyển chúng thành một **tập nhãn có giới hạn**:
- **Học sinh:** giới tính mentor được yêu cầu, lĩnh vực mong muốn, tính cách mong muốn, nhóm triệu chứng.
- **Mentor:** nhãn tính cách, lĩnh vực có thể hỗ trợ, hồ sơ học sinh mong muốn.

Nhãn được lưu (Supabase hoặc cục bộ). Việc ghép cặp sau đó chạy **tất định** trên các nhãn này — LLM là bước chuẩn bị, không nằm trong vòng lặp ghép cặp. Dòng chưa làm giàu sẽ giữ trạng thái "chưa làm giàu" (nhãn rỗng) và điểm bằng 0 cho tới khi bạn làm giàu.

### Tầng 3 · Thuật toán bên trong các tab câu hỏi
Cả bốn câu hỏi dùng chung hai thuật toán quyết định *ai ghép với ai* trong các cặp khả thi:
- **Greedy (tham lam)** — gán từng học sinh một, ưu tiên lựa chọn tốt nhất còn trống. Nhanh; là mốc cơ sở dễ giải thích.
- **Optimal (tối ưu)** — luồng chi phí nhỏ nhất giải toàn bộ cùng lúc: tối đa số cặp được ghép, rồi tối đa tổng điểm. Là mặc định khuyến nghị.

Mỗi câu hỏi xây dựng trên câu trước:

| Câu hỏi | Phương pháp |
|---|---|
| **Q1 · Khả thi** | Chỉ ràng buộc cứng: **giới tính** (giới tính mentor phụ huynh yêu cầu) + **thời gian** (khe giờ học sinh nằm trong khung của mentor) + **sức chứa** (các khối buổi không trùng nhau, có giới hạn). Báo cáo ai chưa ghép + lý do. |
| **Q2 · Kỳ vọng phụ huynh** | Chấm điểm từng cặp khả thi theo mức trùng giữa **lĩnh vực/tính cách mong muốn** của học sinh với lĩnh vực/tính cách của mentor. So với mốc ngẫu nhiên. |
| **Q3 · Phù hợp hai chiều** | Thêm **nhu cầu theo triệu chứng** của học sinh và hồ sơ **học sinh mong muốn** của mentor → điểm hai chiều. Cặp kém phù hợp vào **hàng chờ duyệt**. |
| **Q4 · Từ chối & ghép lại** | Mô phỏng ~20% học sinh từ chối mentor (có hạt giống). Học sinh giữ lại được ghim; em bị từ chối bị cấm mentor cũ và được ghép lại. Báo cáo chất lượng trước/sau. |

### Ghi đè thủ công (con người trong vòng lặp)
Bắt buộc / cấm / bỏ qua cho phép con người ghim một cặp tốt đã biết, cấm một cặp xấu, hoặc loại một người — áp dụng trước khi thuật toán chạy.
""",
}


def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("lang", "en")
    s = STRINGS.get(lang, {}).get(key) or STRINGS["en"].get(key) or key
    return s.format(**kwargs) if kwargs else s


def page_md(name: str) -> str:
    lang = st.session_state.get("lang", "en")
    src = INSTRUCTION if name == "instruction" else DESCRIPTION
    return src.get(lang, src["en"])
