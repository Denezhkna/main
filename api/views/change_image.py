
import os
from PIL import Image
from api.views.parametrs import SCAN_FOLDER_PATH
from api.views import views_scan

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
def convert_images_to_pdf(id_session):
    pdf_name = ""
    user_path = SCAN_FOLDER_PATH+id_session
    #массив типа Image
    data_image = [] 
    #массив для получения файлов и сортировки
    data = views_scan.get_all_scan_from_user(id_session=id_session)

    if len(data) > 0:
            data.sort(key=lambda x: int(x.replace(".png", "")))
            for d in data:
                path = os.path.join(user_path, d)
                image = Image.open(path).convert('RGB')
                data_image.append(image)

            first_image = data_image[0]
            del data_image[0]
            #тут имя сгенерировать
            first_image.save(SCAN_FOLDER_PATH+id_session+'/test.pdf', save_all=True, append_images=data_image)
            pdf_name = "test.pdf"

            return pdf_name
    


