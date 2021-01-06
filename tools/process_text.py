import os
import numpy as np
import cv2


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype = "float32")
    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    # return the ordered coordinates
    return rect

def four_point_transform(image, box):
    # obtain a consistent order of the points and unpack them
    # individually

    lst = []
    lst.append((box[0][0][0], box[0][0][1]))
    lst.append((box[1][0][0], box[1][0][1]))
    lst.append((box[2][0][0], box[2][0][1]))
    lst.append((box[3][0][0], box[3][0][1]))    

    #print(lst)
    lst = np.array(lst, dtype='float32')
    rect = order_points(lst)
    (tl, tr, br, bl) = rect
    tl[0] = tl[0]
    tl[1] = tl[1]-3
    tr[0] = tr[0]
    tr[1] = tr[1]-3
    br[0] = br[0]
    br[1] = br[1]+3
    bl[0] = bl[0]
    bl[1] = bl[1]+3
    
    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")
    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    # return the warped image
    return warped

def crop_image(I, box):

    box[0][0][0] = max(box[0][0][0] - 5, 0)
    box[0][0][1] = max(box[0][0][1] - 2, 0)
    box[1][0][0] = min(box[1][0][0] + 5, I.shape[1])
    box[1][0][1] = max(box[1][0][1] - 2, 0)
    box[2][0][0] = min(box[2][0][0] + 5, I.shape[1])
    box[2][0][1] = min(box[2][0][1] + 2, I.shape[0])
    box[3][0][0] = max(box[3][0][0] - 5, 0)
    box[3][0][1] = min(box[3][0][1] + 2, I.shape[0])
    
    minX = I.shape[1]
    maxX = -1
    minY = I.shape[0]
    maxY = -1

    for point in box:

        x = point[0][0]
        y = point[0][1]

        if x < minX:
            minX = x
        if x > maxX:
            maxX = x
        if y < minY:
            minY = y
        if y > maxY:
            maxY = y

    # Go over the points in the image if thay are out side of the emclosing rectangle put zero
    # if not check if thay are inside the polygon or not

    # Now we can crop again just the envloping rectangle

    return [minX, minY, maxX, maxY]



def remove_mark(str):
    new_str = ''
    for i in str:
        if i in ['á', 'à', 'ạ', 'ã', 'ả', 'ắ', 'ằ', 'ẳ', 'ẵ', 'ặ', 'ă', 'â', 'ấ', 'ầ', 'ẩ', 'ẫ', 'ậ']:
            new_str = new_str + 'a'
        elif i in ['Á','À','Ạ','Ã','Ả','Ắ','Ằ','Ẵ','Ẳ','Ặ','Ă','Â','Ấ','Ầ','Ẩ','Ẫ', 'Ậ']:
            new_str = new_str + 'A'
        elif i in ['é', 'è', 'ẻ', 'ẽ', 'ẹ', 'ế', 'ề', 'ể', 'ễ', 'ệ', 'ê']:
            new_str = new_str + 'e'
        elif i in ['É', 'È', 'Ẻ', 'Ẽ', 'Ẹ', 'Ế', 'Ề', 'Ê', 'Ể', 'Ễ', 'Ệ']:
            new_str = new_str + 'E'
        elif i in ['í', 'ì', 'ỉ', 'ĩ', 'ị']:
            new_str = new_str + 'i'
        elif i in ['Í', 'Ì', 'Ỉ', 'Ĩ', 'Ị']:
            new_str = new_str + 'I'
        elif i in ['ó', 'ò', 'ỏ', 'õ', 'ọ', 'ớ', 'ờ', 'ở', 'ỡ', 'ợ', 'ơ', 'ô', 'ố', 'ồ', 'ổ', 'ỗ', 'ộ']:
            new_str = new_str + 'o'
        elif i in ['Ó', 'Ò', 'Ỏ', 'Õ', 'Ọ', 'Ớ', 'Ờ', 'Ở', 'Ỡ', 'Ợ', 'Ơ', 'Ô', 'Ố', 'Ồ', 'Ổ', 'Ỗ', 'Ộ']:
            new_str = new_str + 'O'
        elif i in ['ú', 'ù', 'ủ', 'ũ', 'ụ', 'ứ', 'ư', 'ừ', 'ử', 'ữ', 'ự']:
            new_str = new_str + 'u'
        elif i in ['Ú', 'Ù', 'Ủ', 'Ũ', 'Ụ', 'Ứ', 'Ư', 'Ừ', 'Ử', 'Ữ', 'Ự']:
            new_str = new_str + 'U'
        elif i == 'Đ':
            new_str = new_str + 'D'
        elif i == 'đ':
            new_str = new_str + 'd'
        elif i in ['ý', 'ỳ', 'ỹ', 'ỷ', 'ỵ']:
            new_str = new_str + 'y'
        elif i in ['Ý', 'Ỳ', 'Ỹ', 'Ỷ', 'Ỵ']:
            new_str = new_str + 'Y'
        else:
            new_str = new_str + i
    return new_str
        
