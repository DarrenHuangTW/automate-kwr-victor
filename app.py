import streamlit as st
import serpapi
import requests
import json
import tldextract
import time
import collections
import pandas as pd
from PIL import Image



all_secrets = st.secrets
# serpapi_api_key = all_secrets['SERPAPI_API_KEY']
semrush_api_key = all_secrets['SEMRUSH_API_KEY']



def get_organic_results(params):
    """
    Function to retrieve organic search results using SerpApi

    Args:
    params (dict): Parameters for the search query

    Returns:
    pd.DataFrame: DataFrame with columns Website, Ranking URL, and Position
    """
    
    serpapi_api_key = params.get('serpapi_api_key', '')
    q = params.get('q', '')
    google_domain = params.get('google_domain', 'google.com.sg')
    gl = params.get('gl', 'sg')
    hl = params.get('hl', 'en')

    url = f'https://serpapi.com/search.json?engine=google&api_key={serpapi_api_key}&q={q}&google_domain={google_domain}&gl={gl}&hl={hl}&num=30'
    response = requests.get(url)

    output_dict = {}
    
    if response.status_code == 200:
        api_output = response.content
        output_dict = json.loads(api_output)

    organic_results = output_dict.get("organic_results", [])  
    raw_html_file = output_dict["search_metadata"]["raw_html_file"]

    ranking_data = []

    for result in organic_results[:30]:  
        link = result.get('link', '')  
        position = result.get('position', '')  
        if link:
            domain = tldextract.extract(link).fqdn
            ranking_data.append([domain, link, position, raw_html_file])
        
    return pd.DataFrame(ranking_data, columns=['Website', 'Ranking URL', 'Position', "HTML"])

def get_ranking_keywords(url, country="sg", api_key=semrush_api_key):
    """
    Function to retrieve ranking keywords from SEMRush's database

    Args:
    api_key (str): SEMRush API key

    Returns:
    list: List of ranking keywords 
    [{'Keyword': 'coffee table', 'Position': '1', 'Search Volume': '5400', 'CPC': '0.73', 'Competition': '1.00'}, {'Keyword': 'coffee table singapore', 'Position': '1', 'Search Volume': '3600', 'CPC': '1.01', 'Competition': '1.00'}, {'Keyword': 'marble coffee table sg', 'Position': '1', 'Search Volume': '1000', 'CPC': '0.99', 'Competition': '0.50'}, {'Keyword': 'side table', 'Position': '4', 'Search Volume': '2900', 'CPC': '0.72', 'Competition': '1.00'}, {'Keyword': 'marble top coffee table singapore', 'Position': '1', 'Search Volume': '390', 'CPC': '0.00', 'Competition': '0.10'}, {'Keyword': 'round coffee table singapore', 'Position': '1', 'Search Volume': '390', 'CPC': '0.90', 'Competition': '1.00'}, {'Keyword': 'solid wood coffee table singapore', 'Position': '1', 'Search Volume': '320', 'CPC': '0.91', 'Competition': '0.39'}, {'Keyword': 'side table singapore', 'Position': '4', 'Search Volume': '1900', 'CPC': '0.95', 'Competition': '1.00'}, {'Keyword': 'marble coffee table singapore', 'Position': '2', 'Search Volume': '1000', 'CPC': '0.99', 'Competition': '0.50'}, {'Keyword': 'small table', 'Position': '3', 'Search Volume': '1600', 'CPC': '0.47', 'Competition': '1.00'}], [{'Keyword': 'coffee table singapore', 'Position': '5', 'Search Volume': '3600', 'CPC': '1.01', 'Competition': '1.00'}, {'Keyword': 'coffee table', 'Position': '8', 'Search Volume': '5400', 'CPC': '0.73', 'Competition': '1.00'}, {'Keyword': 'hipvan coffee table', 'Position': '1', 'Search Volume': '170', 'CPC': '1.04', 'Competition': '1.00'}, {'Keyword': 'round coffee table', 'Position': '8', 'Search Volume': '720', 'CPC': '0.70', 'Competition': '1.00'}, {'Keyword': 'small coffee tables', 'Position': '6', 'Search Volume': '390', 'CPC': '0.72', 'Competition': '1.00'}, {'Keyword': 'round coffee table singapore', 'Position': '6', 'Search Volume': '390', 'CPC': '0.90', 'Competition': '1.00'}, {'Keyword': 'wooden coffee table singapore', 'Position': '3', 'Search Volume': '210', 'CPC': '0.83', 'Competition': '1.00'}, {'Keyword': 'wood coffee table', 'Position': '6', 'Search Volume': '390', 'CPC': '0.69', 'Competition': '1.00'}, {'Keyword': 'glass coffee table', 'Position': '9', 'Search Volume': '390', 'CPC': '0.74', 'Competition': '1.00'}, {'Keyword': 'glass coffee table singapore', 'Position': '4', 'Search Volume': '170', 'CPC': '0.74', 'Competition': '1.00'}]
    """
    import requests

    url = f"https://api.semrush.com/?type=subfolder_organic&key={api_key}&display_limit=30&export_columns=Ph,Po,Nq,Cp,Co&subfolder={url}&database={country}"
    response = requests.get(url)

    
    if response.status_code == 200:
        api_output = response.content

        decoded_output = api_output.decode('utf-8')
        lines = decoded_output.split('\r\n')
        headers = lines[0].split(';')
        json_data = []
        for line in lines[1:]:
            if line:  # Ensure the line is not empty
                values = line.split(';')
                record = {header: value for header, value in zip(headers, values)}
                json_data.append(record)
        
        return json_data

    else:
        return []

