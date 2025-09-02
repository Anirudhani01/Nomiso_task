from sqlalchemy import create_engine, text
from config import DATABASE_URL

def verify_database():
    print(f"🔍 Verifying Database Connection...")
    print(f"Database URL: {DATABASE_URL}")
    
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            # Check employee count
            result = conn.execute(text("SELECT COUNT(*) as count FROM employees"))
            count = result.fetchone()[0]
            print(f"📊 Total employees: {count}")
            
            # Check employee ID range
            result = conn.execute(text("SELECT MIN(emp_id) as min_id, MAX(emp_id) as max_id FROM employees"))
            min_id, max_id = result.fetchone()
            print(f"📈 Employee ID range: {min_id} to {max_id}")
            
            # Check if employee 3000 exists
            result = conn.execute(text("SELECT emp_id, Name, Email FROM employees WHERE emp_id = 3000"))
            emp_3000 = result.fetchone()
            if emp_3000:
                print(f"✅ Employee 3000 found: {emp_3000[1]} ({emp_3000[2]})")
            else:
                print(f"❌ Employee 3000 not found")
                
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    verify_database()
