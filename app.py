import streamlit as st
from upload_pdb import validate_pdb_file, read_pdb_file
from parse_structure import parse_pdb_structure
from generate_peptides import generate_random_peptides
from ai_peptide_suggester import suggest_peptides_with_ai
import py3Dmol

st.title("🧠 AI-Enhanced Peptide Generator")

# File upload
uploaded_file = st.file_uploader("Upload a .pdb file", type=["pdb"])

def show_3d_structure(pdb_content: str, chain: str = "A"):
    """
    Visualize the PDB structure using py3Dmol, focusing on the selected chain.
    """
    view = py3Dmol.view(width=500, height=400)
    view.addModel(pdb_content, 'pdb')
    view.setStyle({"cartoon": {"color": "spectrum"}})
    view.zoomTo()
    view.addLabel(f"Chain {chain}", {"position": {"x":0, "y":0, "z":0}})
    return view

if uploaded_file:
    if not validate_pdb_file(uploaded_file.name):
        st.error("Please upload a valid .pdb file.")
    else:
        pdb_content = uploaded_file.read().decode("utf-8")
        # Chain selection
        chain_id = st.text_input("Target chain", value="A")
        # Number of peptides
        num_peptides = st.slider("Number of peptides to generate", 1, 15, 5)
        # Optional: peptide length
        peptide_length = st.slider("Peptide length", 5, 20, 8)

        # LLM provider selection
        st.subheader("LLM Provider Settings")
        provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic", "Groq", "Mistral"])
        api_key = st.text_input(f"{provider} API Key", type="password")
        model_name = st.text_input(f"{provider} Model Name", value="gpt-4")
        endpoint = st.text_input(f"{provider} API Endpoint (optional)", value="")

        # Parse structure
        try:
            parsed = parse_pdb_structure(pdb_content, chain_id=chain_id)
            st.subheader("Primary Sequence")
            st.code(parsed['sequence'])
            st.subheader("Residue Summary")
            st.write(parsed['residues'])

            # 3D Visualization
            st.subheader("3D Structure Visualization")
            view = show_3d_structure(pdb_content, chain=chain_id)
            st.components.v1.html(view._make_html(), height=420)

            # Generate random peptides
            peptides = generate_random_peptides(
                parsed['sequence'], num_peptides=num_peptides, peptide_length=peptide_length
            )
            st.subheader("Random Peptide Candidates")
            st.write(peptides)

            # AI-assisted suggestions (modular)
            if api_key:
                ai_peptides = suggest_peptides_with_ai(
                    parsed['sequence'], parsed['residues'], provider, api_key, model_name, endpoint, num_peptides=num_peptides
                )
                st.subheader("AI-Suggested Peptides")
                for pep, expl in ai_peptides:
                    st.markdown(f"**{pep}**: {expl}")
            else:
                st.info("Enter your LLM API key to get AI-suggested peptides.")
        except Exception as e:
            st.error(f"Error parsing PDB: {e}")
else:
    st.info("Upload a .pdb file to begin.") 