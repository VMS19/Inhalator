# Software Configuration

1. This guide will document the requierments on the software.
2. The software accesses the reading of 4 sensors:
    1. Oxygen (via a2d)
    2. Battery Level (via a2d)
    3  Air Flow (I2C)
    4. Pressure (I2C)
3. The software also "kicks" an RTC Watchdog which will sound an alarm if the software hangs
4. The software controls LEDs and turn them on/off reflecting the alerts in the system 

The software accesses several data buses as described later.
The software-hardware interfaces is described later. 

## ALARM RAISING LOGIC 
1. If the patients stats are bad then turn LED on using GPIO 25
2. If the sensor or a2d malfunctions then turn LED on using GPIO 24





## HARDWARE 


### OCCUPIED SIGNAL PINOUT

| Raspberry Pin Name (Number) | Sensor Sheild Pin name(VER-A)  | Funcitonality  |
| --------------------------- | ------------------------------ | -------------- |
| GPIO 8 SDA1 I2C (3)         | SDA_RAS||
| GPIO 9 SCL1 I2C (5) 		  |	SCL_RAS||
| GPIO 12 MOSI SPI (19) | P_mosi |a2d mosi input from raspb|
| GPIO 13 MISO SPI (21) | P_miso |a2d miso output to raspb|
| GPIO 14 SCLK SPI (23) | P_sclk |a2d sclk input from raspb| 
| GPIO  11 CE1 SPI (26) | OX_CS | a2d cs input from raspb|	
| GPIO 22 GPCLK2 (31) | busy | a2d busy output to raspb|
|GPIO 21 GPCLK2(29)| WD| WD input from raspb| 
|GPIO 23 PWM1 (33) | EN_SPK_RAS | output from raspb to enabel speaker (IO-HIGH=speaker ON)|
|GPIO 25 (37) | EN_SYSTEM_RAS | output from raspb to enabel system (IO-LOW=RAISE ALARM)|
|GPIO 24 PCM_FS/PWN1 (35) | "#FLT" | output from raspb to LED  (IO-LOW=LED ON )|
|GPIO 28 PCM_DIN (38) | GPIO | output from raspb to LED  (IO-LOW=LED ON )|
|GPIO 27 (36) | INT1_RTC~| output from RTC to raspb input ( NOT USED )|
|GPIO 29 (40) | INT1_RTC~| output from RTC to raspb input ( NOT USED )|

![Alt text](./rasp-3b+-pinout.png?raw=true "Title")

### DATA BUSES

#### I2C BUS
The I2C bus is populated with the following:
1. Raspberry-PI3b+ - master
2. Air-Flow sensor (A.K.A Flow) - <font color='red'>TBD</font>
2. Pressure sensor - <font color='red'>TBD</font>

3. RTC  [manual here](/RTCmanual.pdf)

#### SPI BUS
The SPI bus is populated with the following:
1. Raspberry-PI3b+ - master
2. A2D

### A2D Logic
The A2D has 8 analog inputs.
The populated inputs are (the rest of the inputs are unsued)
1. Channel 0 (CH0) - oxygen sensor amplified output
2. Channel 1 (CH1) - backup battery level measurement
3. Channel 2 (CH2) - TBD 
4. Channel 3 (CH3) - TBD 
5. Channel 4 (CH4) - TBD 
6. Channel 5 (CH5) - TBD 

#### Conversion required in software
Due to hardware constraint the A2D measures a certain value,
but the software needs to output to the screen a function of this value

Denote by Xi the A2D value on channel i ;
Denote by Yi the fucntion of Xi, notice that Yi is a DOUBLE variable;
 
##### CONSTANTS 
 
 VREF = 2.5\
 BIT_ACCURACY = 2**14\
 R23 = 24.3\
 R24 = 348\
 R29 = 348\
 BATT_RDIV = R23/(R23+R29+R24)\
 CONV_COEFF=VREF/ BIT_ACCURACY\
 OX_GAIN=100\
 OX_OFFSET = 1.5\
 VOLTAGE_TO_OX= 0.16 / 0.0005
##### CALCULATION
 Y0 =  VOLTAGE_TO_OX * (CONV_COEFF * X0-OX_OFFSET) / OX_GAIN\
 Y1 = CONV_COEFF * X1 / BATT_RDIV\
 Y2 =  CONV_COEFF * X2\
 Y3 =  CONV_COEFF * X3\
 Y4 =  CONV_COEFF * X4\
 Y5 =  CONV_COEFF * X5
 


## USELESS LINES 
PSS 24 
duplication of INT1_RTC~ 36 , 40
