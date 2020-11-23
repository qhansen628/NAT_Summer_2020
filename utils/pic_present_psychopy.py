import numpy as np
from psychopy import visual, core, event
from time import time, strftime, gmtime
from pylsl import StreamInfo, StreamOutlet
from random import choice
from math import floor




def present(data,val_col_name,arous_col_name, duration=120,width=1000, height=800):

    # Create markers stream outlet
    #info = StreamInfo('Markers', 'Markers', 1, 0, 'int32', 'myuidw43536')
    info = StreamInfo('Markers', 'Markers', 2, 0, 'float32', 'myuidw43536')
    outlet = StreamOutlet(info)

    #markernames = [1, 2]
    start = time()

    # Set up trial parameters
    #n_trials = 2010
    iti = 1
    soa = 2.5
    jitter = 0.3
    record_duration = np.float32(duration)

    # Setup trial list
    #image_type = np.random.binomial(1, 0.5, n_trials)
    #trials = DataFrame(dict(image_type=image_type,
    #                        timestamp=np.zeros(n_trials)))

    #randomly shuffle dataframe
    data = data.sample(frac=1)
    
    #set up psychopy window
    mywin = visual.Window([width, height], monitor='testMonitor', units='deg', winType='pygame',
                          fullscr=False)
    #get path from theme
    def get_path(theme):
        path = 'images/'+row['Theme'].strip() + '.jpg'
        return path
    #load image from path
    def load_image(path):
        return visual.ImageStim(win=mywin, image=path)
    

    #for ii, trial in trials.iterrows():
    for ii,row in data.iterrows():

        theme = row['Theme']
        arousal = row[arous_col_name]
        valence = row[val_col_name]
        
        # Intertrial interval
        core.wait(iti + np.random.rand() * jitter)
        #get path from dataset
        im_path = get_path(theme)
        #get image
        image = load_image(im_path)
        
        image.draw()
     
        # Send marker
        timestamp = time()
        #outlet.push_sample([markernames[label]], timestamp)
        outlet.push_sample([valence,arousal], timestamp)
        
        mywin.flip()
    
        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break
        event.clearEvents()

    # Cleanup
    mywin.close()





if __name__ == '__main__':
    from dataset_generators import generate_dataset
    data = generate_dataset(num_images=160,safe=False,sex='men')
    present(data,'Valence_mean_men','Arousal_mean_men', duration=20)
