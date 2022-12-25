from . import app
from datetime import datetime, date, time, timedelta
from flask import render_template, session, url_for, request, redirect, flash, session, g
from .Forms import Login_form, Patient_create, Patient_delete, delete_result, Patient_update, \
    add_diagnosis, Appointment_create, Doctor_create, Update_Patient1_Form,  \
    LeadToUpdate_Form, DeletePatient_Form, LeadToAppointments_Form, PrescriptionForm
from .Models import UserStore, Patient_test, Patient_Medicine, Patient_details, Diagnosis, Doctor_details, Appointments,Patient_medicine
from .Config import db

# store patient ID for querying
pid = 0
issue_med = None
quantity = []
add_test = None


@app.context_processor
def inject_now():
    return {'now': date.today()}


# Function to implement session management and check the category of stakeholder accessing the website


def check_session():
    print(f"session[user] = {session.get('user')}")
    if 'user' not in session or not session['user']:
        return None
    else:
        stakeholder_type = session['user'][-1]
        print(f'User = {session["user"]}')
        print(f'StakeHolder Type = {stakeholder_type}')
        if stakeholder_type == 'D':
            session['stakeholder'] = 'Doctor'
            return 'Doctor'
        elif stakeholder_type == 'P':
            session['stakeholder'] = 'Patient'
            return 'Patient'
        # elif stakeholder_type == 'P':
        #     session['stakeholder'] = 'pharmacy_executive'
        #     return 'pharmacy_executive'


# ==================================================================================
#                                   Home and Login
# ==================================================================================


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def main():
    if check_session():
        return render_template('index.html', user=session['user'], patient_name=session['username'])
    form = Login_form()
    if request.method == 'POST':
        # Validate the form
        if form.validate_on_submit():
            # Check the credentials
            # if UserStore.query.filter_by(login=request.form.get('username'), password=request.form.get('password')).first():
            cnic = str(request.form.get('username'))
            password=request.form.get('password')
            if UserStore.query.filter_by(login=cnic+"@P", password=password).first():
                flash("Welcome Patient!", "success")
                session['user'] = cnic+'@P'
                session['username'] = Patient_details.query.filter_by(ssn_id=cnic).first().name
                return redirect(url_for('main'))
            elif UserStore.query.filter_by(login=cnic+"@D", password=password).first():
                flash("Welcome Doctor!", "success")
                session['user'] = cnic+'@D'
                session['username'] = Doctor_details.query.filter_by(ssn_id=cnic).first().name
                return redirect(url_for('main'))
            else:
                flash("Invalid credentials!", "danger")
                return render_template('login.html', title="Login", form=form)
    return render_template('login.html', title="Login", form=form)


@app.route("/index")
def index():
    if not check_session():
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    return render_template("index.html")


@app.route("/Appointment", methods=['GET', 'POST'])
def appointment():
    
    # return render_template("Appointment_patient.html")

    # Check that an authorised user only can access this functionality
    if check_session() != 'Patient':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    def time_booked(inp, booked):
        for booking in booked:
            dt = booking.date
            tm = booking.time
            # print(f"Selected time {tm}")
            book_dt_tm = datetime(dt.year, dt.month, dt.day, tm.hour, tm.minute)
            limit1 = book_dt_tm+timedelta(minutes=30)
            limit2 = book_dt_tm-timedelta(minutes=30)
            # print(f"Limit Time {limit}")
            if inp>=book_dt_tm and inp<limit1: # User Selected Time Falls within after 30 minutes of a booking
                return True
            elif inp>limit2 and inp<= book_dt_tm : # Selected Time Falls within previous 30 minutes
                return True
        return False

    doctors = Doctor_details.query.all()
    patients = Patient_details.query.all()
    form = Appointment_create()
    doctor_choices = [(doctor.name, f"{doctor.name} | {doctor.speciality}") for doctor in doctors]
    patient_choices = [(patient.name, f"{patient.name}") for patient in patients]
    speciality = [doctor.speciality for doctor in doctors]
    form.doctor_name.choices =doctor_choices
    form.patient_name.choices =patient_choices

    # If form has been submitted
    if request.method == 'POST':

        if form.validate_on_submit():
            doctor_name = form.doctor_name.data
            patient_name = form.patient_name.data
            date = form.date.data
            time = form.time.data
            hemo = form.hemo.data
            bmi = form.bmi.data
            platelets = form.platelets.data
            blood_sugar = form.blood_sugar.data
            blood_pressure = form.blood_pressure.data
            # Appointments.query.filter_by(time=)
            
            doctor = Doctor_details.query.filter_by(name=doctor_name).first()

            doctor_specialization = doctor.speciality
            inp_datetime = datetime(date.year, date.month, date.day, time.hour, time.minute)
            now = datetime.now()

            # print(f'timenow = {now}')
            # print(f'input time = {inp_datetime}')
            # Check if Doctor Appointments Less than 15
            appointments_for_doctors = Appointments.query.filter_by(doctor_name=doctor_name).count()
            # print(f'Already Booked Appointsments for {doctor_name}: {appointments_for_doctors}')
            booked = Appointments.query.filter(Appointments.date>= now.date())
            if appointments_for_doctors >= 15:
                flash("Doctor is pre-booked", "warning")
            # Check if Time Slot not available:
            elif now>inp_datetime:
                flash("Can't Change Past.", "warning")
            elif time_booked(inp_datetime, booked):
                flash("Time Slot is Booked", "warning")


            else:
                # Add the patient to the database
                details = Appointments(patient_name,doctor_name,doctor_specialization,date,time, hemo,bmi,platelets,blood_sugar,blood_pressure)
                db.session.add(details)
                db.session.commit()
                flash("Appointment Created successfully", "success")
    return render_template("Appointment_patient.html", title="Create Appointment", form=form, patient_name=session['username'])


    # return render_template("Appointment_patient.html", title="Create Patient")

