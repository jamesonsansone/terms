import time
import pandas as pd
import streamlit as st
from utilities import parse_serp_results, extract_keywords
from requests.exceptions import ConnectionError
import json
import serpapi

def fetch_serp_data(keyword):
    params = {
        "engine": "google",
        "q": keyword,
        "api_key": st.secrets["SERPAPI_KEY"]
    }
    
    retries = 3
    for attempt in range(retries):
        try:
            search = serpapi.search(params)
            raw_results = str(search)  # Convert SerpResults object to string
            cleaned_results = raw_results  # Define cleaned_results here
            results = parse_serp_results(raw_results)
            
            # Extract related questions
            related_questions = results.get('related_questions', [])
            related_questions_data = []
            for question_entry in related_questions:
                related_questions_data.append({
                    "Question": question_entry.get('question', 'No question found'),
                    "Snippet": question_entry.get('snippet', 'No snippet found'),
                    "Link": question_entry.get('link', 'No link found')
                })
            
            # Convert to DataFrame
            st.session_state.related_questions_df = pd.DataFrame(related_questions_data)
            
            # Extract organic results
            organic_results = results.get('organic_results', [])
            organic_results_data = []
            for result_entry in organic_results:
                organic_results_data.append({
                    "Position": result_entry.get('position', 'No position found'),
                    "Title": result_entry.get('title', 'No title found'),
                    "Link": result_entry.get("link", "No link found"),
                    "Snippet": result_entry.get('snippet', 'No snippet found')
                })
            
            # Convert to DataFrame
            st.session_state.organic_results_df = pd.DataFrame(organic_results_data)
            
            return results  # Return results if successful

        except ConnectionError as e:
            st.error(f"Connection error: {e}. Retrying ({attempt+1}/{retries})...")
            time.sleep(2)  # Wait for 2 seconds before retrying
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON data: {e}")
            st.text_area("Raw Data", value=cleaned_results, height=300)
            return None
        except Exception as e:
            st.error(f"Error retrieving data from SERPAPI: {e}")
            return None

    st.error("Failed to retrieve data after multiple attempts.")
    return None

def generate_seo_content(client, keyword):
    prompt = f"You are a content marketing specialist that understands user intent. Generate related keywords, SEO questions, and long-tail queries for the keyword to be used for an SEO-friendly article: {keyword}."
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    
    data = response.choices[0].message.content
    lines = data.split('\n')

    keywords = []
    seo_questions = []
    long_tail_queries = []

    current_list = keywords

    for line in lines:
        line = line.strip()
        if line.startswith("### Related Keywords"):
            current_list = keywords
        elif line.startswith("### SEO Questions"):
            current_list = seo_questions
        elif line.startswith("### Long-Tail Queries"):
            current_list = long_tail_queries
        elif line:
            current_list.append(line)

    return keywords, seo_questions, long_tail_queries

def generate_section_from_openai(client, keyword, user_prompt):
    context = ""
    for key, value in st.session_state.article.items():
        if value and isinstance(key, str):  # Ensure key is a string
            context += f"\n\n{key.capitalize()}:\n{value}"

    prompt = f"Based on the keyword '{keyword}' and following the additional context provided, generate the required content to produce a portion of a retirement glossary term SEO page. Be strict in following the prompt. {user_prompt} {context}"
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a knowledgeable content creator specializing in SEO-optimized articles. Use these inputs to construct a complete SEO-friendly article. Do not be editorial. Be more fact-based and terse. We just want to talk about the target keyword from the context of a dictionary term. Use sentence case for all headlines."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )
    
    return response.choices[0].message.content
