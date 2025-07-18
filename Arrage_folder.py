import os
import shutil

# ========== CONFIG ==========
SOURCE_DIR = "cag_reports"
DEST_DIR = "organized_reports"
UNDETECTED_DIR = os.path.join(DEST_DIR, "Undetected_Folders")

# Create base directories
os.makedirs(DEST_DIR, exist_ok=True)
os.makedirs(UNDETECTED_DIR, exist_ok=True)

# List of Indian States & UTs
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Puducherry", "Chandigarh",
    "Andaman and Nicobar Islands", "Dadra and Nagar Haveli and Daman and Diu"
]

def normalize(text):
    return text.lower().replace(" ", "")

def match_state(folder_name):
    folder_name_clean = normalize(folder_name)
    # 1. Exact match
    for state in INDIAN_STATES:
        if normalize(state) == folder_name_clean:
            return state
    # 2. Partial match (unique)
    matches = [state for state in INDIAN_STATES if normalize(state).startswith(folder_name_clean) or folder_name_clean in normalize(state)]
    return matches[0] if len(matches) == 1 else None

# Main logic
def organize_reports_by_folder_name():
    for folder_name in os.listdir(SOURCE_DIR):
        folder_path = os.path.join(SOURCE_DIR, folder_name)
        if not os.path.isdir(folder_path):
            continue

        matched_state = match_state(folder_name)

        if matched_state:
            target_folder = os.path.join(DEST_DIR, matched_state)
            os.makedirs(target_folder, exist_ok=True)
            print(f"📁 '{folder_name}' matched → {matched_state}")
            for file in os.listdir(folder_path):
                if file.lower().endswith(".pdf"):
                    src = os.path.join(folder_path, file)
                    dst = os.path.join(target_folder, file)
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
                        print(f"  📄 Copied: {file}")
                    else:
                        print(f"  ⚠️ Already exists: {file}")
        else:
            # Copy entire folder as-is to Undetected
            target_path = os.path.join(UNDETECTED_DIR, folder_name)
            if not os.path.exists(target_path):
                shutil.copytree(folder_path, target_path)
                print(f"🚫 No match for '{folder_name}' → Copied to Undetected")
            else:
                print(f"⚠️ Undetected folder already exists: {folder_name}")

if __name__ == "__main__":
    organize_reports_by_folder_name()
    print("\n✅ Folder organization complete.")
