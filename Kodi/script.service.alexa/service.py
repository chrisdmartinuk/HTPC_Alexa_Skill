
import sys
import os
import time
import random
import xbmc
import xbmcaddon
import json
import stream
import traceback
import urllib

__addon__ = xbmcaddon.Addon()
__cwd__=xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
BASE_RESOURCE_PATH = os.path.join(__cwd__,'lib')
sys.path.append(BASE_RESOURCE_PATH)


from socketIO_client import SocketIO,LoggingNamespace

addon = xbmcaddon.Addon('script.service.alexa')
user_id = addon.getSetting('authcode')
socket_url = 'http://ec2-54-191-98-39.us-west-2.compute.amazonaws.com'
socket_port= 3000
socketIO = None


supported_movie_addons=['addon.video.pulsar','addon.video.quasar']
supported_series_addons=['addon.video.pulsar','addon.video.quasar']

movie_addons = ['quasar']
series_addons = ['quasar']


def setup_addons():
    video_addons = sendJSONRPC('Addons.GetAddons',{"type":"xbmc.addon.video","content":"video","enabled":"true","properties":["path","name"]})
    
    print video_addons
    return
    for video in video_addons:
        #print video
        if video.name in supported_movie_addons:
            movie_addons.add(video.name) 
        if video.name in supported_series_addons:
            series_addons.add(video.name)


while len(user_id) < 15:
    xbmc.executebuiltin('Notification(Alexa Service,Please enter a valid key into the alexa service)')
    for i in range(60):
        time.sleep(1)
    queue_id = addon.getSetting('authcode')


def sendJSONRPC(method,params=None):
    out = {"id":1,"jsonrpc":"2.0","method":method}
    if params:
        out["params"] = params
    sendstring = json.dumps(out)
    print sendstring
    return json.loads(xbmc.executeJSONRPC(sendstring))


def play_generic_addon(message_attributes):
    addons = sendJSONRPC('Addons.GetAddons',{"enabled":true,"properties":["path","name"]})
    for video in video_addons:
        if message_attributes['addon'] in video.name:
            print "FOUND IT"
    return

def listen_pandora(message_attributes):#(stationname):

    stationname = message_attributes['station']['StringValue']
    
    #xbmc.GUI.ActivateWindow(window="videos",paramaters=['plugin://plugin.audio.pandoki/?play='+pandoraid])
    #pool = Pool(processes=1)
   
    #xbmc.GUI.ActivateWindow(window="videos",paramaters=['plugin://plugin.audio.pandoki/?play='+pandoraid])
    send_response_message("good","good")
    
    sendJSONRPC('Addons.ExecuteAddon',{'addonid':'plugin.audio.pandoki'})
    #xbmc.Addons.ExecuteAddon(addonid='plugin.audio.pandoki')#,params={"search":"hcraes"})
    time.sleep(3)
    menu_select()
    time.sleep(1)
    send_text(stationname,done=True)
    time.sleep(2)
    menu_down()
    time.sleep(1)
    menu_select()
    return
    
def get_current_selection():
    item = sendJSONRPC('XBMC.GetInfoLabels',{"labels":["System.CurrentWindow","System.CurrentControl"]})
   # http://192.168.1.169:8980/jsonrpc?request={%22jsonrpc%22:%222.0%22,%22id%22:1,%22method%22:%22XBMC.GetInfoLabels%22,%22params%22:{%22labels%22:[%22System.CurrentWindow%22,%22System.CurrentControl%22,%22Container.Content%22,%22Container(1).CurrentItem%22,%22Listitem.Label%22]}}
    return item
   
def send_text(text,done):
    sendJSONRPC('Input.SendText',{'text':text,'done':done})

def info():
    sendJSONRPC('Input.Info')  
    
def home():
    sendJSONRPC('Input.Home')   

def back():
    sendJSONRPC('Input.Back')    
    
def context_menu():
    sendJSONRPC('Input.ContextMenu')   
    
def menu_up():
    sendJSONRPC('Input.Up')
    
