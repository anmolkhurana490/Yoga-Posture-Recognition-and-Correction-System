from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import utils # contains our all model processing tasks and other utilities
import sqlite3  # SQLite for user database
import cv2
import time


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# SQLite database for User Authentication
userdb_path = 'data/users.db'

def init_db():
    conn = sqlite3.connect(userdb_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

yoga_poses = eval(utils.read_file('data/yoga_poses.json'))

# Define function for processing image using Mediapipe and showing Body Landmarks
@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        image_data = request.get_json()['image']

        # Decode base64 image
        start_time = time.time()
        frame = utils.decode_image(image_data)
        end_time = time.time()
        print(f"decode took {end_time - start_time:.4f} seconds")

        if frame is None:
            return jsonify({'status': 'error', 'message': 'Failed to decode image'}), 400
        
        # Convert to RGB frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Generate keypoints and landmarks
        keypoints, landmarks = utils.generate_keypoints(rgb_frame)
        if keypoints is None:
            return jsonify({'status': 'success', 'processed_image': image_data})

        # print("Extracted Keypoints Shape:", keypoints.shape)
        # Append keypoints to recent poses
        session['recent_poses'].append(keypoints)

        # Pose Prediction
        if session['current_pose_num'] is None:
            if request.get_json()['results']:
                frame_counts = request.get_json().get('frameCounts', 1)
                recent_poses_length = len(session['recent_poses'])
                required_frames = (frame_counts * 3) // 2

                if required_frames < recent_poses_length:
                    # get last required recent frames
                    keypoints_batch = session['recent_poses'][-required_frames:]
                    session['recent_poses'] = session['recent_poses'][frame_counts:]
                else:
                    keypoints_batch = session['recent_poses']

                ypred = int(utils.model_predict_pose(keypoints_batch))
                pred_pose = yoga_poses[ypred]
            else:
                ypred = None
                pred_pose = None
        else:
            ypred = None
            pred_pose = None

        # draw body landmarks on rgb_frame using keypoints
        if landmarks:
            utils.draw_landmarks(rgb_frame, landmarks)

        # back to BGR frame
        processed_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        # Encode back to base64 image
        start_time = time.time()
        processed_image = utils.encode_image(processed_frame)
        end_time = time.time()
        print(f"encode took {end_time - start_time:.4f} seconds")
        
        return jsonify({'status': 'success', 'processed_image': processed_image, 'pred_pose_num': ypred, 'pred_pose': pred_pose})
    except Exception as e:
        app.logger.error(f"Error processing frame: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Home Page (Requires Login)
@app.route('/')
def home():
    # if 'username' not in session:
    #     return redirect(url_for('login'))
    # return render_template('index.html', username=session['username'])
    return render_template('index.html')

# Trying another Posture
@app.route('/confirm_posture', methods=['POST'])
def confirmPosture():
    pose_num = request.get_json()['pose_num']
    session['current_pose_num'] = pose_num
    print('confirmed')
    return jsonify({'status': 'success'})

# Trying another Posture
@app.route('/select_posture', methods=['POST'])
def selectPosture():
    pose_prompted = request.get_json()['text'].lower()

    if not pose_prompted: # try new posture
        session['current_pose_num'] = None
        return jsonify({'status': 'success', 'pose_num': None, 'pred_pose': None})
    else:
        for i, pose in enumerate(yoga_poses):
            if pose['sanskrit_name'].lower() == pose_prompted or pose['english_name'].lower() == pose_prompted:
                session['current_pose_num'] = i
                return jsonify({'status': 'success', 'pose_num': i, 'pose_selected': pose})
        return jsonify({'status': 'error', 'message': 'Unknown Yoga Posture Name! Please Enter Again'})

# Sign-Up Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insert new user into the database
        try:
            conn = sqlite3.connect(userdb_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another one.', 'danger')

    return render_template('sign_up.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(userdb_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('get_started'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Check Posture
@app.route('/get_started', methods=['GET'])
def get_started():
    session["recent_poses"] = []
    session["current_pose_num"] = None
    if 'username' not in session or not session['username']:
        return redirect(url_for('login'))
    return render_template('posture_result.html');

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import utils # contains our all model processing tasks and other utilities
import sqlite3  # SQLite for user database
import cv2
import time


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# SQLite database for User Authentication
userdb_path = 'data/users.db'

def init_db():
    conn = sqlite3.connect(userdb_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

yoga_poses = eval(utils.read_file('data/yoga_poses.json'))

# Define function for processing image using Mediapipe and showing Body Landmarks
@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        image_data = request.get_json()['image']

        # Decode base64 image
        start_time = time.time()
        frame = utils.decode_image(image_data)
        end_time = time.time()
        print(f"decode took {end_time - start_time:.4f} seconds")

        if frame is None:
            return jsonify({'status': 'error', 'message': 'Failed to decode image'}), 400
        
        # Convert to RGB frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Generate keypoints and landmarks
        keypoints, landmarks = utils.generate_keypoints(rgb_frame)
        if keypoints is None:
            return jsonify({'status': 'success', 'processed_image': image_data})

        # print("Extracted Keypoints Shape:", keypoints.shape)
        # Append keypoints to recent poses
        session['recent_poses'].append(keypoints)

        # Pose Prediction
        if session['current_pose_num'] is None:
            if request.get_json()['results']:
                frame_counts = request.get_json().get('frameCounts', 1)
                recent_poses_length = len(session['recent_poses'])
                required_frames = (frame_counts * 3) // 2

                if required_frames < recent_poses_length:
                    # get last required recent frames
                    keypoints_batch = session['recent_poses'][-required_frames:]
                    session['recent_poses'] = session['recent_poses'][frame_counts:]
                else:
                    keypoints_batch = session['recent_poses']

                ypred = int(utils.model_predict_pose(keypoints_batch))
                pred_pose = yoga_poses[ypred]
            else:
                ypred = None
                pred_pose = None
        else:
            ypred = None
            pred_pose = None

        # draw body landmarks on rgb_frame using keypoints
        if landmarks:
            utils.draw_landmarks(rgb_frame, landmarks)

        # back to BGR frame
        processed_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)

        # Encode back to base64 image
        start_time = time.time()
        processed_image = utils.encode_image(processed_frame)
        end_time = time.time()
        print(f"encode took {end_time - start_time:.4f} seconds")
        
        return jsonify({'status': 'success', 'processed_image': processed_image, 'pred_pose_num': ypred, 'pred_pose': pred_pose})
    except Exception as e:
        app.logger.error(f"Error processing frame: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Home Page (Requires Login)
@app.route('/')
def home():
    # if 'username' not in session:
    #     return redirect(url_for('login'))
    # return render_template('index.html', username=session['username'])
    return render_template('index.html')

# Trying another Posture
@app.route('/confirm_posture', methods=['POST'])
def confirmPosture():
    pose_num = request.get_json()['pose_num']
    session['current_pose_num'] = pose_num
    print('confirmed')
    return jsonify({'status': 'success'})

# Trying another Posture
@app.route('/select_posture', methods=['POST'])
def selectPosture():
    pose_prompted = request.get_json()['text'].lower()

    if not pose_prompted: # try new posture
        session['current_pose_num'] = None
        return jsonify({'status': 'success', 'pose_num': None, 'pred_pose': None})
    else:
        for i, pose in enumerate(yoga_poses):
            if pose['sanskrit_name'].lower() == pose_prompted or pose['english_name'].lower() == pose_prompted:
                session['current_pose_num'] = i
                return jsonify({'status': 'success', 'pose_num': i, 'pose_selected': pose})
        return jsonify({'status': 'error', 'message': 'Unknown Yoga Posture Name! Please Enter Again'})

# Sign-Up Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insert new user into the database
        try:
            conn = sqlite3.connect(userdb_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()

            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose another one.', 'danger')

    return render_template('sign_up.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(userdb_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('get_started'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

# Check Posture
@app.route('/get_started', methods=['GET'])
def get_started():
    session["recent_poses"] = []
    session["current_pose_num"] = None
    if 'username' not in session or not session['username']:
        return redirect(url_for('login'))
    return render_template('posture_result.html');

if __name__ == '__main__':
    app.run(debug=True)
