# Arduino

Low-level software for ROV. Takes JSON key:value pairs from [Raspberry Pi](https://github.com/ncl-ROVers/raspberry-pi) and acts on them accordingly.

## Installation

To install this code on an Arduino you first need to run the appropriate setup script (in arduino-setup ) to assign an ID to the Arduino. This ID dictates the functionality as follows:

* Ard_T: Control for Thrusters on main ROV body
* Ard_A: Control for Arm and other outputs on main ROV body
* Ard_M: Control for any Micro ROV devices
* Ard_I: Sending sensor data back up to surface

After running the setup script, flash arduino-main to the device.

## Expected behaviour

### Arduino T

This Arduino is for controlling the output devices on the main ROV body.

Values in the range 1100 to 1900 will be accepted for Thruster or Motor control where 1100 is full reverse, 1500 is stopped, and 1900 is full forward. However, it's not advised to use values lower than 1350 or higher than 1650 for arm rotation or fish box due to the gearing on these.

Thrusters are given an ID which describes their position on the ROV. Motors are named in a similar fashion.

| Pin | JSON ID | Description                                 |
|-----|---------|---------------------------------------------|
| 2   | Thr_FP  | Forward Port Thruster (front right)         |
| 3   | Thr_FS  | Forward Starboard Thruster (front left)     |
| 4   | Thr_AP  | Aft Port Thruster (back left)               |
| 5   | Thr_AS  | Aft Starboard Thruster (back right)         |
| 6   | Thr_TFP | Top Forward Port Thruster (front right)     |
| 7   | Thr_TFS | Top Forward Starboard Thruster (front left) |
| 8   | Thr_TAP | Top Aft Port Thruster (back left)           |
| 9   | Thr_TAS | Top Aft Starboard Thruster (back right)     |
| 10  | Mot_R   | Arm Rotation Motor                          |
| 11  | Mot_G   | Arm Gripper Motor                           |
| 12  | Mot_F   | Fish Box Opening Motor                      |

### Arduino M

This Arduino is for controlling the thruster on the Micro ROV.

Values in the range 1100 to 1900 will be accepted for Thruster or control where 1100 is full reverse, 1500 is stopped, and 1900 is full forward.

Thrusters are given an ID which describes their position on the ROV.

| Pin | JSON ID | Description                                 |
|-----|---------|---------------------------------------------|
| 3   | Thr_M   | Micro ROV Thruster                          |


### Ret Codes

| Return Code   | Description                                               |
|---------------|-----------------------------------------------------------|
|    0          | No Error                                                  |
|    1          | Outputs Halted.                                           |
|    2          | Left limit hit. Motor stopped                             |
|    3          | Right limit hit. Motor stopped                            |
|    4          | Arduino Booting                                           |
|   -1          | Incoming value out of range                               |
|   -2          | IMU BNO055 not found. Check wiring                        |
|   -3          | IMU BNO055 not initialised                                |
|   -4          | Depth Sensor not found. Check wiring                      |
|   -5          | Depth sensor not initialised                              |
|   -6          | getOutput method doesn't have an option for Arduino       |
|   -7          | getInput method doesn't have an option for Arduino        |
|   -8          | Output device ID is not valid                             |
|   -9          | Input device ID is not valid                              |
|   -10         | Can't call stopOutputs from a non-output Arduino          |
|   -11         | JSON parsing failed                                       |
|   -12         | Arduino ID not set up.                                    |
|   -13         | No message received in the last second. Outputs Halted.   |
|   -14         | RTD High Threshold                                        |
|   -15         | RTD Low Threshold                                         |
|   -16         | REFIN- > 0.85 x Bias                                      |
|   -17         | REFIN- < 0.85 x Bias - FORCE- open                        |
|   -18         | RTDIN- < 0.85 x Bias - FORCE- open                        |
|   -19         | Under/Over voltage                                        |
|   -20         | Sonar not initialised                                     |
|   -21         | Sonar could not update                                    |
|   -22         | Sonar not connected                                       |
|   -23         | Index not valid for setting sensor parameter              |