def menu_down():
    sendJSONRPC('Input.Down')
    
def menu_left():
    sendJSONRPC('Input.Left')
    
def menu_right():
    sendJSONRPC('Input.Right')
    
def menu_select():
    sendJSONRPC('Input.Select')

def watch_netflix(title,netflixid):

    print "received netflixID " + netflixid

    ## THIS METHOD OPENS IN CHROME, NON FULL SCREEN
    
    #url = 'http://netflix.com/watch/'+netflixid
    #print url
    #webbrowser.get(chrome_path).open(url)
    
    #stringparam = ''
    
    ## THIS METHOD USES KODI CHROME LAUNCHER TO LAUNCH FIREFOX IN KIOSK MODE
    
    #if  xbmc.getCondVisibility("system.platform.android"):
    stringparam = 'http://netflix.com/watch/' + netflixid
    #else:
        #stringparam = '?kiosk=yes&mode=showSite&stopPlayback=yes&url=http://netflix.com/watch/'+netflixid

    #headers = {'content-type':'application/json'};
    #payload = {'jsonrpc':'2.0','method':'Addons.ExecuteAddon','params':{'addonid':'plugin.program.chrome.launcher','params':[stringparam]}}
    #print xbmc.JSONRPC.Ping() 
    #xbmc.GUI.ActivateWindow(window="home")  
    #print stringparam
    #os.system("pkill chrome")
    #time.sleep(3)
    launch_chrome(stringparam)
    #sendJSONRPC('Addons.ExecuteAddon',{'addonid':'plugin.program.chrome.launcher','params':[stringparam]})
    #xbmc.Addons.ExecuteAddon(addonid='plugin.program.chrome.launcher',params=[stringparam])


    return send_response_message("Playing, " + title + ", on Netflix",title + " played on Netflix")


def watch_movie_addon(addon,title,imdbid):
    sendJSONRPC('Player.Open',{'item':{"file":"plugin://plugin.video."+addon+"/movie/"+imdbid+"/play"}})

    return send_response_message("Playing the Movie, " + title + ", on " + addon,title + " played on " + addon)



def watch_series_addon(addon,title,tvdbid,seasonNum,episodeNum,episode_title):



    if seasonNum and episodeNum:
        sendJSONRPC('Player.Open',{'item':{"file":"plugin://plugin.video."+addon+"/show/"+tvdbid+"/season/"+seasonNum+"/episode/"+episodeNum+"/play"}})

    	return send_response_message("Playing, " + title + ", " + episode_title + " , on " +addon ,title + " played on " + addon)

    elif seasonNum:
         sendJSONRPC('GUI.ActivateWindow',{"window":"videos","parameters":["plugin://plugin.video."+addon+"/show/"+tvdbid+"/season/"+seasonNum+"/episodes"]})

    	 return send_response_message("Opening, " + title + ", on " + addon,title + " played on " + addon)

    else:
        sendJSONRPC('GUI.ActivateWindow',{"window":"videos","parameters":["plugin://plugin.video."+addon+"/show/"+tvdbid+"/seasons"]})

    	return send_response_message("Opening, " + title + ", on " + addon,title + " played on " + addon)
    
 
def get_currently_playing(message_attributes):
    print "getting currently playing"
    response = sendJSONRPC("Player.GetItem",{ "properties": ["title"], "playerid": GetPlayerID() })
    title = response.get("result",[]).get("item").get("title")
    return tell_response_message("Currently Playing " + title, "Currently Playing " + title)
   
def GetPlayerID():
    info = sendJSONRPC("Player.GetActivePlayers")
    result = info.get("result", [])
    if len(result) > 0:
        return result[0].get("playerid")
    else:
        return None


def play_pause(message_attributes):
    sendJSONRPC("Player.PlayPause", {"playerid":GetPlayerID()})
    send_response_message("Ok","Kodi Pause/Resumed")
    
