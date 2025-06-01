# -*- coding: utf-8 -*-
"""
Created on Mon Apr 14 20:30:09 2025

@author: Matan Eshed
"""

import pandas as pd

# Load participants and life data
participants = pd.read_csv("Participants.csv")
participants.set_index("Qualtrics ID", inplace=True)

# Fix: ensure 'First Session At' and Day columns can hold strings or dates
participants["First Session At"] = participants["First Session At"].astype("object")
for day in range(1, 31):
    col = f"Day {day}"
    if col in participants.columns:
        participants[col] = participants[col].astype("object")

life_data = pd.read_csv("Life Data.csv", encoding='latin1')

# Filter to only 'ID' prompts with valid responses
life_data = life_data[
    (life_data["Prompt Label"] == "ID") &
    (life_data["Response"].notna()) &
    (life_data["Response"].astype(str).str.strip() != "")
].copy()

# Convert to datetime and normalize dates
life_data["Notification Time"] = pd.to_datetime(life_data["Notification Time"], errors="coerce")
life_data["date_only"] = life_data["Notification Time"].dt.normalize()

# Iterate over unique participant IDs
for pid in life_data["Response"].unique():
    pid_data = life_data[life_data["Response"] == pid].sort_values("date_only")

    if pid not in participants.index or pid_data.empty:
        continue

    # Drop duplicate dates — keep only one entry per date
    pid_data = pid_data.drop_duplicates(subset="date_only")

    # First notification date = Day 1
    first_date = pid_data["date_only"].iloc[0]
    participants.at[pid, "First Session At"] = first_date.date()

    # Assign "X" based on day difference
    for date in pid_data["date_only"]:
        day_diff = (date - first_date).days
        if 0 <= day_diff < 30:
            col = f"Day {day_diff + 1}"
            if col in participants.columns:
                participants.at[pid, col] = "X"

# Fill all missing Day fields with 'O'
for day in range(1, 31):
    col = f"Day {day}"
    if col in participants.columns:
        participants[col] = participants[col].fillna("O")

# Reset index if needed
participants.reset_index(inplace=True)

# Save result
participants.to_csv("Participants_Final.csv", index=False)
