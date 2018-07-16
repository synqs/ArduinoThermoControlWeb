int analogPin = 0;
int outPin = 10;
int outLEDPin = 12; //rote LED

//number of measurements before eval
const int nmeas = 10;
int nloopcount = 100;  // number of counts in each loop. Cycle time is 10ms x nloopcount
unsigned long now;
long sumval;
int measnum;
int loopcount;

char mode;   // for incoming serial data

long inputspannung;

/*working variables for PID*/
unsigned long lastTime;
double input, output, setpoint, error;
double errSum, lastErr;
double kp, ki, kd, G, tauI, tauD;

void setup()
{
  Serial.begin(9600);          //  setup serial
  pinMode(outPin, OUTPUT);
  pinMode(outLEDPin, OUTPUT);

  setpoint = 790;

  ////////PID parameters
  G = 2; //gain that we want to use. We find it by adjusting it to be small enough such that the system is not oscillating
  tauI = 500;// in s and obtained from the time constant as we apply a step function
  tauD = 0;
  kp = G;
  ki = G / tauI;
  kd = G*tauD;

  //initialize integrator
  errSum = 40 / nloopcount; // let the loop start at a nice value

  loopcount = 0;
  measnum = 0;
  output = 0;
}

void loop() {
  /////////// first part of the wavepacket control
  delay(10);
  loopcount++;
  if (loopcount == (int)output && output < nloopcount) {
    digitalWrite(outPin, LOW);
    digitalWrite(outLEDPin, LOW);
  }
  if ((int)output == 0) {
    digitalWrite(outPin, LOW);
    digitalWrite(outLEDPin, LOW);
  }
  //////////

  ////// measure every 10th loop cycle
  if ((loopcount % 10) == 0) {
    measnum++;

    sumval = sumval + analogRead(analogPin);
  }

  ///// if enough measurements calculate PID
  if (measnum == nmeas) {
    input = double(sumval) / double(nmeas);
    now = millis();

    //time since last evaluation
    // we want the timeChange to be in seconds and not ms
    // this is necessary as we only know the time constant in actual units
    double timeChange = (double)((now - lastTime) / 1000);

    if (timeChange > 0) {
      //calculate error signal
      error = setpoint - input;

      //update integrator
      errSum += (error * timeChange);

      //limit the integrator to the bounds of the output
      if (errSum * ki > nloopcount) errSum = nloopcount / ki;
      if (errSum * ki < 0) errSum = 0;

      //calculate derivative part
      double dErr = (error - lastErr) / timeChange;

      //compute PI output
      output = kp * error + ki * errSum + kd*dErr;

      //limit PID output to the bounds of the output
      if (output > nloopcount) output = nloopcount;
      if (output < 0) output = 0;

      //remember for next time
      lastErr = error;
      lastTime = now;
    }
    //reset number of aquired measurements and measurement accumulator
    sumval = 0;
    measnum = 0;
  }

  /////////// second part of the wavepacket control
  if (loopcount == nloopcount) {
    loopcount = 0;
    if (output > 0) {
      digitalWrite(outPin, HIGH);
      digitalWrite(outLEDPin, HIGH);
    }
  }
  ////////////////////
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
      long out;
      setpoint = Serial.parseInt();
    }
    if (mode == 'p') {
      G = Serial.parseFloat();
      kp = G;
      ki = G / tauI;
      kd = G * tauD;
      }
    if (mode == 'i') {
      tauI = Serial.parseFloat();
      ki = G / tauI;
      }
    if (mode == 'd') {
        tauD = Serial.parseFloat();
        kd = G*tauD;
        }
  }
}
