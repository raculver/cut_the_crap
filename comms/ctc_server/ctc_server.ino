#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEService.h>
#include <BLEAdvertising.h>
#include <BLECharacteristic.h>

BLEServer *pServer = NULL;
BLECharacteristic *pFlagCharacteristic = NULL;

bool deviceConnected = false;

uint depayPeriod = 400;      // delay per loop (ms)
uint onPeriodRemaining = 0;  // number of loop delay periods remaining for output to be on
uint onPeriodIncrement = 5;  // number of delay periods to add to onPeriodRemaining per invocation
uint onPeriodMax = 50;       // maximum number of delay periods to remain on
uint8_t OUTPUT_CHANNEL = 18; // pin to output on [GPIO18 is pin D10]

#define SERVICE_UUID        "593af084-a37f-4b3a-832a-bcb8e547b259"
#define CHARACTERISTIC_UUID "0829d7d5-9f92-4c66-8117-c0733207dc76"

void writeFlagCharacteristicFalse(){
  uint8_t val = 0;
  pFlagCharacteristic->setValue(&val, 1);
}

// void writeFlagCharacteristicTrue(){
//   uint8_t val = 1;
//   pFlagCharacteristic->setValue(&val, 1);
// }

bool readFlagCharacteristic(){
  uint8_t *data = pFlagCharacteristic->getData();
  size_t len   = pFlagCharacteristic->getLength();
  return len >= 1 && data[0] != 0;
}

class CtcServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) {
    //Serial.println("Device connected.");
    deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer) {
    delay(500);                   // give the bluetooth stack the chance to get things ready

    //Serial.println("Device disconnected. Start advertising.");
    pServer->startAdvertising();  // restart advertising
    deviceConnected = false;
  }
};

void setup() {
  //Serial.begin(115200);
  pinMode(OUTPUT_CHANNEL, OUTPUT);
  digitalWrite(OUTPUT_CHANNEL, LOW);

  // Create the BLE Device
  BLEDevice::init("CTC_Server");

  // Create the BLE Server
  pServer = BLEDevice::createServer();
  pServer->setCallbacks(new CtcServerCallbacks());

  // Create the BLE Service
  BLEService *pService = pServer->createService(SERVICE_UUID);

  // Create a BLE Characteristic
  pFlagCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
  );

  // Start the service
  pService->start();

  // Start advertising
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(false);
  pAdvertising->setMinPreferred(0x0);  // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising(); 
  writeFlagCharacteristicFalse();
  //Serial.println("Device disconnected. Start advertising.");   
}

void loop() {  
  if (deviceConnected) {
    if (readFlagCharacteristic()){
      //Serial.println("On Detected.");
      onPeriodRemaining += onPeriodIncrement;
      //Serial.println(onPeriodRemaining);
    }
    writeFlagCharacteristicFalse();
  }

  delay(depayPeriod);
  if (onPeriodRemaining > 0){
    digitalWrite(OUTPUT_CHANNEL, HIGH);
    onPeriodRemaining--;
    //Serial.println(onPeriodRemaining);
  }
  else{
    digitalWrite(OUTPUT_CHANNEL, LOW);
  }
}
