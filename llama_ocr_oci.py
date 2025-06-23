import oci
import base64
import json
import os
import tempfile
import sys

def get_config(profile_name=None):
    """Get OCI configuration based on profile"""
    if not profile_name:
        profile_name = 'DEFAULT'
    try:
        # Expand the tilde to the user's home directory
        config_path = os.path.expanduser('~/.oci/config')
        print(f"Debug: Loading OCI config from {config_path} with profile {profile_name}")
        
        # Check if the config file exists
        if not os.path.exists(config_path):
            print(f"Error: OCI config file not found at {config_path}")
            return None
            
        config = oci.config.from_file(config_path, profile_name)
        print(f"Debug: Successfully loaded OCI config with keys: {list(config.keys())}")
        print(f"Debug: Using region: {config.get('region', 'Not set')}")
        return config
    except Exception as e:
        print(f"Error loading config for profile {profile_name}: {str(e)}")
        print("Troubleshooting tips:")
        print("1. Ensure the OCI config file exists at ~/.oci/config")
        print("2. Verify the profile name exists in the config file")
        print("3. Check that all required fields are present (user, fingerprint, key_file, tenancy, region)")
        return None

# Default configuration
compartment_id = "ocid1.compartment.oc1..aaaaaaaajbsk4btzn6oymimjelztkawcgf2qwq3jlnhrwn4pnnla2umcsmva"
config = None  # Will be set when processing image

# Service endpoint
endpoint = "https://inference.generativeai.us-chicago-1.oci.oraclecloud.com"

