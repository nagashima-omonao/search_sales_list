import requests
import urllib
import json
import streamlit as st
import pandas as pd
pd.set_option('display.max_colwidth', -1)

api_key = 'AIzaSyAwEpd1hf7X45NlNDf3gRcclbZ5417ijGk'
base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
place_url = 'https://maps.googleapis.com/maps/api/place/details/json?'


def get_details(place_id):
    query_dict = dict(
        placeid=place_id,
        language='ja',
        fields='formatted_phone_number,website',
        key=api_key,
    )
    query_string = urllib.parse.urlencode(query_dict)
    url = place_url + query_string
    response = requests.request("GET", url, headers={}, data={})
    res_dict = json.loads(response.text)
    return (res_dict['result'].get('formatted_phone_number'),
            res_dict['result'].get('website'))


def generate_search_url(query_text, fields):
    query_dict = dict(
        query=query_text,
        language='ja',
        fields=fields,
        key=api_key,
    )
    query_string = urllib.parse.urlencode(query_dict)
    return base_url + query_string


def get_candidates(query_text, max_candidates):
    url = generate_search_url(query_text, 'formatted_address,name')
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    res_dict = json.loads(response.text)
    json.dump(res_dict, open('res.json', 'w'))
    # res_dict = json.load(open('res.json', 'r'))
    print(res_dict.keys())
    print(res_dict['next_page_token'])
    print(res_dict['results'][0].keys())

    candidate_list = list()
    for candidate in res_dict['results']:
        print(candidate['name'])
        print(candidate['formatted_address'])

        phone_number, website = get_details(place_id=candidate['place_id'])
        print(phone_number)
        print(website)

        cand_dict = dict(
            name=candidate['name'],
            address=candidate['formatted_address'],
            phone=phone_number,
            site_url=website,
        )
        candidate_list.append(cand_dict)
        print()
    return pd.DataFrame(candidate_list)

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    return f'<a target="_blank" href="{link}">{link}</a>' if link else ''

# link is the column with hyperlinks

def app():
    max_candidates = st.sidebar.number_input('最大件数', min_value=20, max_value=200)

    query_text = st.text_input('検索ワードを入力')
    query_text = query_text.replace('　', ',').replace(' ', ',')

    if st.button('検索'):
        cand_df = get_candidates(query_text, max_candidates)
        cand_csv = cand_df.to_csv(index=False)
        st.dataframe(cand_df)
        out_file_name = st.text_input('ダウンロードファイル名', 'out.csv')
        st.download_button('ダウンロード', cand_csv, out_file_name, mime='text/csv')
        # cand_df['site_url'] = cand_df['site_url'].apply(make_clickable)
        # st.write(cand_df.to_html(escape=False, index=False), unsafe_allow_html=True, col_space='300px')


if __name__ == '__main__':
    app()
