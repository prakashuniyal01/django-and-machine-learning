import pandas as pd
from faker import Faker
import random

# Initialize Faker instance
fake = Faker()

# Define possible specializations and genders
specializations = ['Cardiologist', 'Dermatologist', 'Neurologist', 'Pediatrician', 'Orthopedic']
genders = ['Male', 'Female']

# Generate dummy doctors
def generate_doctors(n=5):
    doctors = []
    for doctor_id in range(1, n + 1):
        gender = random.choice(genders)
        specialization = random.choice(specializations)
        doctors.append({
            'doctor_id': doctor_id,
            'name': fake.name(),
            'gender': gender,
            'specialization': specialization,
        })
    return pd.DataFrame(doctors)

# Generate dummy appointments
def generate_appointments(doctors_df, n=1000):
    appointments = []
    for _ in range(n):
        doctor = doctors_df.sample(1).iloc[0]  # Randomly select a doctor
        doctor_id = doctor['doctor_id']
        doctor_gender = doctor['gender']
        doctor_specialization = doctor['specialization']

        # patient_id = random.randint(1, 100)  # Assuming you have 100 patients
        patient_gender = random.choice(genders)

        appointment_date = fake.date_this_decade()
        start_time = fake.time()
        end_time = fake.time()
        
        # Ensure the end time is after the start time
        if start_time > end_time:
            start_time, end_time = end_time, start_time
        
        status = random.choice(['SCHEDULED', 'COMPLETED', 'CANCELLED'])
        created_at = fake.date_this_year()
        updated_at = fake.date_this_year()

        appointments.append({
            'doctor_id': doctor_id,
            'doctor_gender': doctor_gender,
            'doctor_specialization': doctor_specialization,
            'patient_gender': patient_gender,
            'appointment_date': appointment_date,
            'start_time': start_time,
            'end_time': end_time,
            'status': status,
            'created_at': created_at,
            'updated_at': updated_at
        })
    
    return pd.DataFrame(appointments)

# Generate dummy data
doctors_df = generate_doctors(n=5)  # 5 doctors
appointments_df = generate_appointments(doctors_df, n=1000)  # 1000 appointments

# Save the data to CSV files
doctors_df.to_csv('doctors_data.csv', index=False)
appointments_df.to_csv('appointments_data.csv', index=False)

print("Dummy data saved to 'doctors_data.csv' and 'appointments_data.csv'")