def encode_image(image_path):
    """Encode image to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_region_from_code(code):
    """Get OCI region identifier from region code."""
    region_mapping = {
        # Australia
        'syd': 'ap-sydney-1',
        'mel': 'ap-melbourne-1',
        
        # Brazil
        'gru': 'sa-saopaulo-1',
        'vcp': 'sa-vinhedo-1',
        
        # Canada
        'yul': 'ca-montreal-1',
        'yyz': 'ca-toronto-1',
        
        # Chile
        'scl': 'sa-santiago-1',
        'vap': 'sa-valparaiso-1',
        
        # Colombia
        'bog': 'sa-bogota-1',
        
        # France
        'cdg': 'eu-paris-1',
        'mrs': 'eu-marseille-1',
        
        # Germany
        'fra': 'eu-frankfurt-1',
        
        # India
        'hyd': 'ap-hyderabad-1',
        'bom': 'ap-mumbai-1',
        
        # Israel
        'mtz': 'il-jerusalem-1',
        
        # Italy
        'lin': 'eu-milan-1',
        
        # Japan
        'kix': 'ap-osaka-1',
        'nrt': 'ap-tokyo-1',
        
        # Mexico
        'qro': 'mx-queretaro-1',
        'mty': 'mx-monterrey-1',
        
        # Netherlands
        'ams': 'eu-amsterdam-1',
        
        # Saudi Arabia
        'ruh': 'me-riyadh-1',
        'jed': 'me-jeddah-1',
        
        # Serbia
        'beg': 'eu-jovanovac-1',
        
        # Singapore
        'sin': 'ap-singapore-1',
        'xsp': 'ap-singapore-2',
        
        # South Africa
        'jnb': 'af-johannesburg-1',
        
        # South Korea
        'icn': 'ap-seoul-1',
        'yny': 'ap-chuncheon-1',
        
        # Spain
        'mad': 'eu-madrid-1',
        
        # Sweden
        'arn': 'eu-stockholm-1',
        
        # Switzerland
        'zrh': 'eu-zurich-1',
        
        # UAE
        'auh': 'me-abudhabi-1',
        'dxb': 'me-dubai-1',
        
        # UK
        'lhr': 'uk-london-1',
        'cwl': 'uk-cardiff-1',
        
        # US
        'iad': 'us-ashburn-1',
        'ord': 'us-chicago-1',
        'phx': 'us-phoenix-1',
        'sjc': 'us-sanjose-1'
    }
    
    code = code.lower()
    return region_mapping.get(code)

def get_region_from_name(name):
    """Get region identifier from full city/region name."""
    name = name.lower()
    city_mapping = {
        # Australia
        'sydney': 'ap-sydney-1',
        'melbourne': 'ap-melbourne-1',
        
        # Brazil
        'sao paulo': 'sa-saopaulo-1',
        'vinhedo': 'sa-vinhedo-1',
        
        # Canada
        'montreal': 'ca-montreal-1',
        'toronto': 'ca-toronto-1',
        
        # Chile
        'santiago': 'sa-santiago-1',
        'valparaiso': 'sa-valparaiso-1',
        
        # Colombia
        'bogota': 'sa-bogota-1',
        
        # France
        'paris': 'eu-paris-1',
        'marseille': 'eu-marseille-1',
        
        # Germany
        'frankfurt': 'eu-frankfurt-1',
        
        # India
        'hyderabad': 'ap-hyderabad-1',
        'mumbai': 'ap-mumbai-1',
        
        # Israel
        'jerusalem': 'il-jerusalem-1',
        
        # Italy
        'milan': 'eu-milan-1',
        
        # Japan
        'osaka': 'ap-osaka-1',
        'tokyo': 'ap-tokyo-1',
        
        # Mexico
        'queretaro': 'mx-queretaro-1',
        'monterrey': 'mx-monterrey-1',
        
        # Netherlands
        'amsterdam': 'eu-amsterdam-1',
        
        # Saudi Arabia
        'riyadh': 'me-riyadh-1',
        'jeddah': 'me-jeddah-1',
        
        # Serbia
        'jovanovac': 'eu-jovanovac-1',
        
        # Singapore
        'singapore': 'ap-singapore-1',
        
        # South Africa
        'johannesburg': 'af-johannesburg-1',
        
        # South Korea
        'seoul': 'ap-seoul-1',
        'chuncheon': 'ap-chuncheon-1',
        
        # Spain
        'madrid': 'eu-madrid-1',
        
        # Sweden
        'stockholm': 'eu-stockholm-1',
        
        # Switzerland
        'zurich': 'eu-zurich-1',
        
        # UAE
        'abu dhabi': 'me-abudhabi-1',
        'dubai': 'me-dubai-1',
        
        # UK
        'london': 'uk-london-1',
        'newport': 'uk-cardiff-1',
        'cardiff': 'uk-cardiff-1',
        
        # US
        'ashburn': 'us-ashburn-1',
        'chicago': 'us-chicago-1',
        'phoenix': 'us-phoenix-1',
        'san jose': 'us-sanjose-1'
    }
    
    # Try exact match first
    for city, region in city_mapping.items():
        if city in name:
            return region
    return None

def extract_region_from_name(name):
    """Extract region from resource name."""
    print(f"\nDebug: Extracting region from name: {name}")
    name = name.lower()
    
    # Check for common patterns first
    if 'mad' in name or 'madrid' in name:
        print(f"Debug: Found Madrid pattern")
        return 'eu-madrid-1'
    elif 'fra' in name or 'frankfurt' in name:
        return 'eu-frankfurt-1'
    elif 'lon' in name or 'lhr' in name or 'london' in name:
        return 'uk-london-1'
    elif 'ash' in name or 'iad' in name or 'ashburn' in name:
        return 'us-ashburn-1'
    elif 'phx' in name or 'phoenix' in name:
        return 'us-phoenix-1'
    elif 'syd' in name or 'sydney' in name:
        return 'ap-sydney-1'
    elif 'mel' in name or 'melbourne' in name:
        return 'ap-melbourne-1'
    elif 'sin' in name or 'singapore' in name:
        return 'ap-singapore-1'
    elif 'bom' in name or 'mumbai' in name:
        return 'ap-mumbai-1'
    elif 'hyd' in name or 'hyderabad' in name:
        return 'ap-hyderabad-1'
    elif 'tok' in name or 'nrt' in name or 'tokyo' in name:
        return 'ap-tokyo-1'
    elif 'osa' in name or 'kix' in name or 'osaka' in name:
        return 'ap-osaka-1'
    elif 'seo' in name or 'icn' in name or 'seoul' in name:
        return 'ap-seoul-1'
    elif 'par' in name or 'cdg' in name or 'paris' in name:
        return 'eu-paris-1'
    elif 'ams' in name or 'amsterdam' in name:
        return 'eu-amsterdam-1'
    elif 'mil' in name or 'lin' in name or 'milan' in name:
        return 'eu-milan-1'
    elif 'sto' in name or 'arn' in name or 'stockholm' in name:
        return 'eu-stockholm-1'
    elif 'zur' in name or 'zrh' in name or 'zurich' in name:
        return 'eu-zurich-1'
    
    # If no pattern match, try exact region codes
    for part in name.split('-'):
        print(f"Debug: Checking part: {part}")
        region = get_region_from_code(part)
        if region:
            print(f"Debug: Found region from code: {region}")
            return region
    
    # Try full city/region name matching as last resort
    region = get_region_from_name(name)
    if region:
        print(f"Debug: Found region from city name: {region}")
        return region
    
    print("Debug: No region pattern found")
    return None

def parse_network_resources(ai_response):
    # Set a default compartment ID
    global compartment_id
    compartment_id = "var.tenancy_ocid"  # Default to variable reference
    """Parse network resources from AI response.
    Args:
        ai_response (str): Response from AI service
    Returns:
        dict: Dictionary containing project name and regions with their resources
    """
    print("\nDEBUG: Starting parse_network_resources function")
    print(f"DEBUG: AI response type: {type(ai_response)}")
    print(f"DEBUG: AI response first 100 chars: {ai_response[:100] if isinstance(ai_response, str) else 'Not a string'}")
    def clean_value(value):
        """Clean markdown characters and extra whitespace from values."""
        if not value:
            return value
        # Remove markdown bold markers
        value = value.replace('**', '')
        # Remove other markdown characters
        value = value.strip('*_ `')
        value = value.strip()
        return "" if value.lower() in ["not provided", "not found", ""] else value

    def clean_line(line):
        """Clean a line of text from markdown and extra whitespace."""
        # Remove markdown bold markers
        line = line.replace('**', '')
        # Remove other markdown characters
        line = line.strip('*_ `')
        return line.strip()
        
    def extract_compartment_from_resource_names(resources):
        """Extract compartment name from resource names if not already set."""
        if resources.get('compartment_name'):
            return resources['compartment_name']
            
        # Try to extract from DRG names
        for region, region_data in resources['regions'].items():
            if region_data.get('drg'):
                drg_name = region_data['drg']
                if isinstance(drg_name, str):
                    match = re.search(r'^([\w\s-]+)-(?:phoenix|ashburn|mumbai|phx|ash|mum)', drg_name, re.IGNORECASE)
                    if match:
                        compartment_name = match.group(1).strip()
                        print(f"Debug: Extracted compartment name from DRG: {compartment_name}")
                        return compartment_name
                    
            # Try to extract from gateway names
            for gateway_type in ['internet_gateway', 'nat_gateway', 'service_gateway']:
                if region_data.get(gateway_type):
                    gateway_name = region_data[gateway_type]
                    if isinstance(gateway_name, str):
                        match = re.search(r'^([\w\s-]+)-(?:phoenix|ashburn|mumbai|phx|ash|mum)', gateway_name, re.IGNORECASE)
                        if match:
                            compartment_name = match.group(1).strip()
                            print(f"Debug: Extracted compartment name from {gateway_type}: {compartment_name}")
                            return compartment_name
                        
            # Try to extract from VCN names
            for vcn_name in region_data.get('vcns', {}).keys():
                match = re.search(r'^([\w\s-]+)[-_](?:phoenix|ashburn|mumbai|phx|ash|mum)', vcn_name, re.IGNORECASE)
                if match:
                    compartment_name = match.group(1).strip()
                    print(f"Debug: Extracted compartment name from VCN: {compartment_name}")
                    return compartment_name
                
            # Try to extract from display names in VCNs
            for vcn_data in region_data.get('vcns', {}).values():
                if isinstance(vcn_data, dict) and 'display_name' in vcn_data:
                    display_name = vcn_data['display_name']
                    match = re.search(r'^([\w\s-]+)-(?:phoenix|ashburn|mumbai|phx|ash|mum)', display_name, re.IGNORECASE)
                    if match:
                        compartment_name = match.group(1).strip()
                        print(f"Debug: Extracted compartment name from VCN display name: {compartment_name}")
                        return compartment_name
                    
        # Default to project name if available
        if resources.get('project_name') and resources['project_name'] != 'default_project':
            return resources['project_name']
            
        return None

    def validate_cidr(cidr, name, resource_type="VCN"):
        """Validate CIDR format and log details."""
        if not cidr:
            print(f"Warning: Empty CIDR for {resource_type} {name}")
            return ""
            
        # Clean the CIDR while preserving essential characters
        cidr = cidr.strip('[]"\'() ')
        cidr = cidr.replace(' ', '')
        
        # Extract CIDR pattern using more flexible regex
        import re
        cidr_pattern = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2})', cidr)
        if not cidr_pattern:
            print(f"Warning: Could not find valid CIDR pattern in {cidr} for {resource_type} {name}")
            return ""
            
        cidr = cidr_pattern.group(1)
        
        try:
            ip, prefix = cidr.split('/')
            prefix = int(prefix)
            
            octets = [int(octet) for octet in ip.split('.')]
            if len(octets) != 4 or not all(0 <= octet <= 255 for octet in octets):
                raise ValueError("Invalid IP address")
                
            if not (8 <= prefix <= 30):
                raise ValueError("Invalid prefix length")
                
            print(f"Debug: Valid CIDR format found for {resource_type} {name}: {cidr}")
            return cidr
            
        except (ValueError, IndexError) as e:
            print(f"Warning: Invalid CIDR format for {resource_type} {name}: {cidr} - {str(e)}")
            return ""

    try:
        print("\nDebug: Starting resource parsing")
        print("Debug: AI Response:")
        print(ai_response)
        
        # Initialize result structure
        result = {
            'project_name': 'default_project',
            'compartment_id': compartment_id,  # Use the global compartment_id
            'compartment_name': None,  # Will be populated if found
            'regions': {},
            'compartments': {}  # Store compartment information
        }
        
        # Process the response line by line
        lines = ai_response.split('\n')
        i = 0
        current_region = None
        current_vcn = None
        
        while i < len(lines):
            line = clean_line(lines[i])
            
            if not line:
                i += 1
                continue
                
            # Extract project name and compartment info
            if line.startswith('Project:'):
                i += 1
                while i < len(lines) and not clean_line(lines[i]).startswith('Region:'):
                    current_line = clean_line(lines[i])
                    if current_line.startswith('Name:'):
                        project_name = clean_value(current_line.split('Name:')[1])
                        if project_name:
                            result['project_name'] = project_name
                            # Also use project name as compartment name if not already set
                            if not result['compartment_name']:
                                result['compartment_name'] = project_name
                                # Add to compartments dictionary
                                result['compartments'][project_name] = {
                                    'name': project_name,
                                    'description': f"{project_name} Compartment",
                                    'enable_delete': True
                                }
                            print(f"Debug: Found project name: {project_name}")
                    elif current_line.startswith('Compartment:') or 'Compartment Name:' in current_line or 'Compartment' in current_line:
                        # Extract compartment name
                        if current_line.startswith('Compartment:'):
                            compartment_name = clean_value(current_line.split('Compartment:')[1])
                        elif 'Compartment Name:' in current_line:
                            compartment_name = clean_value(current_line.split('Compartment Name:')[1])
                        elif 'Compartment' in current_line and ':' in current_line:
                            compartment_name = clean_value(current_line.split(':')[1])
                        else:
                            # Try to extract compartment name using regex
                            match = re.search(r'Compartment\s+([\w\s-]+)', current_line, re.IGNORECASE)
                            if match:
                                compartment_name = match.group(1).strip()
                            else:
                                compartment_name = None
                            
                        if compartment_name:
                            result['compartment_name'] = compartment_name
                            # Add to compartments dictionary
                            result['compartments'][compartment_name] = {
                                'name': compartment_name,
                                'description': f"{compartment_name} Compartment",
                                'enable_delete': True
                            }
                            print(f"Debug: Found compartment name: {compartment_name}")
                    i += 1
                continue
                
            # Process region sections
            if line.startswith('Region:'):
                region_name = clean_value(line.split('Region:')[1])
                if region_name:
                    current_region = region_name
                    print(f"Debug: Processing region: {region_name}")
                    if current_region not in result['regions']:
                        result['regions'][current_region] = {
                            'vcns': {},
                            'subnets': [],
                            'drg': None,
                            'internet_gateway': None,
                            'nat_gateway': None,
                            'service_gateway': None
                        }
                i += 1
                continue
                
            # Process VCN section
            if line.startswith('VCN:'):
                i += 1
                while i < len(lines) and clean_line(lines[i]).startswith('-'):
                    vcn_line = clean_line(lines[i]).strip('- ')
                    vcn_data = {}
                    
                    # Process VCN properties
                    while i < len(lines) and (clean_line(lines[i]).startswith('-') or '  ' in lines[i]):
                        current_line = clean_line(lines[i])
                        if 'Name:' in current_line:
                            vcn_name = clean_value(current_line.split('Name:')[1])
                            if vcn_name:
                                vcn_data['display_name'] = vcn_name
                                current_vcn = vcn_name
                                print(f"Debug: Found VCN: {vcn_name}")
                        elif 'CIDR:' in current_line:
                            vcn_data['cidr_block'] = validate_cidr(clean_value(current_line.split('CIDR:')[1]), vcn_data.get('display_name', 'unknown'))
                        elif 'Description:' in current_line:
                            vcn_data['description'] = clean_value(current_line.split('Description:')[1])
                        i += 1
                        
                    if vcn_data.get('display_name'):
                        result['regions'][current_region]['vcns'][vcn_data['display_name']] = vcn_data
                continue
                
            # Process Subnets section
            if line.startswith('Subnets:'):
                i += 1
                while i < len(lines) and i < len(lines):
                    if not clean_line(lines[i]).startswith('-'):
                        # If we're not on a subnet line anymore, break out
                        if not ('  ' in lines[i] and i > 0 and clean_line(lines[i-1]).startswith('-')):
                            break
                    
                    if clean_line(lines[i]).startswith('-'):
                        # Start of a new subnet
                        subnet_data = {}
                        subnet_line = clean_line(lines[i]).strip('- ')
                        
                        # Check if this line contains the name
                        if 'Name:' in subnet_line:
                            subnet_name = clean_value(subnet_line.split('Name:')[1])
                            if subnet_name:
                                subnet_data['display_name'] = subnet_name
                                print(f"Debug: Found subnet: {subnet_name}")
                        
                        # Move to next line
                        i += 1
                        
                        # Process remaining subnet properties
                        while i < len(lines) and ('  ' in lines[i] or clean_line(lines[i]) == ''):
                            current_line = clean_line(lines[i])
                            if 'CIDR:' in current_line:
                                subnet_data['cidr_block'] = validate_cidr(clean_value(current_line.split('CIDR:')[1]), subnet_data.get('display_name', 'unknown'), "Subnet")
                            elif 'Type:' in current_line:
                                subnet_type = clean_value(current_line.split('Type:')[1])
                                subnet_data['type'] = 'public' if subnet_type.lower() == 'public' else 'private'
                            elif 'Description:' in current_line:
                                subnet_data['description'] = clean_value(current_line.split('Description:')[1])
                            i += 1
                        
                        # Add the subnet to the result if it has a name
                        if subnet_data.get('display_name'):
                            # Associate subnet with current VCN
                            if current_vcn:
                                subnet_data['parent_vcn'] = current_vcn
                            elif result['regions'][current_region]['vcns']:
                                subnet_data['parent_vcn'] = next(iter(result['regions'][current_region]['vcns'].keys()))
                            result['regions'][current_region]['subnets'].append(subnet_data)
                            print(f"Debug: Added subnet {subnet_data['display_name']} to region {current_region}")
                    else:
                        # Skip any non-subnet lines
                        i += 1
                continue
                
            # Process Gateways section
            if line.startswith('Gateways:'):
                i += 1
                while i < len(lines) and i < len(lines):
                    # Break if we're not in the gateways section anymore
                    if not clean_line(lines[i]).startswith('-') and not '  ' in lines[i]:
                        break
                        
                    gateway_line = clean_line(lines[i]).strip('- ')
                    
                    if 'DRG:' in gateway_line:
                        value = clean_value(gateway_line.split('DRG:')[1])
                        if value.lower() == 'yes':
                            project_prefix = result['project_name'].lower().replace(' ', '_')
                            region_code = current_region.lower()
                            result['regions'][current_region]['drg'] = {
                                'display_name': f"{project_prefix}-{region_code}-drg",
                                'enabled': True
                            }
                            print(f"Debug: Added DRG to region {current_region}")
                    elif 'Internet Gateway:' in gateway_line:
                        value = clean_value(gateway_line.split('Internet Gateway:')[1])
                        if value.lower() == 'yes':
                            project_prefix = result['project_name'].lower().replace(' ', '_')
                            region_code = current_region.lower()
                            result['regions'][current_region]['internet_gateway'] = {
                                'display_name': f"{project_prefix}-{region_code}-igw",
                                'enabled': True
                            }
                            print(f"Debug: Added Internet Gateway to region {current_region}")
                    elif 'NAT Gateway:' in gateway_line:
                        value = clean_value(gateway_line.split('NAT Gateway:')[1])
                        if value.lower() == 'yes':
                            project_prefix = result['project_name'].lower().replace(' ', '_')
                            region_code = current_region.lower()
                            result['regions'][current_region]['nat_gateway'] = {
                                'display_name': f"{project_prefix}-{region_code}-ngw",
                                'enabled': True
                            }
                            print(f"Debug: Added NAT Gateway to region {current_region}")
                    elif 'Service Gateway:' in gateway_line:
                        value = clean_value(gateway_line.split('Service Gateway:')[1])
                        if value.lower() == 'yes':
                            project_prefix = result['project_name'].lower().replace(' ', '_')
                            region_code = current_region.lower()
                            result['regions'][current_region]['service_gateway'] = {
                                'display_name': f"{project_prefix}-{region_code}-sgw",
                                'enabled': True
                            }
                            print(f"Debug: Added Service Gateway to region {current_region}")
                    i += 1
                continue
                
            i += 1
        
        print("\nDebug: Final Parsed Resources:")
        print(f"Project Name: {result['project_name']}")
        print(f"Compartment Name: {result.get('compartment_name', 'Not set')}")
        print(f"Compartment ID: {result.get('compartment_id', 'Not set')}")
        print(f"Compartments: {result.get('compartments', {})}")
        
        for region, resources in result['regions'].items():
            print(f"\nRegion: {region}")
            print(f"VCNs: {resources['vcns']}")
            
            # Print all subnets
            print(f"Subnets: {len(resources['subnets'])} found")
            for i, subnet in enumerate(resources['subnets']):
                print(f"  Subnet {i+1}: {subnet['display_name']} - {subnet.get('cidr_block', 'No CIDR')} - Type: {subnet.get('type', 'unknown')} - Parent VCN: {subnet.get('parent_vcn', 'None')}")
                
            print(f"DRG: {resources['drg']}")
            print(f"IGW: {resources['internet_gateway']}")
            print(f"NGW: {resources['nat_gateway']}")
            print(f"SGW: {resources['service_gateway']}")
        
        return result
        
    except Exception as e:
        print(f"Error parsing resources: {str(e)}")
        print("Debug: Stack trace:")
        import traceback
        traceback.print_exc()
        return None

def read_oci_config(profile_name):
    """Read OCI config file and return config values."""
    try:
        config = oci.config.from_file('~/.oci/config', profile_name)
        return {
            'tenancy_ocid': config.get('tenancy'),
            'user_ocid': config.get('user'),
            'fingerprint': config.get('fingerprint'),
            'private_key_path': config.get('key_file'),
            'region': config.get('region', 'us-ashburn-1')
        }
    except Exception as e:
        print(f"Error reading OCI config: {str(e)}")
        return None

def generate_tfvars(resources, region):
    """Generate tfvars content from parsed resources."""
    # Initialize empty tfvars list
    tfvars = []
    
    # Validate inputs
    if not resources or not isinstance(resources, dict):
        print("Error: Invalid resources provided")
        return ""
        
    if not region or not isinstance(region, str):
        print("Warning: Invalid region, using default")
        region = "us-ashburn-1"
    
    # Add region
    tfvars.append(f'region = "{region}"')
    
    # Add compartments
    tfvars.append("\n# Compartments")
    compartments = {}
    if resources.get('compartments') and isinstance(resources['compartments'], dict):
        for name, compartment in resources['compartments'].items():
            if isinstance(compartment, dict) and compartment.get('name'):
                compartments[name] = {
                    'name': compartment.get('name'),
                    'description': compartment.get('description', f"Compartment for {name} resources"),
                    'enable_delete': compartment.get('enable_delete', True)
                }
    tfvars.append(f"compartments = {json.dumps(compartments, indent=2)}")
    
    # Add VCNs
    tfvars.append("\n# VCNs")
    vcns = {}
    if resources.get('vcns') and isinstance(resources['vcns'], dict):
        for name, vcn in resources['vcns'].items():
            if isinstance(vcn, dict) and vcn.get('display_name'):
                vcns[name] = {
                    'compartment_name': vcn.get('compartment_name', next(iter(compartments.keys())) if compartments else 'root'),
                    'display_name': vcn.get('display_name'),
                    'cidr_block': vcn.get('cidr_block', "10.0.0.0/16"),
                    'section': vcn.get('section', 'Main')
                }
    tfvars.append(f"vcns = {json.dumps(vcns, indent=2)}")
    
    # Add subnets
    tfvars.append("\n# Subnets")
    subnets = []
    if resources.get('subnets') and isinstance(resources['subnets'], list):
        for subnet in resources['subnets']:
            if isinstance(subnet, dict) and subnet.get('display_name'):
                subnets.append({
                    'compartment_name': subnet.get('compartment_name', next(iter(compartments.keys())) if compartments else 'root'),
                    'display_name': subnet.get('display_name'),
                    'cidr_block': subnet.get('cidr_block', "10.0.1.0/24"),
                    'type': subnet.get('type', 'private'),
                    'parent_vcn': subnet.get('parent_vcn', next(iter(vcns.keys())) if vcns else 'vcn')
                })
    tfvars.append(f"subnets = {json.dumps(subnets, indent=2)}")
    
    # Add DRG if present
    if resources.get('drg') and isinstance(resources['drg'], dict):
        tfvars.append("\n# DRG")
        drg = {
            'compartment_name': resources['drg'].get('compartment_name', next(iter(compartments.keys())) if compartments else 'root'),
            'display_name': resources['drg'].get('display_name', 'drg'),
            'enabled': resources['drg'].get('enabled', True)
        }
        tfvars.append(f"drg = {json.dumps(drg, indent=2)}")
    
    # Add Internet Gateway if present
    if resources.get('internet_gateway') and isinstance(resources['internet_gateway'], dict):
        tfvars.append("\n# Internet Gateway")
        internet_gateway = {
            'compartment_name': resources['internet_gateway'].get('compartment_name', next(iter(compartments.keys())) if compartments else 'root'),
            'display_name': resources['internet_gateway'].get('display_name', 'igw'),
            'enabled': resources['internet_gateway'].get('enabled', True)
        }
        tfvars.append(f"internet_gateway = {json.dumps(internet_gateway, indent=2)}")
    
    # Add NAT Gateway if present
    if resources.get('nat_gateway') and isinstance(resources['nat_gateway'], dict):
        tfvars.append("\n# NAT Gateway")
        nat_gateway = {
            'compartment_name': resources['nat_gateway'].get('compartment_name', next(iter(compartments.keys())) if compartments else 'root'),
            'display_name': resources['nat_gateway'].get('display_name', 'ngw'),
            'enabled': resources['nat_gateway'].get('enabled', True)
        }
        tfvars.append(f"nat_gateway = {json.dumps(nat_gateway, indent=2)}")
    
    return "\n".join(tfvars)

def generate_terraform(resources, output_dir, profile_name='DEFAULT'):
    print(f"DEBUG: Resources in generate_terraform: {resources}")
    print(f"DEBUG: Regions in resources: {list(resources['regions'].keys())}")
    print(f"DEBUG: Compartment name: {resources.get('compartment_name', 'Not set')}")
    print(f"DEBUG: Compartments: {resources.get('compartments', {})}")
    
    # Ensure compartments key exists
    if 'compartments' not in resources:
        resources['compartments'] = {}
        
    # Add default compartment if none exists
    if not resources['compartments'] and resources.get('compartment_name'):
        comp_name = resources['compartment_name']
        resources['compartments'][comp_name] = {
            'name': comp_name,
            'description': f"{comp_name} Compartment",
            'enable_delete': True
        }
    
    # Print details of each region's resources
    for region, region_data in resources['regions'].items():
        print(f"\nDEBUG: Region {region} details:")
        print(f"  VCNs: {len(region_data['vcns'])} found")
        print(f"  Subnets: {len(region_data['subnets'])} found")
        for i, subnet in enumerate(region_data['subnets']):
            print(f"    Subnet {i+1}: {subnet['display_name']} - {subnet.get('cidr_block', 'No CIDR')} - Parent VCN: {subnet.get('parent_vcn', 'None')}")
        print(f"  Gateways: DRG={region_data['drg'] is not None}, IGW={region_data['internet_gateway'] is not None}, NGW={region_data['nat_gateway'] is not None}, SGW={region_data['service_gateway'] is not None}")
    """Generate Terraform configuration files.
    Args:
        resources (dict): Dictionary containing project name and regions with their resources
        output_dir (str): Directory to write Terraform files
        profile_name (str): OCI config profile name
    Returns:
        bool: True if successful, False otherwise
    """
    print("\nDEBUG: Starting generate_terraform function")
    print(f"DEBUG: Resources type: {type(resources)}")
    print(f"DEBUG: Resources keys: {resources.keys() if isinstance(resources, dict) else 'Not a dict'}")
    print(f"DEBUG: Compartment name: {resources.get('compartment_name', 'Not set')}")
    print(f"DEBUG: Compartments: {resources.get('compartments', {})}")
    print(f"DEBUG: Output directory: {output_dir}")
    try:
        # Ensure we have compartment information
        if not resources.get('compartment_name') and resources.get('project_name'):
            resources['compartment_name'] = resources['project_name']
            print(f"DEBUG: Using project name as compartment name: {resources['compartment_name']}")
            
        # Initialize compartments dictionary if needed
        if not resources.get('compartments') and resources.get('compartment_name'):
            comp_name = resources['compartment_name']
            resources['compartments'] = {
                comp_name: {
                    'name': comp_name,
                    'description': f"{comp_name} Compartment",
                    'enable_delete': True
                }
            }
            print(f"DEBUG: Initialized compartments dictionary with: {comp_name}")
        
        # Read config values
        config_values = read_oci_config(profile_name)
        if not config_values:
            print("Warning: Could not read OCI config, using empty defaults")
            config_values = {
                'tenancy_ocid': "",
                'user_ocid': "",
                'fingerprint': "",
                'private_key_path': "",
                'region': next(iter(resources['regions'].keys())) if resources.get('regions') else 'us-ashburn-1'
            }

        # Create provider.tf
        provider_tf = os.path.join(output_dir, 'provider.tf')
        with open(provider_tf, 'w') as f:
            f.write("""// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
