# generate_listings.py
import sqlite3
import csv
import os
from datetime import datetime

# DB and CSV paths resolved relative to this script's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = os.path.join(BASE_DIR, "google_map_data.db")
CSV_PATH = os.path.join(BASE_DIR, "g_map_master_table_sample.csv")

print(f"DB Path: {DATABASE_URL}")
print(f"CSV Path: {CSV_PATH}")

# 10 High-quality mock business listings in India
MOCK_LISTINGS = [
    {
        "business_name": "Sharma Bakery & Sweets",
        "business_category": "Bakery",
        "subcategory": "Cake Shop, Desserts, Indian Sweets",
        "address": "Shop 12, Prime Arcade, Anand Mahal Road, Adajan",
        "city": "Surat",
        "state": "Gujarat",
        "area": "Adajan",
        "phone_number": "+91 98250 12345",
        "website_url": "https://www.sharmabakerysurat.com",
        "email": "info@sharmabakerysurat.com",
        "reviews_count": 245,
        "ratings": 4.6
    },
    {
        "business_name": "Krishna Dental Care & Implant Centre",
        "business_category": "Clinic",
        "subcategory": "Dentist, Orthodontist, Dental Surgery",
        "address": "201, Landmark Building, Link Road, Andheri West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "area": "Andheri West",
        "phone_number": "+91 22 2673 9876",
        "website_url": "https://www.krishnadentalcare.in",
        "email": "appointments@krishnadentalcare.in",
        "reviews_count": 188,
        "ratings": 4.8
    },
    {
        "business_name": "Royal Palms Luxury Hotel & Suites",
        "business_category": "Hotel",
        "subcategory": "Luxury Stay, Fine Dining, Conference Hall",
        "address": "88, Koregaon Park Road, Lane 5",
        "city": "Pune",
        "state": "Maharashtra",
        "area": "Koregaon Park",
        "phone_number": "+91 20 6612 3400",
        "website_url": "https://www.royalpalmshotelpune.com",
        "email": "reservations@royalpalmshotelpune.com",
        "reviews_count": 512,
        "ratings": 4.7
    },
    {
        "business_name": "FitLife Unisex Gym & Fitness Centre",
        "business_category": "Gym",
        "subcategory": "Fitness Trainer, Yoga Class, Cardio, Weightlifting",
        "address": "4th Floor, Sector 5, HSR Layout",
        "city": "Bengaluru",
        "state": "Karnataka",
        "area": "HSR Layout",
        "phone_number": "+91 80 4956 7890",
        "website_url": "https://www.fitlifegymbengaluru.com",
        "email": "support@fitlifegymbengaluru.com",
        "reviews_count": 320,
        "ratings": 4.5
    },
    {
        "business_name": "Apollo Pharmacy Adajan",
        "business_category": "Pharmacy",
        "subcategory": "Medicines, Healthcare Products, Baby Care",
        "address": "Ground Floor, Sunrise Tower, Adajan",
        "city": "Surat",
        "state": "Gujarat",
        "area": "Adajan",
        "phone_number": "+91 98790 54321",
        "website_url": "https://www.apollopharmacy.in",
        "email": "adajan@apollopharmacy.in",
        "reviews_count": 98,
        "ratings": 4.4
    },
    {
        "business_name": "TechVeda IT Solutions & Consultancy",
        "business_category": "IT Services",
        "subcategory": "Software Development, Web Design, Mobile Apps",
        "address": "Phase II, Hitech City, Madhapur",
        "city": "Hyderabad",
        "state": "Telangana",
        "area": "Madhapur",
        "phone_number": "+91 40 4823 4567",
        "website_url": "https://www.techvedasolutions.com",
        "email": "contact@techvedasolutions.com",
        "reviews_count": 75,
        "ratings": 4.6
    },
    {
        "business_name": "Gourmet Garden Organic Cafe",
        "business_category": "Cafe",
        "subcategory": "Vegetarian Bistro, Specialty Coffee, Organic Food",
        "address": "Shop 4, Palladium Mall, Bodakdev",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "area": "Bodakdev",
        "phone_number": "+91 79 4001 2345",
        "website_url": "https://www.gourmetgardencafe.com",
        "email": "hello@gourmetgardencafe.com",
        "reviews_count": 142,
        "ratings": 4.5
    },
    {
        "business_name": "StyleCraft Hair & Beauty Unisex Salon",
        "business_category": "Salon",
        "subcategory": "Haircut, Bridal Makeup, Facial, Hair Spa",
        "address": "1st Floor, Galaxy Plaza, VIP Road, Vesu",
        "city": "Surat",
        "state": "Gujarat",
        "area": "Vesu",
        "phone_number": "+91 99090 98765",
        "website_url": "https://www.stylecraftsalon.com",
        "email": "appointments@stylecraftsalon.com",
        "reviews_count": 210,
        "ratings": 4.7
    },
    {
        "business_name": "SmartMart Supermarket & Grocery",
        "business_category": "Grocery",
        "subcategory": "Supermarket, Fresh Vegetables, Daily Needs",
        "address": "Ground Floor, Milestone Building, Alkapuri",
        "city": "Vadodara",
        "state": "Gujarat",
        "area": "Alkapuri",
        "phone_number": "+91 265 233 4455",
        "website_url": "https://www.smartmartsupermarket.com",
        "email": "alkapuri@smartmartsupermarket.com",
        "reviews_count": 315,
        "ratings": 4.3
    },
    {
        "business_name": "Speedy Wheels Car Service & Repair",
        "business_category": "Automobile",
        "subcategory": "Car Wash, Wheel Alignment, Engine Repair",
        "address": "Plot 45, MIDC Industrial Area, Satpur",
        "city": "Nashik",
        "state": "Maharashtra",
        "area": "Satpur",
        "phone_number": "+91 253 235 6677",
        "website_url": "https://www.speedywheelscarcare.com",
        "email": "satpur@speedywheelscarcare.com",
        "reviews_count": 110,
        "ratings": 4.5
    }
]

