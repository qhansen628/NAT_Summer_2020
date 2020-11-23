import pandas as pd 
import numpy as np


PEOPLE_GRAPHIC_STRS = ['BDSM','Child labor' ,'Dead bodies' ,'Injury', 'Nude' ,'Severed']
ANIMAL_GRAPHIC_STRS = ['Animal carcass' 'Dog attack']
CATES = {'animals':1, 'objects':2,'people':3,'scenes':4}
NUM_BINS = 3

def get_theme_types(data,category):
    cate_df = data[data['Category'] == category]
    themes = list(cate_df['Theme'].unique())
    theme_types = []
    for theme in themes:
        theme_type = ' '.join(theme.split(' ')[:-1])
        if theme_type not in theme_types:
            theme_types.append(theme_type)
            
    return themes

def get_not_graphic(themes, graphic_strs):
    
    themes_safe = [theme for theme in themes if all([graphic not in theme for graphic in graphic_strs])]
    return themes_safe

def get_safe_indices(df,people_graphic_strs,animal_graphic_strs,verbose=False):

    animal_themes = get_theme_types(df, CATES['animals'])
    animal_themes_safe = get_not_graphic(animal_themes, animal_graphic_strs)

    people_themes = get_theme_types(df, CATES['people'])
    people_themes_safe = get_not_graphic(people_themes,people_graphic_strs)

    themes_to_check = {CATES['animals']:animal_themes_safe,
                        CATES['people']:people_themes_safe}
    safe_inds = []
    for i,row in df.iterrows():
        safe_list = themes_to_check.get(row['Category'],None)
        if safe_list:
            if row['Theme'] in safe_list:
                safe_inds.append(i)
            elif verbose:
                print('rejected:',row['Theme'])
        else:
            safe_inds.append(i)
    return safe_inds


def get_subset_bygender(data,sex = 'men',num_images=160,num_bins=3):
    '''
    return a dataframe of images with even distribution of valence, arousal combos
    for sex the options are man and women, sorry if thats problematic.
    people can do all instead of by gender if they wish
    ''' 
    #get valence, arousal bin combos. bins are from 1 to 4
    #so we want 1,1 1,2 ... 2,3 2,4 ... 3,1 ,3,2 ... 4,1 ... 4,4
    combos = []
    for v_bin in range(1,num_bins+1):
        for a_bin in range(1,num_bins+1):
            combos.append((v_bin,a_bin))

    num_images_per_combo = round(num_images/len(combos))

    v_mean_col = 'Valence_mean_'+sex
    a_mean_col = 'Arousal_mean_'+sex
    v_mean_col_bin = v_mean_col + '_bin'
    a_mean_col_bin = a_mean_col +'_bin'

    
    #make list of bin labels
    bin_labels = list(range(1,num_bins+1))
    #make column of bin number for valence
    data[v_mean_col_bin] = pd.qcut(data[v_mean_col],q=num_bins,labels=bin_labels)
    #make column of bin number of arousal
    data[a_mean_col_bin] = pd.qcut(data[a_mean_col], q=num_bins,labels = bin_labels)

    sample_df = None
   
    for combo in combos:

        combo_subset = data[(data[v_mean_col_bin] == combo[0]) & (data[a_mean_col_bin] == combo[1])]

        if len(combo_subset) == 0:
            
            #don't worry about arousal, and use pics of people
            combo_subset = data[(data[v_mean_col_bin] == combo[0]) & (data['Category'] == 3)]
            combo_samples = combo_subset.sample(num_images_per_combo)

        elif len(combo_subset) <= num_images_per_combo:
            num_needed = num_images_per_combo - len(combo_subset)
            rest_sample = data[(data[v_mean_col_bin] == combo[0]) & (data['Category'] == 3)].sample(num_needed)
            combo_samples = combo_subset.append(rest_sample).drop_duplicates()

        else:
            combo_samples = combo_subset.sample(num_images_per_combo)

        if sample_df is None:
            sample_df = combo_samples
        else: 
            sample_df = sample_df.append(combo_samples)

    sample_df = sample_df.drop_duplicates()
    #if the sample still doesn't have enough images
    #add random samples of the people or animal images until full
    max_loops = len(sample_df)//3 *2 #max_loops is just incase the while loop runs forever, probably wont
    num_loops = 0
    while len(sample_df) < num_images or num_loops >= max_loops:
        
        #people or animals
        extra_sample = data[(data['Category'] == 1) | (data['Category'] == 3)].sample(3)
        sample_df = sample_df.append(extra_sample)
        sample_df = sample_df.drop_duplicates()
    return sample_df