# Provider Block 
# OCI
############################

provider "oci" {
  tenancy_ocid        = var.tenancy_ocid
  user_ocid           = var.user_ocid
  fingerprint         = var.fingerprint
  private_key_path    = var.private_key_path
  region              = var.region
  ignore_defined_tags = ["Oracle-Tags.CreatedBy", "Oracle-Tags.CreatedOn"]
}

terraform {
  required_providers {
    oci = {
      source = "oracle/oci"
      version = "5.40.0"
    }
  }
}
""")

        # Create variables.tf with actual values from config
        variables_tf = os.path.join(output_dir, 'variables.tf')
        with open(variables_tf, 'w') as f:
            f.write(f"""// Copyright (c) 2021, 2022, Oracle and/or its affiliates.

############################
#
# Variables Block
# OCI
#
############################

variable "tenancy_ocid" {{
  type    = string
  default = "{config_values['tenancy_ocid']}"
}}

variable "user_ocid" {{
  type    = string
  default = "{config_values['user_ocid']}"
}}

variable "fingerprint" {{
  type    = string
  default = "{config_values['fingerprint']}"
}}

variable "private_key_path" {{
  type    = string
  default = "{config_values['private_key_path']}"
}}

variable "region" {{
  type    = string
  default = "{config_values['region']}"
}}
""")

        # Create main.tf
        main_tf = os.path.join(output_dir, 'main.tf')
        with open(main_tf, 'w') as f:
            # Create the compartment if we have a compartment name
            if resources.get('compartment_name'):
                compartment_name = resources['compartment_name']
                safe_name = compartment_name.lower().replace(' ', '_').replace('-', '_')
                f.write(f"""
