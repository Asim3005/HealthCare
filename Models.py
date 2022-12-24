
from .Config import db
from datetime import datetime

# UserStore
class UserStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(45), nullable=False)
    password = db.Column(db.String(45), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False,
                             default=datetime.utcnow)

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return 'User ' + str(self.id)

# PatientDetails
class Doctor_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    ssn_id = db.Column(db.String(45), nullable=False, unique=True)
    speciality = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.String(500), nullable=False)
    login_type = db.Column(db.String(5), nullable = False, default= 'D')

    def __init__(self, name, ssn_id, speciality, experience, login_type):
        self.name = name
        self.speciality = speciality
        self.ssn_id = ssn_id
        self.login_type = login_type
        self.experience = experience

    def __repr__(self):
        return 'Doctor ' + str(self.id) + str(self.name)

class Appointments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(45), nullable = False)
    doctor_name = db.Column(db.String(45), nullable = False)
    doctor_specialization = db.Column(db.String(100), nullable = False)
    date = db.Column(db.Date, nullable = False)
    time = db.Column(db.Time, nullable = False)
    hemo = db.Column(db.Float, nullable = True)
    bmi = db.Column(db.Float, nullable = True)
    platelets = db.Column(db.Float, nullable = True)
    blood_sugar = db.Column(db.Float, nullable = True)
    blood_pressure = db.Column(db.String(45), nullable = True)

    def __init__(self,patient_name, doctor_name, doctor_specialization, date,time, hemo, bmi, platelets, blood_sugar, blood_pressure):
        self.blood_sugar = blood_sugar
        self.blood_pressure = blood_pressure
        self.platelets = platelets
        self.bmi = bmi
        self.hemo = hemo
        self.date = date
        self.time = time
        self.doctor_specialization = doctor_specialization
        self.doctor_name = doctor_name
        self.patient_name = patient_name

    def __repr__(self):
        return f'Appointment of {self.patient_name} with {self.doctor_name} on {self.date} at {self.time}'



class Patient_details(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    ssn_id = db.Column(db.String(45), nullable=False, unique=True)
    admission_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(45), nullable=False)
    city = db.Column(db.String(45), nullable=False)
    state = db.Column(db.String(45), nullable=False)
    status = db.Column(db.String(45), nullable=False)
    login_type = db.Column(db.String(5), nullable = False, default = 'P')


    def __init__(self, name, age, ssn_id, admission_date, address, city, state, login_type, status):

        self.name = name
        self.age = age
        self.ssn_id = ssn_id
        self.admission_date = admission_date
        self.address = address
        self.city = city
        self.state = state
        self.status = status
        self.login_type = login_type

    def __repr__(self):
        return 'Patient ' + str(self.id)


# Patient_Medicine
class Patient_Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey(
        'medicine.id'), nullable=False)
    medicine_quantity = db.Column(db.Integer, nullable=False)
    #patient_details_ssn_id = db.Column(db.String(45), nullable=False)

    def __repr__(self):
        return 'P_medicine ' + str(self.id)

class Patient_medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable = False)
    name = db.Column(db.String(45), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    dosage = db.Column(db.String(100), nullable = True)

    def __init__(self, patient_id, name, amount, dosage):
        self.patient_id = patient_id
        self.name = name
        self.amount = amount
        self.dosage = dosage
        super().__init__()
    
    def __repr__(self):
        return 'Medicine ' + str(self.id)
 

# Medicine
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_name = db.Column(db.String(45), nullable=False)
    medicine_amount = db.Column(db.Integer, nullable=False)
    medicine_quantity = db.Column(db.Integer, nullable=False)
    #patient_medicine_id = db.Column(db.Integer, nullable=False)
    patient_details = db.relationship(Patient_Medicine, backref="medicine")

    def __repr__(self):
        return 'Medicine ' + str(self.id)


# Patient_Test
class Patient_test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey(
        'diagnosis.id'), nullable=False)


# Diagnosis
class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(45), nullable=False)
    test_amount = db.Column(db.Integer, nullable=False)
    patient_test = db.relationship(Patient_test, backref="diagnosis")

    def __repr__(self):
        return 'Diagnosis ' + str(self.id)
