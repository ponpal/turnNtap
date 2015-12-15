#include <Wire.h>
#include "Adafruit_TCS34725.h"

#define rightWheelButton 8
#define deleteButton 9
#define tapButton 10 
#define ledPin1 5
#define ledPin2 6
#define ledPin3 7

#define buttonThreshold 250

boolean rwbPressed = false;
boolean dbPressed = false;
boolean tbPressed = false;

/* Example code for the Adafruit TCS34725 breakout library */

/* Connect SCL    to analog 5
   Connect SDA    to analog 4
   Connect VDD    to 3.3V DC
   Connect GROUND to common ground */
   
/* Initialise with default values (int time = 2.4ms, gain = 1x) */
// Adafruit_TCS34725 tcs = Adafruit_TCS34725();

/* Initialise with specific int time and gain values */
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_24MS, TCS34725_GAIN_1X);

void setup(void) {
  Serial.begin(9600);
  
  if (tcs.begin()) {
    //Serial.println("Found sensor");
  } else {
    //Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }

  pinMode(rightWheelButton, INPUT);
  pinMode(deleteButton, INPUT);
  pinMode(tapButton, INPUT);
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  
  // Now we're ready to get readings!
}

// Author: Geertjan
String getColor(int r, int g, int b) {
  if (r > g && r > b) {
    return "R";
  } else if (g > b) {
    return "G";
  } else {
    return "B";
  }
}

void setLeds(int value) {
  digitalWrite(ledPin1, value);
  digitalWrite(ledPin2, value);
  digitalWrite(ledPin3, value);
}

int analogToDigital(int value) {
  return (value > buttonThreshold) ? HIGH : LOW;
}

void loop(void) {
  uint16_t r, g, b, c;

  int rightWheelBVal = digitalRead(rightWheelButton);
  int deleteBVal = digitalRead(deleteButton);
  int tapBVal = digitalRead(tapButton);

  if(rightWheelBVal == HIGH) {
    rwbPressed = true;
  } 

  if(rwbPressed && rightWheelBVal == LOW) {
    Serial.println("rightWheelButton");
    rwbPressed = false;
  }

  if(deleteBVal == HIGH) {
    dbPressed = true;
  }

  if(dbPressed && deleteBVal == LOW) {
    Serial.println("deleteButton");
    dbPressed = false;
  }

  if(tapBVal == HIGH) {
    tbPressed = true;
  }

  if(tbPressed && tapBVal == LOW) {
    Serial.println("tapButton");
    tbPressed = false;
  }
  
  tcs.getRawData(&r, &g, &b, &c);
  
  Serial.println(getColor(r,g,b));
}