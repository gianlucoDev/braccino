/**
 * Represent the position of a Braccio
 */
struct braccioPosition {
  // Base degrees. Allowed values from 0 to 180 degrees.
  int base = 0;
  // Shoulder degrees. Allowed values from 15 to 165 degrees.
  int shoulder = 45;
  // Elbow degrees. Allowed values from 0 to 180 degrees.
  int elbow = 180;
  // Wrist vertical degrees. Allowed values from 0 to 180 degrees.
  int wrist_rot = 180;
  // Wrist rotation degrees. Allowed values from 0 to 180 degrees.
  int wrist_ver = 90;
  // Gripper degrees. Allowed values from 10 to 73 degrees; 10: the gripper is
  //   open, 73: the gripper is closed.
  int gripper = 10;
};

/**
 * Initialize braccio
 * All the servo motors will be positioned in the "safety" position:
 *   Base: 90 degrees
 *   Shoulder: 45 degrees
 *   Elbow: 180 degrees
 *   Wrist vertical: 180 degrees
 *   Wrist rotation: 90 degrees
 *   Gripper: 10 degrees
 */
void braccioBegin();

/**
 * Move all the servos one step closer to the target position.
 *
 * @param stepDelay milliseconds delay between the movement of each servo.
 * Allowed values from 10 to 30 msec.
 * @param targetPosition the position towards witch the Braccio should move.
 */
void braccioServoStep(int stepDelay, braccioPosition targetPosition);

/**
 * @returns the current position of the braccio.
 */
braccioPosition braccioCurrentPostion();
