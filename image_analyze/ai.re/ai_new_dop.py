from imageai.Detection import VideoObjectDetection, ObjectDetection
import cv2
from matplotlib import pyplot as plt
import time
import vk_api
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.upload import VkUpload
import threading
from threading import Thread

vk_session = vk_api.VkApi(token = '#')
vk = vk_session.get_api()
upload = VkUpload(vk)
longpoll = VkBotLongPoll(vk_session, 1111111) # вместо 1111111 - айди группы 
vk_user = vk_api.VkApi(login = "#", password = "#", token = "#") # вместо решоточек - данные
vkUser = vk_user.get_api()
uploadUser = VkUpload(vkUser)

def upload_photo(upload, photo):
    response = upload.photo_messages(photo)[0]
    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'
    return attachment

def message(txt, id, upl = False):
    if upl != False:
        vk.messages.send(
                            user_id = id,
                            random_id = get_random_id(),
                            message = txt,
                            attachment = upload_photo(upload, upl)
                        )
    else:
        vk.messages.send(
                        user_id = id,
                        random_id = get_random_id(),
                        message = txt
                    )

def send_video(txt, id, source):
    attachment = uploadUser.video(source) 
    own = attachment["owner_id"]
    vd = attachment["video_id"]
    key = attachment["access_key"]
    vk.messages.send(
                        user_id = id,
                        random_id = get_random_id(),
                        message = txt,
                        attachment =  f"video{ own }_{ vd }_{ key }", 
                )


id_list = [582508695, 170026886] # айди людей, которые могут пользоваться ботом
user_list = []
detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath("yolo.h5")
detector.loadModel()
custom_p = detector.CustomObjects(person=True)
custom_c = detector.CustomObjects(car=True)
yxnem = 0 

class meeting():
  def __init__(self, box_points, user):
    self.sec = 0 
    self.box_points = box_points
    self.meetings = user.meetings
    self.find = True
  def update(self):
    if self.find == False:
        self.meetings.remove(self)
        return False
    if self.sec > 0:
        self.sec -= 1
    self.find = False
    return True

