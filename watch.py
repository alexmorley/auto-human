import os

import cv2
import telegram
import requests
import numpy as np
from dotenv import load_dotenv
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater


load_dotenv()

TOKEN=os.getenv("TOKEN")
CAM_URL=os.getenv("CAM_URL")

# handle /start commend
def start(update, context):
    chat_contexts.append((update.effective_chat.id, context))
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def any_cats(image, classifier = "haarcascade_frontalcatface_extended.xml"):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
     
    detector = cv2.CascadeClassifier(classifier)
    rects = detector.detectMultiScale(gray, scaleFactor=1.02,
	    minNeighbors=4, minSize=(75, 75)) 
    
    return rects

def take_snapshot(
        filename,
        omega_url = f"http://{CAM_URL}/?action=snapshot"
    ):
    r = requests.get(omega_url, stream=True)
    if r.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)
    else:
        raise requests.RequestException()
    
def make_cat_image(image, rects):
    for (i, (x, y, w, h)) in enumerate(rects):
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(image, "Cat #{}".format(i + 1), (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
    
    return image


chat_contexts = []
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

while True:
    try:
        image_url = f"http://{CAM_URL}/?action=snapshot"
        take_snapshot("snapshot.jpg")
        frame = cv2.imread("snapshot.jpg")
        
        rects = any_cats(frame)
        if len(rects) > 0:
            print('Cat Detected')
            image = make_cat_image(frame, rects)
            cv2.imwrite("cat.jpg", image)
            for id_, context in chat_contexts:
                context.bot.send_message(
                        chat_id=id_,
                        text="I've seen a cat"
                )
                context.bot.send_photo(
                        chat_id=id_,
                        photo=open('cat.jpg', 'rb')
                )
    except requests.RequestException as e:
        print(f"Webcam inaccessible.")
        print(f"{e}")
    except Exception as e:
        print(f"{e}")


