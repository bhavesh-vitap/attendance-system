import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import pickle
import csv
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

print("\nProgram Initiated")

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

path = 'Student_Images'
images = []  # Contains images to view
classNames = os.listdir(path)  # this lists all the files in a directory as an array
Student_names = []
check_it = False
time_global = "12:59:59:P.M"


for i in classNames:
    curImg = cv2.imread(f'{path}/{i}')
    images.append(curImg)
    Student_names.append(os.path.splitext(i)[0])

def find_encodings(images_):
    encode_list = []
    for image in images_:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encoded_face = face_recognition.face_encodings(image)[0]
        encode_list.append(encoded_face)
    return encode_list

encoded_face_train = find_encodings(images)

def mark_attendance(student_name):
    with open('Attendance.csv', 'r+') as f:
        my_data_list = f.readlines()
        name_list = []
        student_name = student_name.split('.')[0]
        reg_no = (student_name.split(', ')[1])
        student_name = student_name.split(', ')[0]
        for line in my_data_list:
            entry = line.split(',')
            name_list.append(entry[0])

        if student_name not in name_list:
            global temp
            temp += 1
            now = datetime.now()
            time = now.strftime('%I:%M:%S:%p')
            date = now.strftime('%d-%B-%Y')
            print(student_name)
            student_data = {"name":student_name, "reg_no":reg_no, "time":time, "date":date}
            db.collection("Faculty").document("Faculty ID").collection("Class ID").document(reg_no).set(student_data)
            f.writelines(f'{student_name}, {reg_no}, {time}, {date}\n')
        # print(name_list)
        f.close()

def capture_it(check_it):
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        faces_in_frame = face_recognition.face_locations(imgS)
        encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)
        for encode_face, face_location in zip(encoded_faces, faces_in_frame):
            matches = face_recognition.compare_faces(encoded_face_train, encode_face)
            faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
            matchIndex = np.argmin(faceDist)
            # print(matchIndex)
            if matches[matchIndex]:
                name = classNames[matchIndex]
                y1, x2, y2, x1 = face_location
                # since we scaled down by 4 times
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                mark_attendance(name)
        cv2.imshow('webcam', img)

        if temp == len(Student_names):
            db.collection("Check").document("check_it").update({"temp": False})
            check_it = False
            cap.release()
            cv2.destroyAllWindows()
            print("\nAttendance stopped.")
            print("\nAll present")
            print("Total number of students present = ", temp)
            break
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            db.collection("Check").document("check_it").update({"temp": False})
            check_it = False
            cap.release()
            cv2.destroyAllWindows()
            print("\nAttendance stopped.")
            print("\nTotal number of students present = ", temp)
            break
        elif db.collection("Check").document("check_it").get().to_dict()["temp"] == False:
            check_it = False
            cap.release()
            cv2.destroyAllWindows()
            print("\nAttendance stopped.")
            print("\nTotal number of students present = ", temp)
            break

    return check_it


while True:

    temp = 0
    check = 0

    print("\n\nReady for execution :) \n")

    while not check_it:
        dic = db.collection("Check").document("check_it").get().to_dict()
        check_it = dic["temp"]
        time.sleep(2)
        #print(dic)

    print("Attendance started...\n")

    #
    if temp == 0 and check == 0:
        check += 1
        docs = db.collection("Faculty").document("Faculty ID").collection("Class ID").where("time", "<=",
                                                                                            time_global).get()
        for doc in docs:
            key = doc.id
            db.collection("Faculty").document("Faculty ID").collection("Class ID").document(key).delete()

        filename = "Attendance.csv"
        f1 = open(filename, "w+")
        f1.close()

    print("Recording attendance...\n")

    check_it = capture_it(check_it)

    continue



