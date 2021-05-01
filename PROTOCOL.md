# Braccino protocol

This file details the communication protocol between the Django server and the Arduino.

## General structure

Every packet starts with a start marker (`0x3C`), followed by the packet id, and ends with an end marker (`0x3E`).
The packet id allows to identify the different packets to handle their contents.

| name             | size    | value  | description                                     |
| ---------------- | ------- | ------ | ----------------------------------------------- |
| `start_marker`   | 1       | `0x3C` | Start marker, signifies the start of the packet |
| `packet_id`      | 1       | `0x00` | Packet id                                       |
| packet fields... | n bytes | ...    | Various packet fields depending on the packet   |
| `end_marker`     | 1       | `0x3E` | End marker, signifies the start of the packet   |

## Packet list

### Django to Arduino

List of packets sent from the django app to the arduino

| id     | name           | description                                                    |
| ------ | -------------- | -------------------------------------------------------------- |
| `0x00` | handshake ping | Sent to the Arduino to check id the correct sketch is uploaded |

#### `0x00` handshake ping

Sent to the Arduino to check id the correct sketch is uploaded.
If the correct sketch is uploaded, the Arduino will respond with the _handshake pong_ packet.
The packet has no fields.

| name           | size | value  | description |
| -------------- | ---- | ------ | ----------- |
| `start_marker` | 1    | `0x3C` | ...         |
| `packet_id`    | 1    | `0x00` | ...         |
| `end_marker`   | 1    | `0x3E` | ...         |

### Arduino to Django

List of packets sent from the arduino to the django app

| id     | name           | description            |
| ------ | -------------- | ---------------------- |
| `0x00` | handshake pong | Reply to the handshake |

#### `0x00` handshake pong

This packet is sent in response to the _handshake ping_ packet.

| name           | size | value  | description |
| -------------- | ---- | ------ | ----------- |
| `start_marker` | 1    | `0x3C` | ...         |
| `packet_id`    | 1    | `0x00` | ...         |
| `end_marker`   | 1    | `0x3E` | ...         |
