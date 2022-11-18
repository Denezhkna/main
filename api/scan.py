
import os
import sane

depth = 8 
mode = 'color' 
#user_part = '/global_forder/scan/63e71a53-4af9-4ac6-8fc4-74e2a5b0c62b'

def test_scan(user_part): 
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
        dev.br_y = 240. 
    except: 
        print('Cannot set scan area, using default') 
 
    params = dev.get_parameters() 
    print('Device parameters:', params) 
 
    dev.start() 
    im = dev.snap() 
    count_files_in_forder = len([f for f in os.listdir(user_part) 
                                    if os.path.isfile(os.path.join(user_part, f))])+1
    print()
    file = user_part+"/"+str(count_files_in_forder)+'.png'
    im.save(file) 
    dev.close() 
    sane.exit() 
    return file
 
#test_scan(user_part)