def Key(x):
    return x[0]

def box_nearest(key1, dic):
    box1 = dic[key1]
    min_dis = 1000
    for key2 in dic:
        if key1 == key2:
            continue
        box2 = dic[key2]
        
        if abs((box2[3] + box2[1])/2-(box1[3]+box1[1])/2) < min_dis:
            min_dis = abs((box2[3] + box2[1])/2-(box1[3]+box1[1])/2)
            key_same = key2 
    
    return key_same

def under_rows(key1, dic):
    box1 = dic[key1]
    lst = []
    for key2 in dic:
        if key1 != key2:
            box2 = dic[key2]
            if box2[0] < box1[0]-(box1[3]-box1[1]):
                continue
        
            if (box1[3]<box2[1] + (box1[3]-box1[1])/2):
                lst.append(box2)
    lst.sort(key=Key)

    return lst        

def under_rows_adress(key1, dic):
    box1 = dic[key1]
    lst = []
    for key2 in dic:
        if key1 != key2:
            box2 = dic[key2]        
            if (box1[3]<box2[1] + (box1[3]-box1[1])/2):
                lst.append(box2)
    lst.sort(key=Key)

    return lst 

def remove_char(key):
    id = ''
    for i in key:
        if i>='0' and i<='9':
            id = id+i
    return id

def remove_low_char(key):
    mark_pos = 0
    key_no_mark = remove_mark(key)
    for i, char in enumerate(key_no_mark):
        if not (char>='A' and char<='Y' or char==' '):
            mark_pos = i
    if mark_pos != 0:
        return key[mark_pos+1:]
    else:
        return key[mark_pos:]
def remove_char_birth(key):
    id = ''
    for i in key:
        if not (i>='a' and i<='z' or (i>='A' and i<='Z')):
            id = id+i
    return id    

def process_birth(key):
    
    birth = ''
    for char in key:
        if char>='0' and char<='9':
            birth = birth + char 
    
    final_birth = ''
    i = -1
    while True:
        i = i+1
        final_birth = final_birth+birth[i]
        if i in {1, 3}:
            final_birth = final_birth + '-'
        if i==len(birth)-1:
            break 
    return final_birth
        
def finalize(key):
    if key == '':
        return ''
    key_no_mark = remove_mark(key)
    i = -1
    while True:
        i = i+1

        char = key_no_mark[i]
        
        if not (('a'<=char and 'y'>=char) or ('A'<=char and 'Y'>=char)or ('0'<=char and '9'>=char)):

            key = key[:i] + key[i+1:]
            key_no_mark = remove_mark(key)
            i = i-1
        else:
            break

    if key == '':
        return ''

    i = len(key)
    key_no_mark = remove_mark(key)
    while True:
        i = i-1
        char = key_no_mark[i]
        if not (('a'<=char and 'y'>=char) or ('A'<=char and 'Y'>=char)or ('0'<=char and '9'>=char)):
            key = key[:i]
        else:
            break 
        if i==0:
            break    
    i = 0
    while True:
        if key[i]==',' and key[i+1]==',':
            key = key[:i] + key[i+1:]
            i = i-1
        i=i+1
        if i == len(key):
            break 
    
    return key 

def count_num_in_key(key):
    count = 0
    # check = False
    for i in key:
        if i >= '0' and i <= '9':
            count = count+1
    return count

def count_upper_in_key(key):
    count = 0
    for i in key:
        if i>='A' and i<='Y':
            count += 1
    return count

def remove_first_lower(key):
    final = ''
    i = 0
    if key[0]>='a' and key[0]<='z':
        pos = key.find(' ')
        final = key[pos:]
        return final 
    else:
        return key

import math 
def distance(p0, p1):
    return math.sqrt(((p0[0]-p1[0])**2+(p0[1]-p1[1])**2))        

def calculate_size_quadrilateral(array):
    p0 = array[0][0]
    p1 = array[1][0]
    p2 = array[2][0]
    p3 = array[3][0]

    p0p1 = distance(p0, p1)
    p1p2 = distance(p1, p2)
    p2p3 = distance(p2, p3)
    p3p0 = distance(p3, p0)
    p0p2 = distance(p0, p2)

    c1 = (p0p1+p1p2+p0p2)/2
    c2 = (p0p2+p2p3+p3p0)/2

    s1 = math.sqrt((c1*(c1-p0p1)*(c1-p1p2)*(c1-p0p2)))
    s2 = math.sqrt((c2*(c2-p0p2)*(c2-p2p3)*(c2-p3p0)))

    return s1+s2 

