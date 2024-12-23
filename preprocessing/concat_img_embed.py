import os
from tqdm import tqdm
import pickle
import numpy as np

root_dir = 'features'

location_name = ['guro', 'seongbuk', 'jongno', 'jungnang', 'mapo', 'dongjak', 'gangnam', 'yangcheon', 
                 'yeongdeungpo', 'geumchun', 'gwanak', 'yongsan', 'seongdong', 'gwangjin', 'seodaemun', 
                 'gangbuk', 'nowon', 'junggu', 'seocho', 'gangdong', 'eunpyeong', 'dongdaemun', 'songpa',
                 'dobong', 'gangseo']


for location in location_name:
    print(f"-- {location} processing --")

    DB_dict = {}

    with open(f'features/clip-features/{location}.pkl', 'rb') as f1:
        clip = pickle.load(f1)

    with open(f'features/dino-features/{location}_embed_dict.pkl', 'rb') as f2:
        dino = pickle.load(f2)

    with open(f'features/color-features/{location}_color.pkl', 'rb') as f3:
        color = pickle.load(f3)

    common_keys = list(set(clip.keys()) & set(dino.keys()) & set(color.keys()))

    for key in tqdm(common_keys):
        
        dino_array = np.squeeze(dino[key])

        final_embed = np.concatenate([clip[key], dino_array, color[key]])

        DB_dict[key] = final_embed
    
    with open(f'features/DB-features/{location}.pkl', 'wb') as file:
        pickle.dump(DB_dict, file)

