import numpy as np
import pandas as pd
import cv2

import redis

###Importing insightface
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise
#time
import time
from datetime import datetime

import os

###connection to redis client
hostname = 'redis-19908.c8.us-east-1-2.ec2.cloud.redislabs.com'
portnumber = 19908
password = 'o1vAP6WdNNNnqJNHXpjB3YJnJKXSxaIB'

r = redis.StrictRedis(host=hostname,
                  port=portnumber,
                  password=password)

# Retrieve data from database
def retrive_data(name):
    retrive_dict = r.hgetall(name)
    retrive_series = pd.Series(retrive_dict)
    retrive_series = retrive_series.apply(lambda x: np.frombuffer(x,dtype=np.float32))
    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))
    retrive_series.index = index
    retrive_df = retrive_series.to_frame().reset_index()
    retrive_df.columns = ['name_role','facial_features']
    retrive_df[['name','role']] = retrive_df['name_role'].apply(lambda x: x.split('@')).apply(pd.Series)
    return retrive_df[['name', 'role','facial_features']]

###configure face analyis (insightface)
faceapp = FaceAnalysis(name='buffalo_sc',
                      root='insightface_model',
                      providers=['CPUExecutionProvider'])
faceapp.prepare(ctx_id=0, det_size=(640,640),det_thresh=0.5)

###ML search algorithm
def ml_search_algorithm(dataframe, feature_column, test_vector,name_role=['name','role'], thresh=0.5):
    """
    cosine similarity base search algorithm
    """
    ### Step 1: take the dataframe (collection of data)
    dataframe = dataframe.copy()
    
     ### Step 2: Index face embeding from the dataframe and convert into an array
    X_list = dataframe[feature_column].tolist()
    x = np.asarray(X_list)
        
    ### Step 3: Calculating Cosine similarity
    similar = pairwise.cosine_similarity(x,test_vector.reshape(1,-1))
    similar_arr = np.array(similar).flatten()
    dataframe['cosine'] = similar_arr
        
    ### Step 4: filter the data
    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        ### Step 5: get the person name
        data_filter.reset_index(drop=True,inplace=True)
        argmax = data_filter['cosine'].argmax()
        person_name, person_role = data_filter.loc[argmax][name_role] 
    
    else:
        person_name = 'Unknown'
        person_role = 'Unknown'
        
    return person_name, person_role

### Real time prediction
# We need to save logs for every one min
class RealTimePred:
    def __init__(self):
        self.logs = dict(name=[], role= [], current_time= [])
    
    def reset_dict(self):
        self.logs = dict(name=[], role= [], current_time= [])
    
    def saveLogs_redis(self):
        #step 1: create log dataframe
        dataframe = pd.DataFrame(self.logs)
      
        #Step 2: drop duplicate name (distinct name)
        dataframe.drop_duplicates('name', inplace=True)

        #step 3: push data to redis database
         #encode data
        name_list = dataframe['name'].tolist()
        role_list = dataframe['role'].tolist()
        ctime_list = dataframe['current_time'].tolist()
        encoded_data = []
        for name, role, ctime in zip(name_list, role_list, ctime_list):
            if name != 'Unknown':
                concat_string = f"{name}@{role}@{ctime}"
                encoded_data.append(concat_string)
        
        if len(encoded_data) > 0:
            r.lpush('attendance:logs', *encoded_data)

        self.reset_dict()

    def face_prediction(self, test_image, dataframe, feature_column,name_role=['name','role'], thresh=0.5):
        #step 0: find current time
        current_time = str(datetime.now())

        #step 1: take the test image and apply to insight face
        results = faceapp.get(test_image)
        test_copy = test_image.copy()

        #step 2: use for loop and extract each embedding and pass it through ml_search_algorithm
        for res in results:
            x1, y1, x2, y2 = res['bbox'].astype(int)
            embeddings = res['embedding']
            person_name, person_role = ml_search_algorithm(dataframe, 
                                                        feature_column,
                                                            test_vector=embeddings, 
                                                            name_role=name_role,
                                                            thresh=thresh)

            if person_name == 'Unknown':
                color = (0,0,255) #bgr
            else:
                color = (0,255,0)

            cv2.rectangle(test_copy,(x1,y1),(x2,y2),color)

            text_gen = person_name
            cv2.putText(test_copy,text_gen,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
            cv2.putText(test_copy, current_time,(x1,y2+10), cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)

            ### save info in logs dict
            self.logs['name'].append(person_name)
            self.logs['role'].append(person_role)
            self.logs['current_time'].append(current_time)
        
        return test_copy

###### Registration Form
class RegistrationForm:
    def __init__(self):
        self.sample = 0
    def reset(self):
        self.sample = 0

    def get_embedding(self,frame):
        #Get results from insightface model
        results = faceapp.get(frame,max_num=1)
        embeddings = None
        for res in results:
            self.sample +=1
            x1, y1, x2, y2 = res['bbox'].astype(int)
            cv2.rectangle(frame, (x1,y1), (x2,y2), (0,255,0,1))
            # put text samples info
            text = f"samples = {self.sample}"
            cv2.putText(frame,text,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.6,(255,255,0),2)

                
            #Extracting facial features
            embeddings = res['embedding']

        return frame, embeddings

    def save_data_in_redis_db(self, name, role):
     
     # Validating the name which is entered
     if name is not None:
         if name.strip != '':
             key = f'{name}@{role}'
         else:
             return 'name_false'
     else:
         return 'name_false'
     
     # face_embedding exists
     if 'face_embedding.txt' not in os.listdir():
         return 'file_false'
     
     # Step 1: load face embedding.txt
     x_array = np.loadtxt('face_embedding.txt', dtype=np.float32)  #flatten array
     
     #Step 2: convert array into array (proper shape)
     received_samples = int(x_array.size/512)
     x_array = x_array.reshape(received_samples,512)
     x_array = np.asarray(x_array)

     #step 3: calculate mean embeddings
     x_mean = x_array.mean(axis=0)
     x_mean = x_mean.astype(np.float32)
     x_mean_bytes = x_mean.tobytes()

     #step 4: save this into redis database
     #redis hashes
     r.hset(name='company:register',key=key,value=x_mean_bytes)

     #removing the file face_embedding.txt
     os.remove('face_embedding.txt')
     self.reset()

     return True