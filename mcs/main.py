

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from fastapi import requests
from pydantic import BaseModel, Field
from swarm_models import GPT4VisionAPI, OpenAIChat
from swarms import Agent, AgentRearrange
from swarms.telemetry.capture_sys_data import log_agent_data

from mcs.security import (
    KeyRotationPolicy,
    SecureDataHandler,
    secure_data,
)

model_name = "gpt-4o"

model = OpenAIChat(
    model_name=model_name,
    max_tokens=4000,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


def patient_id_uu():
    return str(uuid.uuid4().hex)


class RAGAPI:
    def __init__(
        self,
        base_url: str = None,
    ):
        self.base_url = base_url

    def query_rag(self, query: str):
        """
        Query the RAG API with a given prompt.
        """
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={"query": query},
            )
            return str(response.json())
        except Exception as e:
            print(f"An error occurred during the RAG query: {e}")
            return None


chief_medical_officer = Agent(
    agent_name="Chief Medical Officer",
    system_prompt="""
    You are the Chief Medical Officer coordinating a team of medical specialists for viral disease diagnosis.
    Your responsibilities include:
    - Gathering initial patient symptoms and medical history
    - Coordinating with specialists to form differential diagnoses
    - Synthesizing different specialist opinions into a cohesive diagnosis
    - Ensuring all relevant symptoms and test results are considered
    - Making final diagnostic recommendations
    - Suggesting treatment plans based on team input
    - Identifying when additional specialists need to be consulted
    - For each diferrential diagnosis provide minimum lab ranges to meet that diagnosis or be indicative of that diagnosis minimum and maximum
    
    Format all responses with clear sections for:
    - Initial Assessment (include preliminary ICD-10 codes for symptoms)
    - Differential Diagnoses (with corresponding ICD-10 codes)
    - Specialist Consultations Needed
    - Recommended Next Steps
    
    
    """,
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)

# virologist = Agent(
#     agent_name="Virologist",
#     system_prompt="""You are a specialist in viral diseases. For each case, provide:

#     Clinical Analysis:
#     - Detailed viral symptom analysis
#     - Disease progression timeline
#     - Risk factors and complications

#     Coding Requirements:
#     - List relevant ICD-10 codes for:
#         * Confirmed viral conditions
#         * Suspected viral conditions
#         * Associated symptoms
#         * Complications
#     - Include both:
#         * Primary diagnostic codes
#         * Secondary condition codes

#     Document all findings using proper medical coding standards and include rationale for code selection.""",
#     llm=model,
#     max_loops=1,
#     dynamic_temperature_enabled=True,
# )

internist = Agent(
    agent_name="Internist",
    system_prompt="""
    You are an Internal Medicine specialist responsible for comprehensive evaluation.
    
    For each case, provide:
    
    Clinical Assessment:
    - System-by-system review
    - Vital signs analysis
    - Comorbidity evaluation
    
    Medical Coding:
    - ICD-10 codes for:
        * Primary conditions
        * Secondary diagnoses
        * Complications
        * Chronic conditions
        * Signs and symptoms
    - Include hierarchical condition category (HCC) codes where applicable
    
    Document supporting evidence for each code selected.""",
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)

medical_coder = Agent(
    agent_name="Medical Coder",
    system_prompt="""You are a certified medical coder responsible for:
    
    Primary Tasks:
    1. Reviewing all clinical documentation
    2. Assigning accurate ICD-10 codes
    3. Ensuring coding compliance
    4. Documenting code justification
    
    Coding Process:
    - Review all specialist inputs
    - Identify primary and secondary diagnoses
    - Assign appropriate ICD-10 codes
    - Document supporting evidence
    - Note any coding queries
    
    Output Format:
    1. Primary Diagnosis Codes
        - ICD-10 code
        - Description
        - Supporting documentation
    2. Secondary Diagnosis Codes
        - Listed in order of clinical significance
    3. Symptom Codes
    4. Complication Codes
    5. Coding Notes""",
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)

