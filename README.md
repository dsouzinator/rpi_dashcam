# RPi Dashcam
A Raspberry Pi based dashcam

The system has the ability to record from upto 4 webcams at once. 
Saved video can be either logged to an external USB flash drive or memory card.

## Hardware

The system is powered off of 12V supply from the car. It can automatically shut down when the car is switched off.

The 3F capacitor acts as a power backup when the car is switched off until the Pi safely shuts down. A capacitor backup was chosen as it doesn't require speacialized charging circuitry unlike chargeable batteries or replacement like the non-chargeable type.  
**Note:** Ensure capacitor tolerance value does not bring down the capacitance below 3F, if it does, consider putting two or more in parallel.

The volage divider outputs less than 3.3V and acts to sense when the car has been switched off by means of a GPIO port(17) on the RPi.  
**Note:** Ensure resistance tolerance values do not affect output voltage from the voltage divider, voltage greater than 3.3V and current  more than 0.5mA may permanently damage the board.

A Buck Converter steps down the input 12V to 5V output. It also smoothes the falling capacitor voltage as it discharges during a power cut.

Refer to the [circuit diagram](circuit_diagram.PNG) for more details.


## Software

The python script performs several functions:
* Starts recording sessions on all cameras
* Creates and stores all recordings from each session into a common folder
* Deletes old files to free up space when the number of files increases beyond a certain limit or when memory crosses a certain threshold
* Stops recording when car has been turned off and safely shutdowns the RPi
* The script has two classes Camera and Management. The Camera class creates recording sessions for each camera. The Management class manages recording sessions and files.
* Look at the [script](dashcam.py) for more information

**conclusion notes**
This setup assumes the car power goes off whenever the ignition key is turned off.
Future work includes:
  -* connecting a Real Time Clock
  -* circuit and script when car ignition does not turn off power(can do away with capacitor)
