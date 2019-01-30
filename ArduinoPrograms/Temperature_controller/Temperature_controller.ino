
int Temp_in = A1;
float V_out;
float Temperature;
int analogpin = 9;


//number of measurements before eval
const int nmeas = 10;
int nloopcount = 100;  // number of counts in each loop. Cycle time is 10ms x nloopcount
unsigned long now;
long sumval;
int measnum;
int loopcount;

/*working variables for PID*/
unsigned long lastTime;
double input, output, setpoint, error;
double errSum, lastErr;
double kp, ki, kd, G, tauI, tauD;


char mode;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(Temp_in,INPUT);
  pinMode(analogpin,OUTPUT);

  setpoint = 40;
   
  ////////PID parameters
  G = 5; //gain that we want to use. We find it by adjusting it to be small enough such that the system is not oscillating
  tauI = 200;// in s and obtained from the time constant as we apply a step function
  tauD = 0;
  kp = G;
  ki = G / tauI;
  kd = G*tauD;
  
  //initialize integrator
  errSum = 20 / nloopcount; // let the loop start at a nice value

  loopcount = 0;
  measnum = 0;
  output = 0;
  sumval = 0;
  
}

void loop() {
  delay(10);
  loopcount++;

  ////// measure every 10th loop cycle
  if ((loopcount % 1) == 0) {
    measnum++;
    V_out = analogRead(Temp_in)*(5/1024.0);
    Temperature = (V_out-1.25)/0.005; //conversion from voltage to temp 
    sumval = sumval + Temperature;
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
      if (errSum * ki > 255) errSum = 255 / ki;
      if (errSum * ki < 0) errSum = 0;

      //calculate derivative part
      double dErr = (error - lastErr) / timeChange;

      //compute PI output
      output = kp * error + ki * errSum+kd*dErr;

      //output = -1;
      
      //limit PID output to the bounds of the output
      if (output > 255) output = 255;
      if (output < 0) output = 0;

      //remember for next time
      lastErr = error;
      lastTime = now;
    }
    
    analogWrite(analogpin,output);
    //reset number of aquired measurements and measurement accumulator
    sumval = 0;
    measnum = 0;
  }
  
  /////////// second part of the wavepacket control
  if (loopcount == nloopcount) {
    loopcount = 0;
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