synthesizer = Agent(
    agent_name="Diagnostic Synthesizer",
    system_prompt="""You are responsible for creating the final diagnostic and coding assessment.
    
    Synthesis Requirements:
    1. Integrate all specialist findings
    2. Reconcile any conflicting diagnoses
    3. Verify coding accuracy and completeness
    
    Final Report Sections:
    1. Clinical Summary
        - Primary diagnosis with ICD-10
        - Secondary diagnoses with ICD-10
        - Supporting evidence
    2. Coding Summary
        - Complete code list with descriptions
        - Code hierarchy and relationships
        - Supporting documentation
    3. Recommendations
        - Additional testing needed
        - Follow-up care
        - Documentation improvements needed
    
    Include confidence levels and evidence quality for all diagnoses and codes.""",
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)

synthesizer = Agent(
    agent_name="Hierarchical Summarization Agent",
    system_prompt="""You are an expert in hierarchical summarization, skilled at condensing complex medical data into structured, efficient, and accurate summaries. Your task is to generate concise and well-organized summaries that prioritize the most important information while maintaining clarity and completeness.

    ### Summarization Goals:
    1. Extract and prioritize key insights from detailed medical data.
    2. Present information hierarchically, starting with the most critical and broad insights before including finer details.
    3. Ensure summaries are actionable, evidence-backed, and easy to understand by medical professionals.

    ### Output Structure:
    #### 1. Executive Summary:
    - **Primary Focus**: State the main diagnosis or issue.
    - **Key Supporting Evidence**: Highlight critical findings (e.g., lab results, imaging, symptoms).
    - **ICD-10 Codes**: Include codes relevant to the primary diagnosis.

    #### 2. Detailed Findings:
    - **Secondary Issues**: List additional diagnoses or findings with brief explanations.
    - **Supporting Details**: Provide summarized evidence for each finding.

    #### 3. Action Plan:
    - **Recommendations**: Outline immediate next steps (e.g., additional tests, treatments, follow-ups).
    - **Unresolved Questions**: Highlight gaps in data or areas requiring further investigation.

    ### Guidelines for Summarization:
    - **Be Concise**: Use bullet points and short paragraphs for readability.
    - **Prioritize Information**: Rank findings by clinical relevance and urgency.
    - **Maintain Accuracy**: Ensure all summaries are backed by provided data and include confidence levels for findings.
    - **Simplify Complex Data**: Translate medical jargon into clear and accessible language where appropriate.

    ### Example Workflow:
    1. Review the input data for critical findings.
    2. Group findings into primary and secondary categories based on their importance.
    3. Summarize key insights in hierarchical order, ensuring clarity and precision.

    ### Output Style:
    - Clear and professional tone.
    - Consistent structure with easy-to-scan sections.
    - Minimize redundancy while ensuring completeness.""",
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)

summarizer_agent = Agent(
    agent_name="Condensed Summarization Agent",
    system_prompt="""You are an expert in creating concise and actionable summaries from tweets, short texts, and small reports. Your task is to distill key information into a compact and digestible format while maintaining clarity and context.

    ### Summarization Goals:
    1. Identify the most critical message or insight from the input text.
    2. Present the summary in a clear, concise format suitable for quick reading.
    3. Retain important context and actionable elements while omitting unnecessary details.

    ### Output Structure:
    #### 1. Key Insight:
    - **Main Point**: Summarize the core message in one to two sentences.
    - **Relevant Context**: Include key supporting details (if applicable).

    #### 2. Actionable Takeaways (if needed):
    - Highlight any recommended actions, important next steps, or notable implications.

    ### Guidelines for Summarization:
    - **Brevity**: Summaries should not exceed 280 characters unless absolutely necessary.
    - **Clarity**: Avoid ambiguity or technical jargon; focus on accessibility.
    - **Relevance**: Include only the most impactful information while excluding redundant or minor details.
    - **Tone**: Match the tone of the original content (e.g., professional, casual, or informative).

    ### Example Workflow:
    1. Analyze the input for the primary message or intent.
    2. Condense the content into a clear, actionable summary.
    3. Format the output to ensure readability and coherence.

    ### Output Style:
    - Clear, concise, and easy to understand.
    - Suitable for social media or quick report overviews.
    """,
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=False,  # Keeps summaries consistently concise
)

