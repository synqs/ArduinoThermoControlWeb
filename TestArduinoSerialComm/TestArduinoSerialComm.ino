long error;
long input;
long output;
double setpoint;


int incomingByte = 0;   // for incoming serial data


void setup()
{
  Serial.begin(9600);          //  setup serial
 randomSeed(analogRead(0));

  setpoint = 700;
}

void loop() {
  /////////// first part of the wavepacket control
  input = random(1000);
  error = setpoint - input;

  output = random(300);
  Serial.print(setpoint);
  Serial.print(", ");
  Serial.print(input);
  Serial.print(", ");
  Serial.print(error);
  Serial.print(", ");
  Serial.println(output, DEC);
  delay(1000);
  
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    incomingByte = Serial.read();

    // say what you got:
    Serial.print("I received: ");
    Serial.println(incomingByte, DEC);
  }
}
