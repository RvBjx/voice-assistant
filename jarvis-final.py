import pvporcupine
import struct

import pyaudio
import speech_recognition as sr
import pyttsx3
import webbrowser
import random
import requests
from bs4 import BeautifulSoup
import logging
import time
from phue import Bridge
import json
import pyjokes

import os
import keyboard
x = True
while x == True:
    conv_type = input("write (w) or speak (s)? ")
    if conv_type == 'w':
        x = False
    elif conv_type == 's':
        x = False
    else:
        pass
print(("""\

        ██▀▀▀      ▄▄▄            ██▀███        ██▒   █▓      ██▓       ██████      
       ▒██        ▒████▄         ▓██ ▒ ██▒     ▓██░   █▒     ▓██▒     ▒██    ▒      
       ░██        ▒██  ▀█▄       ▓██ ░▄█ ▒      ▓██  █▒░     ▒██▒     ░ ▓██▄        
    ▓██▄██▓       ░██▄▄▄▄██      ▒██▀▀█▄         ▒██ █░░     ░██░       ▒   ██▒     
     ▓███▒    ██▓  ▓█   ▓██▒ ██▓ ░██▓ ▒██▒ ██▓    ▒▀█░   ██▓ ░██░ ██▓ ▒██████▒▒ ██▓ 
     ▒▓▒▒░    ▒▓▒  ▒▒   ▓▒█░ ▒▓▒ ░ ▒▓ ░▒▓░ ▒▓▒    ░ ▐░   ▒▓▒ ░▓   ▒▓▒ ▒ ▒▓▒ ▒ ░ ▒▓▒ 
     ▒ ░▒░    ░▒    ▒   ▒▒ ░ ░▒    ░▒ ░ ▒░ ░▒     ░ ░░   ░▒   ▒ ░ ░▒  ░ ░▒  ░ ░ ░▒  
     ░ ░ ░    ░     ░   ▒    ░     ░░   ░  ░        ░░   ░    ▒ ░ ░   ░  ░  ░   ░   
     ░   ░     ░        ░  ░  ░     ░       ░        ░    ░   ░    ░        ░    ░  
               ░              ░             ░       ░     ░        ░             ░  """))

# -------------------- Setup -------------------

ACCESS_KEY = "xHJTZXeeTD4qh30L9hR2rQw/1NJL05mZT66O63rptiohbqQ8wwUslw=="

r = sr.Recognizer()
engine = pyttsx3.init()

log = "jarvis.log"
logging.basicConfig(filename=log,level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S")

HUE_BRIDGE = "192.168.1.129"
API_KEY = "NF16xKntnYza-6BO9sLEQ1-xERuNL14aQ6DbNgCB"

b = Bridge(HUE_BRIDGE)


CITY = "Nottwil"

global USER
USER = "Mister President"

db = {"USER_NAME":"","CITY_NAME":""}

# ------------------ Speaking ---------------------

def speak(text,conv_type):
    if conv_type == 's':
        engine.say(text)
        engine.runAndWait()
    else:
        print(text)

# ----------------- Update Setup file --------------

def change_setup(variable_to_change, content_to_change):
    db[variable_to_change]=content_to_change
    with open("setup.txt", "w") as f:
        f.write(str(db))  
    f.close()

# ------------------ Setup --------------------
file_exists = os.path.isfile("setup.txt")
if file_exists == False:
    file=open("setup.txt","x")
else:
    file=open("setup.txt","r")
file.close()

if file_exists == False:
    speak("Initializing setup...",conv_type)
    print("Initializing setup...")
    speak("To set up your assistant, type in your name!",conv_type)
    USER=input("Your name: ")
    print("Your name: "+USER)
    CITY=input("City for weather: ")
    print("City for weather: "+CITY)
    
    db["USER_NAME"]=USER
    db["CITY_NAME"]=CITY
    
    with open("setup.txt", "w") as f:
        f.write(str(db))  
    f.close()
    
    
    file=open("setup.txt","r")
    
    db = file.read()
    db = db.replace("'",'"')
    db = json.loads(db)
    
    USER = db["USER_NAME"]
    print("Username set to: "+USER)
    CITY = db["CITY_NAME"]
    print("City set to: "+CITY)
    
    file.close()
    
else:

    speak("Initializing startup...",conv_type)
    file=open("setup.txt","r")
    db = file.read()
    db = db.replace("'",'"')
    db = json.loads(db)
    
    USER = db["USER_NAME"]
    print("Username set to: "+USER)
    CITY = db["CITY_NAME"]
    print("City set to: "+CITY)
    
    file.close()
    
print("Awaiting your call "+USER)

# --------------- Taking Commands -------------------

def takeCommand(conv_type):
    if conv_type == "s":
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 0.7
            audio = r.listen(source)

            try:
                print("Recognizing...")
                query = r.recognize_google(audio, language="en-US")
                print(f"You said: {query}\n")

            except Exception as e:
                print(e)
                print("Sorry, I did not understand what you said.")
                return "None"
            return query
    elif conv_type == "w":
        time.sleep(0.5)
        query = input('Command: ')
        return query

# -------------- Initializing Wake Word Detection ---------------

def main():
    porcupine = None
    pa = None
    audio_stream = None
    
    try:
        porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=["jarvis", "hey google"])
        pa = pyaudio.PyAudio()
        audio_stream = pa.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length)
        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Detected")
                Conversation("s")
                time.sleep(1)
                print("Awaiting your call "+USER)
            elif keyboard.is_pressed('q'):
                print("Detected")
                Conversation("w")
                time.sleep(1)
                print("Awaiting your call "+USER)
    finally:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()

