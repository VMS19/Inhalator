# Software Configuration

This guide will document the requierments on the software.

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

![Alt text](./rasp-3b+-pinout.png?raw=true "Title")

Questions 
PSS 24 


----OX_CS 26

WD 29
----busy 31
EN_SPK_RAS 33
#FLT 35
EN_SYSTEM_RAS 37
GPIO 38

INT1_RTC~ 36 , 40
### NEXT SECd