# ==================================================================================
#                                 Patient Appointment
# ==================================================================================


@app.route("/CreatePatient", methods=['GET', 'POST'])
def create_patient():


    # # Check that an authorised user only can access this functionality
    if check_session() != 'None':
        flash('Please Log out before creating new user.', 'danger')
        return redirect(url_for('main'))

    # If form has been submitted
    form = Patient_create()
    if request.method == 'POST':
        if form.validate_on_submit():
            ssn_id = form.ssn_id.data
            name = form.patient_name.data
            age = form.patient_age.data
            date = form.date.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            password = form.password.data
            # Add the patient to the database
            details = Patient_details(
                name, age, ssn_id, date, address, city, state, "P", status="Admitted")
            db.session.add(details)
            db.session.add(UserStore(str(ssn_id)+'@P',password))
            db.session.commit()
            flash("Registration successfully", "success")

            return redirect(url_for('appointment'))
    return render_template("create_patient.html", title="Create Patient", form=form, patient_name=session['username'])


@app.route("/DeletePatient", methods=["GET", "POST"])
def leadto_delete():
    if check_session() != 'Patient':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    
    form = DeletePatient_Form()
    if request.method == 'POST':
        ssn_data = form.ssn_id.data
        print("INITIATING REDIRECT")
        try:
            Patient_details.query.filter_by(ssn_id=ssn_data).delete()
            UserStore.query.filter_by(login=str(ssn_data)+'@P').delete()
            db.session.commit()
            flash("Deleted successfully", "success")
        except:
            pass
        return redirect(url_for('main'))
    patients = Patient_details.query.all()
    choices = [(patient.ssn_id, f"{patient.name} | {patient.ssn_id}") for patient in patients]

    form.ssn_id.choices = choices

    return render_template("delete_patient1.html", title="Delete Patient", form=form, patient_name=session['username'])



@app.route("/LeadtoUpdate", methods=["GET", "POST"])
def leadto_update():
    if check_session() != 'Patient':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    
    form = LeadToUpdate_Form()
    if request.method == 'POST':
        ssn_data = form.ssn_id.data
        print("INITIATING REDIRECT")
        return redirect(url_for('update_patient1', rec_ssn_data = ssn_data))
    patients = Patient_details.query.all()
    choices = [(patient.ssn_id, f"{patient.name} | {patient.ssn_id}") for patient in patients]

    form.ssn_id.choices = choices

    return render_template("lead_to_update.html", title="Update Patient", form=form, patient_name=session['username'])


@app.route('/PrescribeMedicine/<patient_name>', methods=["GET", "POST"])
def prescribe_medicine(patient_name):
    if check_session() != 'Doctor':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    
    form = PrescriptionForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            name = form.name.data
            amount = form.amount.data
            dosage = form.dosage.data
            
            print(patient_name)
            pat = Patient_details.query.filter_by(name=patient_name).first()
            medicine = Patient_medicine(pat.id,name=name, amount=amount, dosage=dosage )

            db.session.add(medicine)
            db.session.commit()
            flash(f"{name} prescribed to {patient_name}", "success")

            return redirect(url_for('leadto_appointments'))


    return render_template("medicine_prescription.html", title="Prescribe Medicine", form=form, patient_name=patient_name)

