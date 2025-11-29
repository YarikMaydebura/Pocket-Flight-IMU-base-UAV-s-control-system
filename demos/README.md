# PocketFlight Demos

This directory contains demonstration videos and materials showing PocketFlight in action.

## Demo Videos

### 1. System Architecture Explanation

**Description**: Detailed explanation of the system structure, components, and data flow.

**YouTube Link**: [TO BE ADDED]

**Content**:
- System overview
- Component breakdown
- ROS node architecture
- Data flow explanation
- Launch file structure

**Duration**: ~25 seconds

**Original File**: `Explaining_about_structure.mp4`

---

### 2. System Launch and Operation

**Description**: Complete walkthrough of launching the PocketFlight system and flying the drone using smartphone IMU control.

**YouTube Link**: [TO BE ADDED]

**Content**:
- Starting SensorServer app on smartphone
- Launching ROS system
- Gazebo simulation startup
- Drone takeoff sequence
- IMU-based flight control demonstration
- Real-time monitoring

**Duration**: ~2 minutes

**Original File**: `Launching.mp4`

---

## Screenshots

### System Overview

![System Diagram](../docs/images/system_diagram.png)
*Coming soon: Architecture diagram*

### Gazebo Simulation

![Gazebo View](../docs/images/gazebo_simulation.png)
*Coming soon: Screenshot of drone in Gazebo*

### Smartphone Control

![Phone IMU Control](../docs/images/phone_control.png)
*Coming soon: Photo of smartphone controller interface*

### Flood Detection

![Flood Detection](../docs/images/flood_detection.png)
*Coming soon: Flood detection visualization*

---

## How to Upload Your Demos

### For Video Maintainers

If you have access to the original video files and want to upload them to YouTube:

1. **Upload to YouTube**:
   - Create a YouTube channel (if you don't have one)
   - Upload `Explaining_about_structure.mp4`
   - Upload `Launching.mp4`
   - Set videos to "Public" or "Unlisted"

2. **Update This README**:
   - Replace `[TO BE ADDED]` with your YouTube links
   - Format: `https://www.youtube.com/watch?v=VIDEO_ID`

3. **Optional: Create Playlist**:
   - Create a YouTube playlist called "PocketFlight Demos"
   - Add all demo videos to the playlist
   - Share the playlist link in the main README.md

### Video Editing Tips

If you want to edit the videos before uploading:

- **Recommended Software**:
  - OpenShot (free, open-source)
  - Kdenlive (free, open-source)
  - DaVinci Resolve (free version available)

- **Suggested Edits**:
  - Add title cards at the beginning
  - Add captions/subtitles
  - Highlight key moments
  - Add background music (use royalty-free music)
  - Include links to GitHub repository

---

## Creating New Demos

### Recording Tips

**Screen Recording**:
```bash
# Use SimpleScreenRecorder (Ubuntu)
sudo apt install simplescreenrecorder
```

**Terminal Recording**:
```bash
# Use asciinema for terminal demos
sudo apt install asciinema
asciinema rec demo.cast
```

**What to Demonstrate**:

1. **Installation Process**
   - Show key installation steps
   - Highlight common issues and solutions

2. **Basic Flight**
   - Takeoff
   - Forward/backward movement
   - Left/right movement
   - Rotation
   - Hovering
   - Landing

3. **Advanced Features**
   - Flood detection in action
   - Real-time monitoring
   - Parameter tuning
   - Multi-drone coordination (if implemented)

4. **Troubleshooting**
   - Network connection setup
   - Common errors and fixes

---

## Demo Checklist

Before recording a demo:

- [ ] Clean environment (close unnecessary windows)
- [ ] Test all components working
- [ ] Prepare script or outline
- [ ] Check audio/screen capture settings
- [ ] Have backup plan for technical issues

During recording:

- [ ] Speak clearly and explain what you're doing
- [ ] Show terminal outputs
- [ ] Demonstrate smooth flight control
- [ ] Show both Gazebo and real world (if available)
- [ ] Mention key features and benefits

After recording:

- [ ] Edit for clarity and brevity
- [ ] Add captions/annotations
- [ ] Test video playback
- [ ] Upload and update links

---

## Community Contributions

Have you created a demo using PocketFlight? We'd love to feature it!

**Submit Your Demo**:
1. Upload your video to YouTube
2. Open an issue on GitHub with:
   - Video title
   - YouTube link
   - Brief description
   - What features it demonstrates

3. We'll review and potentially feature it here!

---

## Questions?

If you have questions about the demos or want to contribute new ones, please:
- Open an issue on GitHub
- Contact the maintainers
- Check the [Contributing Guide](../CONTRIBUTING.md)

---

**Note**: Videos are hosted externally (YouTube) to keep the repository size manageable. Original video files are not included in this repository.
