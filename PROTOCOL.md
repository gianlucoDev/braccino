# Braccino protocol

This file details the communication protocol between the Django server and the Arduino.

## General structure

Every packet starts with a start marker (`0xFF`), followed by the packet id, and ends with an end marker (`0xF0`).
The packet id allows to identify the different packets to handle their contents.

| name             | size    | value  | description                                     |
| ---------------- | ------- | ------ | ----------------------------------------------- |
| `start_marker`   | 1       | `0xFF` | Start marker, signifies the start of the packet |
| `packet_id`      | 1       | `0x00` | Packet id                                       |
| packet fields... | n bytes |        | Various packet fields depending on the packet   |
| `end_marker`     | 1       | `0xF0` | End marker, signifies the start of the packet   |

## Packet list

### Django to Arduino

List of packets sent from the django app to the arduino

| id     | name         | description                |
| ------ | ------------ | -------------------------- |
| `0x01` | set position | Set the braccio position   |
| `0x02` | get position | Reads the braccio position |

#### `0x01` set position

Sent to the Arduino to set the braccio position.
This packet does not expect any response.

| name           | size | value  | description                             |
| -------------- | ---- | ------ | --------------------------------------- |
| `start_marker` | 1    | `0xFF` |                                         |
| `packet_id`    | 1    | `0x01` |                                         |
| m1             | 1    |        | Desired position of the base joint      |
| m2             | 1    |        | Desired position of the shoulder joint  |
| m3             | 1    |        | Desired position of the elbow joint     |
| m4             | 1    |        | Desired position of the wrist_ver joint |
| m5             | 1    |        | Desired position of the wrist_rot joint |
| m6             | 1    |        | Desired position of the gripper joint   |
| `end_marker`   | 1    | `0xF0` |                                         |

#### `0x02` get position

Sent to the Arduino to request that it sends back the current braccio position.
The Arduino should responde with a _get position reply_ packet.

| name           | size | value  | description |
| -------------- | ---- | ------ | ----------- |
| `start_marker` | 1    | `0xFF` |             |
| `packet_id`    | 1    | `0x02` |             |
| `end_marker`   | 1    | `0xF0` |             |

#### `0x03` set speed

Sent to the Arduino to set the current movement speed.
The speed is actually the delay in milliseconds between each degree of movement of the servos, so it is expressed in ms/deg.

| name           | size | value  | description            |
| -------------- | ---- | ------ | ---------------------- |
| `start_marker` | 1    | `0xFF` |                        |
| `packet_id`    | 1    | `0x03` |                        |
| speed          | 1    |        | Desired movement speed |
| `end_marker`   | 1    | `0xF0` |                        |

### Arduino to Django

List of packets sent from the arduino to the django app

| id     | name               | description                       |
| ------ | ------------------ | --------------------------------- |
| `0x00` | hello              | Signals that the Arduino is ready |
| `0x02` | get position reply | Send the current braccio position |

#### `0x00` hello

This packet is sent to signal to the Dajango app that the Arduino is ready.

| name           | size | value  | description                                   |
| -------------- | ---- | ------ | --------------------------------------------- |
| `start_marker` | 1    | `0xFF` |                                               |
| `packet_id`    | 1    | `0x00` |                                               |
| payload        | 1    | `0xAA` | just a byte to check if the packet is correct |
| `end_marker`   | 1    | `0xF0` |                                               |

#### `0x02` get position reply

This packet is sent to respod to _get position_.

| name           | size | value  | description                            |
| -------------- | ---- | ------ | -------------------------------------- |
| `start_marker` | 1    | `0xFF` |                                        |
| `packet_id`    | 1    | `0x02` |                                        |
| m1             | 1    |        | Curent position of the base joint      |
| m2             | 1    |        | Curent position of the shoulder joint  |
| m3             | 1    |        | Curent position of the elbow joint     |
| m4             | 1    |        | Curent position of the wrist_ver joint |
| m5             | 1    |        | Curent position of the wrist_rot joint |
| m6             | 1    |        | Curent position of the gripper joint   |
| `end_marker`   | 1    | `0xF0` |                                        |
