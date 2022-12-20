import requests
import urllib
import json

api_key = 'AIzaSyAwEpd1hf7X45NlNDf3gRcclbZ5417ijGk'
_base_url = 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?'
base_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json?'
place_url = 'https://maps.googleapis.com/maps/api/place/details/json?'


def generate_phone_url(place_id):    
    query_dict = dict(
        placeid=place_id,
        language='ja',
        fields='formatted_phone_number,website',
        key=api_key,
    )
    query_string = urllib.parse.urlencode(query_dict)
    return place_url + query_string

def generate_search_url(query_text, fields):
    # query_dict = dict(
    #     input=query_text,
    #     inputtype='textquery',
    #     fields=fields,
    #     key=api_key,
    # )
    query_dict = dict(
        query=query_text,
        language='ja',
        fields=fields,
        key=api_key,
    )
    query_string = urllib.parse.urlencode(query_dict)
    return base_url + query_string


def main():
    url = generate_search_url('新宿 整体院', 'formatted_address,name')
    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    print(response.text)
    res_dict = json.loads(response.text)
    json.dump(res_dict, open('res.json', 'w'))
    # res_dict = json.load(open('res.json', 'r'))
    print(res_dict.keys())
    print(res_dict['next_page_token'])
    print(res_dict['results'][0].keys())
    for candidate in res_dict['results']:
        print(candidate['name'])
        print(candidate['formatted_address'])
        
        url = generate_phone_url(place_id=candidate['place_id'])
        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        # phone_number = json.loads(response.text)['result']['formatted_phone_number']
        # print(phone_number)
        print(response.text)
        print()
        break
        print(candidate.get('website', '-'))
        print()


if __name__ == '__main__':
    main()
