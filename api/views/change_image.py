
import os
from PIL import Image
from api.views.parametrs import SCAN_FOLDER_PATH
from api.views import views_scan
from datetime import datetime, timedelta

def image_rotation(id_session, img_name, angle : int):
    img_full_path = SCAN_FOLDER_PATH+id_session+"/"+img_name
    print(img_full_path)
    if not os.path.exists(img_full_path):
        return "Файл не найден"

    image = Image.open(img_full_path)
    rotated_img = image.rotate(angle, expand=True)
    rotated_img.save(img_full_path)
    return img_name

#возможно передавать массив изображений отпользователя, чтобы соединять не всю папку
def convert_images_to_one_pdf(id_session, user_folder):
    pdf_name = ""
    #массив типа Image
    data_image = [] 
    #массив для получения файлов и сортировки
    data = views_scan.get_all_scan_from_user(id_session=id_session, user_folder=user_folder)

    if len(data) > 0:
            data.sort(key=lambda x: int(x.replace(".jpg", "")))
            for d in data:
                path = os.path.join(user_folder, d)
                image = Image.open(path).convert('RGB')
                data_image.append(image)

            first_image = data_image[0]
            del data_image[0]
            #тут имя сгенерировать
            now_date_time = datetime.now()
            now_date_time_str = now_date_time.strftime("%d-%m-%Y_%H-%M-%S")
            name_pdf = id_session+"_"+now_date_time_str+".pdf"
            first_image.save(user_folder+name_pdf, save_all=True, append_images=data_image)

            return name_pdf
    
def convert_images_to_many_pdf(id_session, user_folder):
    pdf_name = ""
    #массив типа Image
    data_image = [] 
    #массив для получения файлов и сортировки
    data = views_scan.get_all_scan_from_user(id_session=id_session, user_folder = user_folder)
    if len(data) > 0:
        i = 1
        for d in data:
            path = os.path.join(user_folder, d)
            image = Image.open(path).convert('RGB')
            now_date_time = datetime.now()
            now_date_time_str = now_date_time.strftime("%d-%m-%Y_%H-%M-%S")
            name_pdf = id_session+"_"+str(i)+"_"+now_date_time_str+".pdf"
            image.save(user_folder+name_pdf)
            data_image.append(name_pdf)
            i = i+1

    return data_image


def convert_png_to_jpg(id_session):
    jpg_name = ""
    user_path = SCAN_FOLDER_PATH+id_session
    #массив типа Image
    data_image = [] 
    #массив для получения файлов и сортировки
    data = views_scan.get_all_scan_from_user(id_session=id_session)


