a. HIPAA and GDPR Compliance
Data Anonymization:

Mask or anonymize patient data when it is no longer needed for diagnostic purposes.
Audit Trails:

Log all access and changes to patient data with timestamps and user IDs.
Store audit logs securely for at least 6 years (as per HIPAA guidelines).
Training and Awareness:

Ensure all developers and operators handling the swarm are trained on HIPAA and GDPR regulations.

5. Agent Communication Protocol
Secure Inter-Agent Communication:

Encrypt messages between agents using shared secrets or public/private key pairs.
Communication Verification:

Add integrity checks (e.g., HMAC) to ensure messages between agents haven’t been tampered with.

- Structured outputs
- List of possible ICD 10 codes with supporting evidences, final_summary icd 10,

- icd 10
  - supporting evidence
- icd 10
  - supporting evidence
- icd 10
  - supporting evidence
- icd 10
  - supporting evidence
- most_likely_code:
   - code:
   - summary


- patient may have many conditions,
- patient needs to identify list of icd 10s, for every code, what is the servicing provider, what is evidence for that code including reference to page number, 
- for every patient, generate unique id, 
- for every doc in the database, attach some unique id, when we query the data using that id, 
- same patient can be handled differently, document from different year'
- for some docs, average doc size is 20+ pages, but others is 300+, biggest document is 30,000 pages, overview of the entire patient and medical history of the patient
- handle the number of pages
- turn around time, handle processes of 100+ pages, process 30,000 pages



Diagnosis or symptions into icd 10 codes
  - agent that goes searches, what labs we could order 
  - Based off a diagnosis, find a lab to monitor condition
  - rule out the condition or monitor the condition
  - lab test results analysis agent, based off lab results -> what diagnosis
  - not just labs, 
  - kidney stones or ultra sound, 
  - monitoring agent that finds how to best monitor a patient
  - urine lab, they have stones, what type of kidney stones, 
  - testing agent for evaluation
  - all conditions and records of all the diagnosises, 
  - is this condition being monitored or not 
  - results of the lab, maybe 
  - alert doctor if diagnosis 
  - identify lab reports from pdfs or ehrs, in reports identify diagnosis, identify normal baselines, and abnormal line, 
  - diagnositic tests for the lab agent
- For each diagnosis, pull lab results,
- egfr
- for each diagnosis, pull lab ranges,
- pull ranges for diagnosis

- if the diagnosis is x, then the lab ranges should be a to b
- train the agents, increase the load of input
- medical history sent to the agent
- setup rag for the agents
- run the first agent -> kidney disease -> don't know the stage -> stage 2 -> lab results -> indicative of stage 3 -> the case got elavated ->
- how to manage diseases and by looking at correlating lab, docs, diagnoses
- put docs in rag ->
- monitoring, evaluation, and treatment
- can we confirm for every diagnosis -> monitoring, evaluation, and treatment, specialized for these things
- find diagnosis -> or have diagnosis, -> for each diagnosis are there evidence of those 3 things
- swarm of those 4 agents, ->
- fda api for healthcare for commerically available papers
- what are the labs that can be ruled out to verify each diagnosis, lab results,
- lab result
- labs and diagbnoses
- 3 main labs one is quest diagnosists, lab core,
- reference laboroties,
- top 15k diagnosises, find out what labs get ordered, another agent will say what labs results indicidate this particular diagnosis
- for monitoring do we order
what lab results indicate this condition

- find lab in document, this is the lab we found, when user click on lab, redirect to diagnosis
- multiple lab results, multiple diagnosiss, indicative of thi code, this code is because of that code of that lab result
- find the position of the lab result in the document, find the diagnosis in the document, find the lab result in the document, find the diagnosis in the document
- result that indicates the abnormal result in the lab that refers to the diagnosis.
- showcase where in the document is the lab results -> correlation

Output format for the api:
  - report:
  - diagnosis_code:
  - lab:
  