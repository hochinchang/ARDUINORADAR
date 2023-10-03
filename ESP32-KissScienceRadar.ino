#include <Ultrasonic.h> //超音波模組
#include <ESP32Servo.h>


const int TRIGGER_PIN = 14;  // 超音波模組的 Trig 腳位連接到 ESP32 的 GPIO 18 腳位
const int ECHO_PIN = 12;     // 超音波模組的 Echo 腳位連接到 ESP32 的 GPIO 19 腳位
const int VCC_PIN = 27;      // 超音波模組的 VCC 腳位連接到 ESP32 的 GPIO 5 腳位
//const int TRIGGER_PIN = 18;  // 超音波模組的 Trig 腳位連接到 ESP32 的 GPIO 18 腳位
//const int ECHO_PIN = 19;     // 超音波模組的 Echo 腳位連接到 ESP32 的 GPIO 19 腳位
//const int VCC_PIN = 5;      // 超音波模組的 VCC 腳位連接到 ESP32 的 GPIO 5 腳位
int distance_last=0; // 上一次的距離
int delaytime=50;   // 0.1秒
float delta_distance;
float speed;
int distance;

//舵機
Servo myservo;  // 建立 Servo 物件

int servoPin=13;
int VCC_Pin_Servo=23;
int angle = 45;    // 定義當前伺服馬達角度
int increment = 1;  // 每次增加或減少的角度


Ultrasonic ultrasonic(TRIGGER_PIN, ECHO_PIN);

void setup() {
  pinMode(VCC_PIN, OUTPUT);
  digitalWrite(VCC_PIN, HIGH);  // 將超音波模組的供電腳位設定為高電位
  Serial.begin(9600);

  pinMode(VCC_Pin_Servo, OUTPUT);
  digitalWrite(VCC_Pin_Servo, HIGH);  // 將舵機的供電腳位設定為高電位
  myservo.attach(servoPin);  // 將伺服馬達連接到數位腳位 

}

void loop() {
  distance = ultrasonic.read(); //讀取距離
  delta_distance = distance_last - distance;
  speed = delta_distance / delaytime*100;
  Serial.print(distance);
  Serial.print(" cm ");
  Serial.print(speed);
  Serial.print(" cm/s ");
  Serial.print(angle);
  Serial.println(" deg");
  distance_last = distance;
  delay(delaytime);

  // 將伺服馬達轉到 0 度
  myservo.write(angle);
  //myservo.write(45);
  //myservo.write(0);
  //delay(1000);
  //myservo.write(45);
  //delay(1000);
  //myservo.write(90);
  //delay(2000);

  angle += increment;
  // 如果伺服馬達到達 0 度或 90 度，則改變方向
//  if (angle < 25 || angle > 65) {
  if (angle < 0 || angle > 90) {
    increment = -increment;

  }

  
  

}
