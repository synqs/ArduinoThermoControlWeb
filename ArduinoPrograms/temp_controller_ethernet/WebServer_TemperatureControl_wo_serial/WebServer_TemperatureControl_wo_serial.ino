/*
  Web Server

 A simple web server that shows the value of the analog input pins.
 using an Arduino Wiznet Ethernet shield.

 Circuit:
 * Ethernet shield attached to pins 10, 11, 12, 13
 * Analog inputs attached to pins A0 through A5 (optional)

 created 18 Dec 2009
 by David A. Mellis
 modified 9 Apr 2012
 by Tom Igoe
 modified 02 Sept 2015
 by Arturo Guadalupi
 
 */

#include <SPI.h>
#include <Ethernet.h>

// Enter a MAC address and IP address for your controller below.
// The IP address will be dependent on your local network:
byte mac[] = {
  0x08, 0x00, 0x27, 0xCE, 0xB0, 0xD8
};
IPAddress ip(129, 206, 182, 240);

// Initialize the Ethernet server library
// with the IP address and port you want to use
// (port 80 is default for HTTP):
EthernetServer server(80);

/* TEMPERATURE CONTROL */
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
  // You can use Ethernet.init(pin) to configure the CS pin
  //Ethernet.init(10);  // Most Arduino shields
  //Ethernet.init(5);   // MKR ETH shield
  //Ethernet.init(0);   // Teensy 2.0
  //Ethernet.init(20);  // Teensy++ 2.0
  //Ethernet.init(15);  // ESP8266 with Adafruit Featherwing Ethernet
  //Ethernet.init(33);  // ESP32 with Adafruit Featherwing Ethernet

  // Open serial communications and wait for port to open:
  
  
  // start the Ethernet connection and the server:
  Ethernet.begin(mac, ip);

  

  // start the server
  server.begin();

  // put your setup code here, to run once:
  
  pinMode(Temp_in,INPUT);
  pinMode(analogpin,OUTPUT);

  setpoint = 130;
   
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

       
  // listen for incoming clients
  EthernetClient client = server.available();
  if (client) {
    
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        mode = client.read();
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (mode == '\n' && currentLineIsBlank) {
          // send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println("Connection: close");  // the connection will be closed after completion of the response
          client.println("Refresh: 5");  // refresh the page automatically every 5 sec
          client.println();
          client.println("<!DOCTYPE HTML>");
          client.println("<html>");

          client.print("setpoint");
          client.print(", ");
          client.print("input");
          client.print(", ");
          client.print("error");
          client.print(", ");
          client.print("output");
          client.print(", ");
          client.print("G");
          client.print(", ");
          client.print("tauI");
          client.print(", ");
          client.println("tauD");
          client.println("<br />");

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
          
          client.println("</html>");
          break;
        }

         
        if (mode == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        } else if (mode != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
        if (mode == 's') {
          long out;
          setpoint = client.parseInt();
        }
        if (mode == 'p') {
          G = client.parseFloat();
          kp = G;
          ki = G / tauI;
          kd = G * tauD;
        }
        if (mode == 'i') {
          tauI = client.parseFloat();
          ki = G / tauI;
        }
        if (mode == 'd') {
          tauD = client.parseFloat();
          kd = G*tauD;
        }
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
    
  }
}
