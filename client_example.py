from mcs.api_client import MCSClient

client = MCSClient()


print(client.run_medical_coder(
    patient_id="123",
    case_description="I have a headache and a cough",
    summarization=True,
    patient_docs="patient_docs.txt",
))