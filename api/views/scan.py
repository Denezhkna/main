
import os
import sane
from api.views import views_scan
from api.views.change_image import image_rotation
from api.views.parametrs import SCAN_FOLDER_PATH


depth = 8 
mode = 'color' 
#user_part = '/global_forder/scan/63e71a53-4af9-4ac6-8fc4-74e2a5b0c62b'

def test_scan(id_session): 
    sane.init() 
    try: 
        dev = sane.open("airscan:e1:RICOH MP 305+ [002673D97517]")  # открываем 
    except: 
        print("Not found scanner") 
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
        dev.br_x = 320. 
        dev.br_y = 200. 
    except: 
        print('Cannot set scan area, using default') 
 
    params = dev.get_parameters() 
    print('Device parameters:', params) 
 
    dev.start() 
    im = dev.snap() 

    user_path = SCAN_FOLDER_PATH+id_session

    data = views_scan.get_all_scan_from_user(id_session=id_session)

    new_file_name = views_scan.get_new_name_scan(data)

    file = user_path+"/"+new_file_name

    im.save(file) 
    data.append(new_file_name)
    #сотрировка не нужна, тк data уже отсортирован, а append добавляет в конец
    #data.sort(key=lambda x: int(x.replace(".png", "")))
    dev.close() 
    sane.exit() 
    image_rotation(id_session = id_session, img_name = new_file_name, angle = 270)
    
    return data
 
#test_scan(user_part)