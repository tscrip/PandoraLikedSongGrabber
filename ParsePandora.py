#!/usr/bin/env python
import requests, os, getpass, re
from BeautifulSoup import BeautifulSoup

#Setting variables
LOGIN_URL = "https://www.pandora.com/login.vm"
LIKES_URL = "http://www.pandora.com/content/tracklikes"
STATIONS_URL = "http://www.pandora.com/content/stations"
STATION_URL = "http://www.pandora.com/content/station"
STATION_THUMBS = "http://www.pandora.com/content/station_track_thumbs"
answer_correctly = False
i = 0

#Creating lists and set
temp_station_list = []
temp_stationname_list = []
temp_song_list = set()

#Getting input from user
pandora_email = raw_input("Please Enter your Pandora Email Address: ")
pandora_password = getpass.getpass("Please Enter your Pandora Password: ")
temp_file_name = raw_input("Please Enter a File Name for your list of music: ")

#Logging user onto pandora
session = requests.session()
response = session.post(LOGIN_URL, data={
"login_username": pandora_email,
"login_password": pandora_password,
})

#Checking to see if users was logged on sucessfully
if "0;url=http://www.pandora.com/people/" not in response.text:
   print "Pandora login failed, check email and password"
else:
    #Getting current Pandora username
    my_pandora_username = re.search('http://www.pandora.com/people/(.*)">', response.text).group(1)
    print "Your Pandora Username: " + my_pandora_username
    
    #Notifying user we logged on successfully
    print "Successfully logged on to Pandora"
    
    #Finding out who we are querying
    while answer_correctly == False:
      querying_you = raw_input("Are you getting your liked songs?(yes or no): ")
      if querying_you == 'yes':
        querying_pandora_username = my_pandora_username
        answer_correctly = True
        
      elif querying_you == 'no':
        querying_pandora_username = raw_input("Please enter the Pandora username you would like to query: ")
        answer_correctly = True
        
    print "Getting ALL stations for username: " + querying_pandora_username
    
    #Getting all stations for user
    stations_response = session.get(STATIONS_URL, params={
                                "startIndex": "0",
                                "webname": querying_pandora_username,
                            })
    stations_HTML = BeautifulSoup(stations_response.text)
    
    #Looping though HTML to get stations
    for station_h3 in stations_HTML.findAll('h3', attrs={'class':'s-0 line-h-1_4 normal'}):
      temp_station_list.append(station_h3.find('a')['href'])
      temp_stationname_list.append(station_h3.find('a').text)
    
    #Looping though stations to get songs
    while i < len(temp_station_list):
      print "Processing: " + temp_stationname_list[i].replace("&amp;", "&")
      
      #Setting variables
      more_pages = True
      like_start_index = 0
      
      #While there are songs, get them
      while more_pages:
        
        #Making request to get songs
        songs_response = session.get(STATION_THUMBS, params={
                                  "stationId": temp_station_list[i][9:],
                                  "page":"true",
                                  "posFeedbackStartIndex": like_start_index,
                                  "posSortAsc": "false",
                                  "posSortBy": "date",
                              })
        songs_HTML = BeautifulSoup(songs_response.text)
        
        #Looping though HTML to get songs
        for song_a in songs_HTML.findAll('div', attrs={'class':'col1'}):
          
          #If song is not in list, add it
          if song_a.findAll('a')[2].text.replace("&amp;", "&").encode('utf-8') + " - " + song_a.findAll('a')[1].text.replace("&amp;", "&").encode('utf-8') not in temp_song_list:
            temp_song_list.add(song_a.findAll('a')[2].text.replace("&amp;", "&").encode('utf-8') + " - " + song_a.findAll('a')[1].text.replace("&amp;", "&").encode('utf-8'))
        
        #Looking for HTML element to determine if there are more songs
        more_button = songs_HTML.find(attrs={'class':'show_more'})
        if more_button != None:
          
          #If there are more songs, get new startindex value
          if more_button.text == "Show more":
            like_start_index = more_button['data-nextstartindex']
          
          #Moving onto next station
          else:
            more_pages = False
            
            #Incrementing
            i += 1
            
        else:
          #Incrementing
          i += 1
          
          more_pages = False
        
    #Configuring write to file
    if os.path.exists(temp_file_name):
    	temp_file = open(temp_file_name, 'a')
    	print "File " + temp_file_name + " already existed... Appending"
    else:
    	temp_file = open(temp_file_name, 'w')
    	print "Creating new file: " + temp_file_name
    
    #Looping through list to get all songs
    for song in sorted(temp_song_list):
      temp_file.write(song + '\n')