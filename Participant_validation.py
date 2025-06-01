# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 20:30:09 2025

@author: Matan Eshed
"""

import pandas as pd

MIN_TIME_TO_COMPLETE = 100 # Seconds
MAX_REPEATED_ANSWERS_PERCENT = 0.8 # Percent, per questionnaire

# Define external validation functions

def has_repeated_answers(q_row, q_columns_groups, pid):
    """
    Returns True if any questionnaire in q_columns_groups has 80% identical answers in a row.
    """
    for q_cols in q_columns_groups:
        answers = q_row[q_cols].tolist()
        if not is_q_valid(answers, pid):
            return True
    return False


def is_short_time(q_row, pid, duration_col='Duration (in seconds)', threshold=MIN_TIME_TO_COMPLETE):
    """
    Returns True if the duration (in seconds) is below the threshold.
    """
    duration_str = q_row.get(duration_col, None)
    duration = pd.to_numeric(duration_str, errors='coerce')

    print(f"Participant {pid} took {round(duration / 60, 2)} minutes to complete the questtionaire")
    return pd.notna(duration) and (duration < threshold)

def is_q_valid(p_answers, pid):
    max_count = 1
    answers_count = 1
    for i in range(1, len(p_answers), 1):
        if p_answers[i] == p_answers[i - 1]:
            answers_count += 1
        else:
            if answers_count > max_count:
                max_count = answers_count

    print(f"Participant {pid} has a maximum of {max_count} ({round((max_count / len(p_answers)) * 100)}%) repeated answers in a row")
    return max_count <= MAX_REPEATED_ANSWERS_PERCENT * len(p_answers)

# Load the data
qual = pd.read_csv('Qualtrics.csv')
participants = pd.read_csv('Participants_Final.csv')

# Identify ranges of columns for each questionnaire
cols = qual.columns.tolist()
q1_cols = cols[cols.index('B-Q12_1'): cols.index('B-Q12_26') + 1]
q2_cols = cols[cols.index('B-Q13_1'): cols.index('B-Q13_27') + 1]
q3_cols = cols[cols.index('B-Q14_1'): cols.index('B-Q15_4') + 1]
questionnaire_groups = (q1_cols, q2_cols, q3_cols)

# Initialize new columns
participants['repeated answers'] = False
participants['short time'] = False

# Index Qualtrics by “Random ID”
qual_indexed = qual.set_index('Random ID')

for idx, part_row in participants.iterrows():
    try:
        # Execute only in case the participant shows up on the participants file
        pid = part_row['Qualtrics ID']
        if pid not in qual_indexed.index:
            continue

        q_row = qual_indexed.loc[pid]
        if isinstance(q_row, pd.DataFrame):
            q_row = q_row.iloc[0]

        # Use external functions for validations
        participants.at[idx, 'repeated answers'] = has_repeated_answers(q_row, questionnaire_groups, pid)
        participants.at[idx, 'short time'] = is_short_time(q_row, pid)

    except Exception:
        continue

# Overwrite the original participants file with updated data
participants.to_csv('Participants_Final.csv', index=False)
