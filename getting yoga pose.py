import json
import os

poses={}

with open("yoga_pose_classes.txt", 'r') as  file:
    for line in file.readlines():
        names = line.split('-')
        poses[names[0].strip()] = {
            "other name": '-'.join(names[1:]).strip()
        }

with open("yoga_poses.json", 'w') as file:
    json.dump(poses, file)

print("JSON file saved successfully!")

for pose_name in poses.keys():
    if not os.path.exists(f"yoga_posture_dataset/{pose_name}"):
        os.mkdir(f"yoga_posture_dataset/{pose_name}")

print("Yoga Pose dirs created successfully")