def generate_listings():
    # 1. SQLite Database Sync
    if not os.path.exists(DATABASE_URL):
        print(f"Error: Database not found at {DATABASE_URL}")
        return

    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    inserted_sqlite = 0
    skipped_sqlite = 0
    inserted_ids = []

    try:
        # Loop through mock listings and insert
        for item in MOCK_LISTINGS:
            # Check for duplicates by name and city
            cursor.execute(
                "SELECT global_business_id FROM g_map_master_table WHERE LOWER(business_name) = ? AND LOWER(city) = ?",
                (item["business_name"].lower(), item["city"].lower())
            )
            exists = cursor.fetchone()

            if exists:
                print(f"Skipping (Already Exists): {item['business_name']} in {item['city']}")
                skipped_sqlite += 1
                continue

            created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            cursor.execute(
                """
                INSERT INTO g_map_master_table (
                    business_name, address, website_url, phone_number, reviews_count, ratings,
                    business_category, subcategory, city, state, area, created_at, email, owner_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["business_name"], item["address"], item["website_url"], item["phone_number"],
                    item["reviews_count"], item["ratings"], item["business_category"], item["subcategory"],
                    item["city"], item["state"], item["area"], created_at, item["email"], None
                )
            )
            new_id = cursor.lastrowid
            inserted_ids.append((new_id, item))
            inserted_sqlite += 1
            print(f"Inserted into DB [ID: {new_id}]: {item['business_name']}")

        conn.commit()
        print(f"\nSQLite Insertions Complete: {inserted_sqlite} inserted, {skipped_sqlite} skipped.")

    except Exception as e:
        conn.rollback()
        print(f"Error during SQLite Sync: {e}")
        conn.close()
        return
    finally:
        conn.close()

    # 2. CSV File Sync
    if os.path.exists(CSV_PATH):
        try:
            inserted_csv = 0
            with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                
                # Check column headers format or just write row
                for new_id, item in inserted_ids:
                    created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    # CSV columns: global_business_id, business_name, address, website_url, phone_number,
                    # reviews_count, ratings, business_category, subcategory, city, state, area, created_at, email
                    writer.writerow([
                        new_id,
                        item["business_name"],
                        item["address"],
                        item["website_url"],
                        item["phone_number"],
                        item["reviews_count"],
                        item["ratings"],
                        item["business_category"],
                        item["subcategory"],
                        item["city"],
                        item["state"],
                        item["area"],
                        created_at,
                        item["email"]
                    ])
                    inserted_csv += 1
            print(f"CSV Append Complete: {inserted_csv} rows appended to CSV.")
        except Exception as e:
            print(f"Error during CSV Sync: {e}")
    else:
        print("CSV file not found, skipping CSV sync.")

if __name__ == "__main__":
    generate_listings()
