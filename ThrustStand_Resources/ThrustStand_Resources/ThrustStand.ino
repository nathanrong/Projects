String inputString = "";
bool readingCommand = false;
unsigned long lastSendTime = 0;

// Initiate values
float thrust = 0.0;
float windSpeed = 0.0;
float voltage = 0.0;
float current = 0.0;
float rpm = 0.0;
int throttle = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  readSerial();
  if (millis() - lastSendTime >= 100) {
      sendData();
      lastSendTime = millis();
    }
  delay(10);
}

void sendData() {
  // Simulate data using time-based sine wave
  float t = millis() / 1000.0;  // time in seconds

  thrust    = (sin(t)       * 0.5 + 0.5) * 500;   // 0 - 500
  windSpeed = (sin(t + 1)   * 0.5 + 0.5) * 30;    // 0 - 30
  voltage   = (sin(t + 2)   * 0.5 + 0.5) * 12 + 6;// 6 - 18
  current   = (sin(t + 3)   * 0.5 + 0.5) * 15;    // 0 - 15
  rpm       = (sin(t + 4)   * 0.5 + 0.5) * 12000; // 0 - 12000
  rpm = throttle;

  // Package all data values into one string
  String telemetry = "<";
  telemetry += "THRST:" + String(thrust, 1) + ",";
  telemetry += "WIND:" + String(windSpeed, 1) + ",";
  telemetry += "VOLT:" + String(voltage, 1) + ",";
  telemetry += "CURR:" + String(current, 1) + ",";
  telemetry += "RPM:" + String(rpm, 0) + ",";
  telemetry += "THROT:" + String(throttle);
  telemetry += ">";

  Serial.println(telemetry);
}

void readSerial() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();

    if (inChar == '[') {
      readingCommand = true;
      inputString = "";
    } else if (inChar == ']' && readingCommand) {
      readingCommand = false;
      processCommand(inputString);
    } else if (readingCommand) {
      inputString += inChar;
    }
  }
}

// Combined command handling and application
void processCommand(String cmd) {
  cmd.trim();

  if (cmd.startsWith("THROTCMD:")) {
    int value = cmd.substring(9).toInt();
    throttle = constrain(value, 0, 100);
    int pwm = map(throttle, 0, 100, 0, 255);
    // analogWrite(9, pwm);  // Apply to ESC pin, whichever that is
  } else {
    // Error catch
    String error = "<ERROR:UNKNOWN_COMMAND>";
    Serial.println(error);
  }
}
