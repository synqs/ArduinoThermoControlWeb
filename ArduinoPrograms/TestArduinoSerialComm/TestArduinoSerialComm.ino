long error;
long input;
long output;
double setpoint;

double kp, ki, kd, G, tauI, tauD;

char mode;   // for incoming serial data

void setup()
{
  Serial.begin(9600);          //  setup serial
 randomSeed(analogRead(0));

  setpoint = 700;

  ////////PID parameters

  G = 1.; //gain that we want to use. We find it by adjusting it to be small enough such that the system is not oscillating
  tauI = 1000.;// in s and obtained from the time constant as we apply a step function
  tauD = 0;
  kp = G;
  ki = G / tauI;
  kd = G * tauD;
}

void loop() {
  /////////// first part of the wavepacket control
  input = random(1000);
  error = setpoint - input;
  output = random(300);
  delay(500);

  // send data only when you receive data:
  if (Serial.available() > 0) {
    // read the incoming byte:
    // say what you got:
    mode = Serial.read();
    if (mode == 'w') {
      // write the current state
      Serial.print(setpoint);
      Serial.print(", ");
      Serial.print(input);
      Serial.print(", ");
      Serial.print(error);
      Serial.print(", ");
      Serial.print(output);
      Serial.print(", ");
      Serial.print(G);
      Serial.print(", ");
      Serial.print(tauI);
      Serial.print(", ");
      Serial.println(tauD, DEC);
    }
    if (mode == 's') {
      // change setpoint
      setpoint = Serial.parseInt();
    }
    if (mode == 'p') {
      // change proportional
      G = Serial.parseFloat();
      kp = G;
      ki = G / tauI;
      kd = G * tauD;
      }
    if (mode == 'i') {
      // change integrator time
      tauI = Serial.parseFloat();
      ki = G / tauI;
      }
    if (mode == 'd') {
      // change differentiator time
        tauD = Serial.parseFloat();
        kd = G*tauD;
        }
  }
}
