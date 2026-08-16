import requests

BASE_URL = "http://localhost:1337/api"

# ------------------------
# PATIENT
# ------------------------

def find_patient(phone):
    if not phone or not str(phone).strip():
        return None

    try:
        url = f"{BASE_URL}/patients"

        params = {
            "filters[phone][$eq]": str(phone).strip()
        }

        response = requests.get(url, params=params, timeout=3)

        if response.status_code != 200:
            return None

        patients = response.json().get("data", [])

        if not patients:
            return None

        patient = patients[0]

        return {
            "id": patient["id"],
            "documentId": patient["documentId"],
            "name": patient.get("name"),
            "phone": patient.get("phone"),
            "age": patient.get("age"),
            "gender": patient.get("gender"),
            "preferred_language": patient.get("preferred_language")
        }

    except requests.exceptions.RequestException as error:
        print(f"Patient lookup failed: {error}")
        return None


def create_patient(patient_data):
    try:
        url = f"{BASE_URL}/patients"

        payload = {
            "data": patient_data
        }

        response = requests.post(url, json=payload, timeout=3)

        if response.status_code in [200, 201]:
            return response.json().get("data")

        return None

    except requests.exceptions.RequestException:
        return None


# ------------------------
# DOCTOR
# ------------------------

def get_doctors(department_name):
    try:
        url = f"{BASE_URL}/doctors?populate=department"

        response = requests.get(url, timeout=3)

        if response.status_code != 200:
            return []

        doctors = response.json().get("data", [])
        result = []

        for doctor in doctors:
            department = doctor.get("department")

            if department and department.get("name") == department_name:
                result.append({
                    "id": doctor["id"],
                    "documentId": doctor["documentId"],
                    "name": doctor["name"],
                    "department": department.get("name"),
                    "specialization": doctor.get("specialization"),
                    "available_days": doctor.get("available_days", []),
                    "available_time": doctor.get("available_time"),
                    "consultation_fee": doctor.get("consultation_fee"),
                    "language": doctor.get("language")
                })

        return result

    except requests.exceptions.RequestException:
        return []


# ------------------------
# APPOINTMENT
# ------------------------

