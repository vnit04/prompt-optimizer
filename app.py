import streamlit as st
import google.generativeai as genai
import json
import time
import os

# Load API key from Streamlit secrets or environment
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = os.getenv("GEMINI_API_KEY", "")

if not api_key:
    st.error("API key not found. Add GEMINI_API_KEY to Streamlit secrets.")
    st.stop()

genai.configure(api_key=api_key)

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Prompt Optimizer",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTextArea textarea { 
        background-color: #1a1a2e; 
        color: white;
        border: 1px solid #21262d;
        border-radius: 8px;
    }
    .stButton button {
        background: linear-gradient(135deg, #00e5ff, #0099bb);
        color: black;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #00c8e0, #007799);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────
st.title("Prompt Optimizer")
st.caption("Transform weak prompts into perfect structured prompts — Built by Vinit")

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("The Perfect Prompt Formula")
    st.markdown("""
    **1. CONTEXT**
    Background info the LLM needs
    
    **2. ROLE**
    Who the LLM should act as
    
    **3. TASK**
    Clear step by step breakdown
    
    **4. FORMAT**
    Exact output structure
    
    **5. CONSTRAINTS**
    Length, style, what to avoid
    """)
    st.divider()
    
    st.header("Example Weak Prompts")
    examples = [
        "explain transformers",
        "write me a chatbot",
        "help me learn AI",
        "analyze my data",
        "write a cover letter",
        "explain machine learning",
    ]
    for ex in examples:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state.example = ex
    
    st.divider()
    st.caption("Built by Vinit")
    st.caption("Final year engineering student")
    st.caption("Nagpur, India")
    st.caption("30-day AI learning journey")

# ── Main Interface ────────────────────────────────────────
col1, col2 = st.columns(2)

# Pre-fill from sidebar example click
if "example" not in st.session_state:
    st.session_state.example = ""

with col1:
    st.subheader("Your Weak Prompt")
    
    weak_prompt = st.text_area(
        "Paste any weak prompt:",
        value=st.session_state.example,
        placeholder="e.g. explain transformers",
        height=140
    )
    
    context = st.text_area(
        "Your context (recommended):",
        placeholder="e.g. I am a final year engineering student learning AI in 30 days",
        height=80
    )
    
    task_type = st.selectbox(
        "Task type:",
        ["Explanation/Learning", "Code Generation",
         "Analysis/Research", "Creative Writing",
         "Data Extraction", "Job/Career", "Other"]
    )
    
    optimize_btn = st.button(
        "Optimize My Prompt",
        use_container_width=True,
        type="primary"
    )

with col2:
    st.subheader("Optimized Prompt")
    
    if optimize_btn and weak_prompt:
        with st.spinner("Analyzing and optimizing..."):
            
            system = """You are an expert prompt engineer with 10 years experience.
Transform weak vague prompts into powerful structured prompts.
A perfect prompt has: context, role, task breakdown, format, constraints.
Never change the original intent. Only improve structure and clarity.
Always make prompts specific, actionable and token-efficient."""

            prompt = f"""Transform this weak prompt into a perfect prompt.

Weak prompt: {weak_prompt}
User context: {context if context else "Not provided"}
Task type: {task_type}

Return ONLY this exact JSON, no other text:
{{
    "optimized": "the complete improved prompt here",
    "role_assigned": "what role you gave the LLM",
    "format_specified": "what output format you specified",
    "improvements": ["improvement 1", "improvement 2", "improvement 3"],
    "quality_score_before": 3,
    "quality_score_after": 8,
    "token_tip": "one tip on token efficiency"
}}"""

            try:
                opt_model = genai.GenerativeModel(
                    "gemini-2.5-flash",
                    system_instruction=system
                )
                result = opt_model.generate_content(prompt)
                clean = result.text.replace("```json","").replace("```","").strip()
                data = json.loads(clean)
                
                # Show optimized prompt
                optimized = data.get("optimized", "")
                st.text_area(
                    "Copy this optimized prompt:",
                    value=optimized,
                    height=180
                )
                
                # Quality scores
                st.subheader("Quality Improvement")
                col_a, col_b, col_c = st.columns(3)
                before = data.get("quality_score_before", 3)
                after = data.get("quality_score_after", 8)
                
                with col_a:
                    st.metric("Before", f"{before}/10")
                with col_b:
                    st.metric("After", f"{after}/10",
                             delta=f"+{after-before}")
                with col_c:
                    improvement = int((after-before)/10*100)
                    st.metric("Improvement", f"{improvement}%")
                
                # What improved
                st.subheader("Improvements Made")
                if "improvements" in data:
                    for imp in data["improvements"]:
                        st.success(f"+ {imp}")
                
                col_d, col_e = st.columns(2)
                with col_d:
                    if "role_assigned" in data:
                        st.info(f"Role: {data['role_assigned']}")
                with col_e:
                    if "token_tip" in data:
                        st.warning(f"Token tip: {data['token_tip']}")
                        
            except json.JSONDecodeError:
                st.error("Could not parse response. Trying again...")
                time.sleep(2)
            except Exception as e:
                st.error(f"Error: {str(e)[:100]}")
                st.info("Rate limited — wait 30 seconds and try again")

    elif optimize_btn:
        st.warning("Please enter a prompt to optimize")
    else:
        st.info("Enter a weak prompt on the left and click Optimize")
        st.markdown("""
        **What makes a perfect prompt?**
        
        Bad: *explain transformers*
        
        Good: *You are a senior AI researcher explaining to a 
        final year engineering student who learned about neural 
        networks yesterday. Explain transformers in exactly 
        4 bullet points. Each bullet = one sentence. 
        Focus on: what changed from RNNs, what attention does, 
        why it matters for LLMs.*
        
        The good prompt gets 3x better results with fewer tokens.
        """)

# ── Before After Comparison ───────────────────────────────
st.divider()
st.subheader("Live Comparison — Weak vs Optimized")
st.caption("See the difference in real time")

if optimize_btn and weak_prompt:
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("**Weak prompt response:**")
        st.caption(f"Prompt: {weak_prompt}")
        try:
            time.sleep(1)
            weak_model = genai.GenerativeModel("gemini-2.5-flash")
            r_weak = weak_model.generate_content(weak_prompt)
            st.markdown(r_weak.text[:500])
        except Exception as e:
            st.info("Rate limited — refresh and try again")
    
    with col4:
        st.markdown("**What an optimized response looks like:**")
        st.caption("The optimized prompt above will produce responses like this:")
        st.info(
            "More structured. More specific. More useful. "
            "Follows the exact format you specified. "
            "Uses fewer tokens to get better results. "
            "Copy the optimized prompt and test it yourself in Claude or Gemini."
        )
