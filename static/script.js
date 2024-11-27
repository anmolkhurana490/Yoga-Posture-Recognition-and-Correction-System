// Constants and Configuration
const VIDEO_INTERVAL = 350; // interval for capturing frames in milliseconds
const RESULT_INTERVAL = 10000; // interval for giving text results (pose prediction, feedback)

// DOM Elements
const video = document.querySelector('.video-display');
const processed_video = document.querySelector('.processed_video_img');
const webcam_button = document.getElementById('webcam-btn');
const video_spinner = document.getElementById('video-spinner');
const posture_name_predicted = document.getElementById('posture-name');
const pred_posture_btn = document.getElementById('confirm-pose-btn');
const wait_button = document.getElementById('wait-btn');
const continue_button = document.getElementById('continue-btn');
const nextPosture_button = document.getElementById('next-posture-btn');
const posture_media_input = document.querySelector('input[name="posture-media-input"]');
const voice_button = document.getElementById('voice-input-btn');
const voiceListening_icon = document.getElementById('voice-listening');
const postureInput_text = document.querySelector('.posture-command-input');
const postureSubmit_btn = document.getElementById('command-submit-btn');

let processing_interval, totalElapsedTime;
let video_type;
let pose_num;

// Initialize Event Listeners
function initEventListeners() {
    // to start webcam when webcam button is clicked
    webcam_button.addEventListener('click', startWebCam);

    // to stop processing frames when video is ended
    video.addEventListener('ended', stopProcessingFrames);

    // to stop processing frames when wait button is clicked
    wait_button.addEventListener('click', () => {
        if (video.src || video.srcObject) {
            video.pause();
            stopProcessingFrames();
        }
    })

    // to start processing frames again when continue button is clicked
    continue_button.addEventListener('click', () => {
        if (video.src || video.srcObject) {
            video.play();
            startProcessingFrames(VIDEO_INTERVAL);
        }
    })

    // when video/image file is uploaded
    posture_media_input.addEventListener('change', handleFileUpload);

    // when user confirms predicted posture
    pred_posture_btn.addEventListener('click', () => {
        pred_posture_btn.disabled = true;
        fetch('/confirm_posture', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 'pose_num': pose_num })
        }).then(response => response.json())
            .then(data => {
                if (data.status == 'success') {
                    console.log('Posture Confirmed');
                    speakFeedback('Great job! Your posture is correct. Keep it up!');
                }
                else console.log(data.message);
            }).catch(error => {
                console.log(error);
            });
    });

    // to move to next posture
    nextPosture_button.addEventListener('click', () => {
        posture_name_predicted.innerText = '';
        selectPosture('');
    })

    // to set posture choosen by the user
    postureSubmit_btn.addEventListener('click', () => {
        let text = postureInput_text.value;
        if (!text) console.log('No text was entered');
        else selectPosture(text);
    });

    // listen to user's voice when voice butto is clicked
    voice_button.addEventListener('click', () => startListening(voice_button));
}

// to start the webcam video
async function startWebCam() {
    try {
        let stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        video.play();
        video_type = 'camera';
        video.addEventListener('loadeddata', () => startProcessingFrames(VIDEO_INTERVAL));
    } catch (error) {
        if(video_type == 'camera') stopProcessingFrames();
        console.log("Some error while accessing live video:", error);
    }
}
startWebCam();


// to capture a frame from video and send it to flask server
// where frameCounts is number of frames of video, after every RESULT_INTERVAL
function captureAndSendFrame(video, results, frameCounts) {
    // capturing frame from video
    let canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    let context = canvas.getContext('2d');
    context.drawImage(video, 0, 0);

    let frameData = canvas.toDataURL('image/jpeg');

    // sending the captured frame to flask server
    sendFileToServer(frameData, results, frameCounts);
}

