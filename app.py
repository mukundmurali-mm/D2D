import streamlit as st
import os
from llama_ocr_oci import process_image
from PIL import Image
import tempfile
import oci

# Set page configuration
st.set_page_config(
    page_title="Diagrams to Deployment",
    page_icon="https://www.oracle.com/asset/web/favicons/favicon-32.png",
    layout="wide"
)

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        return tmp_file.name

def display_terraform_files(region, files):
    """Display the generated Terraform files"""
    with st.expander(f"Configuration for {region}", expanded=True):
        # Display main.tf first if it exists
        if 'main.tf' in files:
            st.markdown(f"### main.tf")
            st.code(files['main.tf'], language="hcl")
            
        # Display provider.tf next if it exists
        if 'provider.tf' in files:
            st.markdown(f"### provider.tf")
            st.code(files['provider.tf'], language="hcl")
            
        # Display variables.tf next if it exists
        if 'variables.tf' in files:
            st.markdown(f"### variables.tf")
            st.code(files['variables.tf'], language="hcl")
            
        # Display all other files
        for filename, content in files.items():
            if filename not in ['main.tf', 'provider.tf', 'variables.tf']:
                st.markdown(f"### {filename}")
                st.code(content, language="hcl")

def get_oci_profiles():
    """Get list of available OCI profiles from config file"""
    try:
        with open(os.path.expanduser('~/.oci/config'), 'r') as f:
            content = f.read()
        profiles = [line.strip()[1:-1] for line in content.split('\n') if line.strip().startswith('[') and line.strip().endswith(']')]
        return profiles
    except Exception as e:
        st.error(f"Error reading OCI config: {str(e)}")
        return ['DEFAULT']

def get_available_models(config, compartment_id):
    """Get available models from OCI Generative AI service
    
    Args:
        config: OCI configuration dictionary
        compartment_id: OCI compartment ID
        
    Returns:
        Dictionary mapping model names to their IDs
    """
    try:
        if not compartment_id:
            st.sidebar.error("Please enter a Compartment ID first")
            return {}
            
        # Initialize the Generative AI client
        generative_ai_client = oci.generative_ai.GenerativeAiClient(config)
        
        # Get list of models
        response = generative_ai_client.list_models(compartment_id=compartment_id)
        
        # Create mapping of model names to IDs
        model_name_to_id = {}
        
        for item in response.data.items:
            # Create a display name that includes the provider
            display_name = f"{item.display_name} ({item.vendor})"
            model_name_to_id[display_name] = item.id
            
        if not model_name_to_id:
            st.sidebar.warning("No models found in the specified compartment")
            
        return model_name_to_id
    except Exception as e:
        st.sidebar.error(f"Error fetching models: {str(e)}")
        return {}

def main():
    st.title("Diagrams to Deployment")
    
    # Add OCI Profile selector in sidebar
    st.sidebar.title("OCI Configuration")
    profiles = get_oci_profiles()
    selected_profile = st.sidebar.selectbox(
        "Select OCI Profile",
        options=profiles,
        index=profiles.index('DEFAULT') if 'DEFAULT' in profiles else 0,
        help="Choose the OCI configuration profile to use for deployment"
    )
    
    # Get OCI config
    config = oci.config.from_file(os.path.expanduser("~/.oci/config"), selected_profile)
    
    # Add compartment ID input
    compartment_id = st.sidebar.text_input(
        "Compartment ID",
        help="Enter the OCID of the compartment containing your AI models"
    )
    
    # Add AI model selector if compartment ID is provided
    selected_model_id = None
    if compartment_id:
        # Get available models
        model_names_to_ids = get_available_models(config, compartment_id)
        
        if model_names_to_ids:
            selected_model_name = st.sidebar.selectbox(
                "Select AI Model",
                options=list(model_names_to_ids.keys()),
                help="Choose the AI model to use for processing"
            )
            
            selected_model_id = model_names_to_ids[selected_model_name]
            st.sidebar.success(f"Selected model ID: {selected_model_id}")
    
    # Initialize working directory
    working_dir = os.path.join(os.getcwd(), "terraform_workspace")
    
    # Upload and process diagram
    uploaded_file = st.file_uploader("Choose an image file", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded OCI Architecture Diagram", use_container_width=True)
        
        if st.button("Generate Terraform Configuration"):
            uploaded_file.seek(0)
            with st.spinner("Processing diagram..."):
                temp_file_path = save_uploaded_file(uploaded_file)
                try:
                    region_configs = process_image(temp_file_path, profile_name=selected_profile, model_id=selected_model_id)
                    
                    if not region_configs:
                        st.error("Failed to process the diagram")
                        return
                    
                    # Get project name from the top level of region_configs
                    project_name = region_configs.get('project_name', 'default_project')
                    
                    # Display configurations and save files
                    for region, region_resources in region_configs.get('regions', {}).items():
                        project_dir = os.path.join(working_dir, project_name)
                        region_dir = os.path.join(project_dir, region)
                        os.makedirs(region_dir, exist_ok=True)
                        
                        # Create a files dictionary for this region
                        files = {}
                        
                        # Generate Terraform files for this region
                        try:
                            from llama_ocr_oci import generate_terraform
                            if generate_terraform({'project_name': project_name, 'regions': {region: region_resources}}, region_dir):
                                # Read the generated files
                                files = {}
                                # Get all .tf files in the directory
                                all_tf_files = [f for f in os.listdir(region_dir) if f.endswith('.tf')]
                                for filename in all_tf_files:
                                    file_path = os.path.join(region_dir, filename)
                                    if os.path.exists(file_path):
                                        with open(file_path, 'r') as f:
                                            files[filename] = f.read()
                                
                                # Display files
                                display_terraform_files(region, files)
                            else:
                                st.error(f"Failed to generate Terraform files for region {region}")
                        except Exception as e:
                            st.error(f"Error generating Terraform files for region {region}: {str(e)}")
                        
                        # Show next steps
                        st.info("""
                        ### Next Steps:
                        1. Navigate to the generated Terraform files in your terminal:
                           ```bash
                           cd terraform_workspace/<project_name>/<region>
                           ```
                        2. Initialize Terraform:
                           ```bash
                           terraform init
                           ```
                        3. Review the planned changes:
                           ```bash
                           terraform plan
                           ```
                        4. Apply the configuration:
                           ```bash
                           terraform apply
                           ```
                        """)
                
                except Exception as e:
                    st.error(f"Error processing diagram: {str(e)}")
                finally:
                    os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
