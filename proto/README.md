## This folder is for PoC of deserialize the protobuf message from Ecoflow MQTT message

# Install dependencies
```
pip install -r requirements.txt
```

# Try the local deserialization
```bash
python mqtt.py --read-local message.txt
```

# Try realtime deserialization via MQTT
```bash
export DEVICE_ID=<your ecoflow device id/serial number>
export ACCOUNT_ID=<your ecoflow account id>
export MQTT_USERNAME=<your ecoflow mqtt username>
export MQTT_PASSWORD=<your ecoflow mqtt password>

python mqtt.py
```

