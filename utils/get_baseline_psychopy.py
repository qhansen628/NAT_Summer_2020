import record
import pic_present_psychopy
from stream import stream
from multiprocessing import Process
import time
from datetime import datetime
import os

def sendData():
    global sending
    sending = Process(target=stream())
    sending.daemon = True
    print(sending, sending.is_alive())
    sending.start()
    print('sending started')
    print(sending, sending.is_alive())
    
    
# Stop datastream and disable baseline recording    
def stopData():
    global sending
    print(sending, sending.is_alive())
    sending.terminate()
    while sending.is_alive() == True:
        time.sleep(0.1)
    sending.close()
    print("sending terminated")
    
def get_baseline(path,duration = 120):
    try:
        sendData()
    except Exception as e:
        print(e)
    else:
        #initialize word presentation process
        stimulus = Process(target=stroopy_words.present, args=(duration))
        #initialize recording process
        recording = Process(target=record.record, args=(duration, path))
        #start stimulus presentation and recording process
        stimulus.start()
        recording.start()
        print(stimulus, stimulus.is_alive())
        print(recording, recording.is_alive())

        time.sleep(duration)
        while stimulus.is_alive() == True or recording.is_alive() == True :
            time.sleep(0.5)
            print("waiting")
        print("ok, finished")
        stimulus.close()
        recording.close()
        print("baseline task complete")

if __name__ == '__main__':
    name = 'Quintin'
    profile_dir = 'data/{}'.format(name)
    baseline_dir = profile_dir + 'baseline'
    model_dir = profile_dir + 'model'

    if not os.path.exists(profile_dir):
        # make data/name dir
        os.makedirs(profile_dir)
        os.makedirs(baseline_dir)
        os.makedirs(model_dir)
    
    date_time_str = datetime.now().strftime("%d-%m-%Y_%H:%M")
    recording_path = baseline_dir + date_time_str

    get_baseline(recording_path)

