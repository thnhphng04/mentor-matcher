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
Mentor and student CSVs are parsed into structured records. The JSON schedule columns (`capacity`, `learning_slot`) become time windows and slots the matcher can compare. Uploading new files replaces the dataset; if Supabase is connected, it's saved to the `dataset_rows` table so it survives a redeploy.

### Layer 2 · LLM enrichment
Students and mentors describe themselves in free text, mixed Vietnamese/English (e.g. "muốn mentor kiên nhẫn", "good at exam prep"). A one-time **OpenAI** pass reads that text and converts it into a small set of structured tags:
- **Student tags:** requested mentor gender, desired focus areas, desired traits, symptom category.
- **Mentor tags:** personality tags, offered focus areas, the kind of student they prefer.

Tags are cached (Supabase or local disk), so this only runs once per row. After that, matching is **fully deterministic** — it just compares tags, with no LLM calls during the matching itself. A row that hasn't been enriched yet has empty tags and scores 0 until you enrich it.

**Why a closed vocabulary?** The LLM isn't free to phrase things however it wants — every tag field is restricted (via OpenAI Structured Outputs) to one of a fixed list of words. That's what lets the scoring step compare tags exactly, like comparing two checklists, instead of trying to interpret loose text:

- **Focus areas** (12 tags, used for `desired_focus` / `offered_focus` / a mentor's `preferred_student.needs`): `emotional-support, time-management, study-habits, life-skills, accountability, motivation, exam-prep, confidence, communication, focus-attention, career-orientation, stress-management`.
- **Personality traits** (10 tags, used for `desired_traits` / `personality_tags`): `friendly, patient, structured, motivating, empathetic, disciplined, encouraging, detail-oriented, calm, energetic`.
- **Symptom categories** (10 tags, `symptom_category`): `anxiety, procrastination, low-motivation, distraction, low-confidence, social-difficulty, academic-pressure, emotional-difficulty, behavioral, none`.
- **Requested mentor gender**: `Male`, `Female`, or not stated.

### Layer 3 · Matching algorithm

**Step 1 — who's even allowed to match?** For every student–mentor pair, check two hard rules:
1. **Gender** — if the parent asked for a specific mentor gender, the mentor must have that gender. If they didn't ask, gender doesn't matter.
2. **Time** — at least one of the student's desired time slots must fit inside one of the mentor's open windows, with enough room left for one session (`session_length` minutes).

Only pairs that pass both rules are *feasible* — the rest of the algorithm only ever looks at feasible pairs.

**Step 2 — score each feasible pair (used by Q2/Q3).** Every feasible pair gets a score from 0 to 1, built from up to four ingredients:

| Ingredient | What it measures | Turned on by |
|---|---|---|
| `focus_overlap` | How much the student's desired focus areas overlap with what the mentor offers | Q2 |
| `trait_match` | How much the student's desired personality traits overlap with the mentor's | Q2 |
| `symptom_fit` | Whether the mentor covers the focus areas that help with the student's symptom | Q3 |
| `mentor_pref` | Whether the student matches what the mentor says they prefer in a student | Q3 |

Overlap is measured with **Jaccard similarity**: (tags both sides have in common) ÷ (total distinct tags across both sides). The final score is a weighted average of whichever ingredients are turned on: `score = Σ(ingredient × weight) / Σ weight`. The weight sliders live in each question's tab — **Q2** sets focus/trait, **Q3** adds symptom/mentor-pref on top. **Q1** leaves every weight at 0, so it scores purely on feasibility.

**Step 3 — how many students can a mentor take?** A mentor's capacity is the number of non-overlapping session slots that fit across their open windows, capped by `max_students_per_mentor`. Each match books a concrete day + start-time slot, so two students can never collide on the same mentor.

**Step 4 — pick the actual pairs.** Two engines, chosen per question:
- **Greedy (baseline).** Sort all feasible pairs by score, best first, and walk the list taking each pair as long as both sides are still free. Simple and easy to explain, but short-sighted — it can hand a mentor to the wrong student early on and leave another student with no options left at all.
- **Optimal (recommended).** Treats matching as a flow problem (`source → student → mentor → sink`, with edge cost = −score) and solves it with **min-cost max-flow** (`networkx.max_flow_min_cost`). It first finds the matching that assigns the *most* students possible (maximizes coverage), and only among those, picks the one with the *highest total score*. This is what avoids the greedy trap.

**Step 5 — repair pass.** A booking conflict can still drop a student after the engine has run. Any dropped student gets one more try on their next-best feasible mentor that still has room — this is what pushes coverage close to 100%.

**What each question adds.**

| Question | Adds |
|---|---|
| **Q1 · Feasible matching** | Hard constraints only. Reports who's unassigned and why. |
| **Q2 · Parent expectations** | Turns on focus/trait scoring. Compared against a random-but-feasible baseline to show the improvement. |
| **Q3 · Two-way fit** | Also turns on symptom-fit and mentor-preference. Weak matches (below a **poor-fit threshold**) go into a review queue instead of being silently accepted. |
| **Q4 · Rejection & re-match** | Simulates real-world drop-out — see below. |

**Q4, step by step:**
1. Run the Q3 optimal match.
2. Each matched student independently "rejects" with probability `p` (default 20%, seeded so the result is reproducible).
3. Students who didn't reject keep their mentor (pinned).
4. Each rejecting student is barred from going back to their old mentor.
5. The rejected students are re-matched against whatever capacity is left.
6. The app reports score and coverage **before vs. after**, so you can see the impact of rejection.

### Manual overrides (human-in-the-loop)
Set in the sidebar, applied *before* the engine runs:
- **Force** — pre-book a specific student → mentor pair (uses up that mentor's capacity).
- **Block** — forbid one specific pair from ever being matched.
- **Skip** — remove a student or mentor from the pool entirely for this run.
""",
    "vi": """
## 📋 Cách hoạt động — các tầng xử lý

### Tầng 1 · Tải dữ liệu
File CSV của mentor và học sinh được đọc và chuyển thành dữ liệu có cấu trúc. Các cột lịch dạng JSON (`capacity`, `learning_slot`) được chuyển thành khung giờ rảnh / khe giờ mong muốn để hệ thống so sánh được. Khi tải file mới lên, dữ liệu cũ sẽ bị thay thế; nếu đã kết nối Supabase, dữ liệu mới được lưu vào bảng `dataset_rows` nên không bị mất khi deploy lại.

### Tầng 2 · Làm giàu dữ liệu bằng LLM
Học sinh và mentor mô tả bản thân bằng văn bản tự do, lẫn lộn tiếng Việt và tiếng Anh (ví dụ "muốn mentor kiên nhẫn", "good at exam prep"...). Một lượt gọi **OpenAI** (chạy **một lần duy nhất** cho mỗi dòng) sẽ đọc đoạn văn bản đó và rút ra một bộ nhãn có cấu trúc:
- **Nhãn của học sinh:** giới tính mentor mong muốn, lĩnh vực muốn được hỗ trợ, tính cách mong muốn ở mentor, nhóm triệu chứng.
- **Nhãn của mentor:** tính cách của mentor, lĩnh vực mentor có thể hỗ trợ, kiểu học sinh mentor thích.

Nhãn được lưu lại (Supabase hoặc ổ đĩa cục bộ) nên chỉ cần làm giàu một lần. Sau bước này, việc ghép cặp **hoàn toàn tất định** — chỉ so sánh nhãn với nhau, không gọi LLM trong lúc ghép. Dòng nào chưa được làm giàu thì nhãn sẽ để trống và điểm là 0 cho tới khi bạn chạy enrichment.

**Vì sao cần một bộ từ vựng cố định?** LLM không được tự do diễn đạt — mỗi trường nhãn bị giới hạn (bằng OpenAI Structured Outputs) chỉ trong một danh sách từ cố định. Nhờ vậy bước chấm điểm có thể so sánh nhãn với nhau như so hai danh sách checklist, thay vì phải "hiểu" văn bản tự do:

- **Lĩnh vực hỗ trợ** (12 nhãn, dùng cho `desired_focus` / `offered_focus` / `preferred_student.needs` của mentor): `emotional-support, time-management, study-habits, life-skills, accountability, motivation, exam-prep, confidence, communication, focus-attention, career-orientation, stress-management`.
- **Tính cách** (10 nhãn, dùng cho `desired_traits` / `personality_tags`): `friendly, patient, structured, motivating, empathetic, disciplined, encouraging, detail-oriented, calm, energetic`.
- **Nhóm triệu chứng** (10 nhãn, `symptom_category`): `anxiety, procrastination, low-motivation, distraction, low-confidence, social-difficulty, academic-pressure, emotional-difficulty, behavioral, none`.
- **Giới tính mentor mong muốn**: `Male`, `Female`, hoặc không nêu rõ.

### Tầng 3 · Thuật toán ghép cặp

**Bước 1 — cặp nào được phép ghép?** Với mỗi cặp học sinh–mentor, hệ thống kiểm tra 2 ràng buộc cứng:
1. **Giới tính** — nếu phụ huynh có yêu cầu giới tính mentor cụ thể, mentor phải đúng giới tính đó. Nếu không yêu cầu, giới tính không quan trọng.
2. **Thời gian** — ít nhất một khe giờ học sinh mong muốn phải nằm trong một khung giờ rảnh của mentor, và phải còn đủ thời lượng cho một buổi học (`session_length` phút).

Chỉ những cặp thỏa cả hai điều kiện mới được coi là *khả thi* — các bước tiếp theo chỉ xét những cặp khả thi này.

**Bước 2 — chấm điểm từng cặp khả thi (dùng ở Q2/Q3).** Mỗi cặp khả thi nhận một điểm số từ 0 đến 1, tính từ tối đa 4 thành phần:

| Thành phần | Đo điều gì | Được bật ở |
|---|---|---|
| `focus_overlap` | Lĩnh vực học sinh muốn trùng với lĩnh vực mentor hỗ trợ đến mức nào | Q2 |
| `trait_match` | Tính cách học sinh muốn trùng với tính cách mentor có đến mức nào | Q2 |
| `symptom_fit` | Mentor có hỗ trợ đúng lĩnh vực mà triệu chứng của học sinh cần hay không | Q3 |
| `mentor_pref` | Học sinh có đúng kiểu mà mentor mong muốn hay không | Q3 |

Mức độ trùng lặp được đo bằng **Jaccard**: (số nhãn cả hai bên cùng có) ÷ (tổng số nhãn khác nhau ở cả hai bên). Điểm cuối cùng là trung bình có trọng số của các thành phần đang bật: `score = Σ(thành_phần × trọng_số) / Σ trọng_số`. Các thanh trượt trọng số nằm trong từng tab câu hỏi — **Q2** đặt trọng số cho focus/trait, **Q3** bật thêm symptom/mentor-pref. **Q1** để mọi trọng số = 0, nên chỉ xét tính khả thi.

**Bước 3 — một mentor nhận được bao nhiêu học sinh?** Sức chứa của một mentor là số khối buổi học không trùng giờ nhau vừa với các khung rảnh của họ, giới hạn thêm bởi `max_students_per_mentor`. Mỗi lượt ghép sẽ "đặt chỗ" một khối ngày + giờ bắt đầu cụ thể, để hai học sinh không bao giờ trùng giờ trên cùng một mentor.

**Bước 4 — chọn cặp ghép thật sự.** Có hai thuật toán, chọn theo từng câu hỏi:
- **Greedy (tham lam — mốc cơ sở).** Sắp xếp mọi cặp khả thi theo điểm từ cao xuống thấp, rồi duyệt qua và ghép ngay nếu cả hai bên còn trống. Đơn giản, dễ giải thích, nhưng thiếu tầm nhìn xa: có thể ghép nhầm một mentor cho học sinh đến trước, khiến một học sinh khác sau đó không còn lựa chọn nào.
- **Optimal (tối ưu — khuyến nghị).** Coi bài toán ghép cặp như một bài toán luồng (`nguồn → học sinh → mentor → đích`, với chi phí mỗi cạnh = −điểm số) và giải bằng thuật toán **luồng cực đại – chi phí nhỏ nhất** (`networkx.max_flow_min_cost`). Thuật toán này trước tiên tìm cách ghép được **nhiều học sinh nhất có thể** (tối đa độ phủ), sau đó trong các phương án ghép nhiều nhất đó mới chọn ra phương án có **tổng điểm cao nhất**. Đây là cách tránh được nhược điểm của greedy.

**Bước 5 — bước sửa chữa (repair pass).** Việc trùng giờ đặt chỗ vẫn có thể khiến một học sinh bị loại sau khi thuật toán đã chạy xong. Học sinh bị loại sẽ được thử lại một lần nữa với mentor khả thi tốt nhất tiếp theo còn chỗ trống — đây là lý do độ phủ (coverage) thường gần đạt 100%.

**Mỗi câu hỏi bổ sung gì.**

| Câu hỏi | Bổ sung |
|---|---|
| **Q1 · Ghép khả thi** | Chỉ xét ràng buộc cứng. Báo cáo ai chưa được ghép và vì sao. |
| **Q2 · Kỳ vọng phụ huynh** | Bật chấm điểm focus/trait. So sánh với một mốc ghép ngẫu nhiên (nhưng vẫn khả thi) để thấy mức cải thiện. |
| **Q3 · Phù hợp hai chiều** | Bật thêm symptom-fit và mentor-preference. Cặp ghép yếu (dưới **ngưỡng kém phù hợp**) sẽ vào hàng chờ duyệt thay vì được chấp nhận âm thầm. |
| **Q4 · Từ chối & ghép lại** | Mô phỏng việc học sinh từ chối ngoài thực tế — xem bên dưới. |

**Q4, từng bước:**
1. Chạy ghép tối ưu của Q3.
2. Mỗi học sinh đã ghép sẽ "từ chối" độc lập với xác suất `p` (mặc định 20%, có hạt giống ngẫu nhiên để kết quả lặp lại được).
3. Học sinh không từ chối được giữ nguyên (ghim) với mentor của mình.
4. Học sinh từ chối sẽ không được ghép lại với mentor cũ.
5. Nhóm học sinh từ chối được ghép lại dựa trên phần sức chứa còn lại.
6. Ứng dụng báo cáo điểm số và độ phủ **trước và sau** để thấy rõ tác động của việc từ chối.

### Ghi đè thủ công (con người tham gia vào quy trình)
Thiết lập ở thanh bên, áp dụng *trước khi* thuật toán chạy:
- **Force (bắt buộc)** — đặt trước một cặp học sinh → mentor cụ thể (chiếm luôn một suất sức chứa của mentor đó).
- **Block (cấm)** — không bao giờ cho phép một cặp cụ thể được ghép với nhau.
- **Skip (bỏ qua)** — loại hẳn một học sinh hoặc mentor ra khỏi danh sách cho lượt chạy này.
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
