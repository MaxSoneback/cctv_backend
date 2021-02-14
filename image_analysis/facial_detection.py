import cv2
import abc
import numpy as np


class FaceDetector:
    def __init__(self, classifier):
        self.classifier = classifier

    @abc.abstractmethod
    def detect_faces(self, frame: np.ndarray, scale_factor: int = 1.3, min_neighbors: int = 5) -> None:
        """
        :param frame: an image frame
        :param scale_factor:
        :param min_neighbors:
        :return:
        """

    @staticmethod
    def draw_bounding_box(frame, bounding_box, text: str = '', color=(255, 0, 0)):
        x, y, w, h = bounding_box
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            color,
            thickness=2
        )

        if not text == '':
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame,
                        text,
                        (x, y - 5),
                        font, 1,
                        (0, 255, 255),
                        2,
                        cv2.LINE_4)


class HaarFaceDetector(FaceDetector):
    class HaarClassifier:
        def __init__(self, classifier, name, color):
            self.classifier = cv2.CascadeClassifier(cv2.data.haarcascades + classifier)
            self.name = name
            self.color = color
            self.bounding_boxes = None

        def detect(self, frame, scale_factor: int = 1.3, min_neighbors: int = 5):
            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            self.bounding_boxes = self.classifier.detectMultiScale(
                image=grayscale,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors
            )
            if self.name == 'profile':
                print(self.bounding_boxes)
                grayscale = cv2.flip(grayscale, 1)
                try:
                    #TODO: Fix!
                    self.bounding_boxes.append(
                        self.classifier.detectMultiScale(
                            image=grayscale,
                            scaleFactor=scale_factor,
                            minNeighbors=min_neighbors
                        )
                    )
                except AttributeError:
                    self.bounding_boxes = self.classifier.detectMultiScale(
                            image=grayscale,
                            scaleFactor=scale_factor,
                            minNeighbors=min_neighbors
                        )

    def __init__(self):
        front_classifier = self.HaarClassifier("haarcascade_frontalface_default.xml", "front", (255,0,0))
        profile_classifier = self.HaarClassifier("haarcascade_profileface.xml", "profile", (0, 255, 0))
        eye_classifier = self.HaarClassifier("haarcascade_eye.xml", "eye", (0, 0, 255))
        super(HaarFaceDetector, self).__init__([front_classifier, profile_classifier, eye_classifier])

    def detect_faces(self, frame: np.ndarray) -> None:
        for classifier in self.classifier:
            classifier.detect(frame)

        for classifier in self.classifier:
            for bounding_box in classifier.bounding_boxes:
                self.draw_bounding_box(frame, bounding_box, classifier.name, classifier.color)
