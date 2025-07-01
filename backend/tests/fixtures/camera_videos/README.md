# Dynamic Camera Videos - Phase 2

This directory contains video fixtures and recordings for Phase 2 dynamic camera stream testing.

## Directory Structure

```
camera_videos/
├── README.md                    # This file
├── recorded_streams/            # Recorded streams from dynamic generation
│   ├── indoor_tracking.mp4      # Indoor person tracking scenario
│   ├── outdoor_vehicle.mp4      # Outdoor vehicle scenario
│   ├── sports_ball.mp4          # Sports ball tracking scenario
│   ├── warehouse.mp4            # Warehouse inspection scenario
│   └── emergency.mp4            # Emergency response scenario
├── sample_outputs/              # Sample output videos for testing
│   ├── 30fps_640x480.mp4        # Standard resolution/fps test
│   ├── 24fps_800x600.mp4        # High resolution test
│   └── 15fps_320x240.mp4        # Low resolution test
└── reference_videos/            # Reference videos for comparison
    ├── real_drone_indoor.mp4    # Real Tello footage for comparison
    └── real_drone_outdoor.mp4   # Real Tello footage for comparison
```

## Phase 2 Video Generation

The dynamic camera system generates videos in real-time with:

- **Multiple tracking objects**: Person, vehicle, ball, box, animal
- **Dynamic movement patterns**: Linear, circular, sine wave, random walk
- **Configurable scenarios**: Indoor, outdoor, warehouse, emergency
- **Real-time frame rate control**: 15-60 FPS support
- **Multiple resolutions**: 320x240 to 1280x720

## Usage for Testing

### Recording Dynamic Streams

```python
from core.virtual_camera import create_sample_scenario

# Create and start a stream
stream = create_sample_scenario()
stream.start_stream()

# Record frames for testing
frames = []
for i in range(300):  # 10 seconds at 30fps
    frame = stream.get_frame()
    if frame is not None:
        frames.append(frame)
    time.sleep(1/30)

stream.stop_stream()
```

### Scenario-based Recording

```python
from config.camera_config import DynamicCameraScenarios, configure_stream_from_scenario
from core.virtual_camera import VirtualCameraStream

# Use pre-configured scenario
scenario = DynamicCameraScenarios.get_indoor_tracking_scenario()
stream = VirtualCameraStream(scenario.width, scenario.height, scenario.fps)
configure_stream_from_scenario(stream, scenario)

# Record scenario
stream.start_stream()
# ... recording logic
stream.stop_stream()
```

## Video Specifications

### Generated Video Properties
- **Codec**: H.264 (when saved to MP4)
- **Color Space**: BGR (OpenCV default)
- **Bit Depth**: 8-bit
- **Frame Format**: Uncompressed numpy arrays during generation

### Quality Settings
- **Standard Quality**: 640x480@30fps for general testing
- **High Quality**: 800x600@30fps for detailed analysis  
- **Performance**: 320x240@15fps for resource-constrained testing

## Integration with Phase 1 & 3

This Phase 2 video generation system is designed to integrate with:

- **Phase 1**: DummyTello class will use these videos for camera stream simulation
- **Phase 3**: Physical simulation will modify these videos based on drone position/orientation

## File Naming Convention

```
{scenario}_{resolution}_{fps}fps_{timestamp}.mp4
```

Examples:
- `indoor_tracking_640x480_30fps_20240630.mp4`
- `warehouse_800x600_24fps_20240630.mp4`
- `emergency_320x240_15fps_20240630.mp4`

## Notes

- Videos are generated in real-time and can be recorded for later playback
- The dynamic system supports both live streaming and pre-recorded playback modes
- Frame timing is precisely controlled for realistic drone camera simulation
- Background patterns include subtle grid lines for depth perception
- All objects include realistic movement physics and boundary checking