def stop(message_attributes):
    sendJSONRPC("Player.Stop", {"playerid":GetPlayerID()})
    send_response_message("Ok","Kodi Stopped")

def play_music(message_attributes):
    return
    
    
def play_movie(message_attributes):#(title,imdbid,netflixid):

    try:
        title = message_attributes['title']['StringValue']
        imdbid = message_attributes['imdbid']['StringValue']
        netflixid = message_attributes['netflixid']['StringValue']
    except:
        return send_response_message("Error Playing Movie on Kodi", "Error playing Movie on Kodi")

    library = library = sendJSONRPC('VideoLibrary.GetMovies',{'properties':["imdbnumber"]})
    #library = xbmc.VideoLibrary.GetMovies(properties=["imdbnumber"])
    try:
        movies = library['result']['movies']
        for movie in movies:
            print movie['imdbnumber']
            if movie['imdbnumber'] == imdbid:
                print "playng " + movie['label'] + " " + str(movie['movieid'])
                tell_response_message("Playing the Movie, " + title + ", locally on Kodi",title + " played locally")
                play_local_movie(movie['movieid'])
                return 
    except:
        print "local movie playback failed"
        
    if netflixid != '-1':
        try:
            return watch_netflix(title,netflixid)
        except:
            return tell_response_message("There was a problem playing with Netflix", "There was a problem playing with Netflix")
        
    else:
        for addon in movie_addons:
            try:
                return watch_movie_addon(addon,title,imdbid)
            except:
                return tell_response_message("There was a problem playing with " + addon, "There was a problem playing with " + addon)

def play_local_movie(movieid):
    sendJSONRPC("Playlist.Clear", {"playlistid": 1})
    sendJSONRPC("Playlist.Add", {"playlistid": 1, "item": {"movieid": int(movieid)}})
    sendJSONRPC('GUI.ActivateWindow',{'window':"videos"})
    sendJSONRPC("Player.Open", {"item": {"playlistid": 1}})
    return

def play_local_show(episode_id):
    sendJSONRPC("Playlist.Clear", {"playlistid": 1})
    sendJSONRPC("Playlist.Add", {"playlistid": 1, "item": {"episodeid": int(episode_id)}})
    sendJSONRPC('GUI.ActivateWindow',{'window':"videos"})
    sendJSONRPC("Player.Open", {"item": {"playlistid": 1}})
    return

