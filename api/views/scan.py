
import os
import sane
from api.views import views_scan
from api.views.change_image import image_rotation
from api.views.parametrs import SCAN_FOLDER_PATH, NAME_SCAN_MACHINE
import time


depth = 8 
mode = 'color' 
#user_part = '/global_forder/scan/63e71a53-4af9-4ac6-8fc4-74e2a5b0c62b'

def test_scan(user_folder, id_session, br_x, br_y): 
    sane.init() 

    try_connect = False
    timeout = time.time()
    while try_connect == False or time.time() - timeout > 10.0:
        try:
            #airscan:e0:RICOH MP 305+ [002673D97517]
            dev = sane.open(NAME_SCAN_MACHINE)
            try_connect = True
            break
        except:
            dev = None

    if not try_connect:
        sane.exit() 
        return "Not found scanner"

    # без параметров погибает и не сканирует 
    params = dev.get_parameters() 

    try: 
        dev.depth = depth 
    except: 
        print('Cannot set depth, defaulting to %d' % params[3]) 
 
    try: 
        dev.mode = mode 
    except: 
        print('Cannot set mode, defaulting to %s' % params[0]) 
 
    try: 
        dev.br_x = br_x  
        dev.br_y = br_y  
    except: 
        print('Cannot set scan area, using default') 
 
    params = dev.get_parameters() 
    print('Device parameters:', params) 
 
    dev.start() 
    im = dev.snap() 

    data = views_scan.get_all_scan_from_user(id_session=id_session, user_folder = user_folder)

    new_file_name = views_scan.get_new_name_scan(data)

    file = user_folder+new_file_name

    im.save(file) 
    data.append(new_file_name)
    #сотрировка не нужна, тк data уже отсортирован, а append добавляет в конец
    #data.sort(key=lambda x: int(x.replace(".png", "")))
    dev.close() 
    sane.exit() 
    image_rotation(id_session = id_session, img_name = new_file_name, angle = 270)
    
    return data
 
#test_scan(user_part)