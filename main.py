from dotenv import load_dotenv
import requests
import urllib
import json
import os
import traceback
import streamlit as st
import pandas as pd
pd.set_option('display.max_colwidth', None)
load_dotenv()

api_key = os.environ['API_KEY']
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


def get_search_results(query_text, fields, next_page_token=''):
    query_dict = dict(
        query=query_text,
        language='ja',
        fields=fields,
        key=api_key,
    )
    if next_page_token:
        query_dict['pagetoken'] = next_page_token
    query_string = urllib.parse.urlencode(query_dict)
    url = base_url + query_string
    response = requests.request("GET", url, headers={}, data={})
    return json.loads(response.text)


def get_candidates(query_text, max_candidates):

    first_flag = True
    next_page_token = ''
    candidate_list = list()
    while first_flag or (next_page_token and len(candidate_list) <= max_candidates):
        first_flag = False

        try:
            res_dict = get_search_results(
                query_text, 'formatted_address,name', next_page_token)
            next_page_token = res_dict.get('next_page_token')
            print(len(res_dict['results']))
            if len(res_dict['results']) == 0:
                print(res_dict)
            for candidate in res_dict['results']:
                phone_number, website = get_details(
                    place_id=candidate['place_id'])
                cand_dict = dict(
                    name=candidate['name'],
                    address=candidate['formatted_address'],
                    phone=phone_number,
                    site_url=website,
                )
                candidate_list.append(cand_dict)
        except Exception:
            t = traceback.format_exc()
            print(t)
            break
        # print(first_flag, next_page_token, len(candidate_list), max_candidates)
        import time
        time.sleep(2)
        print()

    return pd.DataFrame(candidate_list)


def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    return f'<a target="_blank" href="{link}">{link}</a>' if link else ''

# link is the column with hyperlinks


def app():
    max_candidates = st.sidebar.number_input(
        '目安件数', min_value=20, max_value=200,
        help='ここで設定した数値かつ20の倍数が取得されます')

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
