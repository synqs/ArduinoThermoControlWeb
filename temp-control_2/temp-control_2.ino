

int Temp_read1 = A0;
int Temp_read2 = A1;
int Temp_read3 = A2;
float Voltageread1;
float Voltageread2;
float Voltageread3;
float Temperature_1;
float Temperature_2;
float Temperature_3;

char mode;
void setup() {
  // put your setup code here, to run once:
Serial.begin(9600);
pinMode(A0,INPUT);
pinMode(A1,INPUT);
pinMode(A2,INPUT);

}

void loop() {
  // put your main code here, to run repeatedly:
Voltageread1 = analogRead(Temp_read1)*(4.4/1024.0);
Temperature_1 = (Voltageread1-1.25)/0.005;
Voltageread2 = analogRead(Temp_read2)*(4.4/1024.0);
Temperature_2 = (Voltageread2-1.25)/0.005;
Voltageread3 = analogRead(Temp_read3)*(4.4/1024.0);
Temperature_3 = (Voltageread3-1.25)/0.005;

delay(500);
////////////////////
  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    // say what you got:
    mode = Serial.read();
    if (mode == 'w') {
      // write the current state
      Serial.print(Temperature_1);
      Serial.print(", ");
      Serial.print(Temperature_2);
      Serial.print(", ");
      Serial.println(Temperature_3, DEC);
    }
  }
}