def get_subset_all(data,num_images=160,num_bins=3):

    #get valence, arousal bin combos. bins are from 1 to 4
    #so we want 1,1 1,2 ... 2,3 2,4 ... 3,1 ,3,2 ... 4,1 ... 4,4
    combos = []
    for v_bin in range(1,num_bins+1):
        for a_bin in range(1,num_bins+1):
            combos.append((v_bin,a_bin))
    #number of images that each combo should have for even distribution
    num_images_per_combo = round(num_images/len(combos))

    v_mean_col = 'Valence_mean'
    a_mean_col = 'Arousal_mean'
    v_mean_col_bin = v_mean_col + '_bin'
    a_mean_col_bin = a_mean_col +'_bin'

    #make list of bin labels
    bin_labels = list(range(1,num_bins+1))
    #make column of bin number for valence
    data[v_mean_col_bin] = pd.qcut(data[v_mean_col],q=num_bins,labels=bin_labels)
    #make column of bin number of arousal
    data[a_mean_col_bin] = pd.qcut(data[a_mean_col], q=num_bins,labels = bin_labels)

    sample_df = None

    for combo in combos:

        combo_subset = data[(data[v_mean_col_bin] == combo[0]) & (data[a_mean_col_bin] == combo[1])]
        #if we don't have any of that combo, get the same number images of 
        #people with that valence since pictures of people probably elicit more emotion
        if len(combo_subset) == 0:
            
            #don't worry about arousal, and use pics of people
            combo_subset = data[(data[v_mean_col_bin] == combo[0]) & (data['Category'] == 3)]
            combo_samples = combo_subset.sample(num_images_per_combo)

        #if we only get some images of that combo we should fill the rest with same
        #number of images with the same valence and use pics of people
        elif len(combo_subset) < num_images_per_combo:
            num_needed = num_images_per_combo - len(combo_subset)
            rest_sample = data[(data[v_mean_col_bin] == combo[0]) & (data['Category'] == 3)].sample(num_needed)
            combo_samples = combo_subset.append(rest_sample).drop_duplicates()

        #if we have enough of that combo, use those images
        else:
            combo_samples = combo_subset.sample(num_images_per_combo)
        
       
        if sample_df is None:
            sample_df = combo_samples
        else: 
            sample_df = sample_df.append(combo_samples)

    sample_df = sample_df.drop_duplicates()
    
    #if the sample still doesn't have enough images
    #add random samples of the people or animal images until full
    max_loops = len(sample_df)//3 *2 #max_loops is just incase the while loop runs forever, probably wont
    num_loops = 0
    while len(sample_df) < num_images or num_loops >= max_loops:
        
        #people or animals
        extra_sample = data[(data['Category'] == 1) | (data['Category'] == 3)].sample(3)
        sample_df = sample_df.append(extra_sample)
        sample_df = sample_df.drop_duplicates()
            
    return sample_df

#This is the important function here that we will call
def generate_dataset(num_images,safe=True, sex='all'):
    
    if sex == 'all': #use the dataset with values averaged over all genders
        data = pd.read_csv('OASIS_database_2016/OASIS.csv')
    else: #use the dataset with values for both men and women averaged separately
        data = pd.read_csv('OASIS_database_2016/OASIS_bygender.csv')

    if safe == True: #remove graphic images, like porn, uncomfortable bdsm pics, and dead babies
        safe_inds = get_safe_indices(data,PEOPLE_GRAPHIC_STRS,ANIMAL_GRAPHIC_STRS)
        data = data.iloc[safe_inds]
    
    
    if sex == 'all': 
        return get_subset_all(data,num_images,num_bins= NUM_BINS)
    else:
        return get_subset_bygender(data,sex,num_images,num_bins=NUM_BINS)