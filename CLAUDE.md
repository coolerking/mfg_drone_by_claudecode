# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MFG drone automatic following system that uses Tello EDU drones to automatically track and film moving targets. The system consists of three main components:

1. **Backend API** (Raspberry Pi 5) - Drone control, video processing, object recognition and tracking
2. **Admin Frontend** (Windows PC) - Object recognition model training, drone control, tracking start/stop
3. **General User Frontend** (Windows PC) - Real-time video display from drone

## Technology Stack

- **Backend**: Python 3.11 + FastAPI + djitellopy (Raspberry Pi OS Lite 64bit)
- **Frontend Systems**: Python 3.11 + Flask (Windows 11 Pro 64bit)
- **Target Hardware**: Tello EDU drone
- **Client Devices**: iPad Air (Safari browser)

## Architecture

The system implements a distributed architecture where:
- Raspberry Pi 5 serves as the main controller receiving drone camera feeds, running AI models, and sending movement commands
- Two Flask frontends run on the same Windows PC (admin and user interfaces)
- All devices operate on the same home network with internet connectivity
- Real-time video streaming and object tracking coordination between components

## Key Requirements

- Object learning and recognition capabilities
- Real-time drone positioning to keep target centered in frame
- Near real-time camera feed display via web application
- Network operation within home router environment

## Development Notes

This project is in early development stage. When implementing:
- Follow the specific technology versions listed in the README (Python 3.11, specific OS versions)
- Consider the hardware constraints of Raspberry Pi 5 for AI processing
- Ensure real-time performance requirements for drone control and video streaming
- Implement proper network communication protocols between the three system components