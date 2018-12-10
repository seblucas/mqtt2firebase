#!/usr/bin/env python3
# -*- coding: latin-1 -*-
#
#  mqtt2firebase.py
#
#  Copyright 2016 Sébastien Lucas <sebastien@slucas.fr>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#


import os, re, time, json, argparse, signal, threading
import urllib.parse
from queue import Queue, Empty

import requests
import paho.mqtt.client as mqtt # pip install paho-mqtt
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession


verbose = False
FIREBASE_BASE_URL = 'https://{0}.firebaseio.com'

def signal_handler(signal, frame):
  print('You pressed Ctrl+C!')
  stop_event.set()
  t1.join()
  client.disconnect()

def debug(msg):
  if verbose:
    print (msg + "\n")

def environ_or_required(key):
  if os.environ.get(key):
    return {'default': os.environ.get(key)}
  else:
    return {'required': True}

def sendToFirebase(sensorName, payload):
  debug ("Start sendToFirebase")
  try:
    if not args.dryRun:
      if args.topicAsChild:
        r = ref.child(sensorName).push(payload)
      else:
        r = ref.push(payload)
      debug ("payload inserted : " + r.key)
      #client.publish('firebase/new', r.key)
    else:
      debug ("path : {0}\npayload : {1}".format(sensorName, payload))
  except Exception as e:
    print ("Firebase Exception", str(e))
    pass
  debug ("End sendToFirebase")

def process_firebase_messages(lqueue, stop_event):
  firebaseSession = AuthorizedSession(credentials)
  baseUrl = FIREBASE_BASE_URL.format(args.firebaseAppName)

  while not stop_event.is_set():
    try:
      packet = lqueue.get(False)
    except Empty:
      time.sleep(5)
      pass
    else:
      if packet is None:
        continue
      debug("data from queue: " + format(packet))
      firebasePath = args.firebasePath
      if args.topicAsChild:
        firebasePath = urllib.parse.urljoin(args.firebasePath + '/', packet['topic'])
      firebasePath = baseUrl + '/' + firebasePath + '.json'
      debug ("Sending {0} to this URL {1}".format(packet['payload'], firebasePath))
      try:
        if not args.dryRun:
          r = firebaseSession.post(firebasePath, json=packet['payload'], timeout=5)
          debug ("payload inserted : " + r.text)
      except requests.exceptions.Timeout:
        print ("Firebase Timeout")
        pass
      except requests.exceptions.RequestException as e:
        print ("Firebase Exception" + str(e))
        pass
      except:
        print ("Firebase Unknown Exception")
        pass
      #sendToFirebase(packet['topic'], packet['payload'])
      queue.task_done()
  firebaseSession.close()
  debug("Stopping Firebase Thread ...")

def on_connect(client, userdata, flags, rc):
    debug("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(args.topic)

def on_disconnect(client, userdata, rc):
    debug("Disconnected with result code "+str(rc))
    if rc != 0:
      debug("Unexpected disconnection.")

def on_message(client, userdata, msg):
    sensorName = msg.topic.split('/') [-1]
    debug("Received message from {0} with payload {1} to be published to {2}".format(msg.topic, str(msg.payload), sensorName))
    nodeData = msg.payload
    newObject = json.loads(nodeData.decode('utf-8'))
    #sendToFirebase(sensorName, newObject)
    queue.put({ "topic": sensorName, "payload": newObject})



parser = argparse.ArgumentParser(description='Send MQTT payload received from a topic to firebase.', 
  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('-a', '--firebase-credential-json', dest='firebaseApiKey', action="store",
                   help='Firebase API Key / Can also be read from FIREBASE_CREDENTIAL_JSON env var.',
                   **environ_or_required('FIREBASE_CREDENTIAL_JSON'))
parser.add_argument('-c', '--use-topic-as-child', dest='topicAsChild', action="store", default=True,
                   help='Use the last part of the MQTT topic as a child for Firebase.')
parser.add_argument('-m', '--mqtt-host', dest='host', action="store", default="127.0.0.1",
                   help='Specify the MQTT host to connect to.')
parser.add_argument('-n', '--dry-run', dest='dryRun', action="store_true", default=False,
                   help='No data will be sent to the MQTT broker.')
parser.add_argument('-N', '--firebase-app-name', dest='firebaseAppName', action="store",
                   help='The firebase application name / Can also be read from FIREBASE_APP_NAME env var.',
                   **environ_or_required('FIREBASE_APP_NAME'))
parser.add_argument('-p', '--firebase-path', dest='firebasePath', action="store", default="/readings",
                   help='The firebase path where the payload will be saved')
parser.add_argument('-t', '--topic', dest='topic', action="store", default="sensor/raw/#",
                   help='The MQTT topic on which to get the payload, don\'t forget the trailing #.')
parser.add_argument('-T', '--topic-error', dest='topicError', action="store", default="error/firebase", metavar="TOPIC",
                   help='The MQTT topic on which to publish the message (if it wasn\'t a success).')
parser.add_argument('-v', '--verbose', dest='verbose', action="store_true", default=False,
                   help='Enable debug messages.')


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
args = parser.parse_args()
verbose = args.verbose

pathOrCredentials = args.firebaseApiKey
if (pathOrCredentials.startswith ('{')):
  pathOrCredentials = json.loads(pathOrCredentials)

# Define the required scopes
scopes = [
  "https://www.googleapis.com/auth/userinfo.email",
  "https://www.googleapis.com/auth/firebase.database"
]

# Authenticate a credential with the service account
credentials = service_account.Credentials.from_service_account_info(
    pathOrCredentials, scopes=scopes)
# credentials = service_account.Credentials.from_service_account_file(
#     pathOrCredentials, scopes=scopes)

# cred = credentials.Certificate(pathOrCredentials)
# default_app = firebase_admin.initialize_app(cred, {
#   'databaseURL': FIREBASE_BASE_URL.format(args.firebaseAppName)
# })
# ref = db.reference(args.firebasePath)

queue = Queue()
stop_event = threading.Event()
t1 = threading.Thread(target=process_firebase_messages, args=[queue, stop_event])
t1.daemon = True
t1.start()

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(args.host, 1883, 60)

client.loop_forever()

