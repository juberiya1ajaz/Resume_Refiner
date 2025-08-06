# Import necessary libraries
import streamlit as st  # Streamlit for building web UI
import re  # Regular expressions for string operations
import pandas as pd  # Data manipulation and analysis
import altair as alt  # Data visualization library

# Import backend helper functions
from backend import (
    extract_text,  # Function to extract raw text from uploaded resume
    ats_keyword_check,  # Check ATS keyword match between resume and job description
    optimize_resume,  # Optimize resume using LLM
    export_to_docx,  # Export content to DOCX format
    export_to_pdf,  # Export content to PDF format
    fetch_dynamic_skillset_from_perplexity,  # Get dynamic skillset from job description
    parse_sections_with_llm,  # Parse resume into sections using LLM
    regenerate_section_with_llm,  # Regenerate a specific resume section
    score_all_sections  # Score each resume section
)

from copy import deepcopy  # For deep copying Python objects

# Set Streamlit page configuration
st.set_page_config(page_title="AI Resume Optimizer", layout="wide")

# Page title and header separator
st.title("📄 AI Resume Optimizer with Section Scoring & Regeneration")
st.markdown("---")

# File uploader for resume upload
resume_file = st.file_uploader("📤 Upload Your Resume (.pdf or .docx)", type=["pdf", "docx"])

# Text area for pasting job description
job_desc = st.text_area("📌 Paste the Job Description", height=200)

# Initialize session state to store resume data
if "resume_data" not in st.session_state:
    st.session_state.resume_data = {}

# Button to trigger resume analysis and optimization
if st.button("🔍 Analyze & Optimize"):
    # Input validation
    if resume_file is None:
        st.warning("Please upload a resume file.")
    elif not job_desc.strip():
        st.warning("Please paste the job description.")
    else:
        # Extract text from uploaded resume
        with st.spinner("🔍 Extracting resume text..."):
            resume_text = extract_text(resume_file)

        # Extract dynamic skillset from job description
        with st.spinner("🎯 Extracting relevant skillset from JD..."):
            dynamic_skillset = fetch_dynamic_skillset_from_perplexity(job_desc)

        # Run ATS keyword check
        with st.spinner("⚙️ Running ATS keyword check..."):
            ats = ats_keyword_check(resume_text, job_desc)

        # Optimize resume using LLM
        with st.spinner("🧠 Optimizing resume via LLM..."):
            optimized_resume, resume_skills, jd_skills = optimize_resume(resume_text, job_desc, dynamic_skillset)

        # Parse structured resume sections
        with st.spinner("🧾 Parsing sections from resume..."):
            structured_resume = parse_sections_with_llm(resume_text)

        # Score each resume section
        with st.spinner("📊 Scoring each resume section..."):
            section_scores = score_all_sections(structured_resume)

        # Store all outputs in session state
        st.session_state.resume_data = {
            "resume_text": resume_text,
            "ats": ats,
            "optimized_resume": optimized_resume,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "structured_resume": structured_resume,
            "section_scores": section_scores
        }

