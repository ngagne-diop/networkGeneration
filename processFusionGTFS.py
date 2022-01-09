#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''Ce code dans sa version de mai 2020 permet de fusionner les données GTFS mises en ligne des réseaux du :
    Nord : Disponibles : ILEVIA (Métropole lilloise), DKBUS (Dunkerque) et TRANSVILLES (Valenciennes)
           Indisponibles : TUC (Cambrai), Evéole (Douai), Stibus (Maubeuge)
    Pas-de-Calais : Disponibles : Imag'in (Calais), MARINEO (Boulogne/mer), MOUVEO (Saint-Omer)
                    Indisponibles : ARTIS (Arras), TADAO (Lens-Liévin - Hénin-Carvin - Béthune), 
                                    CA2BM (Navettes - Le Touquet-Paris-Plage), TUB (Berck-sur-Mer)
    transport régional ferroviaire : SNCF
    
    ****************************************************************************************************
    Les données GTFS inputs et les détails liés à leur validité et manipulations sont disponibles sur : 
            https://drive.google.com/drive/folders/1cu7pbGw9lXNr8lyfXuAlBRJuy_s5RJnv?usp=sharing
    @ Ngagne DIOP
'''


# In[1]:


import pandas as pd
import os


# In[2]:


# Ce dictionnaire reprend les variables exhaustives des tables : https://developers.google.com/transit/gtfs/reference/

dict_file_column ={
    "agency": ["agency_id","agency_name","agency_url", "agency_timezone",
           "agency_lang","agency_phone", "agency_fare_url","agency_mail"],
    
    "stops": ["stop_id","stop_code","stop_name", "stop_desc","stop_lat","stop_lon",
             "zone_id","stop_url","location_type","parent_station","stop_timezone","wheelchair_boarding",
             "level_id", "platform_code"],
    
    "routes": ["route_id", "agency_id", "route_short_name", "route_long_name", "route_desc",
               "route_type","route_url", "route_color","route_text_color","route_sort_order"],
    
    "trips": ["route_id", "service_id", "trip_id", "trip_headsign", "trip_short_name","direction_id",
             "block_id","shape_id", "wheelchair_accessible", "bikes_allowed"],
    
    "stop_times": ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "stop_headsign",
                  "pickup_type", "drop_off_type", "shape_dist_traveled", "timepoint"],
    
    "calendar": ["service_id", "monday", "tuesday","wednesday", "thursday", "thursday", "friday", "saturday",
                "sunday", "start_date", "end_date"],
    
    "calendar_dates": ["service_id", "date", "exception_type"]
             }


# # Preprocessing function

# In[3]:


#lire un fichier txt
def read_file(file_path):
    df = pd.read_csv(file_path, sep=",",encoding='utf8')
    return df


# In[4]:


def save_file(df, output_path):
    df.to_csv(output_path,index=None, sep=',',encoding='utf8')


# In[5]:


#ajouter une colonne si elle n'exsite pas pour préparer la fusion
def add_column(all_cols, df):
    cols_df  = df.columns
    for col in all_cols:
        if col not in cols_df:
            df[col] = ''
    return df[all_cols]


# In[6]:


def preprocessing_nan_values(input_folder_path,dict_file_column):
    dict_df ={}
    for key in dict_file_column.keys():
        file_path = input_folder_path+"/"+key+".txt"
        cols = dict_file_column[key]
        df = read_file(file_path)
        pre_df = add_column(cols,df)
        dict_df[key] = pre_df
    return dict_df


# In[7]:


# Formatage des données suivant le fichier Excel (gtfs fusion) dispnible dans le dossier de partage
def format_id_values(dict_df, agency_name):
    dict_df_formatted ={}
    #get DataFrame
    df_agency = dict_df["agency"]
    df_stops = dict_df["stops"]
    df_routes = dict_df["routes"]
    df_trips = dict_df["trips"]
    df_stop_times = dict_df["stop_times"]
    df_calendar = dict_df["calendar"]
    df_calendar_dates = dict_df["calendar_dates"]
    
    # formatted data for agency.text
    if agency_name =="marineo":
        df_agency["agency_id"] ="mar"
        df_routes["agency_id"] ="mar"
    dict_df_formatted["agency"] = df_agency
        
     # formatted data for stop.tex 
    df_stops["stop_id"] = df_stops["stop_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    
    df_stops["zone_id"] = df_stops["zone_id"] .apply(lambda x :agency_name +"_"+  str(x)) 
    dict_df_formatted["stops"] = df_stops
    
     # formatted data for routes.txt
    df_routes["route_id"] =df_routes["route_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    dict_df_formatted["routes"] = df_routes
    
     # formatted data for trips.txt
    df_trips["route_id"] = df_trips["route_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    df_trips["service_id"] = df_trips["service_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    df_trips["trip_id"]= df_trips["trip_id"].apply(lambda x :agency_name +"_"+ str(x)) 
    dict_df_formatted["trips"] = df_trips
    
     # formatted data for stop_times.txt
    df_stop_times["trip_id"] = df_stop_times["trip_id"].apply(lambda x :agency_name +"_"+  str(x))
    df_stop_times["stop_id"] = df_stop_times["stop_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    dict_df_formatted["stop_times"] = df_stop_times

     # formatted data for calendar
    df_calendar["service_id"] = df_calendar["service_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    dict_df_formatted["calendar"] = df_calendar
    
    df_calendar_dates["service_id"] = df_calendar_dates["service_id"].apply(lambda x :agency_name +"_"+  str(x)) 
    dict_df_formatted["calendar_dates"] = df_calendar_dates 
    
    return dict_df_formatted


# # Filtered SNCF FIle

# In[8]:


def filtered_sncf(dictionnaire):
    
    dict_df ={}
    dict_df["agency"] = dictionnaire["agency"]
    
    df_stops = dictionnaire["stops"]
    df_routes = dictionnaire["routes"]
    df_trips = dictionnaire["trips"]
    df_stop_times = dictionnaire["stop_times"]
    df_calendar = dictionnaire["calendar"]
    df_calendar_dates = dictionnaire["calendar_dates"]
    
    # Les conditions de filtre
    # Comme les données de la SNCF ot été reconstituées, les limites ont été agrandies pour couvrir le perimetre 
    df_stops = df_stops[(df_stops.stop_lat >= 49.9400)
                        & (df_stops.stop_lat <= 51.0880)
                        & (df_stops.stop_lon >= 1.4969)
                        & (df_stops.stop_lon <= 4.2874)]
    
    dict_df["stops"]=df_stops
    stop_id = df_stops.stop_id.values
    
    df_stop_times =df_stop_times[df_stop_times.stop_id.isin(stop_id)]
    dict_df["stop_times"]=df_stop_times
    trip_id = df_stop_times.trip_id.values
    
    df_trips = df_trips[df_trips.trip_id.isin(trip_id)]
    dict_df["trips"] = df_trips
    route_id = df_trips.route_id.values
    service_id = df_trips.service_id.values
    
    df_routes = df_routes[df_routes.route_id.isin(route_id)]
    dict_df["routes"] = df_routes
    
    df_calendar = df_calendar[df_calendar.service_id.isin(service_id)]
    dict_df["calendar"]=  df_calendar
    
    df_calendar_dates = df_calendar_dates[df_calendar_dates.service_id.isin(service_id)]
    dict_df["calendar_dates"] = df_calendar_dates
    
    return dict_df


# # precessing pipeline

# In[9]:


def pipeline_preprocess(input_folder_path, output_folder_path, agency_name):
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)
    # Formatted nana colums
    dict_formatted_nan = preprocessing_nan_values(input_folder_path,dict_file_column)
    #if agency_name == "sncf":
    #    dict_formatted_nan = filtered_sncf(dict_formatted_nan)
    #formatted ID columns
    dict_formatted_id = format_id_values(dict_formatted_nan, agency_name)
    for key  in dict_formatted_id.keys():
        output_file = output_folder_path+"/"+key+".txt" 
        df = dict_formatted_id[key]
        # Save file
        save_file(df, output_file)


# # Fusion function

# In[10]:



def fusion_data(input_directtory, output_directory):
    
    output_directory = output_directory+"/data"
    if not os.path.exists( output_directory):
        os.makedirs( output_directory)
        
    #Pour chaque table 
    for key in dict_file_column.keys():
        df_list =[]
        for filename in os.listdir(input_directtory):
            input_file = input_directtory+"/"+filename+"/"+key+".txt"
            ouput_file = output_directory+"/"+key+".txt"
            df = read_file(input_file)
            df_list.append(df)
        #Fusion data
        df =   pd.concat(df_list)
        #save fusion
        save_file(df, ouput_file)

        
def fusion_new_data(input_folder_path_new_data, input_folder_old_fusion, output_directory_new, agency_name):
    
    input_folder_new_data_preprocessing = input_folder_old_fusion+"/new_data_"+agency_name
    
    if not os.path.exists( output_directory_new):
        os.makedirs( output_directory_new)
        
    pipeline_preprocess(input_folder_path_new_data, input_folder_new_data_preprocessing, agency_name)
    fusion_data(input_folder_old_fusion,output_directory_new)
    


# # First_Fusion

# In[11]:


### Formate les données fournies dans inputgts et les range dans la sortie_notebook

# Réseau ferroviaire
pipeline_preprocess("inputgtfs/sncf","sortie_notebook/sncf","sncf")
# Réseau Dunekrquois
pipeline_preprocess("inputgtfs/dkbus","sortie_notebook/dkbus","dkbus")
# Réseau de la Métropole lilloise
pipeline_preprocess("inputgtfs/ilevia","sortie_notebook/ilevia","ilevia")
# Réseau de boulogne sur Mer
pipeline_preprocess("inputgtfs/marineo","sortie_notebook/marineo","marineo")
# Réseau IMAG'In de Calais
pipeline_preprocess("inputgtfs/opalebus","sortie_notebook/opalebus","opalebus")
# Réseau de Valenciennes
pipeline_preprocess("inputgtfs/transvilles","sortie_notebook/transvilles","transvilles")
# Réseau de Saint-
pipeline_preprocess("inputgtfs/capso","sortie_notebook/capso","capso")


# In[12]:


# Fusionne toutes les données disponibles dans la sortie_notebook
fusion_data("sortie_notebook", "fusion")


# # Fusion new data

# In[13]:


# En cas de mise à jour de données GTFS par une agence (exemple SNCF), mais attention à la plage de validité avec les autres
# fusion_new_data("sncf_new_data", "fusion", "new_fusion","sncf")


# In[ ]:




