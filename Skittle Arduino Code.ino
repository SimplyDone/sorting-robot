#include <Servo.h>

#define PWM_STIR 5
#define STNDBY 0
#define Bin1 1
#define Bin2 2

Servo piston;
Servo dropper;

bool stirEnabled;

const byte positions[] = {0,1,2,3,4};

void setup() {

  // Set pin outputs for stiring motor
  pinMode(PWM_STIR, OUTPUT);
  pinMode(STNDBY, OUTPUT);
  pinMode(Bin1, OUTPUT);
  pinMode(Bin2, OUTPUT);

  stirEnabled = false;
  digitalWrite(STNDBY, HIGH);
  digitalWrite(Bin1, HIGH);
  analogWrite(PWM_STIR, 0);

  // Attach the two servos
  dropper.attach(3);
  piston.attach(10);

  // Sets the intial position for the piston to a retracte state
  piston.write(135);
  delay(250);

  Serial.begin(9600);

}

// Gets serial input then acts upon
void loop() {

  int cameraByte;

  if (Serial.available() > 0){

    cameraByte = Serial.read();

    doAction(cameraByte);
    
  }

}

// Moves the piston then retracts it
void movePiston(){

  piston.write(0);
  delay(750);
  piston.write(150);
  delay(750);
  
}

//Performs an action given an input
void doAction(int serialInput){

  switch(serialInput){
    case 114: // Move to position 1 and push piston
      dropper.write(0);
      delay(600);
      movePiston();  
      break;
    case 103: // Move to position 2 and push piston
      dropper.write(34);
      delay(600);
      movePiston();  
      break;
    case 121: // Move to position 3 and push piston
      dropper.write(68);
      delay(600);
      movePiston();  
      break;
    case 111: // Move to position 4 and push piston
      dropper.write(101);
      delay(600);
      movePiston();  
      break;
    case 112: /// Move to position 5 and push piston
      dropper.write(135);
      delay(600);
      movePiston();  
      break;
    case 110: //No action
      break;
    case 108: //Toggle stir rod
      if (stirEnabled){
        stirEnabled = false;
        analogWrite(PWM_STIR, 0);
      } else {
        stirEnabled = true;
        analogWrite(PWM_STIR, 40);
      }
      delay(100);
      break;
    case 102: //Turn stir rod on
      analogWrite(PWM_STIR, 40);
      stirEnabled = true;
      delay(100);
      break;
    default: // Move to position 5 and push piston
      dropper.write(135);
      delay(600);
      movePiston();  
      break;
  }
  
 
  
}