class user():
    def __init__(self, id):
        self.id = id 
        self.started = False
        self.rate = 5
        self.out = 0
        self.meetings = []
        self.cordinates = []
    def start(self):
        cap = cv2.VideoCapture("rtsp://stream:LdXq1Fiz@10.1.56.58")
        ret, frame = cap.read()
        height, width = frame.shape[:2]
        frame = cv2.resize(frame, (width // 2, height // 2))
        cap.release()
        cv2.imwrite(f"materials/ForVK{self.id}.png", frame)
        detections = detector.detectCustomObjectsFromImage(
                    custom_objects = custom_c,
                    input_image = f"materials/ForVK{self.id}.png",
                    output_image_path = f'materials/ForVK{self.id}.png',
                    minimum_percentage_probability = 80)
        c = 0
        for i in detections:
            cv2.rectangle(frame, (i['box_points'][0], i['box_points'][1]), (i['box_points'][2], i['box_points'][3]), (0,0,255), 2)
            cv2.putText( frame, f"{c}", ( i['box_points'][0] + (i['box_points'][2] - i['box_points'][0])//2, i['box_points'][1] + (i['box_points'][3] - i['box_points'][1])//2 ), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 1)
            c += 1
        cv2.imwrite(f"materials/ForVK{self.id}.png", frame)
        message("Выберите машину", self.id, f"materials/ForVK{self.id}.png")
        for event in longpoll.listen():
            if event.message.from_id == self.id:
                txt = ""
                for i in event.message.text:
                    if i.isdigit():
                        txt += i
                if len(txt) < 0:
                    message("Введите, пожалуйста, номер машины", self.id)
                    continue 
                txt = int(txt)
                if txt >= len(detections):
                    message("Неправильно указан номер машины", self.id)
                    continue 
                else:
                    self.out = cv2.VideoWriter(f'video{self.id}.avi', cv2.VideoWriter_fourcc(*'XVID'), 5, (width // 2, height // 2))
                    self.cordinates = detections[txt]["box_points"]
                    message("Машина успешно выбрана", self.id)
                    self.start_cont()
                    return 
    def start_cont(self):
        global user_list
        message("Напишите, через сколько секунд надо уведомлять Вас о странных людях около вашей машины", self.id)
        for event in longpoll.listen():
            if event.message.from_id == self.id:
                txt = ""
                for i in event.message.text:
                    if i.isdigit():
                        txt += i
                if len(txt) < 0:
                    message("Введите, пожалуйста, число", self.id)
                    continue 
                else:
                    txt = int(txt) 
                    self.rate = txt
                    message(f"Секунды Успешно установлены ({self.rate} sec)", self.id)
                    self.meetings = []
                    user_list.append(self)
                    return 
    def ending(self):
        global user_list 
        user_list.remove(self)
        self.out.release()
        send_video("Отчет", self.id, f"video{self.id}.avi")
        return 

def mainVkThread():
    while True:
        try:
            for event in longpoll.listen():
                if event.message.from_id in id_list:
                    userr = 0 
                    o = True
                    for i in user_list:
                        if event.message.from_id == i.id:
                            o = False
                            userr = i 
                            break 
                    if o == True:
                        userr = user(event.message.from_id)
                    if len(event.message.text) > 0: 
                        txt = ""
                        for i in event.message.text.lower():
                            if i != " ":
                                txt += i 
                        if txt == "stop" and userr.started == True:
                            userr.started = False 
                        elif userr.started == False and txt == "start":
                            userr.started = True
                            Thread(target=userr.start, args=()).start()
        except Exception as e:
            print(e)

def mainAiThread():
    global yxnem
    while True:
        try:
            yxnem += 1 
            print(f"Still Working {len(user_list)}")
            cap = cv2.VideoCapture("rtsp://stream:LdXq1Fiz@10.1.56.58")
            ret, frame = cap.read()
            height, width = frame.shape[:2]
            frame = cv2.resize(frame, (width // 2, height // 2))
            cap.release()
            cv2.imshow("Jo", frame)
            cv2.imwrite(f'materials/worked.png', frame)
            detections = detector.detectCustomObjectsFromImage(
                custom_objects=custom_p,
                input_image=f'materials/worked.png',
                output_image_path= f'materials/out{yxnem}.png',
                minimum_percentage_probability=80)
            for user in user_list:
                if user.started == False:
                    user.ending()
                    continue
                for b in detections:
                    if b['name'] == 'person':
                        o = True
                        for x in user.meetings:
                            if x.find == False and x.box_points[0] - 20 <= b['box_points'][0] and x.box_points[1] - 20  <= b['box_points'][1] and x.box_points[2] + 20 >= b['box_points'][2] and x.box_points[3] + 20 >= b['box_points'][3]:
                                print(x.box_points)
                                x.box_ponts = b['box_points']
                                print(x.box_points)
                                x.find = True
                                o = False
                                break 
                        if o == True:
                            user.meetings.append( meeting( b['box_points'], user) )
                for i in user.meetings:
                    if i.update() == False:
                        continue
                    if i.box_points[2] > user.cordinates[0] and i.box_points[0] < user.cordinates[2] and i.box_points[3] > user.cordinates[1] and i.box_points[1] < user.cordinates[3]:
                        i.sec += 2
                    if i.sec >= user.rate:
                        i.sec = 0 
                        tosend = cv2.imread("materials//worked.png")
                        cv2.rectangle(tosend, (i.box_points[0], i.box_points[1]), (i.box_points[2], i.box_points[3]), (0,0,255), 7)
                        cv2.imwrite(f'materials/tosend{user.id}.png', tosend)
                        cv2.imwrite(f"materials/out{yxnem}x{user.id}.png", tosend) # записываем ухнем + юзер.ид потому что может быть более одного соприкосновения в кадр
                        vk.messages.send(
                            user_id = user.id,
                            random_id = get_random_id(),
                            message = "Странный человек стоит около машины. Обратите внимание",
                            attachment = upload_photo(upload, f"materials/tosend{user.id}.png")
                        )
                # message("lol", user.id, f"materials/worked.png")
                user.out.write(frame)

        except Exception as e:
            print(e)

Thread(target=mainAiThread, args=()).start()
Thread(target=mainVkThread, args=()).start()
