## Thrust Stand User Interface

**Description**

Python GUI supporting Thrust Stand testing in a wind tunnel. Used alongside Arduino microcontroller and interacting with Arduino Serial Monitor for bilateral communication.

**Required Libraries**
- serial
- pygame-ce
- math (standard library)
- pandas

To install the third party python librarys, run: 
    pip install serial

**Resource Files**

The game uses the following resource files. Ensure they are in the same directory as your script:
- plane-img.png (image of plane)
- wind-icon.png (image of wind gust)
- Helvetica-Bold.ttf (typographic font type file)
- Helvetica.ttf (typographic font type file)
- Oxanium-Bold.ttf (typographic font type file)

**Required Physical Systems**
- Current/Voltage sensor
- Airspeed sensor
- RPM sensor
- Thrust sensor / load cell
- Motor + ESC + Propeller
- Arduino Microcontroller (Arduino UNO R3 used)

Note: the use of different systems, both physical and in code, may result in unexpected results and errors. Before using a different system, ensure that all systems work indepently and with Arduino Serial monitor.

**How to Use**

Steps: 
1) First begin by connecting battery in sensor system
2) Verify max RPM and Thrust are accurately depicted in code: Line 134 for RPM, Line 379 for Thrust
3) Run File
4) To start recording, press Power button
5) To change motor throttle, click on white box above Throttle change button (below Throttle value)
6) Input throtle value and press Push Throttle Button, button will need to be re-armed for another push
7) To save all values to CSV file, press Log button, button will need to be re-armed to relog

Note: 
- Throttle value should reflect instantly; if not, stop run immediately to avoid potentially dangerous command delay times
- Log button records all values from beginning to time of click in CSV file, saved in the same directory as the python file
