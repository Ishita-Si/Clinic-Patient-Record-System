import streamlit as st
from db import get_connection
from datetime import datetime
import pandas as pd

st.title("Clinic Patient Record System")

menu = ["Add Patient", "View Patients", "Add Visit", "View Visit History","Dashboard", "Delete Patient"]

choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Patient":
    st.subheader("Add New Patient")
    name = st.text_input("Patient Name")
    age = st.number_input("Age", min_value=0)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    contact = st.text_input("Contact Info")

    if st.button("Add Patient"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO patients (name, age, gender, contact) VALUES (%s, %s, %s, %s)",
                       (name, age, gender, contact))
        conn.commit()
        conn.close()
        st.success(f"Patient '{name}' added successfully!")

elif choice == "View Patients":
    st.subheader("📋 Patient List")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    data = cursor.fetchall()
    conn.close()

    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("No patients found.")


elif choice == "Add Visit":
    st.subheader("🩺 Add Visit Record")

  
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()
    conn.close()

    patient_dict = {f"{name} (ID: {pid})": pid for pid, name in patients}
    selected_patient = st.selectbox("Select Patient", list(patient_dict.keys()))
    visit_date = st.date_input("Visit Date", value=datetime.today())
    symptoms = st.text_area("Symptoms")
    diagnosis = st.text_area("Diagnosis")

    if st.button("Add Visit"):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO visits (patient_id, visit_date, symptoms, diagnosis) VALUES (%s, %s, %s, %s)",
            (patient_dict[selected_patient], visit_date, symptoms, diagnosis)
        )
        conn.commit()
        conn.close()
        st.success("Visit record added!")


elif choice == "View Visit History":
    st.subheader("📋 Visit History")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.visit_id, p.name, v.visit_date, v.symptoms, v.diagnosis
        FROM visits v
        JOIN patients p ON v.patient_id = p.patient_id
        ORDER BY v.visit_date DESC
    """)
    visits = cursor.fetchall()
    conn.close()

    if visits:
        df = pd.DataFrame(visits, columns=["Visit ID", "Patient Name", "Visit Date", "Symptoms", "Diagnosis"])
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", data=csv, file_name="visit_history.csv", mime='text/csv')
    else:
        st.info("No visit history found.")


elif choice == "Delete Patient":
    st.subheader(" Delete Patient Record")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()
    conn.close()

    if patients:
        patient_dict = {f"{name} (ID: {pid})": pid for pid, name in patients}
        selected_patient = st.selectbox("Select Patient to Delete", list(patient_dict.keys()))

        if st.button("Delete Patient"):
            confirm = st.warning("Are you sure? This will delete the patient and all their visit records.", icon="⚠️")
            really = st.checkbox("Yes, I understand. Proceed.")

            if really:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients WHERE patient_id = %s", (patient_dict[selected_patient],))
                conn.commit()
                conn.close()
                st.success("Patient deleted successfully.")
    else:
        st.info("No patients available to delete.")
elif choice == "Dashboard":
    st.subheader("📊 Clinic Stats Dashboard")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM patients")
    total_patients = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM visits")
    total_visits = cursor.fetchone()[0]

    cursor.execute("""
        SELECT symptoms, COUNT(*) AS count
        FROM visits
        GROUP BY symptoms
        ORDER BY count DESC
        LIMIT 1
    """)
    top_symptom = cursor.fetchone()
    conn.close()

    st.metric("👥 Total Patients", total_patients)
    st.metric("🩺 Total Visits", total_visits)
    if top_symptom:
        st.metric("🔥 Most Common Symptom", top_symptom[0])
    else:
        st.info("No symptom data yet.")