lab_matcher = Agent(
    agent_name="Laboratory-Test-Matcher",
    system_prompt="""
    You are a specialist in laboratory medicine responsible for matching diagnoses with appropriate laboratory tests, providing reference ranges, and identifying the most suitable laboratory locations for patients.

    Primary Responsibilities:
    1. Match diagnoses to appropriate laboratory tests
    2. Provide reference ranges and interpretation guidelines
    3. Indicate test priorities and sequences
    4. Specify collection requirements
    5. Identify the most suitable laboratory locations for patients based on their location and diagnosis

    For each case, provide:

    Test Recommendations:
    - Primary diagnostic tests
    - Confirmatory tests
    - Monitoring tests
    - Differential diagnosis tests
    
    Test Details:
    - Test names and codes (LOINC if applicable)
    - Specimen requirements
    - Reference ranges by:
        * Age
        * Sex
        * Special conditions
    - Critical values
    
    Clinical Correlation:
    - Expected results for specific conditions
    - Interfering factors
    - Result interpretation guidelines
    - Follow-up testing recommendations
    
    Laboratory Location Recommendations:
    - Identify the nearest laboratory locations to the patient based on their address
    - Provide information on laboratory hours, contact details, and any specific requirements for specimen collection
    
    Documentation Requirements:
    - Medical necessity justification
    - ICD-10 codes for coverage
    - Frequency limitations
    - Special authorization requirements
    
    Output Format:
    1. Primary Test Panel
        - Essential tests with rationale
        - Reference ranges
        - Expected results
    2. Secondary Tests
        - Confirmatory tests
        - Monitoring tests
    3. Specimen Requirements
        - Collection instructions
        - Processing notes
    4. Interpretation Guidelines
        - Result interpretation
        - Clinical correlation
    5. Laboratory Location Information
        - Nearest laboratory locations to the patient
        - Laboratory details (hours, contact, specimen collection requirements)
    6. Coverage Documentation
        - Required ICD-10 codes
        - Medical necessity documentation
        
    Always specify:
    - Test sensitivity and specificity when available
    - Time considerations (STAT vs. routine)
    - Cost considerations
    - Alternative test options
    """,
    llm=model,
    max_loops=1,
    dynamic_temperature_enabled=True,
)

# Create agent list
agents = [
    chief_medical_officer,
    # virologist,
    internist,
    medical_coder,
    synthesizer,
    # lab_matcher,
]

# Define diagnostic flow
flow = f"""{chief_medical_officer.agent_name} -> {internist.agent_name} -> {medical_coder.agent_name} -> {synthesizer.agent_name}"""


class MedicalCoderSwarmInput(BaseModel):
    mcs_id: Optional[str] = uuid.uuid4().hex
    patient_id: Optional[str]
    task: Optional[str]
    img: Optional[str]
    patient_docs: Optional[str]
    summarization: Optional[bool]


class MedicalCoderSwarmOutput(BaseModel):
    input: Optional[MedicalCoderSwarmInput]
    run_id: Optional[str] = Field(default=uuid.uuid4().hex)
    patient_id: Optional[str]
    agent_outputs: Optional[str]
    summarization: Optional[str]


class ManyMedicalCoderSwarmOutput(BaseModel):
    runs_id: Optional[str] = uuid.uuid4().hex
    runs: Optional[List[MedicalCoderSwarmOutput]]


