import random
from sqlalchemy import create_engine, text
from config import DATABASE_URL

def populate_employees():
    """Populate employees table with 4653 sample records"""
    print("🔄 Populating employees table with 4653 records...")
    
    engine = create_engine(DATABASE_URL)
    
    # Sample data for realistic employee records
    names = [
        "John Smith", "Emma Johnson", "Michael Brown", "Sarah Davis", "David Wilson",
        "Lisa Anderson", "James Taylor", "Jennifer Martinez", "Robert Garcia", "Amanda Rodriguez",
        "William Lopez", "Jessica White", "Christopher Lee", "Ashley Thompson", "Daniel Clark",
        "Nicole Lewis", "Matthew Hall", "Stephanie Young", "Joshua Allen", "Rebecca King",
        "Andrew Wright", "Lauren Green", "Kevin Baker", "Michelle Adams", "Brian Nelson",
        "Amber Carter", "Steven Mitchell", "Rachel Perez", "Timothy Roberts", "Heather Turner",
        "Jason Phillips", "Melissa Campbell", "Jeffrey Parker", "Danielle Evans", "Ryan Edwards",
        "Stephanie Collins", "Gary Stewart", "Tiffany Sanchez", "Larry Morris", "Crystal Rogers",
        "Justin Reed", "Erica Cook", "Brandon Morgan", "Monica Bell", "Eric Murphy",
        "Katherine Bailey", "Stephen Rivera", "Angela Cooper", "Gregory Richardson", "Tracy Cox"
    ]
    
    cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
              "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", 
              "Fort Worth", "Columbus", "Charlotte", "San Francisco", "Indianapolis", 
              "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit"]
    
    education_levels = ["Bachelor's", "Master's", "PhD", "High School", "Associate's"]
    genders = ["Male", "Female"]
    benched_status = ["Yes", "No"]
    
    try:
        with engine.connect() as conn:
            # Clear existing data
            conn.execute(text("DELETE FROM employees"))
            conn.commit()
            print("✅ Cleared existing employee data")
            
            # Insert 4653 records
            for i in range(1, 4654):
                name = random.choice(names)
                email = f"{name.lower().replace(' ', '.')}{i}@company.com"
                education = random.choice(education_levels)
                joining_year = random.randint(2015, 2024)
                city = random.choice(cities)
                payment_tier = random.randint(1, 5)
                age = random.randint(22, 65)
                gender = random.choice(genders)
                ever_benched = random.choice(benched_status)
                experience = random.randint(0, 15)
                leave_or_not = random.choice([0, 1])
                
                query = text("""
                    INSERT INTO employees (emp_id, Name, Email, Education, JoiningYear, 
                    City, PaymentTier, Age, Gender, EverBenched, ExperienceInCurrentDomain, LeaveOrNot)
                    VALUES (:emp_id, :name, :email, :education, :joining_year, :city, 
                    :payment_tier, :age, :gender, :ever_benched, :experience, :leave_or_not)
                """)
                
                conn.execute(query, {
                    'emp_id': i,
                    'name': name,
                    'email': email,
                    'education': education,
                    'joining_year': joining_year,
                    'city': city,
                    'payment_tier': payment_tier,
                    'age': age,
                    'gender': gender,
                    'ever_benched': ever_benched,
                    'experience': experience,
                    'leave_or_not': leave_or_not
                })
                
                if i % 500 == 0:
                    print(f"📊 Inserted {i} records...")
            
            conn.commit()
            print(f"✅ Successfully populated {4653} employee records!")
            
            # Verify the count
            result = conn.execute(text("SELECT COUNT(*) as count FROM employees"))
            count = result.fetchone()[0]
            print(f"📊 Total employees in database: {count}")
            
            # Show sample records
            result = conn.execute(text("SELECT emp_id, Name, Email, City FROM employees LIMIT 5"))
            print("\n📋 Sample records:")
            for row in result:
                print(f"  ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, City: {row[3]}")
                
    except Exception as e:
        print(f"❌ Error populating database: {e}")

if __name__ == "__main__":
    populate_employees()

