
import os
import cups
import subprocess 
from api.views import views_scan
from api.views.parametrs import PRINT_FOLDER_PATH, NAME_PRINT_MACHINE
import time
import shutil

#Чтобы преобразовать word, excel и тд, сначала преобразоваываем в pdf

def get_preview_file(id_session, file_path):
    user_folder = PRINT_FOLDER_PATH+id_session+"/"
    #data_png = []
    file_extension = os.path.splitext(file_path)[1]
    full_file_name = os.path.basename(file_path)
    file_name = os.path.splitext(full_file_name)[0]
    #file_name = file_path.replace(full_file_name, '')


    clear_folder(user_folder=user_folder)

    #if file_extension == '.png':
     #   data_png.append[file_path]
      #  return data_png

    #if file_extension == '.jpg':
    #    try_convert = convert_jpg_to_png(file_path = file_path, file_name = file_name, user_folder = user_folder)    
    #    if not try_convert:
    #        return "Не удалось преобразовать файл"
        
     #   data_png.append(user_folder+file_name+".png")
    #    return data_png

    if file_extension == '.pdf':
        shutil.copyfile(file_path, user_folder+file_name+".pdf", follow_symlinks=True)
        return file_name+".pdf"
    else:
        try_convert = convert_file_to_pdf(file_path = file_path, user_folder = user_folder)
        if not try_convert:
            return "Не удалось преобразовать файл"
        return file_name+".pdf"
        #file_pdf = user_folder+file_name+".pdf"

    #try_convert = convert_pdf_to_png(file_path = file_pdf, user_folder = user_folder)
    #if not try_convert:
     #   return "Не удалось преобразовать файл"
    #data_png = get_files_in_folder(user_folder = user_folder, data_png = data_png)
    #return data_png

def convert_pdf_to_png(file_path, user_folder): 
    try_convert = False
    timeout = time.time()
    while try_convert == False or time.time() - timeout > 10.0:
                try:
                    res = subprocess.check_output(['pdftoppm',
                            file_path,
                            user_folder,
                            '-png'])
                    try_convert = True
                    break
                except:
                    try_convert = False

    return try_convert 


def create_file_whith_selected_page(id_session, file_name, page_list):
    user_folder = PRINT_FOLDER_PATH+id_session+"/"
    full_path = user_folder + file_name

    param = ['pdftk', full_path, 'cat',]
    for p in page_list:
        param.append(str(p))

    param = param + ['output', user_folder+"print_version_"+file_name]
   
    try_convert = False
    timeout = time.time()
    res = None
    while try_convert == False or time.time() - timeout > 10.0:
        try:
            res = subprocess.check_output(param)
            try_convert = True
            res = "print_version_"+file_name
            break
        except:
            try_convert = False
    return res


#посмотреть параметры печати
def print_file(user_folder, file_name, type_print_file_side, count_copy, identification_doc):
    full_path = user_folder + file_name

    print_params = {"cpi":"12", "lpi":"8", "sides":type_print_file_side, "copies":str(count_copy)}
    if identification_doc:
        print_params['number-up'] = "2"
    #{"number-up":"2"} #2 на одной стороне листа
    try_convert = False
    timeout = time.time()
    res = "Ошибка печати"
    while try_convert == False or time.time() - timeout > 10.0:
        try:
            conn = cups.Connection()
            conn.printFile(NAME_PRINT_MACHINE, full_path, "", print_params) 
            try_convert = True
            res = "Готово"
            break
        except:
            try_convert = False

    return res

def convert_file_to_pdf(file_path, user_folder):
    try_convert = False
    timeout = time.time()
    while try_convert == False or time.time() - timeout > 10.0:
                try:
                    res = subprocess.check_output(['libreoffice',
                                                    '--headless',
                                                    '--convert-to',
                                                    'pdf',
                                                    '--outdir',
                                                    user_folder,
                                                    file_path])
                    if str(res) != "'b'":
                        try_convert = True
                        break
                except:
                    try_convert = False

    return try_convert 

def convert_jpg_to_png(file_path, file_name, user_folder):
    try_convert = False
    timeout = time.time()
    while try_convert == False or time.time() - timeout > 10.0:
                try:
                    res = subprocess.check_output(['convert',
                                        file_path,
                                        user_folder + file_name +".png"])
                    try_convert = True
                    break
                except:
                    try_convert = False

    return try_convert 

def get_files_in_folder(user_folder, data_png):

    for root, dirs, files in os.walk(user_folder):
        for i, file in enumerate(files):
            file_part_name, file_extension = os.path.splitext(user_folder+file)
            if file_extension == ".png" or file_extension == ".jpg":
                data_png.append(file)

    data_png.sort()
    return data_png

def clear_folder(user_folder):
    for root, dirs, files in os.walk(user_folder):
        for file in files:
            os.remove(user_folder+file)