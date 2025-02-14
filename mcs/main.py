import json
import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from pydantic import BaseModel
from swarms import Agent
from mcs.rag_api import ChromaQueryClient

from mcs.security import (
    KeyRotationPolicy,
    SecureDataHandler,
    secure_data,
)


def patient_id_uu():
    return str(uuid.uuid4().hex)


def log_agent_data(data: Dict[str, Any]):
    pass


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
    model_name="groq/deepseek-r1-distill-llama-70b",
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
#     model_name="groq/deepseek-r1-distill-llama-70b",
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
    model_name="groq/deepseek-r1-distill-llama-70b",
    max_loops=1,
    dynamic_temperature_enabled=True,
)

medical_coder = Agent(
    agent_name="Medical Coder",
    system_prompt="""
    You are a highly experienced and certified medical coder with extensive knowledge of ICD-10 coding guidelines, clinical documentation standards, and compliance regulations. Your responsibility is to ensure precise, compliant, and well-documented coding for all clinical cases.

    ### Primary Responsibilities:
    1. **Review Clinical Documentation**: Analyze all available clinical records, including specialist inputs, physician notes, lab results, imaging reports, and discharge summaries.
    2. **Assign Accurate ICD-10 Codes**: Identify and assign appropriate codes for primary diagnoses, secondary conditions, symptoms, and complications.
    3. **Ensure Coding Compliance**: Follow the latest ICD-10-CM/PCS coding guidelines, payer-specific requirements, and organizational policies.
    4. **Document Code Justification**: Provide clear, evidence-based rationale for each assigned code.

    ### Detailed Coding Process:
    - **Review Specialist Inputs**: Examine all relevant documentation to capture the full scope of the patient's condition and care provided.
    - **Identify Diagnoses**: Determine the primary and secondary diagnoses, as well as any symptoms or complications, based on the documentation.
    - **Assign ICD-10 Codes**: Select the most accurate and specific ICD-10 codes for each identified diagnosis or condition.
    - **Document Supporting Evidence**: Record the documentation source (e.g., lab report, imaging, or physician note) for each code to justify its assignment.
    - **Address Queries**: Note and flag any inconsistencies, missing information, or areas requiring clarification from providers.

    ### Output Requirements:
    Your response must be clear, structured, and compliant with professional standards. Use the following format:

    1. **Primary Diagnosis Codes**:
        - **ICD-10 Code**: [e.g., E11.9]
        - **Description**: [e.g., Type 2 diabetes mellitus without complications]
        - **Supporting Documentation**: [e.g., Physician's note dated MM/DD/YYYY]
        
    2. **Secondary Diagnosis Codes**:
        - **ICD-10 Code**: [Code]
        - **Description**: [Description]
        - **Order of Clinical Significance**: [Rank or priority]

    3. **Symptom Codes**:
        - **ICD-10 Code**: [Code]
        - **Description**: [Description]

    4. **Complication Codes**:
        - **ICD-10 Code**: [Code]
        - **Description**: [Description]
        - **Relevant Documentation**: [Source of information]

    5. **Coding Notes**:
        - Observations, clarifications, or any potential issues requiring provider input.

    ### Additional Guidelines:
    - Always prioritize specificity and compliance when assigning codes.
    - For ambiguous cases, provide a brief note with reasoning and flag for clarification.
    - Ensure the output format is clean, consistent, and ready for professional use.
    """,
    model_name="groq/deepseek-r1-distill-llama-70b",
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
    model_name="groq/deepseek-r1-distill-llama-70b",
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

    
    ### Output Style:
    - Clear and professional tone.
    - Consistent structure with easy-to-scan sections.
    - Minimize redundancy while ensuring completeness.
    """,
    model_name="groq/deepseek-r1-distill-llama-70b",
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
    model_name="groq/deepseek-r1-distill-llama-70b",
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
    model_name="groq/deepseek-r1-distill-llama-70b",
    max_loops=1,
    dynamic_temperature_enabled=True,
)


treatment_agent = Agent(
    agent_name="Treatment-Agent",
    system_prompt="""
    You are a specialist in treatment options, responsible for recommending the most effective and cost-efficient treatments for patients, considering both traditional and modern medicine approaches.

    Primary Responsibilities:
    1. Provide treatment recommendations for various diagnoses
    2. Offer multiple treatment methods, including traditional and modern medicine approaches
    3. Rank treatment options based on effectiveness and estimated cost
    4. Consider patient-specific factors, such as age, health status, and allergies
    5. Provide detailed treatment plans, including dosages, frequencies, and duration

    For each case, provide:

    Treatment Recommendations:
    - Multiple treatment options, including traditional and modern medicine approaches
    - Ranking of treatment options based on effectiveness and estimated cost
    - Consideration of patient-specific factors, such as age, health status, and allergies
    
    Treatment Details:
    - Detailed treatment plans, including dosages, frequencies, and duration
    - Information on potential side effects and interactions
    - Monitoring and follow-up requirements
    
    Cost Analysis:
    - Estimated cost of each treatment option
    - Breakdown of costs, including medication, hospitalization, and other expenses
    
    Patient Education:
    - Clear explanations of treatment options and their benefits
    - Instructions for self-care and lifestyle modifications
    - Addressing patient concerns and questions
    
    Output Format:
    1. Treatment Options
        - Ranked list of treatment options with effectiveness and cost analysis
        - Detailed treatment plans
    2. Patient Education
        - Clear explanations of treatment options and their benefits
        - Instructions for self-care and lifestyle modifications
    3. Cost Analysis
        - Estimated cost of each treatment option
        - Breakdown of costs
    4. Monitoring and Follow-up
        - Requirements for monitoring and follow-up care
        - Scheduling and frequency of follow-up appointments
    
    Always specify:
    - Evidence-based information to support treatment recommendations
    - Consideration of patient preferences and values
    - Alternative treatment options for patients with specific needs or restrictions
    """,
    model_name="groq/deepseek-r1-distill-llama-70b",
    max_loops=1,
    dynamic_temperature_enabled=True,
    do_not_use_cluster_ops=True,
)

# Create agent list
agents = [
    medical_coder,
    synthesizer,
    treatment_agent,
]


class MCSAgentOutputs(BaseModel):
    agent_id: Optional[str] = str(uuid.uuid4().hex)
    agent_name: Optional[str] = None
    agent_output: Optional[str] = None
    timestamp: Optional[str] = time.strftime("%Y-%m-%d %H:%M:%S")


class MCSOutput(BaseModel):
    run_id: Optional[str] = str(uuid.uuid4().hex)
    patient_id: Optional[str]
    agent_outputs: Optional[List[MCSAgentOutputs]] = None
    summary: Optional[str]
    timestamp: Optional[str] = time.strftime("%Y-%m-%d %H:%M:%S")


class MedicalCoderSwarm:
    """
    Class to represent a medical coding diagnosis swarm.
    """

    def __init__(
        self,
        name: str = "Medical-coding-diagnosis-swarm",
        description: str = "Comprehensive medical diagnosis and coding system",
        agents: list = agents,
        patient_id: str = "001",
        max_loops: int = 1,
        output_folder_path: str = "reports",
        patient_documentation: str = None,
        agent_outputs: list = any,
        user_name: str = "User",
        key_storage_path: str = None,
        summarization: bool = False,
        rag_on: bool = False,
        rag_url: str = None,
        rag_api_key: str = None,
        *args,
        **kwargs,
    ):
        self.name = name
        self.description = description
        self.agents = agents
        self.patient_id = patient_id
        self.max_loops = max_loops
        self.output_folder_path = output_folder_path
        self.patient_documentation = patient_documentation
        self.agent_outputs = agent_outputs
        self.user_name = user_name
        self.key_storage_path = key_storage_path
        self.summarization = summarization
        self.rag_on = rag_on
        self.rag_url = rag_url
        self.rag_api_key = rag_api_key
        self.agent_outputs = []
        self.patient_id = patient_id_uu()

        self.output_file_path = (
            f"medical_diagnosis_report_{patient_id}.md",
        )

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

        # Output schema
        self.output_schema = MCSOutput(
            patient_id=self.patient_id, agent_outputs=[], summary=""
        )

    def rag_query(self, query: str):
        client = ChromaQueryClient(
            api_key=self.rag_api_key, base_url=self.rag_url
        )

        return client.query(query)

    def _run(
        self, task: str = None, img: str = None, *args, **kwargs
    ):
        """ """
        print("Running the medical coding and diagnosis system.")

        try:
            log_agent_data(self.to_dict())

            if self.rag_on is True:
                db_data = self.rag_query(task)

            case_info = f"Patient Information: {self.patient_id} \n Timestamp: {datetime.now()} \n Patient Documentation {self.patient_documentation} \n Task: {task} "

            if self.rag_on:
                case_info = f"{db_data}{case_info}"

            medical_coder_output = medical_coder.run(case_info)

            # Append output to schema
            self.output_schema.agent_outputs.append(
                MCSAgentOutputs(
                    agent_name=medical_coder.agent_name,
                    agent_output=medical_coder_output,
                )
            )

            # Next agent
            synthesizer_output = synthesizer.run(
                f"From {medical_coder.agent_name} {medical_coder_output}"
            )
            self.output_schema.agent_outputs.append(
                MCSAgentOutputs(
                    agent_name=synthesizer.agent_name,
                    agent_output=synthesizer_output,
                )
            )

            # Next agent
            treatment_agent_output = treatment_agent.run(
                f"From {synthesizer.agent_name} {synthesizer_output}"
            )
            self.output_schema.agent_outputs.append(
                MCSAgentOutputs(
                    agent_name=treatment_agent.agent_name,
                    agent_output=treatment_agent_output,
                )
            )

            if self.summarization is True:
                output = summarizer_agent.run(treatment_agent_output)
                self.output_schema.summary = output

            log_agent_data(self.to_dict())

            return self.output_schema.model_dump_json(indent=4)

        except Exception as e:
            log_agent_data(self.to_dict())
            print(
                f"An error occurred during the diagnosis process: {e}"
            )

    def run(self, task: str = None, img: str = None, *args, **kwargs):
        try:
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
