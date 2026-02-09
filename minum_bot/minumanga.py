import requests
import random
import string

url = 'https://graphql.anilist.co'
manga_name = " "
name_query = '''
query ($search: String) { 
  Page {
    media (search: $search, type: MANGA){
      id
      title {
        romaji
      }
      chapters
      status
    }
  }
}
'''
image_query = '''
query ($id: Int) {
    Media (id: $id, type: MANGA) {
        id
        title{
            romaji
        }
        coverImage {
            large
            color
        }
    }
}
'''
desc_query = '''
query ($id: Int) {
  Media (id: $id, type: MANGA) {
    title {
      romaji
      english
    }
    description (asHtml: false)
  }
}
'''

status_query ='''
query($id: Int) {
    Media (id: $id, type: MANGA) {
        id
        title{
            romaji
            english
        }
        chapters
        status
    }
}
'''
def send_status_query(id):
    variables = {
    'id': f'{int(id)}'
    }
    response = requests.post(url, json={'query': status_query, 'variables': variables})
    json_res = response.json()
    chapters = json_res.get('data', {}).get('Media', {}).get('chapters')
    status = json_res.get('data', {}).get('Media', {}).get('status')
    return [chapters, status]

def send_id_query(manga_title):
  variables = {
    'search': f'{manga_title}'
  }
  response = requests.post(url, json={'query': name_query, 'variables': variables})
  title = response.json()
  media_list = title.get('data', {}).get('Page', {}).get('media', [])
  if not media_list:
    return None
  manga_info = media_list[0]
  manga_chapters = manga_info.get('chapters')
  if not manga_chapters:
    manga_chapters = "Unknown"
  manga = [int(manga_info.get('id', 0)),
    manga_info.get('title', {}).get('romaji', "Unknown Title"),
    manga_chapters,
    manga_info.get('status')]
 
  return manga
 

def send_img_query(id):
  variables = {
    'id': f'{int(id)}'
  }
  response = requests.post(url, json={'query': image_query, 'variables': variables})
  try:
    img_url = response.json()
  except Exception:
    return "https://img.freepik.com/premium-vector/loading-icon-vector-illustration_910989-3650.jpg?semt=ais_hybrid&w=740&q=80"
  cover_img_url = img_url.get('data', {}).get('Media', {}).get('coverImage', {}).get('large')
  if not cover_img_url:
    return "https://img.freepik.com/premium-vector/loading-icon-vector-illustration_910989-3650.jpg?semt=ais_hybrid&w=740&q=80"
  return cover_img_url
  
def send_desc_query(id):
  variables = {
    'id': f'{int(id)}'
  }
  response = requests.post(url, json={'query': desc_query, 'variables': variables})
  try:
    res_json = response.json()
  except Exception:
    return "No description provided..."
  media_list = res_json.get('data', {}).get('Media', {}).get('description')
  if not media_list:
    return "No description provided..."
  clean_media_list = media_list.replace("<b>", "").replace("</b>", "")
  cleaned_desc = clean_media_list.split("<br>")[0]
  return cleaned_desc

def random_code():
    return  "{:010d}".format(random.randint(0, 10**10 - 1))
  

