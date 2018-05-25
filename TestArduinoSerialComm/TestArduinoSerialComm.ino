long error;
long input;
long output;

void setup()
{
  Serial.begin(9600);          //  setup serial
 randomSeed(analogRead(0));

}

void loop() {
  /////////// first part of the wavepacket control
  error = random(300);
  input = random(300);
  output = random(300);
  Serial.print(error);
    Serial.print(", ");
    Serial.print(input);
    Serial.print(", ");
    Serial.println(output, DEC);
  delay(1000);
}
