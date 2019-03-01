int Temp_in = A1;
float V_out;
float Temperature;
int analogpin = 9;


//number of measurements before eval
const int nmeas = 10;

unsigned long now;
long sumval;
int measnum;
int lc;
int lcmax = 100;

/*working variables for PID*/
unsigned long lastTime;
double input, output, setpoint, error;
double errSum, lastErr;
double kp, ki, kd, G, tauI, tauD;

char mode;

#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>

// Listen to the default port 5555, the Yún webserver
// will forward there all the HTTP requests you send
BridgeServer server;

void setup() {
  // Bridge startup
  Bridge.begin();
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
  errSum = 20 / lcmax; // let the loop start at a nice value

  lc = 0;
  measnum = 0;
  output = 0;
  sumval = 0;
  // Listen for incoming connection only from localhost
  // (no one from the external network could connect)
  server.listenOnLocalhost();
  server.begin();
}

void loop() {
  // Get clients coming from server
  BridgeClient client = server.accept();

  // There is a new client?
  if (client) {
    // Process request
    process(client);

    // Close connection and free resources.
    client.stop();
  }

  delay(50); // Poll every 50ms

  
  lc++;
  
    ////// measure every 10th loop cycle
  if ((lc % 1) == 0) {
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
  if (lc == lcmax) {
    lc = 0;
  }
}

void process(BridgeClient client) {
  // read the command
  String command = client.readStringUntil('/');

  // is "read" command?
  if (command == "read") {
    readCommand(client);
  }
  
  // is "digital" command?
  if (command == "digital") {
    digitalCommand(client);
  }

  // is "analog" command?
  if (command == "analog") {
    analogCommand(client);
  }

  // is "mode" command?
  if (command == "mode") {
    modeCommand(client);
  }
}

void readCommand(BridgeClient client) {
  int value = 5;
  int pin = 5;
  String component = client.readStringUntil('/');
  if (component == "all") { 
  }
  // Send feedback to client
  //client.println(F("setpoint, input, error, output, G, tauI, tauD"));
  client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");  // the connection will be closed after completion of the response
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html><body>");
          client.println("setpoint, input, error, output, G, tauI, tauD <br />");
          client.print(setpoint);
          client.print(", ");
          client.print(input);
          client.print(", ");
          client.print(error);
          client.print(", ");
          client.print(output);
          client.print(", ");
          client.print(G);
          client.print(", ");
          client.print(tauI);
          client.print(", ");
          client.println(tauD, DEC);
  client.println("</body></html>");


  // Update datastore key with the current pin value
  String key = "t";
  Bridge.put(key, String(value));
}

void digitalCommand(BridgeClient client) {
  int pin, value;

  // Read pin number
  pin = client.parseInt();

  // If the next character is a '/' it means we have an URL
  // with a value like: "/digital/13/1"
  if (client.read() == '/') {
    value = client.parseInt();
    digitalWrite(pin, value);
  } else {
    value = digitalRead(pin);
  }

  // Send feedback to client
  client.print(F("Pin D"));
  client.print(pin);
  client.print(F(" set to "));
  client.println(value);

  // Update datastore key with the current pin value
  String key = "D";
  key += pin;
  Bridge.put(key, String(value));
}

void analogCommand(BridgeClient client) {
  int pin, value;

  // Read pin number
  pin = client.parseInt();

  // If the next character is a '/' it means we have an URL
  // with a value like: "/analog/5/120"
  if (client.read() == '/') {
    // Read value and execute command
    value = client.parseInt();
    analogWrite(pin, value);

    // Send feedback to client
    client.print(F("Pin D"));
    client.print(pin);
    client.print(F(" set to analog "));
    client.println(value);

    // Update datastore key with the current pin value
    String key = "D";
    key += pin;
    Bridge.put(key, String(value));
  } else {
    // Read analog pin
    value = analogRead(pin);

    // Send feedback to client
    client.print(F("Pin A"));
    client.print(pin);
    client.print(F(" reads analog "));
    client.println(value);

    // Update datastore key with the current pin value
    String key = "A";
    key += pin;
    Bridge.put(key, String(value));
  }
}

void modeCommand(BridgeClient client) {
  int pin;

  // Read pin number
  pin = client.parseInt();

  // If the next character is not a '/' we have a malformed URL
  if (client.read() != '/') {
    client.println(F("error"));
    return;
  }

  String mode = client.readStringUntil('\r');

  if (mode == "input") {
    pinMode(pin, INPUT);
    // Send feedback to client
    client.print(F("Pin D"));
    client.print(pin);
    client.print(F(" configured as INPUT!"));
    return;
  }

  if (mode == "output") {
    pinMode(pin, OUTPUT);
    // Send feedback to client
    client.print(F("Pin D"));
    client.print(pin);
    client.print(F(" configured as OUTPUT!"));
    return;
  }

  client.print(F("error: invalid mode "));
  client.print(mode);
}