def play_series(message_attributes):

    #print message_attributes
    title = message_attributes['title']['StringValue']
    imdbid = message_attributes['imdbid']['StringValue']

    show_tvdbid, episode_tvdbid, season_number, episode_number, episode_title = None,None,None,None,None

    netflixid = message_attributes['netflixid']['StringValue']
    if 'show_tvdbid' in message_attributes:
        show_tvdbid = message_attributes['show_tvdbid']['StringValue']
    if 'episode_tvdbid' in message_attributes:
        episode_tvdbid = message_attributes['episode_tvdbid']['StringValue']
    if 'season_number' in message_attributes:
        season_number = message_attributes['season_number']['StringValue']
    if 'episode_number' in message_attributes:
        episode_number = message_attributes['episode_number']['StringValue']
    if 'episode_title' in message_attributes:
        episode_title = message_attributes['episode_title']['StringValue']

    library = sendJSONRPC('VideoLibrary.GetTVShows',{'properties':["imdbnumber"]})
    #library = xbmc.VideoLibrary.GetTVShows(properties=["imdbnumber"])
    
    print library
    #return
    try:
        shows = library['result']['tvshows']
        for show in shows:
            #print movie['imdbnumber']
            if show['imdbnumber'] == show_tvdbid:
            
                if not season_number:
                    sendJSONRPC('GUI.ActivateWindow',{'window':"videos","parameters":["videodb://2/2/"+str(show['tvshowid'])]})
                    return ask_response_message("Which Season?",title + " opened locally")
                    
               
                    

                elif not episode_number:
                    sendJSONRPC('GUI.ActivateWindow',{'window':"videos","parameters":["videodb://2/2/"+str(show['tvshowid'])+"/"+season_number]})
                    return ask_response_message("Which Episode?",title + " opened locally")
                #print "playing " + show['label']# + " " + str(show['movieid'])
                
                
                if season_number == 'next':
                
                    episodes = sendJSONRPC('VideoLibrary.GetEpisodes',{'tvshowid':show['tvshowid'],'filter':{'field':'playcount', 'operator':'is','value':'0'},'properties':['season','episode']})['result']['episodes']
                    episode = random.choice(episodes)
                    play_local_show(episode['episodeid'])
                    return tell_response_message("Playing, " + title + "," + episode_title + ", locally on Kodi",title + " played locally")
                
                episodes = sendJSONRPC('VideoLibrary.GetEpisodes',{'tvshowid':show['tvshowid'],'properties':['season','episode']})['result']['episodes']
                
                if season_number == 'random':

                    episode = random.choice(episodes)
                    play_local_show(episode['episodeid'])
                    return tell_response_message("Playing, " + episode['showtitle'] + "," + episode['oriignaltitle'] + ", locally on Kodi",episode['showtitle'] + " played locally")
                  
                elif season_number == 'latest':
                
                    episode = episodes[-1]
                    return tell_response_message("Playing, " + title + "," + episode_title + ", locally on Kodi",title + " played locally")
                    
                    
                for episode in episodes: 
                    #print " checking " + season_number + " vs " + episode['season'] + " and " + episode_number + " vs " +episode['episode']
                    if episode['season'] == int(season_number) and episode['episode'] == int(episode_number):
                        print "playing " + show['label'] + " " + str(episode['episodeid'])
                        play_local_show(episode['episodeid'])
                        return tell_response_message("Playing, " + title + "," + episode_title + ", locally on Kodi",title + " played locally")
                    
                         
    except:
        print "local show playback failed"
    
    if netflixid != '-1':
        try:
            return watch_netflix(title,netflixid)
        except:
            return tell_response_message("There was a problem playing with Netflix", "There was a problem playing with Netflix")
        
    else:
        for addon in series_addons:
            try:
                return watch_series_addon(addon, title,show_tvdbid,season_number,episode_number,episode_title)
            except:
                return tell_response_message("There was a problem playing with " + addon, "There was a problem playing with " + addon)
        
    
    return tell_response_message("Couldn't find a source", "Couldn't find a source")


def play_random_movie():
    movies_response = sendJSONRPC('VideoLibrary.GetMovies')
    movies = movies_response['result']['movies']
    random_movie = random.choice(movies)
    play_local_movie(random_movie['movieid'])

    return jsonify(result={"status": 200})


def play_internet_stream(message_attributes):

    
    print message_attributes
    send_response_message("good","good")
    # Try to play on Kodi
    streamNum = 0
    while 'url' + str(streamNum) in message_attributes:
        print "Stream number + " + str(streamNum)
        urlin = message_attributes['url' + str(streamNum)]['StringValue']
        print "calling getURL"
        url = stream.GetStreams(urlin)
        streamNum = streamNum +1
        
        print "URL is " + str(url)
        if url:
            return sendJSONRPC('Player.Open',{'item':{"file":url}})
            

    url=message_attributes['url0']['StringValue']
    
    os.system("pkill chrome")
    
    if "youtube" in url:
        url = url.replace("watch?v=","/v/")
        url = url +  "&autoplay=1"
    
    launch_chrome(url)
    
    return 


def launch_chrome(url):

    
    print "URL IS: " + url
    
    if xbmc.getCondVisibility("system.platform.android"):
        xbmc.executebuiltin("XBMC.StartAndroidActivity(com.android.chrome,android.intent.action.VIEW,,"+url+")")
    else:
        url = '?kiosk=yes&mode=showSite&stopPlayback=yes&url='+url
        sendJSONRPC('Addons.ExecuteAddon',{'addonid':'plugin.program.chrome.launcher','params':[url]})     
    return
    
    
