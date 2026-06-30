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
        "tab_questions": "❓ Questions",
        "tab_enrichment": "🤖 Enrichment",
        "raw_data": "Raw data",
        "enriched_tags": "Enriched tags",
        "auto_enriching": "Enriching {kind}… {d}/{n}",
        "auto_enriched_done": "Uploaded & auto-enriched — saved to {backend}.",
        "upload_no_key_warn": "Data uploaded but not enriched (no OPENAI_API_KEY). "
                              "Set the key and re-upload.",
        "auto_enrich_on": "✓ New uploads are auto-enriched and saved to {backend}.",
        "auto_enrich_off": "⚠️ No OPENAI_API_KEY — uploads will load unenriched (Q2/Q3 score 0).",
        # --- matching progress (Q1-Q4 Run buttons) ---
        "stage_feasibility": "Building feasible pairs (gender + time constraints)…",
        "stage_scoring": "Scoring feasible pairs…",
        "stage_engine": "Running the **{engine}** engine…",
        "stage_engine_optimal_hint": "(min-cost max-flow — can take up to ~30s on the full dataset)",
        "stage_booking": "Booking sessions…",
        "stage_repair": "Repair pass — re-trying dropped students…",
        "stage_done": "Done.",
        "stage_initial": "Initial match (Q3) — {inner}",
        "stage_final": "Re-matching rejected students — {inner}",
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
        "q1_settings_caption": "Using Q1 settings — session length: {session}min, max capacity: {cap}.",
        "q4_inherits": "Inherits Q2 weights (focus: {focus}, trait: {trait}) and Q3 weights "
                       "(symptom: {symptom}, mentor_pref: {pref}) — set in their tabs.",
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
        "tab_questions": "❓ Câu hỏi",
        "tab_enrichment": "🤖 Làm giàu (LLM)",
        "raw_data": "Dữ liệu gốc",
        "enriched_tags": "Nhãn đã làm giàu",
        "auto_enriching": "Đang làm giàu {kind}… {d}/{n}",
        "auto_enriched_done": "Đã tải lên & tự động làm giàu — lưu vào {backend}.",
        "upload_no_key_warn": "Đã tải dữ liệu nhưng chưa làm giàu (thiếu OPENAI_API_KEY). "
                              "Hãy đặt khóa và tải lại.",
        "auto_enrich_on": "✓ Dữ liệu tải lên sẽ được tự động làm giàu và lưu vào {backend}.",
        "auto_enrich_off": "⚠️ Thiếu OPENAI_API_KEY — dữ liệu tải lên chưa được làm giàu (Q2/Q3 = 0 điểm).",
        # --- tiến trình ghép cặp (nút Run ở Q1-Q4) ---
        "stage_feasibility": "Đang xây dựng các cặp khả thi (ràng buộc giới tính + thời gian)…",
        "stage_scoring": "Đang chấm điểm các cặp khả thi…",
        "stage_engine": "Đang chạy thuật toán **{engine}**…",
        "stage_engine_optimal_hint": "(luồng chi phí nhỏ nhất — có thể mất tới ~30 giây với toàn bộ dữ liệu)",
        "stage_booking": "Đang đặt lịch buổi học…",
        "stage_repair": "Bước sửa chữa — đang thử ghép lại học sinh bị loại…",
        "stage_done": "Hoàn tất.",
        "stage_initial": "Ghép ban đầu (Q3) — {inner}",
        "stage_final": "Đang ghép lại học sinh bị từ chối — {inner}",
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
        "q1_settings_caption": "Dùng cài đặt của Q1 — thời lượng buổi: {session} phút, sức chứa tối đa: {cap}.",
        "q4_inherits": "Kế thừa trọng số Q2 (lĩnh vực: {focus}, tính cách: {trait}) và Q3 "
                       "(triệu chứng: {symptom}, mentor_pref: {pref}) — đặt ở các tab đó.",
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

