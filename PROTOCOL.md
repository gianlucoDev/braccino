# Braccino protocol

This file details the communication protocol between the Django server and the Arduino.

## General structure

Every packet starts with a start marker (`0x3C`), followed by the packet id, and ends with an end marker (`0x3E`).
The packet id allows to identify the different packets to handle their contents.

| name             | size    | value  | description                                     |
| ---------------- | ------- | ------ | ----------------------------------------------- |
| `start_marker`   | 1       | `0x3C` | Start marker, signifies the start of the packet |
| `packet_id`      | 1       | `0x00` | Packet id                                       |
| packet fields... | n bytes |        | Various packet fields depending on the packet   |
| `end_marker`     | 1       | `0x3E` | End marker, signifies the start of the packet   |

## Packet list

### Django to Arduino

List of packets sent from the django app to the arduino

| id     | name         | description                |
| ------ | ------------ | -------------------------- |
| `0x01` | set position | Set the braccio position   |
| `0x01` | get position | Reads the braccio position |

#### `0x01` set position

Sent to the Arduino to set the braccio position.
This packet does not expect any response.

| name           | size | value  | description                          |
| -------------- | ---- | ------ | ------------------------------------ |
| `start_marker` | 1    | `0x3C` |                                      |
| `packet_id`    | 1    | `0x01` |                                      |
| m1             | 1    |        | Desired position of the first joint  |
| m2             | 1    |        | Desired position of the second joint |
| m3             | 1    |        | Desired position of the third joint  |
| m4             | 1    |        | Desired position of the fourth joint |
| m5             | 1    |        | Desired position of the fifth joint  |
| m6             | 1    |        | Desired position of the sixth joint  |
| `end_marker`   | 1    | `0x3E` |                                      |

### `0x02` get position

Sent to the Arduino to request that it sends back the current braccio position.
The Arduino should responde with a _get position reply_ packet.

| name           | size | value  | description |
| -------------- | ---- | ------ | ----------- |
| `start_marker` | 1    | `0x3C` |             |
| `packet_id`    | 1    | `0x00` |             |
| `end_marker`   | 1    | `0x3E` |             |

### Arduino to Django

List of packets sent from the arduino to the django app

| id     | name               | description                       |
| ------ | ------------------ | --------------------------------- |
| `0x00` | hello              | Signals that the Arduino is ready |
| `0x02` | get position reply | Send the current braccio position |

#### `0x00` handshake pong

This packet is sent to signal to the Dajango app that the Arduino is ready.

| name           | size | value  | description |
| -------------- | ---- | ------ | ----------- |
| `start_marker` | 1    | `0x3C` |             |
| `packet_id`    | 1    | `0x00` |             |
| `end_marker`   | 1    | `0x3E` |             |

#### `0x02` get position reply

This packet is sent to respod to _get position_.

| name           | size | value  | description                         |
| -------------- | ---- | ------ | ----------------------------------- |
| `start_marker` | 1    | `0x3C` |                                     |
| `packet_id`    | 1    | `0x02` |                                     |
| m1             | 1    |        | Curent position of the first joint  |
| m2             | 1    |        | Curent position of the second joint |
| m3             | 1    |        | Curent position of the third joint  |
| m4             | 1    |        | Curent position of the fourth joint |
| m5             | 1    |        | Curent position of the fifth joint  |
| m6             | 1    |        | Curent position of the sixth joint  |
| `end_marker`   | 1    | `0x3E` |                                     |
