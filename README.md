# Medical Diagnosis Swarm Architecture


[![Join our Discord](https://img.shields.io/badge/Discord-Join%20our%20server-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/agora-999382051935506503) [![Subscribe on YouTube](https://img.shields.io/badge/YouTube-Subscribe-red?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@kyegomez3242) [![Connect on LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/kye-g-38759a207/) [![Follow on X.com](https://img.shields.io/badge/X.com-Follow-1DA1F2?style=for-the-badge&logo=x&logoColor=white)](https://x.com/kyegomezb)

A production-grade multi-agent system for comprehensive medical diagnosis and coding using specialized AI agents.


## Installation

```bash
pip install mcs
```

## Usage

```python

from mcs.main import MedicalCoderSwarm
import json

if __name__ == "__main__":
  # Example patient case
  patient_case = """
  Patient: 45-year-old White Male
  Location: New York, NY

  Lab Results:
  - egfr 
  - 59 ml / min / 1.73
  - non african-american
  
  """
  
  swarm = MedicalCoderSwarm(patient_id="Patient-001", max_loops=1, patient_documentation="")
  
  swarm.run(task=patient_case)
  
  print(json.dumps(swarm.to_dict()))
```


## Architecture Overview

```mermaid
flowchart TB
    CMO[Chief Medical Officer] --> V[Virologist]
    V --> I[Internist]
    I --> MC[Medical Coder]
    MC --> S[Synthesizer]
    
```

## Features

- **Specialized Agent Roles**: Each agent has specific medical expertise and responsibilities
- **Structured Diagnostic Flow**: Organized pipeline from initial assessment to final synthesis
- **ICD-10 Coding Integration**: Comprehensive medical coding at each diagnostic stage
- **Automated Report Generation**: Standardized medical and coding reports
- **Evidence-Based Decision Making**: Multi-stage verification and synthesis process

## Agent Responsibilities

```mermaid
mindmap
  root((Medical Swarm))
    Chief Medical Officer
      Initial Assessment
      Coordinate Specialists
      Treatment Plans
      Lab Range Analysis
    Virologist
      Viral Analysis
      Disease Progression
      Risk Assessment
    Internist
      System Review
      Vitals Analysis
      Comorbidity Evaluation
    Medical Coder
      ICD-10 Assignment
      Coding Compliance
      Documentation Review
    Synthesizer
      Integration
      Reconciliation
      Final Assessment
```

## Diagnostic Flow Process

```mermaid
sequenceDiagram
    participant P as Patient Case
    participant CMO as Chief Medical Officer
    participant V as Virologist
    participant I as Internist
    participant MC as Medical Coder
    participant S as Synthesizer
    
    P->>CMO: Initial Data
    CMO->>V: Preliminary Assessment
    V->>I: Viral Analysis
    I->>MC: Comprehensive Review
    MC->>S: Coded Diagnosis
    S->>P: Final Report
```


## API Usage
We have established an api in the `/api` folder. To run the api locally you must git clone, and then run:

```bash
cd api

chmod +x bootup.sh

./bootup.sh

```

## Docker Usage

To build and run the Docker container for the Medical Coder Swarm, follow these steps:

1. **Build the Docker Image**:
  ```bash
  docker build -t mcs .
  ```

2. **Run the Docker Container**:
  ```bash
  docker run --rm mcs
  ```

## Docker Compose

```bash
docker-compose up
```

### To stop the services, run:
```bash
docker-compose down
```




## Lab Range Analysis

The system includes specialized functionality for analyzing lab results against diagnostic criteria:

- Automated range checking for common tests (e.g., eGFR)
- Diagnosis-specific range validation
- Multi-factor analysis for complex diagnoses

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- Built with the Swarms framework
- Utilizes GPT-4 for advanced medical reasoning
- ICD-10 coding standards compliance

## Contact

For questions and support, please open an issue in the repository.
