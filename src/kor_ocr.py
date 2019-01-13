try:
    import Image
except ImportError:
    from PIL import Image
import pytesseract
from os import listdir
import os
from os.path import isfile, join
import cv2
input_path = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation/data/frames/'
output_path = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation/data/ocr_result/'
try:
    os.stat(output_path)
except:
    os.mkdir(output_path)

onlyfiles = [f for f in listdir(input_path) if isfile(join(input_path, f))]
file_scription = {}
for file in onlyfiles:
    try:
        img = cv2.imread(input_path + file)
        img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # ret, mask = cv2.threshold(img2gray, 200, 255, cv2.THRESH_BINARY)
        # image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
        # ret, new_img = cv2.threshold(image_final, 200, 255, cv2.THRESH_BINARY)

        # ret, mask = cv2.threshold(img2gray, 190, 255, cv2.THRESH_BINARY)
        # image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
        # ret, new_img = cv2.threshold(image_final, 190, 255, cv2.THRESH_BINARY)

        ret, mask = cv2.threshold(img2gray, 198, 255, cv2.THRESH_BINARY)
        image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
        ret, new_img = cv2.threshold(image_final, 198, 255, cv2.THRESH_BINARY)

        cv2.imwrite(input_path + '_' + file, new_img)
        ocr_result =pytesseract.image_to_string(Image.open(input_path + '_' + file), lang='kor')
        os.remove(input_path + '_' + file)

        if len(ocr_result) > 0:
            file_scription[file] = ocr_result
        else:
            file_scription[file] = 'unknown_image_text'
    except Exception as e:
        file_scription[file] = 'file error'
        print(e)

for fn, script in file_scription.items():
    if script != 'unknown_status':
        print('%s:%s'%(fn, script))