### 1. Prepare data — 📁 Data & Enrichment tab
- View the current students/mentors tables — **Raw data** and **Enriched tags** are shown in separate sections.
- Upload replacement CSVs (same columns) — this replaces the dataset and **automatically runs LLM enrichment on every uploaded row**, saving the new tags. (Needs an OpenAI API key; without one, the data loads unenriched and Q2/Q3 score 0 until it's enriched.)

### 2. Run the questions — tabs Q1 → Q4
Each tab has its own controls and a **Run** button:
- **Q1 — Feasible:** set session length, capacity, gender, engine → match on hard constraints. See who's unassigned and **why**.
- **Q2 — Parent expectations:** set focus/trait weights → score by what the parent/student asked for, compared to a random baseline.
- **Q3 — Two-way fit:** set symptom/mentor-preference weights (builds on Q2) → two-sided score + a **review queue** of weak matches.
- **Q4 — Rejection & re-match:** set rejection probability → simulate ~20% rejecting and re-match; see score before/after.

### 3. Manual overrides — left sidebar
- **Force pair:** pin a student to a mentor. **Block pair:** forbid a pairing. **Skip:** remove someone from the pool.
- Pick people **by name** (searchable), click **Add pair**. Overrides apply on the next **Run**.

### Tip
Q1 always works, even on unenriched data. If Q2/Q3 show a score of 0, the data hasn't been enriched yet — re-upload the same CSVs in the **Data & Enrichment** tab to trigger enrichment.
""",
    "vi": """
## 📖 Cách sử dụng ứng dụng

Ứng dụng ghép **học sinh với mentor**. Làm theo thứ tự từ trên xuống; mỗi câu hỏi (Q1–Q4) chỉ chạy khi bạn bấm nút **Run** của nó.

### 1. Chuẩn bị dữ liệu — tab 📁 Dữ liệu & Làm giàu
- Xem bảng học sinh/mentor — **Dữ liệu gốc** và **Nhãn đã làm giàu** được hiển thị ở hai khu vực riêng.
- Tải lên CSV thay thế (cùng cột) — thao tác này thay thế bộ dữ liệu và **tự động chạy làm giàu bằng LLM cho mọi dòng vừa tải lên**, rồi lưu nhãn mới. (Cần có khóa API OpenAI; nếu không có, dữ liệu sẽ tải lên ở trạng thái chưa làm giàu và Q2/Q3 cho điểm 0 cho tới khi được làm giàu.)

### 2. Chạy các câu hỏi — tab Q1 → Q4
Mỗi tab có điều khiển riêng và một nút **Run**:
- **Q1 — Khả thi:** đặt thời lượng buổi, sức chứa, giới tính, thuật toán → ghép theo ràng buộc cứng. Xem ai chưa được ghép và **lý do**.
- **Q2 — Kỳ vọng phụ huynh:** đặt trọng số lĩnh vực/tính cách → chấm điểm theo mong muốn của phụ huynh/học sinh, so với mốc ngẫu nhiên.
- **Q3 — Phù hợp hai chiều:** đặt trọng số triệu chứng/mong muốn của mentor (cộng dồn Q2) → điểm hai chiều + **hàng chờ duyệt** các cặp kém phù hợp.
- **Q4 — Từ chối & ghép lại:** đặt xác suất từ chối → mô phỏng ~20% từ chối và ghép lại; xem điểm trước/sau.

### 3. Ghi đè thủ công — thanh bên trái
- **Cặp bắt buộc:** ghim một học sinh với một mentor. **Cặp cấm:** cấm một cặp. **Bỏ qua:** loại một người khỏi danh sách.
- Chọn người **theo tên** (tìm kiếm được), bấm **Thêm cặp**. Ghi đè áp dụng ở lần **Run** kế tiếp.

### Lưu ý
Q1 luôn chạy được, kể cả với dữ liệu chưa làm giàu. Nếu Q2/Q3 hiện điểm 0, nghĩa là dữ liệu chưa được làm giàu — hãy tải lại đúng các file CSV đó trong tab **Dữ liệu & Làm giàu** để kích hoạt làm giàu.
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

All four questions share the same three building blocks, then each question turns on a different combination of them — that's the whole "tunable" idea.

- **Feasible pairs.** For every student–mentor pair, check two hard rules: (1) **gender** — if the parent asked for a specific mentor gender, the mentor must have it, otherwise gender doesn't matter; (2) **time** — at least one of the student's desired time slots must fit inside one of the mentor's open windows, with room for one `session_length`-minute session. Only pairs that pass both are *feasible* — every question below only ever matches within this feasible set.
- **Capacity & booking.** A mentor's capacity is the number of non-overlapping session slots that fit across their open windows, capped by `max_students_per_mentor`. Each match books a concrete day + start-time slot, so two students never collide on the same mentor.
- **Two engines.** *Greedy* sorts feasible pairs by score (best first) and takes each pair while both sides are still free — simple, but it can strand a student whose only good mentor was already taken. *Optimal* (recommended) models matching as a min-cost max-flow problem (`source → student → mentor → sink`, edge cost = −score) and solves it with `networkx.max_flow_min_cost`: it first maximizes *how many* students get matched, then — among all such maximal matchings — maximizes the *total score*. After either engine runs, a **repair pass** retries any student dropped by a booking conflict on their next-best feasible mentor with room, pushing coverage close to 100%.

---

**Q1 · Feasible matching.** Build the feasible pairs above; every scoring weight is 0 (this question is feasibility-only, no preferences considered yet). Run the chosen engine plus the repair pass. Output: who's assigned, who's unassigned, and *why* (gender mismatch, no overlapping time slot, or the mentor was already at capacity).

**Q2 · Parent/student expectations.** Same feasible pairs and engine as Q1, but now every pair gets a real score instead of 0:

`score = (focus_overlap × w_focus + trait_match × w_trait) / (w_focus + w_trait)`

- `focus_overlap` — Jaccard overlap of the student's `desired_focus` and the mentor's `offered_focus`.
- `trait_match` — Jaccard overlap of the student's `desired_traits` and the mentor's `personality_tags`.

The engine now optimizes for this score instead of running blind. Reported against a **random feasible baseline** (same feasible pairs and engine, but edges shuffled instead of scored) to show the real lift from using expectations.

**Q3 · Two-way fit.** Builds on Q2 — keeps its focus/trait weights — and turns on two more ingredients:
- `symptom_fit` — does the mentor cover the focus areas that would help the student's `symptom_category` (via a fixed symptom → focus-area map, e.g. *procrastination → time-management, accountability*)?
- `mentor_pref` — does the student's `desired_focus` satisfy what the mentor says they want in `preferred_student.needs`?

All four ingredients blend into one weighted score (`score = Σ(ingredient × weight) / Σ weight`). Any assigned pair whose score falls below the **poor-fit threshold** is pulled into a review queue — still matched (coverage stays high), but flagged for a human to double-check.

**Q4 · Rejection & re-match.** Builds on Q3 — runs the Q3 optimal match first, then simulates real-world drop-out:
1. Each matched student independently "rejects" with probability `p` (default 20%, seeded by `random_seed` so the result is reproducible).
2. Students who didn't reject are pinned to their mentor — kept exactly as-is.
3. Each rejecting student is barred from going back to their old mentor.
4. The rejected students are re-matched — same Q3 scoring, same optimal engine — against whatever capacity is left.
5. The app reports mean score and coverage **before vs. after**, so you can see exactly how much rejection hurts match quality and how much the re-match recovers.

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

Cả 4 câu hỏi dùng chung 3 "khối nền" bên dưới, và mỗi câu hỏi chỉ bật thêm một số thành phần khác nhau trên nền chung đó — đây chính là điều giúp công cụ "tinh chỉnh được".

- **Cặp khả thi.** Với mỗi cặp học sinh–mentor, kiểm tra 2 ràng buộc cứng: (1) **giới tính** — nếu phụ huynh có yêu cầu giới tính mentor cụ thể, mentor phải đúng giới tính đó, nếu không thì giới tính không quan trọng; (2) **thời gian** — ít nhất một khe giờ học sinh mong muốn phải nằm trong một khung giờ rảnh của mentor, đủ thời lượng cho một buổi `session_length` phút. Chỉ những cặp thỏa cả hai mới là *khả thi* — mọi câu hỏi bên dưới chỉ ghép trong tập cặp khả thi này.
- **Sức chứa & đặt lịch.** Sức chứa của một mentor là số khối buổi học không trùng giờ nhau vừa với các khung rảnh của họ, giới hạn thêm bởi `max_students_per_mentor`. Mỗi lượt ghép sẽ "đặt chỗ" một khối ngày + giờ bắt đầu cụ thể, để hai học sinh không bao giờ trùng giờ trên cùng một mentor.
- **Hai thuật toán ghép.** *Greedy (tham lam)* sắp xếp các cặp khả thi theo điểm từ cao xuống thấp và ghép ngay nếu cả hai bên còn trống — đơn giản, nhưng có thể bỏ rơi một học sinh mà mentor phù hợp duy nhất đã bị lấy mất. *Optimal (tối ưu — khuyến nghị)* coi bài toán ghép như bài toán luồng chi phí nhỏ nhất (`nguồn → học sinh → mentor → đích`, chi phí mỗi cạnh = −điểm số) và giải bằng `networkx.max_flow_min_cost`: trước tiên tối đa *số học sinh* được ghép, sau đó — trong các phương án ghép nhiều nhất đó — mới tối đa *tổng điểm*. Sau khi thuật toán nào chạy xong, một **bước sửa chữa (repair pass)** sẽ thử ghép lại học sinh bị loại do trùng giờ đặt chỗ với mentor khả thi tốt tiếp theo còn chỗ, giúp độ phủ thường gần đạt 100%.

---

**Q1 · Ghép khả thi.** Xây dựng tập cặp khả thi như trên; mọi trọng số chấm điểm đều bằng 0 (câu hỏi này chỉ xét tính khả thi, chưa xét sở thích nào cả). Chạy thuật toán đã chọn cùng bước sửa chữa. Kết quả: ai được ghép, ai chưa được ghép, và *vì sao* (sai giới tính, không trùng khe giờ nào, hoặc mentor đã hết chỗ).

**Q2 · Kỳ vọng của phụ huynh/học sinh.** Dùng lại tập cặp khả thi và thuật toán của Q1, nhưng giờ mỗi cặp có điểm số thật thay vì 0:

`score = (focus_overlap × w_focus + trait_match × w_trait) / (w_focus + w_trait)`

- `focus_overlap` — độ trùng Jaccard giữa `desired_focus` của học sinh và `offered_focus` của mentor.
- `trait_match` — độ trùng Jaccard giữa `desired_traits` của học sinh và `personality_tags` của mentor.

Thuật toán giờ tối ưu theo điểm số này thay vì chạy "mù". Kết quả được so sánh với một **mốc ghép ngẫu nhiên nhưng vẫn khả thi** (cùng tập cặp khả thi và thuật toán, nhưng cạnh được xáo trộn thay vì chấm điểm) để thấy rõ mức cải thiện thực sự nhờ dùng kỳ vọng.

**Q3 · Phù hợp hai chiều.** Xây dựng trên nền Q2 — giữ nguyên trọng số focus/trait — và bật thêm 2 thành phần:
- `symptom_fit` — mentor có hỗ trợ đúng lĩnh vực giúp ích cho nhóm triệu chứng (`symptom_category`) của học sinh hay không (qua một bảng ánh xạ triệu chứng → lĩnh vực cố định, ví dụ *trì hoãn → quản lý thời gian, tự kỷ luật*)?
- `mentor_pref` — lĩnh vực học sinh mong muốn (`desired_focus`) có đáp ứng đúng điều mentor mong muốn ở học sinh (`preferred_student.needs`) hay không?

Cả 4 thành phần được trộn thành một điểm số có trọng số (`score = Σ(thành_phần × trọng_số) / Σ trọng_số`). Bất kỳ cặp đã ghép nào có điểm dưới **ngưỡng kém phù hợp** sẽ được đưa vào hàng chờ duyệt — vẫn được ghép (độ phủ vẫn cao), nhưng được gắn cờ để con người kiểm tra lại.

**Q4 · Từ chối & ghép lại.** Xây dựng trên nền Q3 — chạy ghép tối ưu của Q3 trước, sau đó mô phỏng việc từ chối ngoài thực tế:
1. Mỗi học sinh đã ghép sẽ "từ chối" độc lập với xác suất `p` (mặc định 20%, dùng `random_seed` để kết quả lặp lại được).
2. Học sinh không từ chối được ghim nguyên trạng với mentor của mình.
3. Học sinh từ chối sẽ không được ghép lại với mentor cũ.
4. Nhóm học sinh từ chối được ghép lại — vẫn dùng cách chấm điểm của Q3, vẫn dùng thuật toán optimal — dựa trên phần sức chứa còn lại.
5. Ứng dụng báo cáo điểm trung bình và độ phủ **trước và sau**, để thấy rõ việc từ chối làm giảm chất lượng ghép cặp bao nhiêu, và việc ghép lại khôi phục được bao nhiêu.

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
