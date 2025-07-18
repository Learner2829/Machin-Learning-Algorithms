import os
import shutil

# === List of all Indian states (title case) ===
STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi", "Jammu and Kashmir", "Ladakh"
]

# === Normalize for comparison (e.g. 'AndhraPradesh') ===
def normalize(s):
    return s.lower().replace(" ", "")

normalized_states = {normalize(state): state for state in STATES}

# === Input and Output folders ===
SOURCE_FOLDER = "organized_reports/Unknown"
DESTINATION_FOLDER = "organized_reports"
DEFAULT_FOLDER = "Central_Government"

os.makedirs(os.path.join(DESTINATION_FOLDER, DEFAULT_FOLDER), exist_ok=True)

# === Process ===
for filename in os.listdir(SOURCE_FOLDER):
    if not filename.lower().endswith(".pdf"):
        continue

    full_src_path = os.path.join(SOURCE_FOLDER, filename)
    filename_parts = filename.replace("_", " ").replace("-", " ").split()
    matched_state = None

    for word in filename_parts:
        for norm_state, original_state in normalized_states.items():
            if word.lower() in norm_state:
                matched_state = original_state
                break
        if matched_state:
            break

    dest_folder = os.path.join(DESTINATION_FOLDER, matched_state or DEFAULT_FOLDER)
    os.makedirs(dest_folder, exist_ok=True)

    shutil.copy2(full_src_path, os.path.join(dest_folder, filename))
    print(f"📄 '{filename}' → 📁 '{matched_state or DEFAULT_FOLDER}'")

print("\n✅ Done organizing PDFs by filename.")
