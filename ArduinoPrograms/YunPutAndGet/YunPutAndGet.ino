/*
  Running shell commands using Process class.

 This sketch demonstrate how to run linux shell commands
 using a YunShield/Yún. It runs the wifiCheck script on the Linux side
 of the Yún, then uses grep to get just the signal strength line.
 Then it uses parseInt() to read the wifi signal strength as an integer,
 and finally uses that number to fade an LED using analogWrite().

 The circuit:
 * YunShield/Yún with LED connected to pin 9

 created 12 Jun 2013
 by Cristian Maglie
 modified 25 June 2013
 by Tom Igoe

 This example code is in the public domain.

 http://www.arduino.cc/en/Tutorial/ShellCommands

 */
#include <Bridge.h>

// Listen to the default port 5555, the Yún webserver
// will forward there all the HTTP requests you send

void setup() {
  Bridge.begin();	// Initialize the Bridge
}

void loop() {
   Bridge.put("temp", String(12344));
  delay(50); // Poll every 50ms

}