def analyze_keywords(keyword_lists):
    """Analyzes a list of keyword sublists to find the most common keywords.

    Args:
        keyword_lists: A list of lists, where each inner list contains keyword dictionaries.

    Returns:
        A list of tuples, where each tuple contains a keyword and its total frequency, 
        sorted in descending order of frequency. 
    """

    all_keywords = []
    for sublist in keyword_lists:
        for item in sublist:
            all_keywords.append(item['Keyword'])

    keyword_counts = collections.Counter(all_keywords)
    return sorted(keyword_counts.items(), key=lambda item: item[1], reverse=True)



# with st.expander("Inputs to try"):
#     st.write("Keywords: coffee table")
#     st.write("Websites:")
#     st.write("https://urbanmood.sg/")
#     st.write("www.hipvan.com/furniture-all")
#     st.write("https://www.islandliving.sg/collections/coffee-side-tables")
#     st.write("www.comfortfurniture.com.sg")


st.header("Keyword Research Tools - Overdose", divider='rainbow')

kwr_input = Image.open('kwr_input.png')
kwr_output = Image.open('kwr_output.png')
semrush_image = Image.open('semrush.png')
serpapi_image = Image.open('serpapi.png')

with st.expander("How it works"):
    st.markdown("### Inputs")
    st.image(kwr_input)
    st.divider()
    st.markdown("### Outputs")
    st.image(kwr_output)

with st.expander("Can I trust the data"):
    st.markdown("### Ranking data")
    st.markdown("**Ranking data come from SerpApi. It searches the keyword with your configurations and returns the top 30 results.**")
    st.image(serpapi_image)
    st.divider()
    st.markdown("### Keyword Data:")
    st.markdown("**keyword data comes from SEMrush's database. You can find the raw data in the output.**")
    st.image(semrush_image)


# Configurations
st.sidebar.subheader("Configurations")
country = st.sidebar.selectbox("Select country", ["sg", "au", "nz", "us", "tw", "ph"], index=0)
language = st.sidebar.selectbox("Enter language", ["en", "zh-tw"], index=0)
google_domain = st.sidebar.selectbox("Select Google domain", ["google.com.sg", "google.com.au", "google.com.nz", "google.com", "google.com.tw", "google.com.ph"], index=0)

st.sidebar.divider()
st.sidebar.subheader("SerpApi API Key:")
serpapi_api_key = st.sidebar.text_input("Enter your SerpApi API Key")


account_url = f"https://serpapi.com/account?api_key={serpapi_api_key}"
response = requests.get(account_url)
account_details = response.json()

if serpapi_api_key:
    st.sidebar.write(f"Plan Name: {account_details['plan_name']}")
    st.sidebar.write(f"Total Searches Left: {account_details['total_searches_left']}")
else:
    st.sidebar.error("API key is required.")


st.sidebar.caption("Enjoy using this API key before it runs out. If you find it useful, sign up for a free account at serpapi.com to receive 100 credits!")
st.sidebar.caption("783e584e5945e13bc2d42966d9d38ca9fc3a7ed81c9e01ff3df15d8cdc130234")

tab1, tab2 = st.tabs(["App", "FAQ"])