class MedicalCoderSwarm:
    def __init__(
        self,
        name: str = "Medical-coding-diagnosis-swarm",
        description: str = "Comprehensive medical diagnosis and coding system",
        agents: list = agents,
        flow: str = flow,
        patient_id: str = "001",
        max_loops: int = 1,
        output_type: str = "all",
        output_folder_path: str = "reports",
        patient_documentation: str = None,
        agent_outputs: list = any,
        rag_enabled: bool = False,
        rag_url: str = None,
        user_name: str = "User",
        key_storage_path: str = None,
        summarization: bool = False,
        vision_enabled: bool = False,
        *args,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.agents = agents
        self.flow = flow
        self.patient_id = patient_id
        self.max_loops = max_loops
        self.output_type = output_type
        self.output_folder_path = output_folder_path
        self.patient_documentation = patient_documentation
        self.agent_outputs = agent_outputs
        self.rag_enabled = rag_enabled
        self.rag_url = rag_url
        self.user_name = user_name
        self.key_storage_path = key_storage_path
        self.summarization = summarization
        self.vision_enabled = vision_enabled
        self.agent_outputs = []
        self.patient_id = patient_id_uu()

        if self.vision_enabled:
            self.change_agent_llm()

        self.diagnosis_system = AgentRearrange(
            name="Medical-coding-diagnosis-swarm",
            description="Comprehensive medical diagnosis and coding system",
            agents=agents,
            flow=flow,
            max_loops=max_loops,
            output_type=output_type,
            *args,
            **kwargs,
        )

        if self.rag_enabled:
            self.diagnosis_system.memory_system = RAGAPI(
                base_url=rag_url
            )

        self.output_file_path = (
            f"medical_diagnosis_report_{patient_id}.md",
        )

        # Change the user name for all agents in the swarm
        self.change_agent_user_name(user_name)

        # Initialize with production configuration
        self.secure_handler = SecureDataHandler(
            master_key=os.environ["MASTER_KEY"],
            key_storage_path=self.key_storage_path,
            rotation_policy=KeyRotationPolicy(
                rotation_interval=timedelta(days=30),
                key_overlap_period=timedelta(days=2),
            ),
            auto_rotate=True,
        )

    def change_agent_llm(self):
        """
        Change the language model for all agents in the swarm.
        """
        model = GPT4VisionAPI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4o",
            max_tokens=4000,
        )

        for agent in self.agents:
            agent.llm = model

    def change_agent_user_name(self, user_name: str):
        """
        Change the user name for all agents in the swarm.
        """
        for agent in self.agents:
            self.user_name = user_name

        return agents

    def _run(
        self, task: str = None, img: str = None, *args, **kwargs
    ):
        """ """
        print("Running the medical coding and diagnosis system.")

        try:
            log_agent_data(self.to_dict())

            case_info = f"Patient Information: {self.patient_id} \n Timestamp: {datetime.now()} \n Patient Documentation {self.patient_documentation} \n Task: {task}"

            output = self.diagnosis_system.run(
                task=case_info, img=img, *args, **kwargs
            )

            if self.summarization is True:
                output = summarizer_agent.run(output)

            self.agent_outputs.append(output)
            log_agent_data(self.to_dict())

            return output
        except Exception as e:
            log_agent_data(self.to_dict())
            print(
                f"An error occurred during the diagnosis process: {e}"
            )

    def run(self, task: str = None, img: str = None, *args, **kwargs):
        try:

            if self.secure_handler:
                return self.secure_run(
                    task=task, img=img, *args, **kwargs
                )
            else:
                return self._run(task, img, *args, **kwargs)
        except Exception as e:
            log_agent_data(self.to_dict())
            print(
                f"An error occurred during the diagnosis process: {e}"
            )

    def secure_run(
        self, task: str = None, img: str = None, *args, **kwargs
    ):
        """
        Securely run the medical coding and diagnosis system.
        Ensures data is encrypted during transit and at rest.
        """
        print(
            "Starting secure run of the medical coding and diagnosis system."
        )

        try:
            # Log the current state of the system for traceability
            log_agent_data(self.to_dict())

            # Prepare case information
            case_info = {
                "patient_id": self.patient_id,
                "timestamp": datetime.now().isoformat(),
                "patient_documentation": self.patient_documentation,
                "task": task,
            }

            # Encrypt case information for secure processing
            encrypted_case_info = self.secure_handler.encrypt_data(
                case_info
            )
            print("Case information encrypted successfully.")

            # Decrypt case information before passing to the swarm
            decrypted_case_info = self.secure_handler.decrypt_data(
                encrypted_case_info
            )
            print("Case information decrypted for swarm processing.")

            # Run the diagnosis system with decrypted data
            output = self.diagnosis_system.run(
                decrypted_case_info, img, *args, **kwargs
            )

            # Encrypt the swarm's output for secure storage and transit
            encrypted_output = self.secure_handler.encrypt_data(
                output
            )
            print("Swarm output encrypted successfully.")

            # Decrypt the swarm's output for internal usage
            decrypted_output = self.secure_handler.decrypt_data(
                encrypted_output
            )
            print("Swarm output decrypted for internal processing.")

            # Append decrypted output to agent outputs
            self.agent_outputs.append(decrypted_output)

            # Save encrypted output as part of the patient data
            self.save_patient_data(self.patient_id, encrypted_output)

            print(
                "Secure run of the medical coding and diagnosis system completed successfully."
            )
            return decrypted_output

        except Exception as e:
            # Log the current state and error
            log_agent_data(self.to_dict())
            print(f"An error occurred during the secure run: {e}")
            return "An error occurred during the diagnosis process. Please check the logs for more information."

    def batched_run(
        self,
        tasks: List[str] = None,
        imgs: List[str] = None,
        *args,
        **kwargs,
    ):
        """
        Run the medical coding and diagnosis system for multiple tasks.
        """
        # logger.add(
        #     "medical_coding_diagnosis_system.log", rotation="10 MB"
        # )

        try:
            print(
                "Running the medical coding and diagnosis system for multiple tasks."
            )
            outputs = []
            for task, img in zip(tasks, imgs):
                case_info = f"Patient Information: {self.patient_id} \n Timestamp: {datetime.now()} \n Patient Documentation {self.patient_documentation} \n Task: {task}"
                output = self.run(case_info, img, *args, **kwargs)
                outputs.append(output)

            return outputs
        except Exception as e:
            print(
                f"An error occurred during the diagnosis process: {e}"
            )
            return "An error occurred during the diagnosis process. Please check the logs for more information."

    def _serialize_callable(
        self, attr_value: Callable
    ) -> Dict[str, Any]:
        """
        Serializes callable attributes by extracting their name and docstring.

        Args:
            attr_value (Callable): The callable to serialize.

        Returns:
            Dict[str, Any]: Dictionary with name and docstring of the callable.
        """
        return {
            "name": getattr(
                attr_value, "__name__", type(attr_value).__name__
            ),
            "doc": getattr(attr_value, "__doc__", None),
        }

    def _serialize_attr(self, attr_name: str, attr_value: Any) -> Any:
        """
        Serializes an individual attribute, handling non-serializable objects.

        Args:
            attr_name (str): The name of the attribute.
            attr_value (Any): The value of the attribute.

        Returns:
            Any: The serialized value of the attribute.
        """
        try:
            if callable(attr_value):
                return self._serialize_callable(attr_value)
            elif hasattr(attr_value, "to_dict"):
                return (
                    attr_value.to_dict()
                )  # Recursive serialization for nested objects
            else:
                json.dumps(
                    attr_value
                )  # Attempt to serialize to catch non-serializable objects
                return attr_value
        except (TypeError, ValueError):
            return f"<Non-serializable: {type(attr_value).__name__}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts all attributes of the class, including callables, into a dictionary.
        Handles non-serializable attributes by converting them or skipping them.

        Returns:
            Dict[str, Any]: A dictionary representation of the class attributes.
        """
        return {
            attr_name: self._serialize_attr(attr_name, attr_value)
            for attr_name, attr_value in self.__dict__.items()
        }

    @secure_data(encrypt=True)
    def save_patient_data(self, patient_id: str, case_data: str):
        """Save patient data with automatic encryption"""
        try:
            data = {
                "patient_id": patient_id,
                "case_data": case_data,
                "timestamp": datetime.now().isoformat(),
            }

            with open(f"{patient_id}_encrypted.json", "w") as file:
                json.dump(data, file)

            print(
                f"Encrypted patient data saved for ID: {patient_id}"
            )
        except Exception as e:
            print(f"Error saving encrypted patient data: {e}")
            raise