def score_nguyenquan(key):
    s = 0
    for i in {'ng', 'gu', 'uy', 'ye', 'en', 'n ', ' q', 'qu', 'ua','an'}:
        if key.find(i) != -1:
            s = s+1
    for i in {'ngu', 'guy', 'uye', 'yen', 'en ', 'n q',' qu', 'qua', 'uan'}:
        if key.find(i) != -1:
            s = s+3
    for i in {'nguy', 'guye', 'uyen', 'yen ', 'en q', 'n qu', ' qua', 'quan'}:
        if key.find(i) != -1:
            s = s+5
        
    return s
def score_dkhk(key):
    s = 0
    for i in {'No', 'oi', 'i ', ' D', 'DK', 'KH', 'HK', 'K ', ' t', 'th', 'hu',
        'uo', 'on', 'ng', 'g ', ' t', 'tr', 'ru', 'u:'}:
        if key.find(i) != -1:
            s = s+1
    for i in {'Noi', 'oi ', 'i D', ' DK', 'DKH', 'KHK', 'HK ', 'K t', ' th',
        'thu', 'huo', 'uon', 'ong', 'ng ', 'g t', ' tr', 'tru','ru:'}:
        if key.find(i) != -1:
            s = s+3
    for i in {'Noi ', 'oi D', 'i DK', ' DKH', 'DKHK', 'KHK ', 'HK t', 'K th',
        ' thu', 'thuo', 'huon','uong','ong ', 'ng t', 'g tr', ' tru', 'tru:'}:
        if key.find(i) != -1:
            s = s+5
    return s
def remove_last_char(pred):
    if pred is not None:
        if pred[-1] in {'.', ',','-', '/'}:
            pred = pred[:-1]
    return pred 

def sort_key_left2right(dic):
    string = ''

    if len(dic) == 1:
        for key in dic:
            string = key
    else:
        for i, key in enumerate(dic):
            if i == 0:
                a = key
            else:
                b = key    
        string = a + b

    return string
def score_conghoa(key):
    s = 0
    for i in {'CO', 'ON', 'NG', 'G ', ' H', 'HO', 'OA', 'A ','XA', 'A ', ' H',
        'HO', 'OI', 'I ', ' C', 'CH', 'HU', 'U ', ' N', 'NG', 'GH', 'HI', 'IA',
        'A ', ' V', 'VI', 'IE', 'ET', 'T ', ' N', 'NA', 'AM'}:
        if key.find(i) != -1:
            s = s+1
    return s

def cut_roi(dic, copy_img, dic_o):
    max1 = 0
    max2 = 0

    for key in dic:
        key_no_mark = remove_mark(key)
        sc_dkhk = score_dkhk(key_no_mark)
        sc_conghoa = score_conghoa(key_no_mark)      

        #print(key,' ' ,sc_dkhk)
        #print(key,' ', sc_conghoa)  
    
        if sc_dkhk > max1:
            max1 = sc_dkhk
            box_dkhk = dic_o[key]
            #print('1', key)
        if sc_conghoa > max2:
            max2 = sc_conghoa
            box_conghoa = dic_o[key]
            #print('2', key)

    width_conghoa = box_conghoa[1][0][0] - box_conghoa[0][0][0]
    height_conghoa = box_conghoa[3][0][1] - box_conghoa[0][0][1]

    topleft = [max(int(box_conghoa[0][0][0] - width_conghoa/3),0), max(int(box_conghoa[0][0][1] - height_conghoa/2),0)]
    topright = [min(int(box_conghoa[1][0][0] + width_conghoa/7), copy_img.shape[1]), max(int(box_conghoa[1][0][1] - height_conghoa/2), 0)]
    botleft = [max(int(box_dkhk[3][0][0] - width_conghoa/3), 0), min(int(box_dkhk[3][0][1] + height_conghoa*2.5), copy_img.shape[0])]
    botright = [min(int(botleft[0]+topright[0]-topleft[0]),copy_img.shape[1]), min(int(topright[1] + botleft[1]-topleft[1]), copy_img.shape[0])]


    #copy_img = cv2.circle(copy_img,(topleft[0], topleft[1]), 5, (0,255,0), -1)
    #copy_img = cv2.circle(copy_img,(topright[0], topright[1]), 5, (0,255,0), -1)
    #copy_img = cv2.circle(copy_img,(botleft[0], botleft[1]), 5, (0,255,0), -1)
    #copy_img = cv2.circle(copy_img,(botright[0], botright[1]), 5, (0,255,0), -1)


    box = [[topleft], [topright], [botright], [botleft]]
    #print('box', box)
    #print(box)
    #warped =  four_point_transform(copy_img, box)
    box_rec = crop_image(copy_img, box)
    #print('rec', box_rec[0], box_rec[1])
    save_img = copy_img[int(box_rec[1]):int(box_rec[3]), int(box_rec[0]):int(box_rec[2])]    
    cv2.imwrite('out.jpg', save_img)