############################
# Resource Block - Identity
# Create Compartment
############################

resource "oci_identity_compartment" "{safe_name}_compartment" {{  
  name           = "{compartment_name}"
  description    = "{compartment_name} Compartment"
  compartment_id = var.tenancy_ocid
  enable_delete  = true
}}
""")
            
            # Write VCNs for each region
            for region, region_resources in resources['regions'].items():
                f.write(f"""
############################
# Resource Block - Network
# Create VCNs - {region}
############################
""")
                for vcn_name, vcn in region_resources['vcns'].items():
                    f.write(f"""
resource "oci_core_vcn" "{vcn_name.replace(' ', '_').replace('-', '_')}" {{
  compartment_id = {f"oci_identity_compartment.{resources['compartment_name'].lower().replace(' ', '_').replace('-', '_')}_compartment.id" if resources.get('compartment_name') else "var.tenancy_ocid"}
  cidr_blocks    = ["{vcn['cidr_block']}"]
  display_name   = "{vcn['display_name']}"
  dns_label      = "{vcn_name.replace('-', '')[:15]}"
}}
""")

                # Write Subnets for this region
                f.write(f"""
############################
# Resource Block - Network
# Create Subnets - {region}
############################
""")
                # Write all subnets for this region
                for subnet in region_resources['subnets']:
                    subnet_name = subnet['display_name'].replace('-', '_')
                    parent_vcn = subnet['parent_vcn'].replace('-', '_')
                    
                    f.write(f"""
