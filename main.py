import streamlit as st
from openai import OpenAI
import pandas as pd
from api_calls import fetch_serp_data, generate_seo_content, generate_section_from_openai

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Session state initialization
if 'article' not in st.session_state:
    st.session_state.article = {
        'introduction': None,
        'benefits': None,
        'FAQ': None
    }

if 'keywords' not in st.session_state:
    st.session_state.keywords = []

if 'seo_questions' not in st.session_state:
    st.session_state.seo_questions = []

if 'long_tail_queries' not in st.session_state:
    st.session_state.long_tail_queries = []

if 'related_questions_df' not in st.session_state:
    st.session_state.related_questions_df = None

if 'organic_results_df' not in st.session_state:
    st.session_state.organic_results_df = None

if 'keywords_df' not in st.session_state:
    st.session_state.keywords_df = None

if 'seo_questions_df' not in st.session_state:
    st.session_state.seo_questions_df = None

if 'long_tail_queries_df' not in st.session_state:
    st.session_state.long_tail_queries_df = None

st.header("Updated: Article Outline + Content Writer")

# Input for keyword
keyword = st.text_input("Enter the main keyword for the article:")

# Fetch SERP Data
if st.button("Fetch SERP Data"):
    if keyword:
        fetch_serp_data(keyword)
    else:
        st.error("Please enter a keyword.")

st.write("---")

# Display SERPAPI DataFrames if they exist
if st.session_state.related_questions_df is not None:
    st.write("### Related Questions")
    st.dataframe(st.session_state.related_questions_df)

if st.session_state.organic_results_df is not None:
    st.write("### Organic Results")
    st.dataframe(st.session_state.organic_results_df)

# Generate SEO Data
if st.button("Generate SEO Data"):
    if keyword:
        keywords, seo_questions, long_tail_queries = generate_seo_content(client, keyword)
        st.session_state.keywords = keywords
        st.session_state.seo_questions = seo_questions
        st.session_state.long_tail_queries = long_tail_queries

        st.session_state.keywords_df = pd.DataFrame(st.session_state.keywords, columns=["Keyword"])
        st.session_state.seo_questions_df = pd.DataFrame(st.session_state.seo_questions, columns=["SEO-Focused Question"])
        st.session_state.long_tail_queries_df = pd.DataFrame(st.session_state.long_tail_queries, columns=["Long-Tail Query"])
    else:
        st.error("Please enter a keyword.")

# Display SEO data if it exists
if st.session_state.keywords_df is not None:
    st.write("### Related Keywords")
    st.dataframe(st.session_state.keywords_df)

if st.session_state.seo_questions_df is not None:
    st.write("### SEO-Focused Questions")
    st.dataframe(st.session_state.seo_questions_df)

if st.session_state.long_tail_queries_df is not None:
    st.write("### Long-Tail Queries")
    st.dataframe(st.session_state.long_tail_queries_df)

# Text area for user to input the content
user_prompt = st.text_area("""Enter your prompt for generating the content. Include the keywords manually as needed.""")

# Generate content based on the user prompt
if st.button("Generate Content"):
    if keyword and user_prompt:
        content = generate_section_from_openai(client, keyword, user_prompt)
        # Add the generated content to the article in session storage
        st.session_state.article[len(st.session_state.article)] = content
        st.markdown("**Generated Content:**")
        st.write(content)
    else:
        st.error("Please ensure a keyword and prompt are provided.")

# Display the entire article so far
if st.button("Show Entire Article"):
    st.markdown("### Entire Article")
    for key, value in st.session_state.article.items():
        if value:
            st.write(value)
