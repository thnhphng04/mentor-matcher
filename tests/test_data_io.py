import pandas as pd

from matcher.data_io import (MENTOR_COLUMNS, STUDENT_COLUMNS, mentors_from_df,
                             students_from_df, validate_columns)


def test_validate_columns_detects_missing():
    df = pd.DataFrame({"ID": [1], "Name": ["x"]})
    missing = validate_columns(df, STUDENT_COLUMNS)
    assert "gender" in missing and "learning_slot" in missing
    assert validate_columns(pd.DataFrame(columns=STUDENT_COLUMNS), STUDENT_COLUMNS) == []


def test_students_from_df_parses_slots():
    df = pd.DataFrame([{
        "ID": "s1", "Name": "S", "gender": "male",
        "learning_slot": '[{"day": "monday", "start_time": "17:30"}]',
        "symptom": "nervous", "expectation": "cùng giới (Male)",
    }])
    students = students_from_df(df)
    assert len(students) == 1
    s = students[0]
    assert s.gender == "Male"               # normalised
    assert s.slots[0].day == "monday" and s.slots[0].start == 1050  # 17*60+30


def test_mentors_from_df_parses_windows():
    df = pd.DataFrame([{
        "ID": "m1", "Name": "M", "gender": "Female",
        "capacity": '[{"day": "tuesday", "slots": [{"start_time": "09:00", "end_time": "10:00"}]}]',
        "personalites": "patient", "expectation": "grade 7",
    }])
    mentors = mentors_from_df(df)
    assert mentors[0].windows[0].day == "tuesday"
    assert mentors[0].windows[0].start == 540 and mentors[0].windows[0].end == 600