# <---------------------------------------------------------------------------------------------->
# <---------------------------------------------------------------------------------------------->
# <---------------------------------------------------------------------------------------------->
@app.route('/PrescribedMedicines/<patient_name>', methods=["GET"])
def prescribed_medicine(patient_name):
    if check_session() == 'None':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))

    pat = Patient_details.query.filter_by(name=patient_name).first()
    medicines = Patient_medicine.query.filter_by(patient_id=pat.id)



    return render_template("medicine_prescribed.html", title="Prescribed Medicines", patient_name=patient_name, medicines=medicines)


@app.route("/LeadtoAppointments", methods=["GET", "POST"])
def leadto_appointments():
    if check_session() != 'Doctor':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    
    form = LeadToAppointments_Form()
    if request.method == 'POST':
        doctor_id = form.doctor_name.data
        print("INITIATING REDIRECT")
        return redirect(url_for('view_appointments', id=doctor_id))
    
    doctors = Doctor_details.query.all()
    choices = [(doctor.id, f"{doctor.name} | {doctor.speciality}") for doctor in doctors]
    print(choices)
    form.doctor_name.choices = choices

    return render_template("lead_to_appointments.html", title="Check Appointments", form=form)





@app.route("/UpdatePatient1/<rec_ssn_data>", methods=['GET', 'POST'])
def update_patient1(rec_ssn_data):
    print(rec_ssn_data)


    # Check that an authorised user only can access this functionality
    if check_session() != 'Patient':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))

    # If form has been submitted
    form = Update_Patient1_Form()
    pat = Patient_details.query.filter_by(ssn_id=rec_ssn_data).first()
    
    
    if request.method == 'POST':
        if form.validate_on_submit():
            ssn_id = form.ssn_id.data
            name = form.patient_name.data
            age = form.patient_age.data
            date = form.date.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            # Add the patient to the database
            pat: Patient_details
            pat = Patient_details.query.filter_by(ssn_id=ssn_id).first()
            pat.name = name
            pat.age = age
            pat.admission_date = date
            pat.address = address
            pat.city = city
            pat.state = state

            db.session.add(pat)
            db.session.commit()
            flash("Updated successfully", "success")

            return redirect(url_for('update_patient1', rec_ssn_data = ssn_id))

    form.ssn_id.data = rec_ssn_data
    form.patient_name.data = pat.name
    form.patient_age.data = pat.age
    form.date.data = pat.admission_date
    form.address.data = pat.address
    form.city.data = pat.city
    form.state.data = pat.state


    return render_template("update_patient1.html", title="Update Patient", form=form, patient_name=session['username'])


@app.route("/CreateDoctor", methods=['GET', 'POST'])
def create_doctor():


    # Check that an authorised user only can access this functionality
    if check_session() == 'Patient':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))

    # If form has been submitted
    form = Doctor_create()
    if request.method == 'POST':
        if form.validate_on_submit():
            doctor_name = form.doctor_name.data
            login_type = 'D'
            doctor_speciality = form.doctor_speciality.data
            qualify_n_experience = form.qualify_n_experience.data
            ssn = form.ssn_id.data

            # Add the patient to the database
            details = Doctor_details(doctor_name, ssn, doctor_speciality, qualify_n_experience, login_type)
            password = form.password.data
            db.session.add(UserStore(str(ssn)+'@D',password))

            db.session.add(details)
            db.session.commit()
            flash("Registration successfully", "success")
    return render_template("create_doctor.html", title="Create Doctor", form=form)


@app.route("/ViewAppointments/<id>", methods=['GET'])
def view_appointments(id):
    print("doctor database id = ", id)


    # Check that an authorised user only can access this functionality
    if check_session() != 'Doctor':
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))

    doctor = Doctor_details.query.filter_by(id=id).first()
    appointments = Appointments.query.filter_by(doctor_name=doctor.name)
    return render_template("view_appointment.html", title="View Appointments", appointments=appointments)
    # If form has been submitted
   
# ==================================================================================
#                              Delete an existing patient
# ==================================================================================

# ==================================================================================
#                    Update the detains of an existing patient
# ==================================================================================

# ==================================================================================
#                   View all the admitted patients in record
# ==================================================================================


@app.route("/ViewAllPatients")
def view_patient():

    # Check that an authorised user only can access this functionality
    # if check_session() != 'registration_desk_executive':
    #     flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
    #     return redirect(url_for('main'))
    # Query for all admitted patients
    patient = Patient_details.query.filter_by(status="Admitted")
    return render_template("view_patients.html", patients=patient)


