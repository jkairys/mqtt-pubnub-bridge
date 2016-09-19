import time
import logging
import copy

logger = logging.getLogger('mqtt-pubnub-bridge')
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add ch to logger
ch.setFormatter(formatter)
logger.addHandler(ch)





from pubnub import Pubnub

pubnub = Pubnub(
  publish_key="pub-c-fb55ae11-11cd-4792-ada4-4ec898c0ebc5",
  subscribe_key="sub-c-8b96bdca-7e49-11e6-b27b-02ee2ddab7fe"
)

def callback(message, channel):
  print("{channel}: {msg}".format(channel=channel, msg=message))

def error(message):
  print("ERROR : " + str(message))

def connect(message):
  print("CONNECTED")


def reconnect(message):
  print("RECONNECTED")


def disconnect(message):
  print("DISCONNECTED")

pubnub.subscribe(
  channels='kyberd',
  callback=callback,
  error=callback,
  #connect=connect,
  #reconnect=reconnect,
  #disconnect=disconnect
)

#pubnub.publish(channel='kyberd', message='Erm...', callback=callback, error=callback)
pubnub.publish(channel='kyberd', message='Hello from the PubNub Python SDK')






ob = {
  'weather': {
    'ttl': None
  },
  'inverter': {
    'ttl': None
  }
}
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
  logger.info("MQTT connected with result code "+str(rc))
  client.subscribe("inverter/#")
  client.subscribe("weather/#")
  logger.info("Subscribed to MQTT channels")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
  pl = str(msg.payload.decode('utf-8'))
  path = msg.topic.split("/")
  #print("Received {0}".format(path[0]))
  if(path[0] == "weather" and path[1] != "{station}"):
    station = path[1]
    qty = path[2]

    #print("Got {:} - {:}".format(station, qty))
    if(station not in ob['weather']):
      ob['weather'][station] = {}

    ob['weather'][station][qty] = pl
    ob['weather']['ttl'] = 500

  if(path[0] == "inverter" and path[1] != "{station}"):
    qty = path[1]

    ob['inverter'][qty] = pl
    ob['inverter']['ttl'] = 500

  #payload = msg.payload.decode('utf-8').strip()
  #print("MQTT message: "+msg.topic+" "+str(msg.payload.decode('utf-8')))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.0.3", 1883, 60)
# start background thread
client.loop_start()

logger.info("moving right along...")


INTERVAL = 100
while True:
  time.sleep(INTERVAL/1000)
  for o in ob:
    if(ob[o]['ttl'] is None):
      continue

    ob[o]['ttl'] = ob[o]['ttl'] - INTERVAL
    if ob[o]['ttl'] <= 0:
      #print(ob[o])
      publish = copy.copy(ob[o])
      del(publish['ttl'])
      print("Updating {o} - {v}".format(o=o, v=publish))

      pubnub.publish(channel=o, message=ob[o])
      ob[o]['ttl'] = None
