# Braccino protocol

This file details the communication protocol between the Django app and the Arduino.

## Packet structure

Packets are sent using COBS encoding.
The byte `0x00` is the packet delimiter, it indicates the end of a packet.
Every packet is identified by an ID, wich is always the first field.

| name             | type | value  | description                                   |
| ---------------- | ---- | ------ | --------------------------------------------- |
| `packet_id`      | byte | `0x00` | Packet id                                     |
| packet fields... | ...  |        | Various packet fields depending on the packet |

## Data types

These are the data types used in the protocol.

| name | size (bytes) | signed | endianness    | description                                                             |
| ---- | ------------ | ------ | ------------- | ----------------------------------------------------------------------- |
| byte | 1            | no     | little-endian | An simple unsigned bytes, represents number from 0 to 255.              |
| bool | 1            |        |               | Represents a boolean value. 0x00 is interpreted as false, 0x01 as true. |

## Packet list

### Django to Arduino

List of packets sent from the Django app to the Arduino.

| id     | name           | description                                               |
| ------ | -------------- | --------------------------------------------------------- |
| `0x01` | set angles     | Sets the Braccio angles                                   |
| `0x02` | position query | Asks whether the Braccio has reached the desired position |
| `0x03` | set speed      | Sets the Braccio speed                                    |

#### `0x01` set angles

Sent to the Arduino to set the braccio position.
This packet does not expect any response.

| name      | type | value    | description                             |
| --------- | ---- | -------- | --------------------------------------- |
| packet_id | byte | `0x01`   |                                         |
| base      | byte | 0 - 180  | Desired position of the base joint      |
| shoulder  | byte | 15 - 165 | Desired position of the shoulder joint  |
| elbow     | byte | 0 - 180  | Desired position of the elbow joint     |
| wrist_ver | byte | 0 - 180  | Desired position of the wrist_ver joint |
| wrist_rot | byte | 0 - 180  | Desired position of the wrist_rot joint |
| gripper   | byte | 10 - 73  | Desired position of the gripper joint   |

#### `0x02` get position

Sent to the Arduino to request that it sends back whether it has reached the desired position.
The Arduino should respond with a _get position reply_ packet.

| name      | type | value  | description |
| --------- | ---- | ------ | ----------- |
| packet_id | byte | `0x02` |             |

#### `0x03` set speed

Sent to the Arduino to set the current movement speed.
The speed is actually the delay in milliseconds between each degree of movement of the servos, so it is expressed in ms/deg.

| name      | type | value  | description            |
| --------- | ---- | ------ | ---------------------- |
| packet_id | byte | `0x03` |                        |
| speed     | byte | 0 - 30 | Desired movement speed |

### Arduino to Django

List of packets sent from the arduino to the django app

| id     | name                 | description                                                  |
| ------ | -------------------- | ------------------------------------------------------------ |
| `0x00` | hello                | Signals that the Arduino is ready                            |
| `0x02` | position query reply | Returns whether the Braccio has reached the desired position |

#### `0x00` hello

This packet is sent to signal to the Django app that the Arduino is ready.

| name      | type | value  | description                                   |
| --------- | ---- | ------ | --------------------------------------------- |
| packet_id | byte | `0x00` |                                               |
| payload   | byte | `0xAA` | just a byte to check if the packet is correct |

#### `0x02` get position reply

This packet is sent in response to _get position_.

| name         | type | value  | description                                          |
| ------------ | ---- | ------ | ---------------------------------------------------- |
| start_marker | byte | `0xFF` |                                                      |
| on_position  | bool |        | Whether the Braccio has reached the desired position |