# ==================================================================================
#                                   Issue Medicines
# ==================================================================================


@app.route("/GetPatientDetails/Medicine", methods=["GET", "POST"])
def get_patient():

    # Check that an authorised user only can access this functionality
    # if check_session() != 'pharmacy_executive':
    #     flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
    #     return redirect(url_for('main'))

    form = Patient_delete()
    if request.method == 'POST':
        if form.validate_on_submit():
            global pid
            global issue_med
            pid = int(form.patient_id.data)
            # Query for patient details
            patient = Patient_details.query.filter(
                Patient_details.id == int(form.patient_id.data))
            for patient_1 in patient:
                if patient_1:
                    flash("Patient found!", "success")
                    issue_med = None
                    medicine = med_patient(patient_1)
                    if medicine != None:
                        return render_template("get_patient_details.html", title="Search patient", patient=patient, medicine=medicine.all())
                    else:
                        return render_template("get_patient_details.html", title="Search patient", patient=patient)
            flash("patient not found", "danger")
    return render_template("get_patient_details.html", title="Get Patient Details", form=form)


# @app.route("/IssueMedicine", methods=["GET", "POST"])
# def issue_medicine():
#     # Check that an authorised user only can access this functionality
#     if check_session() != 'pharmacy_executive':
#         flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
#         return redirect(url_for('main'))
#     global issue_med
#     global pid
#     form = issue_medicine_form()
#     form.medicine_name.choices = []
#     medicine = Medicine.query.all()
#     for med in medicine:
#         # Populate the medicine select form
#         form.medicine_name.choices += [(med.medicine_name, med.medicine_name + ' || Qty: ' + str(med.medicine_quantity))]
#     if form.validate_on_submit():
#         name = form.medicine_name.data
#         quantity = form.quantity.data
#         # Query for medicines
#         med = Medicine.query.filter(
#             Medicine.medicine_name == form.medicine_name.data).first()
#         medid = med.id
#         rate = med.medicine_amount
#         # Update issue_med dict
#         if issue_med == None:
#             issue_med = {}
#             issue_med[name] = {
#                 'name': name, 'quantity': quantity, 'medid': medid, 'rate': rate}
#         else:
#             issue_med[name] = {
#                 'name': name, 'quantity': quantity, 'medid': medid, 'rate': rate}
#         flash("Medicine Added!", "success")
#         return render_template("issue_medicine.html", form=form, medicine=issue_med)
#     return render_template("issue_medicine.html", form=form, medicine=issue_med)


@app.route("/medicine_update", methods=["GET", "POST"])
def update():
    # Check that an authorised user only can access this functionality
    # if check_session() != 'pharmacy_executive':
    #     flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
    #     return redirect(url_for('main'))
    global issue_med
    global pid
    for i in issue_med:
        med_name = str(issue_med[i]['name'])
        med_id = int(issue_med[i]['medid'])
        med_quant = int(issue_med[i]['quantity'])
        # Query for Medicines
        medicine = Medicine.query.filter(
            Medicine.medicine_name == med_name).first()
        current_quant = medicine.medicine_quantity
        new_quant = current_quant-med_quant
        # Query for patient_medicines
        patient = Patient_Medicine.query.filter(
            Patient_Medicine.patient_id == pid, Patient_Medicine.medicine_id == med_id).first()
        if patient == None:
            # Query for Patient_Medicine 
            db.session.add(Patient_Medicine(
                patient_id=pid, medicine_quantity=med_quant, medicine_id=med_id))
            medicine.medicine_quantity = new_quant
            db.session.commit()
        else:
            # Update Medicine Quantity
            medicine.medicine_quantity = new_quant
            patient.medicine_quantity += med_quant
            db.session.commit()
    issue_med = None
    flash("successfully updated", "success")
    return redirect(url_for('get_patient'))




# ==================================================================================
#                                   Diagnostics
# ==================================================================================


# ==================================================================================
#                                   Patient Billing
# ==================================================================================

# ==================================================================================
#                                 Delete the user Session
# ==================================================================================


@app.route("/logout")
def logout():
    # Remove user from the session
    if not check_session():
        flash('You are not authorised to access that! Please login with proper credentials.', 'danger')
        return redirect(url_for('main'))
    if 'user' in session:
        session['user'] = None
        flash("Successfully Logged Out!", "success")
    return redirect(url_for('main'))