resource "oci_core_subnet" "{subnet_name.replace(' ', '_').replace('-', '_')}" {{
  compartment_id = {f"oci_identity_compartment.{resources['compartment_name'].lower().replace(' ', '_').replace('-', '_')}_compartment.id" if resources.get('compartment_name') else "var.tenancy_ocid"}
  vcn_id         = oci_core_vcn.{parent_vcn}.id
  cidr_block     = "{subnet['cidr_block']}"
  display_name   = "{subnet['display_name']}"
  dns_label      = "{subnet_name[:15]}"
  prohibit_public_ip_on_vnic = {str(subnet['type'] != 'public').lower()}
}}
""")

                # Write DRG if present
                if region_resources['drg']:
                    drg = region_resources['drg']
                    drg_name = drg['display_name'] if drg['display_name'] else 'drg'
                    
                    f.write(f"""
############################
# Resource Block - Network
# Create DRG - {region}
############################

resource "oci_core_drg" "{drg_name.replace(' ', '_').replace('-', '_')}" {{
  compartment_id = {f"oci_identity_compartment.{resources['compartment_name'].lower().replace(' ', '_').replace('-', '_')}_compartment.id" if resources.get('compartment_name') else "var.tenancy_ocid"}
  display_name   = "{drg_name}"
}}

