import requests
import os

# --- UPGRADE: The data model now supports multiple documents per city ---
DOCUMENTS = {
    "Mumbai": [
        {
            "id": "DCPR_2034",
            "url": "https://portal.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/Chief%20Engineer%20(Development%20Plan)/Docs/SANCTIONED%20DP2034/DCPR/DCPR%202034.pdf",
            "output_path": "io/Mumbai_DCPR_2034.pdf"
        }
    ],
    "Pune": [
        {
            "id": "PMRDA_DCR_2018",
            "url": "https://www.pmrda.gov.in/wp-content/uploads/2025/04/Final-PMRDA-DCPR-2018-.pdf",
            "output_path": "io/Pune_DCR.pdf"
        }
    ],
    "Ahmedabad": [
        {
            "id": "AUDA_GDCR_Part1",
            "url": "https://www.auda.org.in/uploads/Assets/rdp/commongdcr08012016052529533.pdf",
            "output_path": "io/Ahmedabad_DCR_Part1.pdf"
        },
        {
            "id": "AUDA_GDCR_Part2",
            "url": "https://ahmedabadcity.gov.in/Uploads/FormsFonts/Town%20Development%20Department%20(B.P.S.P.)/Final_Notification_CGDCR_2017_PART_II_PLANNING_REGULATION_min.pdf", # <-- IMPORTANT: REPLACE THIS
            "output_path": "io/Ahmedabad_DCR_Part2.pdf"
        }
    ]
}

# --- Download Logic (Now handles the new structure) ---
def download_files():
    print("--- Checking and Downloading Source Documents for All Regions ---")
    os.makedirs("io", exist_ok=True)
    
    for city, doc_list in DOCUMENTS.items():
        for doc in doc_list:
            if os.path.exists(doc["output_path"]):
                print(f"'{doc['output_path']}' already exists. Skipping.")
            else:
                print(f"Downloading {doc['id']} for {city}...")
                try:
                    response = requests.get(doc["url"], timeout=60)
                    response.raise_for_status()
                    with open(doc["output_path"], "wb") as f:
                        f.write(response.content)
                    print(f"Successfully saved to '{doc['output_path']}'")
                except requests.exceptions.RequestException as e:
                    print(f"!!! FAILED to download {doc['id']}. Error: {e}")

if __name__ == "__main__":
    download_files()

    

