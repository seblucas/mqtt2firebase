# mqtt2firebase

Push data coming from a MQTT broker (collecting data from sensors) into Firebase using Firebase Admin SDK. 

I use it to store data from a lot of sensor around my house. The UI can be found [here](https://github.com/seblucas/firebase-sensor).

# Usage

## Prerequisite

You simply need Python3 (never tested with Python2.7) and the only dependencies are `firebase-admin` (to access your Firebase realtime database) and `paho-mqtt` (for MQTT broker interaction) so this line should be enough  :

```bash
pip3 install paho-mqtt firebase-admin
```

## Getting your credentials

You just have to follow [Firebase's excellent documentation](https://firebase.google.com/docs/admin/setup).

## Using the script

Easy, first try a dry-run command :

```bash
./mqtt2firebase.py -a '<PATH TO YOUR CREDENTIALS>' -N '<FIREBASE_APP_NAME>' -n -v
```

About the path to your credentials, you can also use the json directly instead of a path. See the `docker-compose.yml` for more details.

and then a real command :

```bash
./mqtt2firebase.py -a '<PATH TO YOUR CREDENTIALS>' -N '<FIREBASE_APP_NAME>'
```

The secrets can also be set with environment variables, see the help for more detail.

## Help

```bash
/ # mqtt2firebase.py --help
usage: mqtt2firebase.py [-h] [-a FIREBASEAPIKEY] [-m HOST] [-n]
                        [-N FIREBASEAPPNAME] [-p FIREBASEPATH] [-t TOPIC]
                        [-T TOPIC] [-v]

Send MQTT payload received from a topic to firebase.

optional arguments:
  -h, --help            show this help message and exit
  -a FIREBASEAPIKEY, --firebase-credential-json FIREBASEAPIKEY
                        Firebase API Key / Can also be read from
                        FIREBASE_CREDENTIAL_JSON env var. (default: None)
  -m HOST, --mqtt-host HOST
                        Specify the MQTT host to connect to. (default:
                        127.0.0.1)
  -n, --dry-run         No data will be sent to the MQTT broker. (default:
                        False)
  -N FIREBASEAPPNAME, --firebase-app-name FIREBASEAPPNAME
                        The firebase application name / Can also be read from
                        FIREBASE_APP_NAME env var. (default: None)
  -p FIREBASEPATH, --firebase-path FIREBASEPATH
                        The firebase path where the payload will be saved
                        (default: /readings)
  -t TOPIC, --topic TOPIC
                        The MQTT topic on which to get the payload, don't
                        forget the trailing #. (default: sensor/raw/#)
  -T TOPIC, --topic-error TOPIC
                        The MQTT topic on which to publish the message (if it
                        wasn't a success). (default: error/firebase)
  -v, --verbose         Enable debug messages. (default: False)

```

## Docker

I added a sample Dockerfile, I personaly use it with a `docker-compose.yml` like this one :

```yml
version: '3'

services:
  mqtt2firebase:
    build: https://github.com/seblucas/mqtt2firebase.git
    image: mqtt2firebase-python3:latest
    restart: always
    command: "-m mosquittp -p readings -t 'test/raw/#' -v"
    environment:
      FIREBASE_APP_NAME: XXX
      FIREBASE_CREDENTIAL_JSON: >-
        {
          "type": "XXX",
          "project_id": "XXX",
          "private_key_id": "XXX",
          "private_key": "-----BEGIN PRIVATE KEY-----XXX-----END PRIVATE KEY-----\n",
          "client_email": "XXX",
          "client_id": "XXX",
          "auth_uri": "XXX",
          "token_uri": "XXX",
          "auth_provider_x509_cert_url": "XXX",
          "client_x509_cert_url": "XXX"
        }
```


# Limits

 * None I hope ;).

# License

This program is licenced with GNU GENERAL PUBLIC LICENSE version 3 by Free Software Foundation, Inc.