// handle file upload and send the file to the backend
function handleFileUpload(event) {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
        video.srcObject = null;
        video.src = null;

        // show the spinner
        video_spinner.style.display = 'block';

        // send uploaded file to server
        if (file.type.match('image')) {
            stopProcessingFrames();
            sendFileToServer(e.target.result, true, 1); // will give results for this image only
        }
        else {
            video.src = e.target.result;
            video.play();
            video.muted = true;
            video_type = 'file';
            video.addEventListener('loadeddata', () => {
                startProcessingFrames(VIDEO_INTERVAL);
                // hide the spinner when video is loaded
                video_spinner.style.display = 'none';
            });
        }
    }
    // reading file in base64 format
    reader.readAsDataURL(file);
}

// to send the image (frame or uploaded file) to the flask server
function sendFileToServer(fileData, results, frameCounts) {
    let start = Date.now()
    fetch('/process_frame', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image: fileData, results: results, frameCounts: frameCounts })
    }).then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    }).then(data => {
        if (data.status == 'success') {
            processed_video.src = 'data:image/jpeg;base64,' + data.processed_image;
            if (data.pred_pose_num != null) {
                posture_name_predicted.innerText = `${data.pred_pose.sanskrit_name} (${data.pred_pose.english_name})`;
                speakFeedback(`Are you Performing ${data.pred_pose.sanskrit_name}, also known as ${data.pred_pose.english_name}`);
                pose_num = data.pred_pose_num;
                pred_posture_btn.disabled = false;
            }
            let end = Date.now();
            console.log(`Time taken: ${end - start}ms`);
        } else {
            console.log(data.message);
        }
        // hide the spinner once processing is done
        video_spinner.style.display = 'none';
    }).catch((error) => {
        console.log(error);
    })
}

function startProcessingFrames(interval) {
    if (!processing_interval) {
        totalElapsedTime = 0;
        processing_interval = setInterval(() => {
            // give results only after every RESULT_INTERVAL
            totalElapsedTime += interval;
            // console.log(totalElapsedTime)
            if (totalElapsedTime >= RESULT_INTERVAL) {
                totalElapsedTime -= RESULT_INTERVAL;
                console.log('Predicting the Pose');
                captureAndSendFrame(video, results = true, Math.floor(RESULT_INTERVAL/VIDEO_INTERVAL));
            }
            else captureAndSendFrame(video, results = false);
        }, interval);
    };
}

function stopProcessingFrames() {
    if (processing_interval) {
        clearInterval(processing_interval);
        processing_interval = null;
        totalElapsedTime = 0;
    }
}

// select new posture (either default or chosen by user)
function selectPosture(posture) {
    fetch('/select_posture', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: posture })
    }).then(response => response.json())
        .then(data => {
            if (data.status == 'success') {
                console.log('Posture selected');
                if (posture)
                    posture_name_predicted.innerText = `${data.pose_selected.sanskrit_name} (${data.pose_selected.english_name})`;
                pred_posture_btn.disabled = true;
            }
            else confirm(data.message);
        }).catch(error => {
            console.log(error);
        });
}


// to give speech feedback to user when text comes from server
function speakFeedback(text) {
    const synth = window.speechSynthesis;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-IN';

    utterance.rate = 0.9; // speeech speed
    utterance.pitch = 1; // speech pitch
    synth.speak(utterance);
}
// speakFeedback('Great job! Your posture is correct. Keep it up!');

// start listening to user voice input when voice button is clicked
function startListening(voice_button) {
    // show spinner and hide voice button
    voice_button.style.display = 'none';
    voiceListening_icon.style.display = 'block';

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-IN';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = (event) => {
        console.log('starts listening');
    }

    recognition.onresult = (event) => {
        // the most recent and confident result transcript
        const command = event.results[0][0].transcript.toLowerCase();
        postureInput_text.value = command;

        console.log('User command:', command);
    }

    recognition.onerror = (event) => {
        console.log("Error while listening:", event.error);
    }

    recognition.onend = () => {
        // Show voice button back and hide spinner when recognition ends
        voice_button.style.display = 'block';
        voiceListening_icon.style.display = 'none';
    };
    recognition.start();
}

document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
})