# Display results if resume data exists
if st.session_state.resume_data:
    data = st.session_state.resume_data
    st.success("✅ Resume analyzed and optimized!")
    st.markdown("<br>", unsafe_allow_html=True)

    # ATS Keyword Match display
    st.subheader("📈 ATS Keyword Match")
    st.write(f"**Matching Keywords:** {', '.join(data['ats']['matching_keywords'][:15])}")
    st.write(f"**Missing Keywords:** {', '.join(data['ats']['missing_keywords'][:15])}")
    st.write(f"**Coverage:** {data['ats']['coverage_percent']}%")

    # Display extracted skills
    st.subheader("💼 Extracted Skills")
    st.write(f"**From Resume:** {', '.join(sorted(data['resume_skills']))}")
    st.write(f"**From JD:** {', '.join(sorted(data['jd_skills']))}")

    # Option to show raw resume text
    show_raw = st.checkbox("📄 Show Raw Resume Text")
    if show_raw:
        st.text_area("🧾 Raw Extracted Resume", data['resume_text'], height=300)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📚 Detected Resume Sections with Feedback")

    # Setup current editable sections in session state
    original_sections = {}
    if "current_sections" not in st.session_state:
        st.session_state.current_sections = {}

    # Split parsed resume into sections
    sections = data["structured_resume"].split("=== ")
    for sec in sections:
        if sec.strip():
            header, *content = sec.strip().split("\n", 1)
            header = re.sub(r"^=+\s*|\s*=+$", "", header).strip()
            content_text = content[0].strip() if content else ""

            original_sections[header] = content_text
            if header not in st.session_state.current_sections:
                st.session_state.current_sections[header] = content_text

            # Layout: Text area and buttons side-by-side
            col_text, col_btns = st.columns([6, 2])

            # Editable text area for section content
            with col_text:
                st.session_state.current_sections[header] = st.text_area(
                    f"✏️ {header}",
                    value=st.session_state.current_sections[header],
                    height=150,
                    key=f"edit_{header}"
                )

                # Display score for section
                score_text = data["section_scores"].get(header, "")
                if score_text:
                    match = re.search(r"Score:\s*\*{0,2}(\d+/10)\*{0,2}", score_text)
                    if match:
                        st.markdown(f"**Score:** {match.group(1)}")

            # Regenerate and reset buttons
            with col_btns:
                st.markdown("<div style='height: 110px;'></div>", unsafe_allow_html=True)  # Button alignment
                b1, b2 = st.columns([1, 1])

                with b1:
                    if st.button(f"🔄 Regenerate", key=f"regen_{header}", help="Regenerate"):
                        with st.spinner(f"Regenerating '{header}'..."):
                            regenerated = regenerate_section_with_llm(header, st.session_state.current_sections[header])
                            st.session_state.current_sections[header] = regenerated

                with b2:
                    if st.button(f"♻️ Reset", key=f"reset_{header}", help="Reset"):
                        st.session_state.current_sections[header] = original_sections[header]
                        
            # # Full feedback in an expander
            # full_score_text = data["section_scores"].get(header, "").strip()
            # if full_score_text:
            #     with st.expander(f"📊 Score & Feedback for '{header}'", expanded=True):
            #         st.markdown(full_score_text)
    st.markdown("---")
    st.markdown("### 📈 Section Scores Overview")

    # Prepare data for bar chart visualization of section scores
    chart_data = []
    for sec, feedback in data["section_scores"].items():
        match = re.search(r"(\d{1,2})\s*/\s*10", feedback)
        if match:
            chart_data.append((sec, int(match.group(1).split("/")[0])))

    if chart_data:
        df_chart = pd.DataFrame(chart_data, columns=["Section", "Score"])

        # Define color scale based on score
        def score_to_color(score):
            if score <= 5:
                return "skyblue"
            elif score < 8:
                return "blue"
            else:
                return "navy blue"

        df_chart["Color"] = df_chart["Score"].apply(score_to_color)

        # Create bar chart using Altair
        bar_chart = alt.Chart(df_chart).mark_bar().encode(
            x=alt.X("Score:Q", title="Score (out of 10)", scale=alt.Scale(domain=[0, 10])),
            y=alt.Y("Section:N", sort="-x", title="Resume Section"),
            color=alt.Color("Color:N", scale=None),
            tooltip=["Section", "Score"]
        ).properties(
            width=600,
            height=300,
            title="📊 Section Scores Overview"
        )

        st.altair_chart(bar_chart, use_container_width=True)

    # Final download section
    st.markdown("---")  
    st.header("Download") 

    # Compile manually edited resume
    st.markdown("### 📥 Download Final Edited Resume (Manual Edits Applied)")
    final_resume = ""
    for section, content in st.session_state.current_sections.items():
        final_resume += f"=== {section} ===\n{content.strip()}\n\n"
        # final_resume += f"{section}\n{'-' * len(section)}\n{content.strip()}\n\n"

    # Export final resume in DOCX and PDF
    docx_bytes = export_to_docx(final_resume)
    st.download_button("⬇️ Download as DOCX", docx_bytes, "structured_resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    pdf_bytes = export_to_pdf(final_resume)
    st.download_button("⬇️ Download as PDF", pdf_bytes, "structured_resume.pdf", "application/pdf")

    # Export AI-optimized resume (no manual edits)
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### 🧠 Download AI-Optimized Resume (No Manual Edits)")
    opt_docx = export_to_docx(data['optimized_resume'])
    st.download_button("⬇️ Download Optimized Resume as DOCX", opt_docx, "optimized_resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    opt_pdf = export_to_pdf(data['optimized_resume'])
    st.download_button("⬇️ Download Optimized Resume as PDF", opt_pdf, "optimized_resume.pdf", "application/pdf")

    # Export only section scores and feedback
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📊 Download Section Scores & Feedback Only")
    score_summary = ""
    for section, full_score_text in data["section_scores"].items():
        score_summary += f"=== {section} ===\n{full_score_text.strip()}\n\n"

    score_docx = export_to_docx(score_summary)
    st.download_button("⬇️ Download Scores as DOCX", score_docx, "resume_scores.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    score_pdf = export_to_pdf(score_summary)
    st.download_button("⬇️ Download Scores as PDF", score_pdf, "resume_scores.pdf", "application/pdf")

# Footer
st.markdown("---")
st.caption("Built with 🧠 Perplexity, 🐍 spaCy, 📊 NLTK, Streamlit.")
