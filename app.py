import os
import cv2
import numpy as np
import streamlit as st
from tensorflow.keras.models import load_model
from info_page import show_info_page 

# Load the model
script_dir = os.path.dirname(os.path.abspath(__file__))
model_file_path = os.path.join(script_dir, 'models', 'model_1.h5')
model = load_model(model_file_path)

# Define image dimensions
img_length = 50
img_width = 50

# Define CSS styles dynamically based on theme settings
def generate_css(primary_color, secondary_background_color):
    css = f"""
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #ffffff; /* Set background color to white */
        }}
        .container {{
            display: flex;
            flex-direction: column; /* Change flex-direction to column */
            align-items: center; /* Align items to center */
            height: 100vh;
            justify-content: center; /* Vertically center content */
        }}
        .input-side, .output-side {{
            width: 80%; /* Adjust width to take up 80% of the container */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px; /* Add margin to separate input and output sides */
        }}
        .input-side {{
            background-color: {secondary_background_color}; /* Use secondary background color */
        }}
        .output-side {{
            background-color: #fff;
        }}
        .title {{
            font-size: 2rem;
            color: {primary_color}; /* Use primary color for title */
            margin-bottom: 10px; /* Reduce margin bottom for title */
        }}
        .button {{
            background-color: {primary_color}; /* Use primary color for buttons */
            color: #ffffff; /* Set text color to white */
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .button:hover {{
            background-color: #4786a5; /* Darken the background color on hover */
        }}
        .prediction {{
            font-size: 1.5rem;
            margin-bottom: 10px;
        }}
        .probability {{
            font-size: 1.5rem;
            margin-bottom: 20px;
        }}
        .output-image {{
            max-width: 400px; /* Set maximum width for output image */
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
    </style>
    """
    return css

def process_image(img):
    img = cv2.resize(img, (img_length, img_width))
    input_data = np.array([img], dtype=np.float32) / 255.0
    prediction = model.predict(input_data)
    result = "True" if prediction[0][0] > 0.5 else "False"
    return result, prediction[0][0]

def process_video(video_path, frame_number):
    video = cv2.VideoCapture(video_path)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = video.read()
    video.release()
    return frame

def main():
    # Get theme settings from config.toml
    primary_color = st.config.get_option("theme.primaryColor")
    secondary_background_color = st.config.get_option("theme.secondaryBackgroundColor")

    # Render CSS styles
    css = generate_css(primary_color, secondary_background_color)
    st.markdown(css, unsafe_allow_html=True)

    # Main content
    page = st.sidebar.selectbox("Go to", ["PolypDetect", "Info Page", "Comments", "QR Code"])

    if page == "PolypDetect":
        st.title('PolypDetect')
        st.write("""
        This website utilizes a Machine Learning Model to detect polyps in the colon.
        Polyps are clumps of cells that form on the lining of the colon.
        Polyps have been linked to high severity in patients who have an Inflammatory Bowl Disease (IBS).
        This website can help doctors to ensure that they identify all polyps, as some can be discrete.
        Please remember that the model is not perfect, so use it as a second method.
        """)

        # Input side
        st.markdown('<div class="input-side">', unsafe_allow_html=True)
        st.markdown('<h2 class="title" style="color: #4786a5;">Upload Image or Video</h2>', unsafe_allow_html=True)  # Mellow blue color
        uploaded_file = st.file_uploader("Choose an image or video...", type=["jpg", "jpeg", "png", "mp4", "mov"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Output side
        st.markdown('<div class="output-side">', unsafe_allow_html=True)
        if uploaded_file is not None:
            st.markdown('<h2 class="title" style="color: #4786a5;">Detection Result</h2>', unsafe_allow_html=True)  # Mellow blue color
            # Perform detection and display result
            if uploaded_file.type.startswith('image'):
                img = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
                if st.button('Detect Polyps'):  # Move the button outside of the condition
                    result, probability = process_image(img)
                    # Display the original image
                    st.markdown(f'<p class="prediction">Prediction: {result}</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="probability">Model Output: {probability}</p>', unsafe_allow_html=True)
                    st.image(img, caption='Original Image', width=500, output_format='JPEG')
            elif uploaded_file.type.startswith('video'):
                video_path = os.path.join(script_dir, 'temp_video.mp4')  # Temporarily save video as .mp4
                with open(video_path, 'wb') as f:
                    f.write(uploaded_file.read())
                frame_number = st.number_input("Frame Number", value=0, step=1)
                selected_frame = process_video(video_path, frame_number)
                st.image(cv2.cvtColor(selected_frame, cv2.COLOR_BGR2RGB), caption='Selected Frame', channels='RGB', width=500, output_format='JPEG')
                st.markdown('<h2 class="title" style="color: #4786a5;">Detection Result</h2>', unsafe_allow_html=True)  # Mellow blue color
                # Perform detection and display result
                result, probability = process_image(selected_frame)
                st.markdown(f'<p class="prediction">Prediction: {result}</p>', unsafe_allow_html=True)
                st.markdown(f'<p class="probability">Probability: {probability}</p>', unsafe_allow_html=True)
                
    elif page == "Info Page":
        show_info_page(primary_color, secondary_background_color)  # Call the show_info_page function with theme colors

    elif page == "QR Code":
        st.title("QR Code")
        qr_image_path = "polypdetect_qr_code.png"
        st.image(qr_image_path, caption="Please use the QR code to send this app to people you know!", width=500)

    elif page == "Comments":
        st.title('Comments')
        st.write("""
        Leave your comments and feedback below:
        """)

        # Add comment box
        user_name = st.text_input("Your Name", max_chars=50)
        comment = st.text_area("Your Comment", max_chars=200)
        if st.button("Submit"):
            if len(comment.strip()) > 0:
                # Add the comment to the list
                with open("comments.txt", "a") as file:
                    file.write(f"{user_name}: {comment}\n")
                st.success("Comment submitted successfully!")
                comment = ""
            else:
                st.warning("Please enter a comment before submitting.")
        
        # Display comments
        st.write("### Comments:")
        comments = []
        with open("comments.txt", "r") as file:
            comments = file.readlines()
        if comments:
            for comment_text in comments:
                # Split comment into name and message parts
                parts = comment_text.split(":", 1)
                if len(parts) == 2:
                    name, comment_msg = parts
                    # Display the name above the comment
                    st.write(f"**{name.strip()}**")
                    st.write(f"{comment_msg.strip()}")
                else:
                    st.write(comment_text.strip())

        # Add button to delete all comments
        if st.button("Delete All Comments"):
            # Clear the comments file
            with open("comments.txt", "w") as file:
                file.truncate(0)
            st.success("All comments deleted successfully!")
            # Reset the page
            st.experimental_rerun()

if __name__ == "__main__":
    main()