# --------------- Commands ----------------------

def log(command, query, output):
    logging.info(command)
    logging.info(f"Input: {query}, Output: {output}")

def getWeather(CITY, query):
    url = f"https://www.google.com/search?q={CITY}+weather&hl=en"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
    res = requests.get(url, headers=headers)
    print("Searching...\n")
    soup = BeautifulSoup(res.text, "html.parser")
    location = soup.select("#wob_loc")[0].getText().strip()
    time = soup.select("#wob_dts")[0].getText().strip()
    info = soup.select("#wob_dc")[0].getText().strip()
    temp = soup.select("#wob_tm")[0].getText().strip()
    speak(f"There's currently {info} in {CITY}",conv_type)
    speak(f"The temperature is {temp} degrees.",conv_type)
    output = (f"There's currently {info} in {CITY}.") + (f" The temperature is {temp} degrees.")
    log("Weather",query,output)

def lights(status, lamps, query):
    if status == "on":
        response_me = requests.get("http://" + HUE_BRIDGE + "/api/" + API_KEY + "/groups/1")
        json_data = json.loads(response_me.text)
        if json_data["state"]["any_on"] == False:
            b.set_light(2, "on", True)
            b.set_light(4, "on", True)
            b.set_light(13, "on", True)
            log("Lights",query,"Lights turn on")
            speak("Okay "+USER+". The lights are on",conv_type)
        else:
            speak("The lights are already on",conv_type)
            log("Lights",query,"The lights are already on")
    elif status == "off":
        response_me = requests.get("http://" + HUE_BRIDGE + "/api/" + API_KEY + "/groups/1")
        json_data = json.loads(response_me.text)
        if json_data["state"]["any_on"] == True:
            b.set_light(2, "on", False)
            b.set_light(4, "on", False)
            b.set_light(13, "on", False)
            log("Lights",query,"Lights turn off")
            speak("Okay "+USER+". The lights are out",conv_type)
        else:
            speak("The lights are already out",conv_type)
            log("Lights",query,"The lights are already out")

# ----------------------- Conversation -------------------------

def Conversation(conv_type):
    if __name__ == "__main__":
        logging.info(" --- Start --- ")
        query = takeCommand(conv_type).lower()
        
        if "hello" in query:
            file=open("hello.txt","r")
            m=file.readlines()
            l=[]
            for i in range(0,len(m)-1):
                x=m[i]
                z=len(x)
                a=x[:z-1]
                l.append(a)
            l.append(m[i+1])
            greeting=random.choice(l)
            global USER
            speak(greeting + USER,conv_type)
            output=greeting
            file.close()
            log("Greeting",query,output)
    
        elif "goodbye" in query:
            file=open("goodbye.txt","r")
            m=file.readlines()
            l=[]
            for i in range(0,len(m)-1):
                x=m[i]
                z=len(x)
                a=x[:z-1]
                l.append(a)
            l.append(m[i+1])
            farewell=random.choice(l)
            speak(farewell + USER,conv_type)
            output=farewell
            file.close()
            log("Farewell",query,output)
        
        # Search in either google or youtube (depending on the use of word "youtube")
        elif "search" in query:
            query_to_log = query
            if "google" in query:
                query = query.replace("google", "")
            if "search" in query:
                query = query.replace("search", "")
            if "for" in query:
                query = query.replace("for", "")
            if "after" in query:
                query = query.replace("after", "")
            if "youtube" in query:
                if "on youtube" in query:
                    query = query.replace("on youtube", "")
                query = query.replace("youtube", "")
                speak("Searching for"+ query,conv_type)
                url = "https://www.youtube.com/results?search_query={}".format(query)
                webbrowser.open(url)
                output=url
            else:
                speak("Searching, for"+ query,conv_type)
                url = "https://www.google.com.tr/search?q={}".format(query)
                webbrowser.open(url)
                output=url
            log("Search",query_to_log,output)
            
            
        elif "play music" in query:
            speak("Playing your favourite music on YouTube",conv_type)
            url = "https://www.youtube.com/watch?v=rUxyKA_-grg"
            webbrowser.open(url)
            log("Play Music",query,"Playing music from LofiGirl")
            
            
        elif "weather" in query:
            #speak("Which city would you like the weather for?",conv_type)
            #city = takeCommand().lower()
            getWeather(CITY, query)
            
        elif "lights on" in query:
            lights("on","all",query)
            
        elif "lights off" in query:
            lights("off","all",query)
            
        elif "power off" in query:
            log("--- Shut down ---",query,"End")
            quit()
        
        elif "change my name" in query:
            speak("How would you like me to call you?",conv_type)
            new_name = takeCommand().lower()
            if "call" in new_name:
                new_name = new_name.replace("call", "")
            if "me" in new_name:
                new_name = new_name.replace("me", "")
            if "you" in new_name:
                new_name = new_name.replace("you", "")
            if "can" in new_name:
                new_name = new_name.replace("can", "")
            USER = new_name
            speak("I will call you: " + USER + " from now on.",conv_type)
            change_setup("USER",USER)
        
        elif "joke" in query:
            joke = pyjokes.get_joke()
            speak(joke,conv_type)
            
        else:
            speak("Sorry, I didn't get that. Please try again.",conv_type)
            log("Error",query,"Sorry, I didn't get that. Please try again.")
            
main()