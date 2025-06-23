# Diagrams to Deployment (D2D)

Diagrams to Deployment (D2D) is a powerful tool that converts Oracle Cloud Infrastructure (OCI) network diagrams into deployable Terraform code. Using advanced OCR (Optical Character Recognition) and AI capabilities, D2D analyzes network diagrams to extract components such as VCNs, subnets, and gateways, then generates ready-to-use Terraform configurations for your OCI infrastructure.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Web Interface](#web-interface-recommended)
  - [Command Line Interface](#command-line-interface)
- [Diagram Requirements](#diagram-requirements)
- [Visual Guide](#visual-guide)
- [Generated Files](#generated-files)
- [Troubleshooting](#troubleshooting)
- [Advanced Usage](#advanced-usage)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Diagram Analysis**: Uses Oracle's Generative AI service to extract network components from diagrams
- **Multi-Region Support**: Handles diagrams with multiple OCI regions
- **Terraform Generation**: Creates complete Terraform configurations including:
  - VCNs (Virtual Cloud Networks)
  - Subnets (Public and Private)
  - Gateways (Internet, NAT, Service, and Dynamic Routing)
  - Compartments
  - Security Lists
- **OCI Profile Integration**: Works with your existing OCI CLI profiles
- **User-Friendly Interface**: Simple web interface built with Streamlit

## Prerequisites

Before using D2D, ensure you have:

1. **Python 3.8+** installed on your system
2. **OCI SDK** configured with valid credentials
3. **Terraform** installed (for deploying the generated code)
4. **OCI CLI** configured with at least one profile
5. Active OCI account with access to Generative AI services

## Installation

### 1. OCI Configuration

#### For Windows:
1. Install OCI CLI:
   ```powershell
   # Download OCI CLI installer from Oracle website
   # Run the installer and follow the prompts
   ```
2. Configure OCI:
   ```powershell
   oci setup config
   ```
   - Follow the prompts to enter your tenancy OCID, user OCID, and region
   - The config file will be created at `%USERPROFILE%\.oci\config`

#### For macOS:
1. Install OCI CLI:
   ```bash
   bash -c "$(curl -L https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh)"
   ```
2. Configure OCI:
   ```bash
   oci setup config
   ```
   - Follow the prompts to enter your tenancy OCID, user OCID, and region
   - The config file will be created at `~/.oci/config`

### 2. Python Environment Setup

1. Clone the repository or download the application files
2. Install required dependencies:

#### For Windows:
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### For macOS:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure OCI**
   Ensure you have a valid OCI configuration at `~/.oci/config`

3. **Launch the Application**
   ```bash
   streamlit run app.py
   ```

4. **Using D2D**
   - Select your OCI profile from the sidebar
   - Upload your network diagram (PNG/JPG)
   - Click "Generate Terraform Configuration"
   - Review the generated Terraform files
   - Follow the "Next Steps" to deploy your infrastructure

## Configuration

### OCI Configuration

D2D requires a valid OCI configuration to authenticate with Oracle Cloud services. The application uses the standard OCI configuration file located at `~/.oci/config`.

1. Ensure you have a valid OCI configuration file at `~/.oci/config`
2. The file should contain at least one profile (DEFAULT is used if none is specified)
3. Each profile should include:
   - `user` (OCID of your user)
   - `fingerprint` (of your API key)
   - `key_file` (path to your private key)
   - `tenancy` (OCID of your tenancy)
   - `region` (your home region)

Example configuration:

```
[DEFAULT]
user=ocid1.user.oc1..aaaaaaaaxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
key_file=~/.oci/oci_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaaxxx
region=us-ashburn-1

[PRODUCTION]
user=ocid1.user.oc1..aaaaaaaaxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
key_file=~/.oci/prod_api_key.pem
tenancy=ocid1.tenancy.oc1..aaaaaaaaxxx
region=us-phoenix-1
```

## Usage

### Web Interface (Recommended)

1. Ensure your virtual environment is activated
2. Start the Streamlit application:
   ```bash
   streamlit run app.py
   ```
3. The application will open in your default web browser at `http://localhost:8501`
4. In the sidebar, select your OCI configuration profile
5. Upload your OCI architecture diagram (supported formats: PNG, JPG, JPEG)
6. Review your uploaded diagram in the preview
7. Click "Generate Terraform Configuration" to process the diagram
8. Review the generated Terraform files for each detected region
9. Follow the displayed "Next Steps" to deploy your infrastructure

### Command Line Interface

You can also use D2D directly from the command line:

```bash
python llama_ocr_oci.py /path/to/your/diagram.png
```

This will:
1. Process the diagram
2. Create a `terraform_workspace` directory in your current working directory
3. Generate Terraform files organized by project and region

When using the command line interface, you'll see output similar to:

```
Processing diagram: network_diagram.png

DEBUG: Loading OCI config from ~/.oci/config with profile DEFAULT
DEBUG: Successfully loaded OCI config with keys: ['user', 'fingerprint', 'key_file', 'tenancy', 'region']
DEBUG: Using region: us-ashburn-1

Project Name: production

Processing region: us-ashburn-1
Generated Terraform configuration for region us-ashburn-1 in /Users/username/terraform_workspace/production/us-ashburn-1

Terraform configuration generated successfully in /Users/username/terraform_workspace
```

## Diagram Requirements

For best results, your network diagrams should:

1. Clearly show VCNs with their names and CIDR blocks
2. Indicate subnet names, CIDR blocks, and whether they are public or private
3. Show which gateways are present (Internet, NAT, Service, DRG)
4. Include region information
5. Use standard OCI network diagram conventions

Example of a well-structured diagram annotation:
```
Region: us-ashburn-1
VCN: prod-ash-hub-vcn (10.0.0.0/16)
Subnets:
- prod-ash-web-subnet (10.0.1.0/24) - Public
- prod-ash-app-subnet (10.0.2.0/24) - Private
Gateways: Internet Gateway, NAT Gateway, Service Gateway
```

### Example Diagram Annotations

For best results, your diagrams should include clear annotations. Here are examples of good annotations:

#### VCN Annotation
```
VCN: prod-ash-hub-vcn
CIDR: 10.0.0.0/16
Description: Hub VCN for us-ashburn-1 region
```

#### Subnet Annotation
```
Subnet: prod-ash-web-subnet
CIDR: 10.0.1.0/24
Type: Public
Description: Web tier subnet
```

#### Gateway Annotation
```
Gateways:
- Internet Gateway: Yes
- NAT Gateway: Yes
- Service Gateway: Yes
- DRG: Yes
```

## Visual Guide

### Application Interface

When you launch the application, you'll see a clean interface with:
- A sidebar for OCI profile selection
- A file uploader for your network diagram
- A "Generate Terraform Configuration" button

```
┌─────────────────────────────────────────────────────────────┐
│ ◀ Diagrams to Deployment                                    │
│                                                             │
│   [OCI Configuration]                                       │
│   Select OCI Profile: [DEFAULT ▼]                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│ Diagrams to Deployment                                      │
│                                                             │
│ Choose an image file [Browse files]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Example Workflow

#### 1. Upload a Network Diagram

Upload a diagram that clearly shows your OCI network components:

```
┌─────────────────────────────────────────────────────────────┐
│ Diagrams to Deployment                                      │
│                                                             │
│ [Uploaded OCI Architecture Diagram]                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                                                       │  │
│  │  Region: us-ashburn-1                                 │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │ VCN: prod-ash-hub-vcn (10.0.0.0/16)             │  │  │
│  │  │                                                 │  │  │
│  │  │  ┌─────────────────┐      ┌─────────────────┐   │  │  │
│  │  │  │Public Subnet    │      │Private Subnet   │   │  │  │
│  │  │  │prod-ash-web     │      │prod-ash-app     │   │  │  │
│  │  │  │10.0.1.0/24      │      │10.0.2.0/24      │   │  │  │
│  │  │  └─────────────────┘      └─────────────────┘   │  │  │
│  │  │                                                 │  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │  │  │
│  │  │  │Internet │ │NAT      │ │Service │ │DRG     │ │  │  │
│  │  │  │Gateway  │ │Gateway  │ │Gateway │ │        │ │  │  │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └────────┘ │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                       │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│ [Generate Terraform Configuration]                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### 2. Processing the Diagram

When you click "Generate Terraform Configuration", the application will:
- Process the diagram using OCR and AI
- Extract network components
- Generate Terraform code

#### 3. Reviewing Generated Terraform

After processing, you'll see expandable sections for each region with the generated Terraform files:

```
┌─────────────────────────────────────────────────────────────┐
│ Diagrams to Deployment                                      │
│                                                             │
│ [Uploaded OCI Architecture Diagram]                         │
│                                                             │
│ ▼ Configuration for us-ashburn-1                            │
│                                                             │
│   ### main.tf                                               │
│   ```hcl                                                    │
│   # VCN for prod-ash-hub-vcn                                │
│   resource "oci_core_vcn" "prod_ash_hub_vcn" {              │
│     compartment_id = var.compartment_id                     │
│     display_name   = "prod-ash-hub-vcn"                     │
│     cidr_block     = "10.0.0.0/16"                          │
│     dns_label      = "prodashvcn"                           │
│   }                                                         │
│                                                             │
│   # Public subnet for prod-ash-web-subnet                   │
│   resource "oci_core_subnet" "prod_ash_web_subnet" {        │
│     compartment_id = var.compartment_id                     │
│     vcn_id         = oci_core_vcn.prod_ash_hub_vcn.id       │
│     display_name   = "prod-ash-web-subnet"                  │
│     cidr_block     = "10.0.1.0/24"                          │
│     ...                                                     │
│   ```                                                       │
│                                                             │
│   ### Next Steps:                                           │
│   1. Navigate to the generated Terraform files in your      │
│      terminal:                                              │
│      ```bash                                                │
│      cd terraform_workspace/<project_name>/<region>         │
│      ```                                                    │
│   2. Initialize Terraform:                                  │
│      ```bash                                                │
│      terraform init                                         │
│      ```                                                    │
│   3. Review the planned changes:                            │
│      ```bash                                                │
│      terraform plan                                         │
│      ```                                                    │
│   4. Apply the configuration:                               │
│      ```bash                                                │
│      terraform apply                                        │
│      ```                                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Generated Files

The tool generates the following Terraform files for each region:

- **main.tf**: Core infrastructure resources (VCNs, subnets, gateways)
- **provider.tf**: OCI provider configuration
- **variables.tf**: Variable declarations
- **terraform.tfvars**: Variable values specific to your environment

### Generated Directory Structure

After processing, your Terraform files will be organized as follows:

```
terraform_workspace/
└── project_name/
    ├── us-ashburn-1/
    │   ├── main.tf
    │   ├── provider.tf
    │   ├── variables.tf
    │   └── terraform.tfvars
    └── us-phoenix-1/
        ├── main.tf
        ├── provider.tf
        ├── variables.tf
        └── terraform.tfvars
```

## Application Structure

- `app.py`: Main application file containing the Streamlit interface and core application logic
- `llama_ocr_oci.py`: Contains image processing and OCR functionality
- `image_reader.py`: Contains the OCI image processing and AI service integration
- `requirements.txt`: Python package dependencies
- `terraform_workspace/`: Contains Terraform configurations for OCI infrastructure

## Troubleshooting

### Common Issues

1. **OCI Authentication Errors**
   - Verify your OCI configuration file is correct
   - Check that your API key is valid and not expired
   - Ensure your user has appropriate permissions

2. **Diagram Recognition Issues**
   - Use clearer diagrams with text that is easy to read
   - Ensure network components are clearly labeled
   - Try using the standard OCI architecture diagram format

3. **Terraform Generation Errors**
   - Check the console output for specific error messages
   - Verify that the extracted network information is correct
   - Try running with the `USE_MOCK_DATA=True` environment variable to test the Terraform generation process

4. **Python Dependencies**
   - If you encounter any module not found errors, ensure all dependencies are installed:
     ```bash
     pip install -r requirements.txt
     ```

5. **Connection Issues**
   - Verify your internet connection
   - Check if OCI services are accessible from your network
   - Ensure your OCI credentials haven't expired

### Debug Mode

To enable additional debugging information:

```bash
python -m llama_ocr_oci --debug /path/to/your/diagram.png
```

Or for the web interface:

```bash
DEBUG=True streamlit run app.py
```

## Advanced Usage

### Environment Variables

- `USE_MOCK_DATA`: Set to `True` to use mock data instead of calling the AI service (useful for testing)
- `DEBUG`: Set to `True` to enable additional debug logging
- `OCI_CONFIG_PROFILE`: Specify which OCI profile to use (defaults to 'DEFAULT')

### Testing with Mock Data

For testing without calling the OCI Generative AI service:

```bash
USE_MOCK_DATA=True python llama_ocr_oci.py test_diagram.png
```

## Limitations

- The tool currently focuses on network infrastructure components
- Custom security rules and route rules may require manual adjustment
- Very complex diagrams with many components may not be fully recognized

## Contributing

Contributions to improve D2D are welcome! Please feel free to reach out to me(mukund.m.murali@oracle.com) for suggestions, bug reports, or feature requests.