# Attach DRG to VCN
resource "oci_core_drg_attachment" "{drg_name.replace('-', '_')}_attachment" {{
  drg_id = oci_core_drg.{drg_name.replace('-', '_')}.id
  vcn_id = oci_core_vcn.{list(region_resources['vcns'].keys())[0].replace('-', '_')}.id
}}
""")

                # Write Internet Gateway if present
                if region_resources['internet_gateway']:
                    igw = region_resources['internet_gateway']
                    igw_name = igw['display_name'] if igw['display_name'] else 'internet_gateway'
                    
                    f.write(f"""
############################
# Resource Block - Network
# Create Internet Gateway - {region}
############################

resource "oci_core_internet_gateway" "{igw_name.replace(' ', '_').replace('-', '_')}" {{
  compartment_id = {f"oci_identity_compartment.{resources['compartment_name'].lower().replace(' ', '_').replace('-', '_')}_compartment.id" if resources.get('compartment_name') else "var.tenancy_ocid"}
  vcn_id         = oci_core_vcn.{list(region_resources['vcns'].keys())[0].replace('-', '_')}.id
  display_name   = "{igw_name}"
  enabled        = true
}}
""")

                # Write NAT Gateway if present
                if region_resources['nat_gateway']:
                    ngw = region_resources['nat_gateway']
                    ngw_name = ngw['display_name'] if ngw['display_name'] else 'nat_gateway'
                    
                    f.write(f"""
############################
# Resource Block - Network
# Create NAT Gateway - {region}
############################

resource "oci_core_nat_gateway" "{ngw_name.replace(' ', '_').replace('-', '_')}" {{
  compartment_id = {f"oci_identity_compartment.{resources['compartment_name'].lower().replace(' ', '_').replace('-', '_')}_compartment.id" if resources.get('compartment_name') else "var.tenancy_ocid"}
  vcn_id         = oci_core_vcn.{list(region_resources['vcns'].keys())[0].replace('-', '_')}.id
  display_name   = "{ngw_name}"
}}
""")

                # Write Service Gateway if present
                if region_resources['service_gateway']:
                    sgw = region_resources['service_gateway']
                    sgw_name = sgw['display_name'] if sgw['display_name'] else 'service_gateway'
                    
                    f.write(f"""
############################
# Resource Block - Network
# Create Service Gateway - {region}
############################

resource "oci_core_service_gateway" "{sgw_name.replace(' ', '_').replace('-', '_')}" {{
  compartment_id = {f"oci_identity_compartment.{resources['compartment_name'].lower().replace(' ', '_').replace('-', '_')}_compartment.id" if resources.get('compartment_name') else "var.tenancy_ocid"}
  vcn_id         = oci_core_vcn.{list(region_resources['vcns'].keys())[0].replace('-', '_')}.id
  display_name   = "{sgw_name}"
  services {{
    service_id = data.oci_core_services.all_oci_services.services[0].id
  }}
}}

