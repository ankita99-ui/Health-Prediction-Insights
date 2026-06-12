"""Seed the database with sample patients via the API.

Run while the backend is up:  python seed_data.py

Going through the API (instead of inserting into the database directly)
means every record is validated and gets a real AI-generated remark.
"""

import requests

API = "http://127.0.0.1:8000/api/patients"

# Mix of healthy, borderline and clearly abnormal blood values.
PATIENTS = [
    ("Rahul Sharma",    "1992-03-18", "rahul.sharma@example.com",    92.0, 15.1, 172.0),
    ("Priya Nair",      "1988-07-02", "priya.nair@example.com",      85.0, 13.4, 165.0),
    ("Amit Verma",      "1975-11-25", "amit.verma@example.com",     118.0, 14.0, 210.0),
    ("Sneha Kulkarni",  "1995-01-09", "sneha.kulkarni@example.com",  78.0, 12.8, 158.0),
    ("Vikram Singh",    "1969-06-14", "vikram.singh@example.com",   152.0, 13.9, 255.0),
    ("Meera Iyer",      "1983-09-30", "meera.iyer@example.com",     108.0, 13.1, 214.0),
    ("John Dsouza",     "1990-12-05", "john.dsouza@example.com",     88.0, 15.6, 188.0),
    ("Fatima Khan",     "1979-04-21", "fatima.khan@example.com",    145.0, 11.2, 232.0),
    ("Arjun Reddy",     "1998-08-11", "arjun.reddy@example.com",     95.0, 16.2, 179.0),
    ("Kavita Joshi",    "1986-02-27", "kavita.joshi@example.com",   102.0, 11.6, 196.0),
    ("Suresh Patil",    "1962-10-08", "suresh.patil@example.com",   168.0, 12.4, 268.0),
    ("Ananya Das",      "2000-05-16", "ananya.das@example.com",      81.0, 13.7, 150.0),
    ("Mohan Pillai",    "1971-01-31", "mohan.pillai@example.com",   126.0, 13.0, 241.0),
    ("Ritu Agarwal",    "1993-06-23", "ritu.agarwal@example.com",    90.0, 10.8, 184.0),
    ("Karan Malhotra",  "1985-03-07", "karan.malhotra@example.com", 110.0, 14.5, 226.0),
    ("Lakshmi Menon",   "1958-09-19", "lakshmi.menon@example.com",  139.0, 11.9, 249.0),
    ("Rohit Bansal",    "1996-11-12", "rohit.bansal@example.com",    87.0, 15.0, 168.0),
    ("Zoya Sheikh",     "1991-07-28", "zoya.sheikh@example.com",     64.0, 12.5, 175.0),
    ("Deepak Chawla",   "1968-04-03", "deepak.chawla@example.com",  131.0, 13.3, 290.0),
    ("Nisha Thomas",    "1989-12-15", "nisha.thomas@example.com",    99.0, 14.8, 205.0),
]


def main():
    created, skipped = 0, 0
    for name, dob, email, glucose, hb, chol in PATIENTS:
        response = requests.post(API, json={
            "full_name": name,
            "date_of_birth": dob,
            "email": email,
            "glucose": glucose,
            "haemoglobin": hb,
            "cholesterol": chol,
        }, timeout=30)

        if response.status_code == 201:
            remark = response.json()["remarks"].split(" - ")[0]
            print(f"  + {name:18s} -> {remark}")
            created += 1
        elif response.status_code == 409:   # already seeded earlier
            print(f"  . {name:18s} -> already exists, skipped")
            skipped += 1
        else:
            print(f"  ! {name:18s} -> FAILED: {response.text}")

    print(f"\nDone: {created} created, {skipped} skipped.")


if __name__ == "__main__":
    main()
