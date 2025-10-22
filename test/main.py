import cv2
import face_recognition
import os
import numpy as np
from datetime import datetime
import pickle
import csv

path = 'Student_Images'
images = []  # Contains images to view
classNames = os.listdir(path)  # this lists all the files in a directory as an array
Student_names = []
temp = 0
unknown_faces = []

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
            f.writelines(f'{student_name}, {reg_no}, {time}, {date}\n')
        print(name_list)

# take pictures from webcam
cap = cv2.VideoCapture(0)
while True:
    success, img = cap.read()
    print(img)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    faces_in_frame = face_recognition.face_locations(imgS)
    encoded_faces = face_recognition.face_encodings(imgS, faces_in_frame)
    for encode_face, face_location in zip(encoded_faces, faces_in_frame):
        matches = face_recognition.compare_faces(encoded_face_train, encode_face)
        face = encode_face
        faceDist = face_recognition.face_distance(encoded_face_train, encode_face)
        matchIndex = np.argmin(faceDist)
        print(matches)
        if not matches[matchIndex]:
            'name = classNames[matchIndex]'
            y1, x2, y2, x1 = face_location
            # since we scaled down by 4 times
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, "unknown", (x1 + 6, y2 - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            'mark_attendance(name)'



    cv2.imshow('webcam', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\nTotal number of students present = ", temp)
        break

