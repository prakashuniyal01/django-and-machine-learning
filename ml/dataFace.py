import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker instance
fake = Faker()

# Generate dummy data
def generate_appointments(n=1000):
    appointments = []
    for _ in range(n):
        doctor_id = random.randint(1, 5)  # Assuming you have 5 doctors
        patient_id = random.randint(1, 100)  # Assuming you have 100 patients
        appointment_date = fake.date_this_decade()
        start_time = fake.time()
        end_time = fake.time()
        
        # Make sure the end time is after the start time
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        
        status = random.choice(['SCHEDULED', 'COMPLETED', 'CANCELLED'])
        reason_for_visit = fake.text(max_nb_chars=100)
        created_at = fake.date_this_year()
        updated_at = fake.date_this_year()

        appointments.append({
            'doctor': doctor_id,
            'patient': patient_id,
            'appointment_date': appointment_date,
            'start_time': start_time,
            'end_time': end_time,
            'status': status,
            'reason_for_visit': reason_for_visit,
            'created_at': created_at,
            'updated_at': updated_at
        })
    
    return pd.DataFrame(appointments)

# Generate 1000 dummy appointments
appointments_df = generate_appointments(n=1000)

# Save it to a CSV file
appointments_df.to_csv('appointments_data.csv', index=False)
print("Dummy data saved to 'appointments_data.csv'")
