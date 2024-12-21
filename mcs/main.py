"""
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
- 

"""

from datetime import datetime
import json
import os
from typing import Any, Callable, Dict, List
import uuid

from swarms import Agent, AgentRearrange, create_file_in_folder
from loguru import logger
from swarm_models import OpenAIChat
from dotenv import load_dotenv
from swarms.telemetry.capture_sys_data import log_agent_data

model_name = "gpt-4o"

model = OpenAIChat(model_name=model_name, max_tokens=4000, openai_api_key=os.getenv("OPENAI_API_KEY"))

load_dotenv()

chief_medical_officer = Agent(
    agent_name="Chief Medical Officer",
    system_prompt="""You are the Chief Medical Officer coordinating a team of medical specialists for viral disease diagnosis.
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
)

virologist = Agent(
    agent_name="Virologist",
    system_prompt="""You are a specialist in viral diseases. For each case, provide:
    
    Clinical Analysis:
    - Detailed viral symptom analysis
    - Disease progression timeline
    - Risk factors and complications
    
    Coding Requirements:
    - List relevant ICD-10 codes for:
        * Confirmed viral conditions
        * Suspected viral conditions
        * Associated symptoms
        * Complications
    - Include both:
        * Primary diagnostic codes
        * Secondary condition codes
    
    Document all findings using proper medical coding standards and include rationale for code selection.""",
    llm=model,
    max_loops=1,
)

internist = Agent(
    agent_name="Internist",
    system_prompt="""You are an Internal Medicine specialist responsible for comprehensive evaluation.
    
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
)



# Create agent list
agents = [
    chief_medical_officer,
    virologist,
    internist,
    medical_coder,
    synthesizer,
]

# Define diagnostic flow
flow = f"""{chief_medical_officer.agent_name} -> {virologist.agent_name} -> {internist.agent_name} -> {medical_coder.agent_name} -> {synthesizer.agent_name}"""




class MedicalCoderSwarm:
    def __init__(
        self,
        name: str = "Medical-coding-diagnosis-swarm",
        description: str = "Comprehensive medical diagnosis and coding system",
        agents: list = agents,
        flow: str = flow,
        patient_id: str = None,
        max_loops: int = 1,
        output_type: str = "dict",
        output_folder_path: str = "reports",
        patient_documentation: str = None,
        agent_outputs: list = any,
        *args, 
        **kwargs
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
        self.agent_outputs = []
        
        self.diagnosis_system = AgentRearrange(
            name="Medical-coding-diagnosis-swarm",
            description="Comprehensive medical diagnosis and coding system",
            agents=agents,
            flow=flow,
            max_loops=max_loops,
            output_type=output_type,
            *args,
            **kwargs
        )
        
        self.output_file_path = f"medical_diagnosis_report_{uuid.uuid4().hex}.md",
        
    def run(self, task: str = None, img: str = None, *args, **kwargs):
        """
        Run the medical coding and diagnosis system.
        """
        logger.info("Running the medical coding and diagnosis system.")
        
        try:
            log_agent_data(self.to_dict())
            case_info = f"Patient Information: {self.patient_id} \n Timestamp: {datetime.now()} \n Patient Documentation {self.patient_documentation} \n Task: {task}" 
            
            output = self.diagnosis_system.run(case_info, img, *args, **kwargs)
            self.agent_outputs.append(output)
            log_agent_data(self.to_dict())
            
            create_file_in_folder(self.output_folder_path, self.output_file_path, output)
            
            return output
        except Exception as e:
            logger.error(f"An error occurred during the diagnosis process: {e}")
            log_agent_data(self.to_dict())
            return "An error occurred during the diagnosis process. Please check the logs for more information."

    def batched_run(self, tasks: List[str] = None, imgs: List[str] = None, *args, **kwargs):
        """
        Run the medical coding and diagnosis system for multiple tasks.
        """
        logger.add("medical_coding_diagnosis_system.log", rotation="10 MB")
        
        try:
            outputs = []
            for task, img in zip(tasks, imgs):
                case_info = f"Patient Information: {self.patient_id} \n Timestamp: {datetime.now()} \n Patient Documentation {self.patient_documentation} \n Task: {task}" 
                output = self.run(case_info, img, *args, **kwargs)
                outputs.append(output)
                
            return outputs
        except Exception as e:
            logger.error(f"An error occurred during the diagnosis process: {e}")
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
    