# App
with tab1:
    # Keywords
    st.markdown("## Keywords")
    keywords_list = st.text_area("Enter a list of keywords (one keyword per line, up to 10 keywords)").strip()
    if keywords_list and keywords_list.count('\n') > 10:
        st.error("Please provide no more than 10 keywords.")
    keywords = [keyword.strip() for keyword in keywords_list.split('\n')]


    # Targeting Websites
    st.markdown("## Targeting Websites")
    option = st.radio("Select an option", ("Proceed with top 5 ranking URLs", "Proceed with specific websites"), index=0)
    if option == "Proceed with specific websites":
        websites = []
        websites_list = st.text_area("Enter a list of websites (one website per line, up to 5)").strip()
        websites = [tldextract.extract(website.strip()).fqdn for website in websites_list.split('\n') if website]
    else:
        websites = []


    # Initialization
    if st.button("Let's Go!"):


        st.markdown("## Top ranking pages and commonly ranked keywords")

        i = 1
        for seed_keyword in keywords:

            st.markdown(f"#### {i}. Seed Keyword: {seed_keyword}")

            params = {
                "serpapi_api_key": serpapi_api_key,
                "q": seed_keyword,
                "google_domain": google_domain,
                "gl": country,
                "hl": language
            }

            # Get SERP data from SerpAPI and return target_urls to look up
            results = get_organic_results(params)

            if not websites:
                target_urls = results.loc[results['Position'].isin([1, 2, 3, 4, 5]), ['Website', 'Ranking URL', 'Position', 'HTML']].values.tolist()
            else:
                target_urls = []
                for website in websites:
                    website_data = results.loc[results['Website'] == website, ['Website', 'Ranking URL', 'Position', 'HTML']].drop_duplicates(subset='Website').values.tolist()
                    if not website_data:
                        target_urls.append([website, None, '30+', results.loc[0, 'HTML']])
                    else:
                        target_urls.extend(website_data)
            
            st.markdown(f"#### Target URLs:")
            st.write(f"SERP mockup: {target_urls[0][-1]}")
            
            target_urls_df = pd.DataFrame(target_urls, columns=['Website', 'Ranking URL', 'Position', 'HTML'])
            target_urls_df = pd.DataFrame(target_urls_df, columns=['Website', 'Ranking URL', 'Position'])

            st.write(target_urls_df)
            



            # Get Keywords data from SEMrush API
            output_data = []  
            for website, ranking_url, position, html in target_urls:

                if '?srsltid=' in ranking_url:
                    ranking_url = ranking_url.split('?srsltid=')[0]
                print(ranking_url)
                print(country)
                keywords = get_ranking_keywords(ranking_url, country=country, api_key=semrush_api_key)
                print(keywords)
                print("@@@")
                if position == '30+':
                    output_data.append({"Seed Keyword": seed_keyword, 
                                        "Website": website, 
                                        "Top Ranking URL": "N/A", 
                                        "HTML": html,
                                        "Keyword": "N/A",
                                        "Position": position,
                                        "Search Volume": 0,
                                        "CPC": "N/A", 
                                        "Competition": "N/A"
                                        })
                else:
                    for keyword in keywords:
                        if int(keyword['Position']) <= 20:
                            output_data.append({"Seed Keyword": seed_keyword, 
                                                "Website": website, 
                                                "Top Ranking URL": ranking_url, 
                                                "HTML": html,
                                                "Keyword": keyword['Keyword'],
                                                "Position": keyword['Position'],
                                                "Search Volume": keyword['Search Volume'],
                                                "CPC": keyword['CPC'], 
                                                "Competition": keyword['Competition']
                                                })
                
            output_data_df = pd.DataFrame(output_data)
                    
            keyword_frequency = output_data_df.groupby(['Seed Keyword', 'Keyword']).size().reset_index(name='Frequency')
            keyword_frequency = keyword_frequency[['Seed Keyword', 'Keyword', 'Frequency']]
            df_merged = pd.merge(output_data_df, keyword_frequency, on=['Seed Keyword', 'Keyword'], how='left')
            df_merged = df_merged[['Seed Keyword', 'Website', 'Top Ranking URL', 'Keyword', 'Frequency', 'Position', 'Search Volume', 'CPC', 'Competition']]

            
            top_keywords = df_merged.loc[df_merged['Seed Keyword'] == seed_keyword].sort_values(by='Frequency', ascending=False)
            top_keywords['Search Volume'] = top_keywords['Search Volume'].astype(int)

            highest_freq = top_keywords['Frequency'].max()
            second_highest_freq = top_keywords[top_keywords['Frequency'] < highest_freq]['Frequency'].max()

            top_keywords_output = top_keywords[top_keywords['Frequency'].isin([highest_freq, second_highest_freq])].sort_values(by=['Frequency', 'Search Volume'], ascending=[False, False]).drop_duplicates(subset=['Keyword'])
            
            st.markdown(f"#### Most Frequent & 2nd Most Frequent Keywords:")                   
            st.write(top_keywords_output[['Seed Keyword', 'Keyword', 'Frequency', 'Search Volume', 'CPC', 'Competition']])
            
            with st.expander(f"### Raw Data: {seed_keyword}"):
                st.write(df_merged)
            
            i += 1

            st.write("---")

