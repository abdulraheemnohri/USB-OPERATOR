#include <Arduino.h>
#include <ArduinoJson.h>

// USB-OPERATOR demo firmware: read-only protocol example.
// It deliberately does NOT expose GPIO writes, relay switching or motor control.
static const char* PROTOCOL = "usb-operator-jsonl/1";
static const size_t MAX_LINE = 512;

void sendResponse(const char* id, bool ok, JsonObject data, const char* error = nullptr) {
  StaticJsonDocument<768> response;
  response["protocol"] = PROTOCOL;
  response["id"] = id;
  response["ok"] = ok;
  if (ok) response["data"].set(data);
  else response["error"] = error ? error : "request_failed";
  serializeJson(response, Serial);
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
}

void loop() {
  if (!Serial.available()) return;
  String line = Serial.readStringUntil('\n');
  if (line.length() == 0 || line.length() > MAX_LINE) return;
  StaticJsonDocument<512> request;
  if (deserializeJson(request, line)) return;
  const char* protocol = request["protocol"] | "";
  const char* id = request["id"] | "";
  const char* action = request["action"] | "";
  if (strcmp(protocol, PROTOCOL) != 0 || strlen(id) == 0) return;
  StaticJsonDocument<768> dataDoc;
  JsonObject data = dataDoc.to<JsonObject>();
  if (strcmp(action, "identify") == 0) {
    data["board"] = "ESP32"; data["firmware"] = "usb-operator-readonly-demo/1";
    sendResponse(id, true, data);
  } else if (strcmp(action, "status") == 0) {
    data["status"] = "ready"; data["uptime_ms"] = millis();
    sendResponse(id, true, data);
  } else if (strcmp(action, "read") == 0) {
    const char* channel = request["parameters"]["channel"] | "default";
    if (strcmp(channel, "temperature") == 0) data["temperature_raw"] = analogRead(34);
    else if (strcmp(channel, "default") == 0) data["adc_gpio34_raw"] = analogRead(34);
    else { sendResponse(id, false, data, "unsupported_channel"); return; }
    sendResponse(id, true, data);
  } else {
    sendResponse(id, false, data, "action_not_supported_read_only_firmware");
  }
}
