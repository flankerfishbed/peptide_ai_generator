import streamlit as st
from upload_pdb import validate_pdb_file
from parse_structure import parse_pdb_structure
from ai_peptide_suggester import suggest_peptides_with_ai
import py3Dmol

st.title("🧠 AI-Enhanced Peptide Generator")

# Step 1: LLM API credentials first
st.subheader("LLM Provider Settings")
provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic", "Groq", "Mistral"])
api_key = st.text_input(f"{provider} API Key", type="password")
if api_key:
    st.success("✅ API key accepted!")
model_name = st.text_input(f"{provider} Model Name", value="gpt-4")
endpoint = st.text_input(f"{provider} API Endpoint (optional)", value="")

if api_key:
    # Step 2: File upload only after API info is provided
    uploaded_file = st.file_uploader("Upload a .pdb file", type=["pdb"])
    if uploaded_file:
        if not validate_pdb_file(uploaded_file.name):
            st.error("Please upload a valid .pdb file.")
        else:
            pdb_content = uploaded_file.read().decode("utf-8")
            chain_id = st.text_input("Target chain", value="A")
            num_peptides = st.slider("Number of peptides to generate", 1, 15, 5)
            try:
                parsed = parse_pdb_structure(pdb_content, chain_id=chain_id)
                st.subheader("Primary Sequence")
                st.code(parsed['sequence'])
                st.subheader("Residue Summary")
                st.write(parsed['residues'])

                # 3D Visualization
                st.subheader("3D Structure Visualization")
                def show_3d_structure(pdb_content: str, chain: str = "A"):
                    view = py3Dmol.view(width=500, height=400)
                    view.addModel(pdb_content, 'pdb')
                    view.setStyle({"cartoon": {"color": "spectrum"}})
                    view.zoomTo()
                    view.addLabel(f"Chain {chain}", {"position": {"x":0, "y":0, "z":0}})
                    return view
                view = show_3d_structure(pdb_content, chain=chain_id)
                st.components.v1.html(view._make_html(), height=420)

                # LLM-based peptide suggestions only
                st.subheader("AI-Suggested Peptides")
                ai_peptides = suggest_peptides_with_ai(
                    parsed['sequence'], parsed['residues'], provider, api_key, model_name, endpoint, num_peptides=num_peptides
                )
                st.write("DEBUG: ai_peptides output", ai_peptides)
                for pep in ai_peptides:
                    st.markdown(f"### 🧬 Peptide: `{pep['sequence']}`")
                    st.markdown("**Properties:**")
                    for k, v in pep['properties'].items():
                        st.markdown(f"- **{k}:** {v}")
                    st.markdown("**Reason for Selection:**")
                    st.info(pep['explanation'])
            except Exception as e:
                st.error(f"Error parsing PDB: {e}")
    else:
        st.info("Upload a .pdb file to begin.")
else:
    st.info("Enter your LLM API key and provider info to begin.") 