data "oci_core_services" "all_oci_services" {{
  filter {{
    name   = "name"
    values = ["All .* Services In Oracle Services Network"]
    regex  = true
  }}
}}
""")

        print(f"\nGenerated Terraform files in {output_dir}")
        return True

    except Exception as e:
        print(f"Error generating Terraform files: {str(e)}")
        print("Debug: Stack trace:")
        import traceback
        traceback.print_exc()
        return False

def process_image(image_path, profile_name='DEFAULT', model_id=None):
    """Process the image and generate Terraform files.
    Args:
        image_path (str): Path to the image file
        profile_name (str): OCI config profile name to use
        model_id (str, optional): OCID of the generative AI model to use. If not provided, a default model will be used.
    Returns:
        dict: Dictionary containing region -> files mapping
    """
    try:
        print("\nDEBUG: Starting process_image function")
        # Get configuration for the specified profile
        config = get_config(profile_name)
        
        # Check if we should use mock data for testing
        use_mock_data = os.environ.get('USE_MOCK_DATA', '').lower() in ('true', '1', 't', 'yes')
        if use_mock_data:
            print("\nDEBUG: Using mock data for testing (USE_MOCK_DATA=True)")
            # Return mock data for testing
            mock_ai_response = """
Region: us-ashburn-1
VCN:
- Name: test-ash-hub-vcn
  CIDR: 10.0.0.0/16
  Description: Hub VCN for us-ashburn-1 region
Subnets:
- Name: test-ash-web-subnet
  CIDR: 10.0.1.0/24
  Type: Public
  Description: Web tier subnet
- Name: test-ash-app-subnet
  CIDR: 10.0.2.0/24
  Type: Private
  Description: Application tier subnet
Gateways:
- DRG: yes
- Internet Gateway: yes
- NAT Gateway: yes
- Service Gateway: yes
"""
            resources = parse_network_resources(mock_ai_response)
            if resources:
                # Set compartment name for testing
                resources['compartment_name'] = 'test'
                resources['compartments'] = {
                    'test': {
                        'name': 'test',
                        'description': 'Test Compartment',
                        'enable_delete': True
                    }
                }
                return resources
            
        # If not using mock data or mock data failed, proceed with normal flow
        if not config:
            raise Exception(f"Failed to load OCI configuration for profile: {profile_name}")
            
        # Initialize the Generative AI client
        generative_ai_inference_client = oci.generative_ai_inference.GenerativeAiInferenceClient(
            config=config,
            service_endpoint=endpoint,
            retry_strategy=oci.retry.NoneRetryStrategy(),
            timeout=(10, 240)
        )
        
        # Encode the image
        base64_image = encode_image(image_path)
        if not base64_image:
            raise Exception("Failed to encode image")
            
        image_url = oci.generative_ai_inference.models.ImageUrl(
            url=f"data:image/jpeg;base64,{base64_image}"
        )
        
        # Create the text content
        text_content = oci.generative_ai_inference.models.TextContent(
            text="""Extract network components from this OCI diagram using this EXACT format:

Project:
Name: <project name>

Region: <region name>
VCN:
- Name: <vcn display name - DO NOT use CIDR as name>
  CIDR: <vcn cidr>
  Description: Hub VCN for <region name> region
Subnets:
- Name: <subnet display name - DO NOT use CIDR as name>
  CIDR: <subnet cidr>
  Type: <Public/Private>
  Description: <purpose of subnet>
Gateways:
- DRG: <yes/no>
- Internet Gateway: <yes/no>
- NAT Gateway: <yes/no>
- Service Gateway: <yes/no>

Region: <next region name if exists>
[Repeat same structure]

