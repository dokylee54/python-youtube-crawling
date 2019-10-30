import requests
import csv
import json
from pprint import pprint
import urllib.request
from sys import argv

'''
env : python 3.6.8
usage : python youtube_crawling.py {subscription_key} {channel_id}
'''

#subscription_key = "AIzaSyBn-a5we3nt_9chFZokm5WNZ4oLvd1OY9E"
subscription_key = argv[1]
#channel_id = "UCAxdWlT5uFu8_mxdFkhJ0rw"
channel_id = argv[2]

channels_url = "https://www.googleapis.com/youtube/v3/channels"
playlistItems_url = "https://www.googleapis.com/youtube/v3/playlistItems"
video_url = "https://www.googleapis.com/youtube/v3/videos"

# input: http url, parameters list
def request_youtube_api(url, params):

    response = requests.get( url=url, params=params )
    response.raise_for_status()
    response = response.json()

    return response

# convert image URL into image file
def save_image_fromUrl(image_url, image_filename):
    urllib.request.urlretrieve(
        image_url, 
        '.\\images\\' + image_filename + '.jpg'
    )
    print("* save img successfully *")

# remove emoji
import emoji

def give_emoji_free_text(text):
    allchars = [str for str in text]
    emoji_list = [c for c in allchars if c in emoji.UNICODE_EMOJI]
    clean_text = ' '.join([str for str in text.split() if not any(i in str for i in emoji_list)])
    return clean_text


if __name__=="__main__" :

    # csv file
    f = open('youtube_channelUploadsInfo.csv', 'w', encoding='utf-8-sig', newline='')
    wr = csv.writer(f)
    # first row
    wr.writerow(["num", "videoID", "title", "publishedAt", 
                "duration", "viewCount", "commentCount",
                "likeCount", "dislikeCount"])

    '''
    find playlistItems_id
    '''
    params = {
        'part': 'contentDetails', 'id': channel_id,
        'key': subscription_key
    }
    response = request_youtube_api(channels_url, params)

    playlistItems_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print("playlistItems_id = {0}".format(playlistItems_id))


    '''
    get video info
    '''
    #get next page token -> get all uploads
    nextPageToken = ""
    all_video_info = []
    while nextPageToken != "nothing":
        
        params = {
            'part': 'snippet', 'maxResults': 50, # maxResults -> 0 ~ 50
            'pageToken': nextPageToken, 'playlistId': playlistItems_id, 
            'key': subscription_key
        }
        response = request_youtube_api( url=playlistItems_url, params=params )

        # parsing json data
        playlistItems = response['items']

        # print the number of uploads
        all_videoCount = response['pageInfo']['totalResults']
        print("\n{0} videos\n".format(all_videoCount))

        for idx, value in enumerate(playlistItems):            
            base_info = value['snippet']

            video_id = base_info['resourceId']['videoId'] #for statistics

            video_num = base_info['position'] + 1 # set a starting number to 1, not 0
            video_title = give_emoji_free_text(base_info['title'])
            video_imageUrl = base_info['thumbnails']['high']['url']
            video_publishedAt = base_info['publishedAt'].split('T')[0]

            print("#{0}\n".format(video_num))

            # request details of video
            video_statistics_params = {
                'part': 'statistics',
                'id': video_id,
                'key': subscription_key
            }
            video_statistics = request_youtube_api(video_url, video_statistics_params)
            
            video_statistics = video_statistics['items'][0]['statistics']
            video_viewCount = video_statistics['viewCount']
            if 'commentCount' in video_statistics:  # comment util could not be allowed 
                video_commentCount = video_statistics['commentCount']
            else: video_commentCount = 'NOT allowed'
            video_likeCount = video_statistics['likeCount']
            video_dislikeCount = video_statistics['dislikeCount']

            # request video duration info
            video_duration_params = {
                'part': 'contentDetails',
                'id': video_id,
                'key': subscription_key
            }
            video_duration_baseinfo = request_youtube_api(video_url, video_duration_params)

            video_duration = video_duration_baseinfo['items'][0]['contentDetails']['duration'].split('PT')[1]

            # json for each video info
            video_info = {
                "num" : video_num,
                "videoID" : video_id,
                "title" : video_title,
                "publishedAt" : video_publishedAt,
                "duration" : video_duration,
                "viewCount" : video_viewCount,
                "commentCount" : video_commentCount,
                "likeCount" : video_likeCount,
                "dislikeCount" : video_dislikeCount
            }
            pprint(video_info)
            all_video_info.append(video_info)

            # csv file for video info
            wr.writerow([video_num, video_id, video_title, video_publishedAt, 
                        video_duration, video_viewCount, video_commentCount, 
                        video_likeCount, video_dislikeCount])

            # # save the thumbnail image
            # image_filename = str(video_num) + '+' + video_id
            # save_image_fromUrl(video_imageUrl, image_filename) 


        # get next page token
        if 'nextPageToken' in response: 
            nextPageToken = response['nextPageToken']
            print("previous page DONE -> next page token : {0}".format(nextPageToken))
        else:
            nextPageToken = "nothing"
            print("\n\nDONE!!")

    f.close()
    # pprint(all_video_info)


