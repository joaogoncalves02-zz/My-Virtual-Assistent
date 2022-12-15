from datetime import datetime
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import psutil
import subprocess

# Speech Engine
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) # 0 = Male | 1 = Female
activationWord = 'computer' # Single Word

# WebBrower
edge_path="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
webbrowser.register('edge', None, webbrowser.BackgroundBrowser(edge_path))

# Wolfram Alpha
appId = 'TGX532-HJKKGQ6R8K'
wolframClient = wolframalpha.Client(appId)

# PsUtil
memoryUsage = psutil.virtual_memory().percent
cpuUsage = psutil.cpu_percent()
diskUsage = psutil.disk_usage('C:')

# SubProcess


def speak(text, rate = 120):
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def parseCommand():
    listener = sr.Recognizer()
    print('Listening for a command')

    with sr.Microphone() as source:
        listener.pause_threshold = 2
        input_speech = listener.listen(source)

    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language='en_gb')
        print(f'The input speech was: {query}')
    except Exception as exception:
        print('I did not quite catch that')
        speak('I did not quite catch that')
        print(exception)
        return 'None'
    
    return query

def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query)
    if not searchResults:
        print('No WIKIPEDIA RESULTS')
        return 'No results received'
    try:
        wikiPage = wikipedia.page(searchResults[0])
    except wikipedia.DisambiguationError as error:
        wikiPage = wikipedia.page(error.options[0])
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary)
    return wikiSummary

def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframAlpha(query = ''):
    response = wolframClient.query(query)

    # @success: Wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. This can also contain subpods
    if response['@success'] == 'false':
        return 'Could not compute'
    
    # Query resolved
    else:
        result = ''
        # Question
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        # May contain the answer, has the highest confidence value
        # If it's primary, or has the title of result or definition, then it's the official result
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            # Get the result
            result = listOrDict(pod1['subpod'])
            # Remove the bracketed section
            return result.split('(')[0]
        else: 
            question = listOrDict(pod0['subpod'])
            # Remove the bracketed section
            return result.split('(')[0]
            # Search Wikipedia instead
            speak('Computation failed. Querying universal database')
            return search_wikipedia(question)


# Main Loop
if __name__ == '__main__':
    speak('All systems nominal.')
    
    while True:
        # Parse as a list
        query = parseCommand().lower().split()

        if query[0] == activationWord:
            query.pop(0)
            
            # List commands
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Greetings, all.')
                else:
                    query.pop(0) # Remove say
                    speech = ' '.join(query)
                    speak(speech)

            # Navigation
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening...')
                query = ' '.join(query[2:])
                webbrowser.get('edge').open_new(query)

            #Wikipedia
            if query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Querying the universal datebank.')
                speak(search_wikipedia(query))

            # Wolfram Alpha
            if query[0] == 'computer' or query[0] == 'compute':
                query = ' '.join(query[1:])
                speak('Computing')
                try:
                    result = search_wolframAlpha(query)
                    speak(result)
                except:
                    speak('Unable to compute.')

            if query[0] == 'exit':
                speak('Goodbye')
                break
            
            if query[0] == 'lock':
                query = ' '.join(query[1:])
                speak('Ok , your pc will lock now')
                subprocess.call('rundll32.exe user32.dll, LockWorkStation')

            if query[0] == 'shut down' or (query[0] == 'turn' and query[1] == 'off'):
                query = ' '.join(query[1:])
                speak('Ok , your pc will shutdown n 10 sec make sure you exit from all applications in 10 sec make sure you exit from all applications')
                subprocess.call(["shutdown", "/l"])