def recent_episodes(message_attributes):
    print "made it to recent episodes"
    response = sendJSONRPC("VideoLibrary.GetRecentlyAddedEpisodes", { "properties": [ "title", "showtitle" ],"limits":{"end":5}})
    print response
    try:
        episodes = response['result']['episodes']
    except:
        return  tell_response_message("You have no new Episodes","No new Episodes")
    speech = "Your newest episodes are. "
    for episode in episodes:
        speech = speech + episode['showtitle'] +', ' + episode['title'] + '.  '
        
    print speech
    return  tell_response_message(speech,speech)
    
def recent_movies(message_attributes):
    sendJSONRPC("VideoLibrary.GetRecentlyAddedMovies", { "properties": [ "title"],"limits":{"end":5 }})
    try:
        movies = response['result']['movies']
    except:
        return  tell_response_message("You have no new Movies","No new Movies")
    speech = "Your newest movies are: "
    for movie in movies:
        speech = speech + movie['title'] + '.  '
    return tell_response_message(speech,speech)

def navigate(message_attributes):
    where = message_attributes['nav']['StringValue']
    num = 1
    if message_attributes['num']['StringValue']:
        num = int(message_attributes['num']['StringValue'])
        
    found = False
    for i in range (0,num):
        
        if where == 'up':
            menu_up()
            found = True
        elif where == 'down':
            menu_down()
            found = True
        elif where == 'left':
            menu_left()
            found = True
        elif where == 'right':
            menu_right()
            found = True
        elif where == 'select':
            select()
            found = True
        elif where == 'info':
            info()
            found = True
        elif where == 'home':
            home()
            found = True
        elif where == 'menu':
            context_menu()
            found = True
        elif where == 'back':
            back()
            found = True
   
    if found:
        return send_response_message("OK","Navigate " + where + " received")
    else:
        return send_response_message("No navigation command for " + where,"Navigate " + where + " received")

def ask_response_message(voice,card):
    send_response_message(voice,card,"ask")
      

def tell_response_message(voice,card):
    send_response_message(voice,card,"tell")
   

def send_response_message(voice,card,body = "OK"):

    message = {
        'MessageBody':'body',
        'MessageAttributes':{
            'voice':{
                    'StringValue':voice,
                    'DataType':'String'
            },
            'card':{
                    'StringValue':card,
                    'DataType':'String'
            }
        }
    }
    socketIO.emit('client message',message)
    return


message_router = {
    'movie': play_movie,
    'series': play_series,
    'pandora': listen_pandora,
    'sports': play_internet_stream,
    'addon': play_generic_addon,
    'navigate':navigate,
    'playpause':play_pause,
    'stop':stop,
    'playing':get_currently_playing,
    'recent_movies':recent_movies,
    'recent_episodes':recent_episodes
	#'music': play_music
}
    
xbmc.executebuiltin('Notification(Alexa Service,Started,5000,/icon.png)')

def handle_disconnect(*args):
    xbmc.executebuiltin('Notification(Alexa Service,Disconnect, reconnecting!, 5000,/icon.png)')


def execute_command(*args):
    arg = args[0]
    print('execute_command', arg)
    
    #json_args = json.loads(args)
    #print json_args
    try:
        message_router[arg['message']['body']](arg['message']['message_attributes'])
    except Exception as e:
        print e
        traceback.print_exc()
        send_response_message("Error with command " + message[0].body + ". Make sure your schema is up to date","ERROR:" + str(e) + " "+ str(traceback.format_exc()))
        

def reconnect():
    global socketIO
    socketIO.emit('add client',user_id)

    
    
    
#setup_addons()   
socketIO = SocketIO(socket_url,socket_port,LoggingNamespace)
socketIO.emit('add client',user_id)
socketIO.on('disconnect',handle_disconnect)
socketIO.on('server message',execute_command)
socketIO.on('reconnect',reconnect)
#socketIO.wait()
    
    
while(1):
    socketIO.wait()
    print "listening again"

    #time.sleep(1)
