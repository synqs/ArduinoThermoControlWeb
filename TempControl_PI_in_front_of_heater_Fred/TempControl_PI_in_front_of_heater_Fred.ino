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


long inputspannung;

/*working variables for PID*/
unsigned long lastTime;
double input, output, setpoint, error;
double errSum, lastErr;
double kp, ki, kd, G, tau;

void setup()
{
  Serial.begin(9600);          //  setup serial
  pinMode(outPin, OUTPUT);
  pinMode(outLEDPin, OUTPUT);

  setpoint = 700;

  ////////PID parameters
  tau = 1000;// in s and obtained from the time constant as we apply a step function
  G = 10; //gain that we want to use. We find it by adjusting it to be small enough such that the system is not oscillating
  kp = G;
  ki = G / tau;
  kd = 0;

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
      output = kp * error + ki * errSum;

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

    //output some stuff to the serial port for monitoring

  }

  /////////// second part of the wavepacket control
  if (loopcount == nloopcount) {
    loopcount = 0;
    Serial.print(error);
    Serial.print(", ");
    Serial.print(input);
    Serial.print(", ");
    Serial.println(output, DEC);
    if (output > 0) {
      digitalWrite(outPin, HIGH);
      digitalWrite(outLEDPin, HIGH);
    }
  }
  ////////////////////

}