IMPORTANT:
- Extract EXACT names and CIDRs
- DO NOT use CIDR blocks as names for VCNs or subnets
- For VCN names, use format: <project>-<region>-hub-vcn (e.g., disd-phx-hub-vcn)
- For subnet names, use format: <project>-<region>-<purpose>-subnet (e.g., disd-phx-web-subnet)
- Mark Public subnet if connected to Internet Gateway
- List ALL regions shown
- Include ALL subnets with their CIDRs
- Do not make up or modify values"""
        )
        
        # Create the image content
        image_content = oci.generative_ai_inference.models.ImageContent(
            image_url=image_url
        )
        
        # Create the message
        message = oci.generative_ai_inference.models.Message(
            role="USER",
            content=[text_content, image_content]
        )
        
        # Create the chat request with increased max_tokens
        chat_request = oci.generative_ai_inference.models.GenericChatRequest(
            messages=[message],
            max_tokens=4000,
            temperature=0.1,
            frequency_penalty=0,
            presence_penalty=0,
            top_p=0.9
        )
        
        # Set the serving mode with the model ID
        if not model_id:
            print("Error: No model_id provided. Please select a model from the UI.")
            return None
            
        serving_mode = oci.generative_ai_inference.models.OnDemandServingMode(
            model_id=model_id
        )
        
        # Create the chat details
        chat_detail = oci.generative_ai_inference.models.ChatDetails(
            serving_mode=serving_mode,
            compartment_id=compartment_id,
            chat_request=chat_request
        )
        
        # Make the API call
        try:
            print("\nDebug: About to make API call to OCI Generative AI service")
            print(f"Debug: Using endpoint: {endpoint}")
            print(f"Debug: Using compartment ID: {compartment_id}")
            print(f"Debug: Using region: {config.get('region', 'Not set')}")
            print(f"Debug: Config keys: {list(config.keys())}")
            
            chat_response = generative_ai_inference_client.chat(chat_detail)
            
            print("\nDebug: Full Chat Response:")
            print(chat_response.data)
            print("\nDebug: Response type:", type(chat_response.data))
            print("\nDebug: Response attributes:", dir(chat_response.data))
        except oci.exceptions.ServiceError as se:
            print(f"\nOCI Service Error: {se}")
            print(f"Error code: {se.code}")
            print(f"Error message: {se.message}")
            print(f"Request endpoint: {se.request_endpoint}")
            print(f"Troubleshooting tips: {se.troubleshooting_tips}")
            raise Exception(f"OCI Service Error: {se.message}")
        except Exception as e:
            print(f"\nUnexpected error during API call: {str(e)}")
            raise
        
        # Extract the response text
        ai_response = None
        
        try:
            # Direct access to the response structure we know exists
            if hasattr(chat_response.data, 'chat_response'):
                chat_response_data = chat_response.data.chat_response
                if hasattr(chat_response_data, 'choices') and len(chat_response_data.choices) > 0:
                    first_choice = chat_response_data.choices[0]
                    if hasattr(first_choice, 'message'):
                        message = first_choice.message
                        if hasattr(message, 'content') and len(message.content) > 0:
                            first_content = message.content[0]
                            if hasattr(first_content, 'text'):
                                ai_response = first_content.text
                                print("\nDebug: Successfully extracted text from response")
                                
        except Exception as e:
            print(f"Error accessing response data: {str(e)}")
            print("Debug: Stack trace:")
            import traceback
            traceback.print_exc()
        
        if not ai_response:
            print("Error: Could not extract text from AI response")
            print("Debug: Full response data:")
            print(chat_response.data)
            return None
        
        print("\nDebug: AI Service Response:")
        print(ai_response)
        
        # Parse the response and generate tfvars
        print("\nDEBUG: About to parse AI response")
        print(f"DEBUG: AI response type: {type(ai_response)}")
        
        resources = parse_network_resources(ai_response)
        if not resources:
            print("Error: Failed to parse resources from AI response")
            return None
            
        # Try to extract compartment name if not already set
        if not resources.get('compartment_name'):
            compartment_name = extract_compartment_from_resource_names(resources)
            if compartment_name:
                resources['compartment_name'] = compartment_name
                # Add to compartments dictionary
                resources['compartments'][compartment_name] = {
                    'name': compartment_name,
                    'description': f"{compartment_name} Compartment",
                    'enable_delete': True
                }
                print(f"Debug: Extracted compartment name from resource names: {compartment_name}")
            
        print("\nDebug: Parsed Resources:")
        print(f"DEBUG: Resources type: {type(resources)}")
        print(f"DEBUG: Resources keys: {resources.keys() if isinstance(resources, dict) else 'Not a dict'}")
        print(f"DEBUG: Compartment name: {resources.get('compartment_name', 'Not set')}")
        print(f"DEBUG: Compartments: {resources.get('compartments', {})}")
        
        if isinstance(resources, dict) and 'regions' in resources:
            for region, region_resources in resources['regions'].items():
                print(f"\nRegion: {region}")
                print(f"VCNs: {region_resources['vcns']}")
                print(f"Subnets: {region_resources['subnets']}")
                print(f"DRG: {region_resources['drg']}")
                print(f"IGW: {region_resources['internet_gateway']}")
                print(f"NGW: {region_resources['nat_gateway']}")
                print(f"SGW: {region_resources['service_gateway']}")
        else:
            print(f"DEBUG: Resources is not properly structured: {resources}")

        # Get project name from resources or use a default
        print(f"\nDEBUG: About to get project_name from resources")
        print(f"DEBUG: Resources type: {type(resources)}")
        
        if not isinstance(resources, dict):
            print(f"ERROR: Resources is not a dictionary, it's a {type(resources)}")
            print(f"DEBUG: Resources content: {resources}")
            project_name = 'default_project'
        else:
            try:
                project_name = resources.get('project_name')
                print(f"DEBUG: Got project_name: {project_name}")
                if not project_name or project_name is None:
                    print("Warning: No project name found in resources, using default")
                    project_name = 'default_project'
            except Exception as e:
                print(f"ERROR getting project_name: {str(e)}")
                print(f"DEBUG: Resources: {resources}")
                project_name = 'default_project'
            
        # Create base output directory
        base_dir = os.path.join(os.getcwd(), "terraform_workspace")
        project_dir = os.path.join(base_dir, project_name)
        
        # Process each region's configuration
        for region, region_resources in resources['regions'].items():
            print(f"\nProcessing region: {region}")
            
            # Create region directory
            region_dir = os.path.join(project_dir, region)
            os.makedirs(region_dir, exist_ok=True)
            print(f"\nCreating Terraform files in: {region_dir}")
            
            # Generate Terraform files for this region
            # Create a complete resources dictionary with compartment information
            region_terraform_resources = {
                'project_name': project_name,
                'compartment_name': resources.get('compartment_name', project_name),
                'compartments': resources.get('compartments', {}),
                'regions': {region: region_resources}
            }
            
            # Ensure compartments key exists
            if 'compartments' not in region_terraform_resources:
                region_terraform_resources['compartments'] = {}
                
            # Add default compartment if none exists
            if not region_terraform_resources['compartments'] and region_terraform_resources.get('compartment_name'):
                comp_name = region_terraform_resources['compartment_name']
                region_terraform_resources['compartments'][comp_name] = {
                    'name': comp_name,
                    'description': f"{comp_name} Compartment",
                    'enable_delete': True
                }
            
            if not generate_terraform(region_terraform_resources, region_dir):
                print(f"Error: Failed to generate Terraform configuration for region {region}")
                continue
                
            print(f"Generated Terraform configuration for region {region} in {region_dir}")
        
        print(f"\nTerraform configuration generated successfully in {base_dir}")
        return resources
        
    except oci.exceptions.ServiceError as e:
        print(f"Error processing diagram: {str(e)}")
        return None
    except Exception as e:
        print(f"Error processing diagram: {str(e)}")
        print("Debug: Stack trace:")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    try:
        # Get image path from command line or use default
        image_path = sys.argv[1] if len(sys.argv) > 1 else "diagram.png"
        print(f"\nProcessing diagram: {image_path}")
        
        # Process the image and get resources
        result = process_image(image_path)
        if not result:
            print("\nError: Failed to process diagram")
            sys.exit(1)
            
        # Create base output directory
        output_dir = os.path.join(os.getcwd(), "terraform_workspace")
        os.makedirs(output_dir, exist_ok=True)
        
        # Get project name from result
        project_name = result.get('project_name', 'default_project')
        print(f"\nProject Name: {project_name}")
        
        # Create project directory
        project_dir = os.path.join(output_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Process each region's configuration
        for region, resources in result.get('regions', {}).items():
            print(f"\nProcessing region: {region}")
            
            # Create region directory
            region_dir = os.path.join(project_dir, region)
            os.makedirs(region_dir, exist_ok=True)
            
            # Generate Terraform files for this region
            if not generate_terraform({'project_name': project_name, 'regions': {region: resources}}, region_dir):
                print(f"Error: Failed to generate Terraform configuration for region {region}")
                continue
                
            print(f"Generated Terraform configuration for region {region} in {region_dir}")
        
        print(f"\nTerraform configuration generated successfully in {output_dir}")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
