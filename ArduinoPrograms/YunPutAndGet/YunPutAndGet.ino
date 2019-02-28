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

#include <Bridge.h>

void setup() {
  Bridge.begin();	// Initialize the Bridge

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
  delay(50); // Poll every 50ms

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
    Bridge.put("temp", String(input));
    loopcount = 0;
  }
}
