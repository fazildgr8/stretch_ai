# Dex Teleop Example App

This is a modified version of [stretch dex teleop](https://github.com/hello-robot/stretch_dex_teleop) which collects data for use training [Dobb-E](https://dobb-e.com/) policies.

## Installation

Follow the [Stretch dex teleop](https://github.com/hello-robot/stretch_dex_teleop) instructions to calibrate your camera and make sure things are working.

Webcam should be plugged into your workstation or laptop (``leader pc'')


## Running


### On the Robot

These steps replace the usual server *for now*.

Start the image server:
```
python -m stretch.app.dex_teleop.send_d405_images -r
```

Start the follower:
```
python -m stretch.app.dex_teleop.follower
```

### On the Leader PC

Run the leader script:

```bash
python -m stretch.app.dex_teleop.leader
```

A window should appear, showing the view from the end effector camera. This should be roughly real time; if not, improve your network connection somehow. Press space to start and stop recording demonstrations.


When collecting data, you should set task, user, and environment, instead of just using the default for all of the above. For example:
```bash
python -m stretch.app.dex_teleop.leader --task grasp_cup --user Chris --env ChrisKitchen1
```

Collect a few demonstrations per example task/environment that you want to test in.

