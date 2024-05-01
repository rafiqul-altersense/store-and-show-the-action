from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import json
import cv2
import numpy as np
from starlette.responses import FileResponse

from selenium.webdriver.common.by import By

app = FastAPI()

# Global variable to store actions
actions = []
recorded_frames = []

# Function to log Selenium actions
def log_action(action_type, *args):
    actions.append((action_type, args))

# Function to initialize the Selenium driver
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Function to perform Selenium actions
def perform_actions():
    driver = initialize_driver()
    driver.get("https://www.google.com")

    # take screenshot and store it as numpy array so that we can use it later for make video
    screenshot = driver.get_screenshot_as_png()
    screenshot = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)
    recorded_frames.append(screenshot)

    time.sleep(2)  # Wait for page to load
    
    # Example actions: searching for a term on Google
    # search_box = driver.find_element_by_name('q')
    search_box = driver.find_element(by=By.NAME, value='q')

    search_box.send_keys("codewithrafiq")
    
    # take screenshot and store it as numpy array so that we can use it later for make video
    screenshot = driver.get_screenshot_as_png()
    screenshot = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)
    recorded_frames.append(screenshot)

    search_box.send_keys(Keys.RETURN)
    time.sleep(2)  # Wait for search results to load
    
    # Example action: clicking on the first search result link
    # first_link = driver.find_element_by_css_selector('#search .g a')
    first_link = driver.find_element(by=By.CSS_SELECTOR, value='#search .g a')
    first_link.click()

    # take screenshot and store it as numpy array so that we can use it later for make video
    screenshot = driver.get_screenshot_as_png()
    screenshot = cv2.imdecode(np.frombuffer(screenshot, np.uint8), 1)
    recorded_frames.append(screenshot)

    time.sleep(5)  # Wait for page to load
    
    driver.quit()

# Function to generate video from captured frames
def generate_video(frames):
    height, width, _ = frames[0].shape
    # save images also
    for i, frame in enumerate(frames):
        cv2.imwrite(f'frame_{i}.png', frame)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter('selenium_actions.mp4', fourcc, 10.0, (width, height))

    for frame in frames:
        video_writer.write(frame)

    video_writer.release()

# Route to perform actions and store the interaction
@app.get("/store_interaction")
def store_interaction():
    global actions
    actions = []  # Clear the stored actions
    perform_actions()
    with open('selenium_actions.json', 'w') as f:
        json.dump(actions, f)  # Save the actions to a JSON file
    return {"message": "Interaction stored successfully"}

# Route to show stored interaction as video
@app.get("/show_interaction_video")
def show_interaction_video():
    # Generate video from captured frames
    generate_video(recorded_frames)
    
    # Return the generated video file
    return FileResponse("selenium_actions.mp4", media_type="video/mp4")


# / hello world
@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", port=4004, reload=True, workers=1)
