# Multi-Signal Viewer
![Application Overview](Images/overview.png "Overview of Multi-Signal Viewer")

## Overview
The Multi-Signal Viewer is a powerful desktop application that provides many signal analysis capabilities through a user-friendly interface. The application features four distinct operational modes: **Default Mode**, **Real-Time Mode**, **Glowing Mode**, and **Non-Rectangular Graph Mode**.

---

## Features

### 1. Default Mode
- **Dual Viewer Interface**:
  - Two synchronized signal viewers for simultaneous signal analysis
  - Independent signal loading in each viewer
  - Ability to transfer signals between viewers


- **Playback Controls**:
  - Play, pause, and rewind functionality
  - Adjustable playback speed
  - Zoom and pan capabilities
- **Signal Customization**:
  - Adjustable colors and names for each signal
  - Vertical and horizontal scaling via sliders
  - Show/hide signal options
- **Viewer Synchronization**:
  - Option to link viewers for synchronized control
  - Matching time scales and playback states

### 2. Real-Time Mode
- **API Integration**:
  - Connect to live data sources via API link
  - Real-time signal visualization
  - Continuous data monitoring
- **Dynamic Controls**:
  - Play and pause functionality
  - Live data streaming display

### 3. Glowing Mode
- **Signal Selection**:
  - Highlight and select specific signal segments
  - Precise control over selection boundaries
- **Segment Manipulation**:
  - Reorder selected segments freely
  - Adjust segment parameters(Interpolation order, gap or overlap)
  - Customize glowing effects
- **PDF Report Generation**:
  - Add modified segments to report
  - Generate and export professional PDF reports

### 4. Non-Rectangular Graph Mode
- **Specialized Visualization**:
  - Display of non-rectangular signal patterns
- **Interactive Features**:
  - Play/pause functionality
  - Speed control
  - Color customization
---

## How to Use

### Default Mode
1. Launch the application.
2. Click "Browse" to load signals into either viewer.
3. Use playback controls to analyze signals:
   - Play/Pause button
   - Speed slider
   - Zoom controls
4. Customize signal display:
   - Change colors
   - Adjust scaling
   - Modify names
5. Toggle viewer synchronization as needed.

### Real-Time Mode
1. Switch to Real-Time Mode.
2. Enter the API link for your data source.
4. Monitor incoming signals with play and pause control.

### Glowing Mode
1. Load your signals.
2. Select segments:
   - Click glow and drag to highlight
   - Adjust selection boundaries
3. Manipulate segments:
   - Drag to reorder
   - Apply effects
4. Generate reports:
   - Add segments to report
   - Export as PDF.

### Non-Rectangular Graph Mode
1. Switch to Non-Rectangular Graph Mode.
3. Use specialized controls:
   - Adjust view parameters
   - Control playback
   - Customize display.

---

## Installation

### Prerequisites
- Python 3.x
- Git (for cloning repository)

### Setup Instructions
```bash
# Clone the repository
git clone https://github.com/Mostafaali3/DSP-Signal-Viewer.git

# Navigate to project directory
cd multi-signal-viewer

# Install required packages
pip install -r requirements.txt

# Run the application
python main.py
```

---

## Dependencies

The Multi-Signal Viewer relies on the following technologies and libraries to deliver its robust functionality:

| **Dependency**       | **Description**                                       |
|-----------------------|-------------------------------------------------------|
| Python 3.x           | Core programming language.                            |
| NumPy                | Numerical computations for signal processing.         |
| Pandas               | Data manipulation and analysis.                       |
| SciPy                | Advanced scientific computing and interpolation.      |
| PyQt5                | GUI framework for building desktop applications.      |
| PyQtGraph            | Fast plotting and 2D/3D visualization in PyQt.        |
| Validators           | URL validation for real-time API integration.         |
| Requests             | API integration for fetching real-time data.          |
| ReportLab            | PDF generation for exporting reports.                 |


---

## Contributors

Meet the amazing team behind the Multi-Signal Viewer:

| **Name**            | **Role**                | **Contributions**                                     |
|---------------------|-------------------------|------------------------------------------------------|
| Kareem Abdel Nabi   | Lead Developer          | Core architecture, signal processing, and UI design. |
| John Doe            | API Specialist          | Real-time mode and API integration.                 |
| Jane Smith          | Visualization Expert    | Non-rectangular graph rendering and visual design.  |
| Ahmed Ali           | Documentation Writer    | Comprehensive documentation and tutorials.          |
| Emily Clark         | QA Engineer             | Ensuring application quality and user experience.   |

Your feedback and contributions are always welcome! Feel free to fork the repository and make your improvements.



