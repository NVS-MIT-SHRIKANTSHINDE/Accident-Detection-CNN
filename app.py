from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import tensorflow as tf
import cv2


from base64 import b64encode

app = Flask(__name__)
app.jinja_env.filters['b64encode'] = b64encode

# Load the trained model
model = tf.keras.models.load_model('trained_model.h5')
 
 
# Define the function to predict a single frame
def predict_frame(img):
    img_array = tf.keras.utils.img_to_array(img)
    img_batch = np.expand_dims(img_array, axis=0)
    prediction = (model.predict(img_batch) > 0.5).astype("int32")
    if(prediction[0][0] == 0):
        return("Accident Detected")
    else:
        return("No Accident")

# Define the route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Define the route for the form submission
@app.route('/', methods=['POST'])
def upload():
    # Get the input video file
    video = request.files['video']

    # Save the video file to a temporary location
    video_path = 'video.mp4'
    video.save(video_path)
    # Open the video file and read the frames
    c = 1
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        grabbed, frame = cap.read()
        if c % 50 == 0:
            print(c)
            if not grabbed:
                break
            resized_frame = tf.keras.preprocessing.image.smart_resize(frame, (250, 250), interpolation='bilinear')
            prediction = predict_frame(resized_frame)
            print(prediction)
            frames.append((frame, prediction))
            if(prediction == 'Accident Detected'):
                result = predict_frame(resized_frame)
               
                break
        c = c + 1 
 
    cap.release()
    if(prediction == 'Accident Detected'):
        # Convert the last frame to JPEG format
        last_frame, _ = frames[-1]
        _, jpeg_data = cv2.imencode('.jpg', last_frame)
        jpeg_url = 'data:image/jpeg;base64,' + b64encode(jpeg_data).decode('utf-8')
        
        import tempfile
        
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        temp_file.write(jpeg_data) 
         
         
         
        temp_file.close()
        # import pywhatkit as whatsapp
        # # Send message and image on WhatsApp using PyWhatKit
        # whatsapp.sendwhats_image('+918459289424',temp_file.name ,'accident detected at '+ str(c)+" th frame " )
        # import os
        # # Delete the temporary file
        # os.unlink(temp_file.name)
    
   
    # Render the template with the results
        return render_template('result.html', result=result, frame_url=jpeg_url)
    else :
         return render_template('result.html', result=0)


       

if __name__=='__main__':
    app.run() 
    