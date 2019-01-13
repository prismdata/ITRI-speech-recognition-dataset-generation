import cv2
import numpy as np;

def captch_ex(file_name):
    img = cv2.imread(file_name)
    height, width = img.shape[:2]
    print('width:%s, height:%s'%(width, height))

    img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # ret, mask = cv2.threshold(img2gray, 180, 255, cv2.THRESH_BINARY)
    ret, mask = cv2.threshold(img2gray, 210, 255, cv2.THRESH_BINARY)
    image_final = cv2.bitwise_and(img2gray, img2gray, mask=mask)
    ret, new_img = cv2.threshold(image_final, 180, 255, cv2.THRESH_BINARY)  # for black text , cv.THRESH_BINARY_INV
    #line  8 to 12  : Remove noisy portion
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,
                                                         3))  # to manipulate the orientation of dilution , large x means horizonatally dilating  more, large y means vertically dilating more
    dilated = cv2.dilate(new_img, kernel, iterations=9)  # dilate , more the iteration more the dilation
    # for cv2.x.x
    _, contours, hierarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # findContours returns 3 variables for getting contours
    # for cv3.x.x comment above line and uncomment line below
    #image, contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    index = 1
    mask = np.full((img.shape[0], img.shape[1]), 0, dtype=np.uint8)  # mask is only
    for contour in contours:
        # get rectangle bounding contour
        [x, y, w, h] = cv2.boundingRect(contour)

        # Don't plot small false positives that aren't text
        if w < 35 and h < 35:
            continue
        # draw rectangle around contour on original image
        print('x start%d x end%d y start%d y end%d'%(x, x+w, y, y+h))
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)

        #you can crop image and send to OCR  , false detected will return no text :)
        # cropped = img_final[y :y +  h , x : x + w]
        # s = file_name + '_crop_' + str(index) + '.jpg'
        # index = index + 1
        # cv2.imwrite(s , cropped)
        # index = index + 1

    # write original image with added contours to disk
    cv2.imshow('captcha_result', img)
    cv2.waitKey()

input_path = '/Users/prismdata/Documents/prismdata/ml_spark/ITRI-speech-recognition-dataset-generation/data/frames/'
file_name = input_path+'drama_sample1-0005893-2.png'
captch_ex(file_name)