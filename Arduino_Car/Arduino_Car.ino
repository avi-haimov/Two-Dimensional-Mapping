#include <SoftwareSerial.h>

SoftwareSerial bluetoothSerial(10, 11);  // Bluetooth communication using software serial on pins 10 (RX) and 11 (TX)

// Function to measure the distance using an HC-SR04 sensor
float checkdistance(int triggerPin, int echoPin) 
{
  digitalWrite(triggerPin, LOW);    // Set trigger pin to LOW
  delayMicroseconds(2);              // Create a 2 microsecond delay
  digitalWrite(triggerPin, HIGH);   // Set trigger pin to HIGH for 10 microseconds
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);    // Set trigger pin back to LOW

  // Measure the duration for the echo signal to return and calculate distance in centimeters
  float distance = pulseIn(echoPin, HIGH) / 58.00; // Divide the one-way time by 2 and convert to distance using an approximation factor

  delay(10);                         // Add a delay for stability
  return distance;                   // Return the calculated distance
}

// Pin configuration in the setup function
void setup() {
  pinMode(12, OUTPUT);   // Trigger pin for X-axis HC-SR04 sensor
  pinMode(13, INPUT);    // Echo pin for X-axis HC-SR04 sensor
  pinMode(2, OUTPUT);    // Motor control pin
  pinMode(5, OUTPUT);    // Motor speed pin
  pinMode(4, OUTPUT);    // Motor control pin
  pinMode(6, OUTPUT);    // Motor speed pin
  Serial.begin(9600);    // Initialize serial communication
}

// Main program loop
void loop() {
  // Measure the distance using the HC-SR04 sensor
  switch(Serial.readString()[0])
  {
    case 'S':
      Stop();
      break;
    case 'B':
      Move_Backward(70);
      break;
    case 'L':
      Rotate_Left(54);
      delay(1010);
      Stop();
      break;
    case 'F':
      Move_Forward(100);
      delay(2000);
      break;
    case 'R':
      Rotate_Right(54);
      delay(1010);
      Stop();
      break;
    case 'D':
      Get_Data();
      break;
  }
}

// Function to stop the motors
void Stop() {
  digitalWrite(2, LOW);       // Set motor control pins to LOW
  analogWrite(5, 0);          // Set motor speed pins to 0 (off)
  digitalWrite(4,HIGH);       // Set motor control pins to LOW
  analogWrite(6, 0);          // Set motor speed pins to 0 (off)
}

// Function to move backward
void Move_Backward(int speed) {
  digitalWrite(2, LOW);       // Set motor control pins to LOW
  analogWrite(5, speed);      // Set motor speed pins to the specified speed
  digitalWrite(4,HIGH);     // Set motor control pins to LOW
  analogWrite(6, speed);      // Set motor speed pins to the specified speed
}

// Function to rotate left
void Rotate_Left(int speed) {
  digitalWrite(2, LOW);       // Set motor control pins to LOW
  analogWrite(5, speed);      // Set motor speed pins to the specified speed
  digitalWrite(4, LOW);       // Set motor control pins to LOW
  analogWrite(6,speed);          // Set motor speed pins to 0 (off)
}

// Function to rotate right
void Rotate_Right(int speed) {
  digitalWrite(2, HIGH);       // Set motor control pins to LOW
  analogWrite(5, speed);      // Set motor speed pins to the specified speed
  digitalWrite(4, HIGH);       // Set motor control pins to LOW
  analogWrite(6,speed);          // Set motor speed pins to 0 (off)
}

// Function to move forward
void Move_Forward(int speed) {
  digitalWrite(2, HIGH);      // Set motor control pins to HIGH
  analogWrite(5, speed);      // Set motor speed pins to the specified speed
  digitalWrite(4,LOW);      // Set motor control pins to HIGH
  analogWrite(6, speed);      // Set motor speed pins to the specified speed
}
// Function to get data in square
void Get_Data()
{
  Stop();   // Stop the motors before starting data collection
  delay(200);  // Wait for a short delay to ensure stability
  Serial.println(checkdistance(12, 13));
  const int time_const = 4200;  // Define a constant time interval (in milliseconds) for data collection
  int times = 4;                // Number of times to repeat the data collection process
  for(;times > 0;times--)
  {
    int ticks = time_const;  // Initialize a variable to track the remaining time in the data collection interval
    Move_Forward(100);
    for(;ticks > 0; ticks = ticks - 50)
    {
      Serial.println(checkdistance(12, 13)); // Measure and print the distance at each interval
    }
    Stop();
    Serial.println("Next");
    Rotate_Left(54);
    delay(1010);
    Stop();
  } 
  Serial.println("Stop");
}