def create_appointment(appointment_data):
    try:
        url = f"{BASE_URL}/appointments"

        payload = {
            "data": {
                "appointment_date": appointment_data["appointment_date"],
                "appointment_time": appointment_data["appointment_time"],
                "symptoms": ", ".join(appointment_data.get("symptoms", [])),
                "appointment_status": "Confirmed",
                "patient": appointment_data.get("patient_document_id") or appointment_data.get("patient_id"),
                "doctor": appointment_data["doctor_document_id"]
            }
        }

        response = requests.post(url, json=payload, timeout=3)

        print("Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code in [200, 201]:
            return response.json().get("data")

        return None

    except requests.exceptions.RequestException as e:
        print(e)
        return None

# ------------------------
# HISTORY
# ------------------------

def get_patient_history(patient_document_id):
    try:
        url = f"{BASE_URL}/appointments"

        params = {
            "populate[0]": "doctor",
            "populate[1]": "doctor.department",
            "populate[2]": "patient",
            "sort": "appointment_date:desc"
        }

        response = requests.get(url, params=params, timeout=3)

        if response.status_code != 200:
            print(f"History fetch failed: {response.text}")
            return None

        appointments = response.json().get("data", [])

        # Filter appointments belonging to this patient
        patient_appointments = [
            appt for appt in appointments
            if appt.get("patient") and
            appt["patient"].get("documentId") == patient_document_id
        ]

        if not patient_appointments:
            return None

        # Latest appointment (already sorted by date descending)
        last = patient_appointments[0]

        doctor = last.get("doctor")
        symptoms = last.get("symptoms", "")

        return {
            "last_doctor": doctor.get("name") if doctor else None,
            "last_department": (
                doctor.get("department", {}).get("name")
                if doctor else None
            ),
            "last_visit_date": last.get("appointment_date"),
            "last_appointment_time": last.get("appointment_time"),
            "last_appointment_status": last.get("appointment_status"),
            "previous_symptoms": [
                s.strip() for s in symptoms.split(",")
            ] if symptoms else [],
            "visit_count": len(patient_appointments)
        }

    except requests.exceptions.RequestException as e:
        print(f"History error: {e}")
        return None


# ------------------------
# TEST
# ------------------------

def test_connection():
    url = f"{BASE_URL}/doctors?populate=department"

    response = requests.get(url)

    print(response.status_code)
    print(response.json())






# import requests

# BASE_URL = "http://localhost:1337/api"

# # def find_patient(phone):

# #     url = f"{BASE_URL}/patients"

# #     params = {
# #         "filters[phone][$eq]": phone
# #     }

# #     response = requests.get(url, params=params)

# #     if response.status_code != 200:
# #         return None

# #     data = response.json()

# #     if data.get("data"):
# #         return data["data"][0]

# #     return None

# # def create_patient(patient_data):

# #     url = f"{BASE_URL}/patients"

# #     payload = {
# #         "data": patient_data
# #     }

# #     response = requests.post(url, json=payload)

# #     if response.status_code not in [200, 201]:
# #         return None

# #     return response.json().get("data")

# import requests

# BASE_URL = "http://localhost:1337/api"

# def find_patient(phone):
#     try:
#         url = f"{BASE_URL}/patients"

#         params = {
#             "filters[phone][$eq]": phone
#         }

#         response = requests.get(url, params=params, timeout=3)

#         if response.status_code != 200:
#             return None

#         data = response.json()

#         if data.get("data"):
#             return data["data"][0]

#         return None

#     except requests.exceptions.RequestException:
#         return None


# def create_patient(patient_data):
#     try:
#         url = f"{BASE_URL}/patients"

#         payload = {
#             "data": patient_data
#         }

#         response = requests.post(url, json=payload, timeout=3)

#         if response.status_code in [200, 201]:
#             return response.json().get("data")

#         return {
#             "id": 1,
#             **patient_data
#         }

#     except requests.exceptions.RequestException:
#         return {
#             "id": 1,
#             **patient_data
#         }

# def get_doctors(department_name):

#     url = f"{BASE_URL}/doctors"

#     params = {
#         "populate": "department"
#     }

#     response = requests.get(url, params=params)

#     if response.status_code != 200:
#         return []

#     doctors = response.json()["data"]

#     result = []

#     for doctor in doctors:
#         dept = doctor.get("department")

#         if dept and dept.get("name") == department_name:
#             result.append({
#                 "id": doctor["id"],
#                 "name": doctor["name"],
#                 "available_time": doctor.get("available_time"),
#                 "consultation_fee": doctor.get("consultation_fee")
#             })

#     return result

#     # doctors = {
#     #     "Cardiology": [
#     #         {
#     #             "id": 1,
#     #             "name": "Dr. Raj Sharma"
#     #         }
#     #     ],

#     #     "Orthopedics": [
#     #         {
#     #             "id": 2,
#     #             "name": "Dr. Amit Gupta"
#     #         }
#     #     ],

#     #     "General Medicine": [
#     #         {
#     #             "id": 3,
#     #             "name": "Dr. Neha Verma"
#     #         }
#     #     ]
#     # }

#     # return doctors.get(department, [])

# def create_appointment(appointment_data):

#     # url = f"{BASE_URL}/appointments"

#     # payload = {
#     #     "data": appointment_data
#     # }

#     # response = requests.post(url, json=payload)

#     # return response.json()["data"]

#     return {
#         "id": 101,
#         "status": "Confirmed",
#         **appointment_data
#     }

# def get_patient_history(patient_id):

#     # url = f"{BASE_URL}/appointments"

#     # params = {
#     #     "filters[patient][id][$eq]": patient_id
#     # }

#     # response = requests.get(url, params=params)

#     # return response.json()["data"]

#     return {
#         "last_doctor": "Dr. Raj Sharma",
#         "last_department": "Cardiology",
#         "last_visit_date": "2026-08-10",
#         "previous_symptoms": [
#             "chest pain",
#             "shortness of breath"
#         ]
#     }

# def test_connection():
#     url = f"{BASE_URL}/doctors"

#     response = requests.get(url)

#     print(response.status_code)
#     print(response.text)