# FAQ
with tab2:
    st.header("FAQ")

    with st.expander("Q1: Curious about what this tool can do for you?"):
        st.write("This tool facilitates keyword research by analyzing competitor websites. It identifies common keywords they use to achieve high search engine rankings.")

    with st.expander("Q2: How do I decide between 'specific websites' and 'top 5 ranking URLs'?"):
        st.markdown("""
        - **Specific websites**: Perfect when you’ve got your eye on certain SEO superstars you want to learn from, ex: top SEO players in the industry.
        - **Top 5 ranking URLs**: Ideal if you’re letting curiosity lead and want to see who tops the charts for a keyword. The downside is that you may not get meaningful data if the top 5 results contain a mixed bag results of different page types - Wikipedia, dictionary, YouTube, article, e-commerce website, etc.
        """)
        
    with st.expander("Q3: How do the settings for 'country', 'language', and 'Google domain' influence my results?"):
        st.write("These settings specify the searcher's conditions, including their location, language, and the Google domain they use, affecting the search results.")

    with st.expander("Q4: What are SerpApi and SEMrush, and why are API keys necessary?"):
        st.write("SerpApi fetches search engine results, while SEMrush provides keyword data. API keys are essential for linking your accounts to these services. Obtain a free SerpApi API Key by signing up at https://serpapi.com/ to receive 100 free searches monthly, no credit card required. The SEMrush API uses the shared OD API with our SEMrush account.")

    with st.expander("Q5: What kind of data is returned?"):
        st.markdown("This tool leverages SerpApi to retrieve live data for the ranking URLs of keywords and SEMrush for the ranking of keywords on URLs. It considers a keyword's ranking only if it's 30 or lower, as rankings above 30 are considered to have minimal value. For this reason, the tool exclusively includes keywords where a webpage's position is 30 or lower.")
    
    with st.expander("Q6: What does the 'Frequency' column in the output data mean?"):
        st.write("The 'Frequency' column indicates the occurrence rate of a specific keyword across analyzed websites, highlighting its potential significance. It serves as the 'intersect' in our keyword research process. By default, the output displays the most and second most frequent keywords to minimize noise from branded keywords unique to certain websites. Expand the 'Raw Data' section to view and download all keywords ranked by each analyzed website.")

    with st.expander("Q7: Feeling lazy and want to grasp a list of seed keywords for a client website to start with?"):
        st.markdown("Sure, we've got you covered! Check out this [Google Colab script](https://colab.research.google.com/drive/1FVRA8fnls2VPUTlHiQ4x6pAOIxYjvcWo) that can magically pull out menu items to use as seed keywords.")

    with st.expander("Q8: With so many keyword tools out there, why should I pick this one?"):
        st.write("Great question! This little project is all about making things easier. It cuts right to the chase, giving you the relevant terms without the usual fuss of sifting through the noise. Plus, it's smart enough to skip over those pesky branded terms that can clutter your results.")

    with st.expander("Q9: Is there a downside to this shortcut to keyword research?"):
        st.write("While it's convenient, don't forget the old-school charm of diving deep into keyword research to gain a comprehensive understanding of the client's industry. Please ensure to dedicate time to exploring in order to truly understand the lay of the land.")

    with st.expander("Q10: Found a bug?"):
        st.write("Please reach out to Darren Huang over on Slack. It's super helpful if you include a screenshot and jot down the steps that led to the hiccup.")

    with st.expander("Q11: Got a spark of inspiration or feedback to share?"):
        st.write("I'd love to hear that! I'd love to hear that! Although I created it, the original idea was inspired by Daniel Hogben. Just send your thoughts over to Darren through Slack, and I'll be happy to chat!")



# Features to add

# Implement error handling for situations where API credits for SerpAPI and SEMrush are depleted.

# Investigate the possibility of tracking API usage for each run.

# Incorporate a password authentication feature, as this application will be public.

# (Done) Provide an option for users to opt out of specifying websites, instead automatically take the first 5 ranking URLs in the SERP.

# Notify users when a specific URL does not rank within the top X positions for a seed keyword.

# Alert users when a specific URL lacks ranking data from the SEMRush API.



# check grammar

# provide overview and guidance

# (done) Add index

# (done) KW Frequency

# (done) second most frequent keywords

# (Done) Add a column to the DataFrame (df) for the SERP Mockup, referencing the link: https://serpapi.com/searches/f160c4d5e45faf4d/65ef007266d81fd43e26f25a.html.

# (Done) To save on API calls, use SerpAPI once for each seed keyword to return the first 30 pages and ranking pages from the specified website, rather than using a site-specific search.

# (DONE) Add a column for frequency in the output DataFrame. Options for sorting include: (1) by seed keyword, then by website, or (2) by seed keyword, then by frequency in descending order.

# (DONE) Seed keyword workflow: Identify top-ranking URLs (from specified websites or the top 5) >> Extract common keywords with the highest frequency.

# (Done) Print output by seed keywords, rather than complete all first then process  

