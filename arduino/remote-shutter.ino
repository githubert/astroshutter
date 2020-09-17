int command = 0;

void setup() {
  Serial.begin(9600);

  pinMode(2, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(2, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    command = Serial.read();

    if( command == 'c' ) { /* Close, aka stop capturing photo */
      digitalWrite(LED_BUILTIN, LOW);
      digitalWrite(2, LOW);
    } else if( command == 'r' ) { /* Release, aka press the button */
      digitalWrite(LED_BUILTIN, HIGH);
      digitalWrite(2, HIGH);
    }
  }
}
