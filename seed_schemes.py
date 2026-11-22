import mysql.connector

import os
from dotenv import load_dotenv

load_dotenv()

def seed_schemes():
    schemes = [
        # Pensions
        ("Indira Gandhi National Old Age Pension Scheme (IGNOAPS)", "Provides a monthly pension to BPL citizens aged 60 years or above. Apply at your local Gram Panchayat."),
        ("Indira Gandhi National Widow Pension Scheme (IGNWPS)", "Provides a monthly pension to BPL widows aged 40-59 years. Required documents include death certificate of husband."),
        ("National Family Benefit Scheme (NFBS)", "Provides a one-time lump sum assistance to a BPL household on the death of the primary breadwinner."),
        
        # Ration Card
        ("One Nation One Ration Card (ONORC)", "Allows beneficiaries to claim their subsidized food grains from any Fair Price Shop (FPS) across the country using their existing ration card."),
        ("Antyodaya Anna Yojana (AAY)", "Provides highly subsidized food grains (rice at Rs. 3/kg, wheat at Rs. 2/kg) to the poorest of the poor families."),
        ("Pradhan Mantri Garib Kalyan Anna Yojana (PMGKAY)", "Provides an additional 5 kg of free food grains per person per month to all NFSA beneficiaries."),
        
        # Scholarships
        ("Pre-Matric Scholarship for SC/ST Students", "Financial assistance for students from Scheduled Castes and Scheduled Tribes studying in classes 9 and 10 to reduce dropout rates."),
        ("Post-Matric Scholarship Scheme for Minorities", "Provides financial assistance to students belonging to minority communities pursuing higher education from class 11 to Ph.D."),
        ("National Means-cum-Merit Scholarship (NMMS)", "Awards scholarships to meritorious students of economically weaker sections to arrest their dropout at class 8 and encourage them to continue study at secondary stage."),
        
        # General Government / Farmers
        ("Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)", "Provides direct income support of Rs. 6,000 per year in three equal installments to all landholding farmer families."),
        ("Pradhan Mantri Fasal Bima Yojana (PMFBY)", "Provides comprehensive crop insurance cover against non-preventable natural risks from pre-sowing to post-harvest stages.")
    ]

    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            database=os.getenv("DB_NAME", "gramai_db"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", "")
        )
        cursor = conn.cursor()
        
        print("Inserting schemes...")
        for name, desc in schemes:
            # Insert if it doesn't already exist (simple check)
            cursor.execute("SELECT id FROM imported_schemes WHERE name = %s", (name,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO imported_schemes (name, description) VALUES (%s, %s)",
                    (name, desc)
                )
        
        conn.commit()
        print("Successfully inserted 11 schemes into the database.")
        
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    seed_schemes()
