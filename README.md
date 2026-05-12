
* * *

# AI-Driven Cyber Deception: LLM Enhanced SSH Honeypot

## Technical Overview

This project is a modular, high-fidelity SSH honeypot designed for defensive cybersecurity research and threat intelligence gathering. Unlike traditional low-interaction honeypots that rely on static scripts, this system utilizes Large Language Models (LLMs) to simulate a dynamic Ubuntu 22.04 LTS environment. It is engineered to deceive sophisticated attackers, maintain stateful persistence, and map malicious activities to the MITRE ATT&CK framework in real-time.

## Key Architectural Components

### 1\. Virtual Filesystem (VFS) Engine

A stateful simulation layer that manages directory structures, file permissions, and navigation logic. This ensures that core shell commands (e.g., `cd`, `pwd`, `ls`) remain 100% consistent throughout a session, providing a stable foundation for the AI deception layer.

### 2\. LLM-Driven Terminal Simulation

The system delegates complex command execution (e.g., `grep`, `awk`, `cat /etc/passwd`, `network reconnaissance`) to an LLM. The AI is constrained by strict system prompting to ensure it remains in character as a hardened Linux server, generating realistic error messages and synthetic file contents.

### 3\. Session Intelligence & State Management

Every connection is assigned a unique UUID. The Session Manager tracks command history, cumulative risk scores, and attacker behavior across the entire lifecycle of the intrusion. This allows the AI to maintain context (e.g., remembering a file the attacker created in a previous step).

### 4\. Telemetry & MITRE ATT&CK Mapping

The system includes an automated classification engine that cross-references attacker input with the MITRE ATT&CK matrix. It identifies tactics such as:

-   **T1033**: System Owner/User Discovery
    
-   **T1083**: File and Directory Discovery
    
-   **T1552**: Unsecured Credentials
    
-   **T1548**: Abuse Elevation Control Mechanism
    

## Repository Structure

-   `ai/`: Logic for LLM API integration and prompt engineering.
    
-   `core/`: Internal engines for filesystem simulation, session tracking, and threat classification.
    
-   `models/`: Pydantic data models ensuring type-safety for logs and session profiles.
    
-   `telemetry/`: Structured logging system designed for SIEM ingestion (ELK/Splunk).
    
-   `config/`: Environment-based configuration management.
    

## Installation and Deployment

### Prerequisites

-   Python 3.9+
    
-   OpenAI or DeepSeek API Key
    

### Setup

1.  Clone the repository:
    
    Bash
    
        git clone https://github.com/HiveMind.git
        cd HiveMind
    
2.  Install required dependencies:
    

Bash

       pip install -r requirements.txt

3.  Configure environment variables in a `.env` file:
    

Code snippet

       DEEPSEEK_API_KEY=your_api_key_here
       HONEYPOT_HOSTNAME=ubuntu-srv-prod
       LOG_LEVEL=INFO

4.  Execute the honeypot:
    
    Bash
    
        python main.py
    

## Telemetry Specifications

Logs are output in structured JSON format to facilitate automated analysis. Each entry includes:

-   **Session ID**: Unique identifier for the attacker.
    
-   **Risk Score**: A quantitative measure of the session's threat level (0-100).
    
-   **Attack Tags**: Relevant MITRE ATT&CK tactics and technique IDs.
    
-   **Context**: The working directory and user privileges at the time of command execution.
    

## Research Objectives

This honeypot is intended for use in studying:

1.  LLM effectiveness in cyber deception and attacker engagement.
    
2.  The evolution of lateral movement techniques in cloud-native environments.
    
3.  Automated risk scoring and session profiling in Security Operations Centers (SOC).
    

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Disclaimer

This software is provided for research and educational purposes only. The author is not responsible for any misuse or damage caused by this program. Ensure you have explicit permission before deploying this system on any network.
