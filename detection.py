

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import cv2
import imutils
from imutils import face_utils
from scipy.spatial import distance
from pygame import mixer
import dlib
import base64
from flask_cors import CORS 


mixer.init()
mixer.music.load("music.wav")
class BlinkDetectorApp:
    def __init__(self,app, socketio):
        self.app = Flask(__name__)
        self.socketio = socketio
        self.flag = 0
        self.cap = None
        self.thresh = 0.25
        self.frame_check = 20

        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        self.socketio.on_event('connect', self.handle_connect)
        self.socketio.on_event('disconnect', self.handle_disconnect)
        self.socketio.on_event('start-recording', self.start_recording)
        self.socketio.on_event('stop-recording', self.stop_detecting)


    def eye_aspect_ratio(self, eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def detect_blinks(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        global flag
        for face in faces:
            shape = self.predictor(gray, face)
            shape = face_utils.shape_to_np(shape)
            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)
            ear = (leftEAR + rightEAR) / 2.0
            # leftEyeHull = cv2.convexHull(leftEye)
            # rightEyeHull = cv2.convexHull(rightEye)
            # cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
            # cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
            if ear < self.thresh:
                self.flag += 1
                if self.flag >= self.frame_check:
                    cv2.putText(frame, "****************ALERT!****************", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(frame, "****************ALERT!****************", (10, 325),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    mixer.music.play()
            else:
                self.flag=0
            print(self.flag)
            return self.flag
    
         
    
    def handle_connect(self):
        print('Client connected')

    
    def handle_disconnect(self):
        print('Client disconnected')

    
    def start_recording(self):
        self.cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            self.detect_blinks(frame)
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = base64.b64encode(buffer)
            self.socketio.emit('video_frame', {'frame': frame_bytes.decode('utf-8')})
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        out.release()
        cv2.destroyAllWindows()
        emit('recording-finished', {'message': 'Recording finished'})

    
    def stop_detecting(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            emit('detection-stopped', {'message': 'Detection stopped'})

if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app)
    socketio = SocketIO(app, cors_allowed_origins="*")
    blink_app = BlinkDetectorApp(app,socketio)
    socketio.run(app, debug=True, port=8000)
