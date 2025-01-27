
## database 
```sql
-- Users Table

CREATE TABLE users (
    user_id         BIGSERIAL PRIMARY KEY,        -- or INT AUTO_INCREMENT
    email           VARCHAR(255) UNIQUE NOT NULL,
    phone           VARCHAR(20) UNIQUE NOT NULL,  -- consider E.164 format for phone
    password_hash   VARCHAR(255) NOT NULL,        -- store hashed+salted password
    role            VARCHAR(20) NOT NULL,         -- e.g. 'ADMIN', 'DOCTOR', 'PATIENT'
    
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    gender          VARCHAR(10),                  -- e.g. 'Male', 'Female', 'Other'
    date_of_birth   DATE,
    
    address         TEXT,
    bio             TEXT,
    profile_photo   VARCHAR(255),                 -- store a file path or cloud URL
    
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Optionally, is_active or deleted_at for soft-delete:
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- Why a single users table?
-- 
-- Simpler authentication logic (one place to store login credentials).
-- Common user fields in one table.
-- Use the role column to distinguish whether it’s an admin, doctor, or patient.


-- Doctors Table

 CREATE TABLE doctors (
    doctor_id       BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    license_number  VARCHAR(100) UNIQUE NOT NULL,
    years_experience INT,
    clinic_name     VARCHAR(255),
    clinic_address  TEXT,
    
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_doctor_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_specialization
        FOREIGN KEY (specialization_id) REFERENCES specializations(specialization_id)
        ON DELETE SET NULL
);

-- This table stores Doctor-specific fields.
-- user_id references the main users table.
-- ON DELETE CASCADE ensures that if the user is removed, related doctor info also goes away (adjust as per your logic).


-- Patients Table

CREATE TABLE patients (
    patient_id      BIGSERIAL PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    
    insurance_details  VARCHAR(255),     -- e.g., policy number
    medical_history    TEXT,            -- summary of past conditions, or store in separate table
    emergency_contact  VARCHAR(20),
    
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_patient_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- This table stores Patient-specific fields.


-- Specializations Table

CREATE TABLE specializations (
    specialization_id BIGSERIAL PRIMARY KEY,
    name              VARCHAR(255) UNIQUE NOT NULL,  -- e.g., 'Cardiologist', 'Dermatologist', etc.
    description       TEXT                           -- Optional: details about the specialization
);

-- Optionally store repeated weekly schedules or more complex patterns.
-- Alternatively, store date-specific availability if each day is different and dynamic.


-- Appointments Table

CREATE TABLE appointments (
    doctor_id       BIGINT NOT NULL,
    patient_id      BIGINT NOT NULL,
    
    appointment_date DATE NOT NULL,
    start_time      TIME NOT NULL,
    end_time        TIME NOT NULL,
    status          VARCHAR(50) NOT NULL DEFAULT 'SCHEDULED', -- e.g. 'SCHEDULED', 'COMPLETED', 'CANCELLED'
    
    reason_for_visit TEXT,
    
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_appointment_doctor
        FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id),
    CONSTRAINT fk_appointment_patient
        FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- References both doctors and patients.
-- status could be tracked to handle cancellations, rescheduling, etc.
```