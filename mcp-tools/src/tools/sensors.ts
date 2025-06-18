import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { FastAPIClient } from '../bridge/api-client.js';
import { Logger } from '../utils/logger.js';

/**
 * Sensor data tools for monitoring drone telemetry
 */
export class SensorTools {
  private client: FastAPIClient;
  private logger;

  constructor(client: FastAPIClient, logger: Logger) {
    this.client = client;
    this.logger = logger.createComponentLogger('SensorTools');
  }

  /**
   * Get all sensor tools
   */
  getTools(): Tool[] {
    return [
      this.getDroneBatteryTool(),
      this.getDroneTemperatureTool(),
      this.getDroneFlightTimeTool(),
      this.getDroneBarometerTool(),
      this.getDroneDistanceTofTool(),
      this.getDroneAccelerationTool(),
      this.getDroneVelocityTool(),
      this.getDroneAttitudeTool(),
      this.getDroneSensorSummaryTool(),
    ];
  }

  /**
   * Tool: Get battery level
   */
  private getDroneBatteryTool(): Tool {
    return {
      name: 'drone_battery',
      description: 'Get the current battery level of the drone as a percentage (0-100%).',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get drone temperature
   */
  private getDroneTemperatureTool(): Tool {
    return {
      name: 'drone_temperature',
      description: 'Get the current internal temperature of the drone in Celsius.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get flight time
   */
  private getDroneFlightTimeTool(): Tool {
    return {
      name: 'drone_flight_time',
      description: 'Get the cumulative flight time of the drone in seconds.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get barometer reading
   */
  private getDroneBarometerTool(): Tool {
    return {
      name: 'drone_barometer',
      description: 'Get the current barometric pressure reading from the drone in hPa.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get ToF sensor distance
   */
  private getDroneDistanceTofTool(): Tool {
    return {
      name: 'drone_distance_tof',
      description: 'Get the distance measurement from the Time-of-Flight sensor in millimeters.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get acceleration data
   */
  private getDroneAccelerationTool(): Tool {
    return {
      name: 'drone_acceleration',
      description: 'Get the current acceleration values for X, Y, and Z axes in g-force.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get velocity data
   */
  private getDroneVelocityTool(): Tool {
    return {
      name: 'drone_velocity',
      description: 'Get the current velocity values for X, Y, and Z axes in cm/s.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get attitude data
   */
  private getDroneAttitudeTool(): Tool {
    return {
      name: 'drone_attitude',
      description: 'Get the current attitude (orientation) of the drone including pitch, roll, and yaw angles in degrees.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Tool: Get comprehensive sensor summary
   */
  private getDroneSensorSummaryTool(): Tool {
    return {
      name: 'drone_sensor_summary',
      description: 'Get a comprehensive summary of all drone sensor data including battery, position, attitude, and environmental data.',
      inputSchema: {
        type: 'object',
        properties: {},
        required: [],
      },
    };
  }

  /**
   * Execute sensor tool
   */
  async executeTool(name: string, args: unknown): Promise<unknown> {
    this.logger.info(`Executing sensor tool: ${name}`, { args });

    try {
      switch (name) {
        case 'drone_battery':
          return await this.executeBattery();
        case 'drone_temperature':
          return await this.executeTemperature();
        case 'drone_flight_time':
          return await this.executeFlightTime();
        case 'drone_barometer':
          return await this.executeBarometer();
        case 'drone_distance_tof':
          return await this.executeDistanceTof();
        case 'drone_acceleration':
          return await this.executeAcceleration();
        case 'drone_velocity':
          return await this.executeVelocity();
        case 'drone_attitude':
          return await this.executeAttitude();
        case 'drone_sensor_summary':
          return await this.executeSensorSummary();
        default:
          throw new Error(`Unknown sensor tool: ${name}`);
      }
    } catch (error) {
      this.logger.error(`Sensor tool ${name} failed`, error);
      throw error;
    }
  }

  /**
   * Execute battery level check
   */
  private async executeBattery(): Promise<unknown> {
    this.logger.info('Getting battery level...');

    const data = await this.client.getBattery();
    const batteryLevel = data.battery;

    this.logger.info(`Battery level: ${batteryLevel}%`);

    return {
      success: true,
      message: `Battery level: ${batteryLevel}%`,
      data: {
        battery: batteryLevel,
        status: this.getBatteryStatus(batteryLevel),
        warning: this.getBatteryWarning(batteryLevel),
        estimated_flight_time: this.estimateFlightTime(batteryLevel),
      },
    };
  }

  /**
   * Execute temperature check
   */
  private async executeTemperature(): Promise<unknown> {
    this.logger.info('Getting drone temperature...');

    const data = await this.client.getTemperature();
    const temperature = data.temperature;

    this.logger.info(`Drone temperature: ${temperature}°C`);

    return {
      success: true,
      message: `Drone temperature: ${temperature}°C`,
      data: {
        temperature: temperature,
        temperature_fahrenheit: Math.round((temperature * 9/5) + 32),
        status: this.getTemperatureStatus(temperature),
        warning: this.getTemperatureWarning(temperature),
      },
    };
  }

  /**
   * Execute flight time check
   */
  private async executeFlightTime(): Promise<unknown> {
    this.logger.info('Getting cumulative flight time...');

    const data = await this.client.getFlightTime();
    const flightTime = data.flight_time;

    this.logger.info(`Cumulative flight time: ${flightTime}s`);

    return {
      success: true,
      message: `Cumulative flight time: ${this.formatFlightTime(flightTime)}`,
      data: {
        flight_time_seconds: flightTime,
        flight_time_minutes: Math.floor(flightTime / 60),
        flight_time_formatted: this.formatFlightTime(flightTime),
      },
    };
  }

  /**
   * Execute barometer reading
   */
  private async executeBarometer(): Promise<unknown> {
    this.logger.info('Getting barometer reading...');

    const data = await this.client.getBarometer();
    const barometer = data.barometer;

    this.logger.info(`Barometer: ${barometer} hPa`);

    return {
      success: true,
      message: `Barometric pressure: ${barometer} hPa`,
      data: {
        barometer: barometer,
        pressure_status: this.getPressureStatus(barometer),
        altitude_estimate: this.estimateAltitudeFromPressure(barometer),
      },
    };
  }

  /**
   * Execute ToF sensor distance
   */
  private async executeDistanceTof(): Promise<unknown> {
    this.logger.info('Getting ToF sensor distance...');

    const data = await this.client.getDistanceTof();
    const distance = data.distance_tof;

    this.logger.info(`ToF distance: ${distance}mm`);

    return {
      success: true,
      message: `ToF sensor distance: ${distance}mm (${(distance / 10).toFixed(1)}cm)`,
      data: {
        distance_mm: distance,
        distance_cm: Math.round(distance / 10),
        distance_meters: (distance / 1000).toFixed(3),
        proximity_warning: distance < 300 ? 'Very close to obstacle!' : distance < 500 ? 'Close to obstacle' : 'Clear',
      },
    };
  }

  /**
   * Execute acceleration reading
   */
  private async executeAcceleration(): Promise<unknown> {
    this.logger.info('Getting acceleration data...');

    const data = await this.client.getAcceleration();
    const acceleration = data.acceleration;

    this.logger.info(`Acceleration: X=${acceleration.x}g, Y=${acceleration.y}g, Z=${acceleration.z}g`);

    return {
      success: true,
      message: `Acceleration: X=${acceleration.x}g, Y=${acceleration.y}g, Z=${acceleration.z}g`,
      data: {
        acceleration,
        magnitude: Math.sqrt(acceleration.x ** 2 + acceleration.y ** 2 + acceleration.z ** 2).toFixed(3),
        stability: this.getStabilityStatus(acceleration),
      },
    };
  }

  /**
   * Execute velocity reading
   */
  private async executeVelocity(): Promise<unknown> {
    this.logger.info('Getting velocity data...');

    const data = await this.client.getVelocity();
    const velocity = data.velocity;

    this.logger.info(`Velocity: X=${velocity.x}cm/s, Y=${velocity.y}cm/s, Z=${velocity.z}cm/s`);

    return {
      success: true,
      message: `Velocity: X=${velocity.x}cm/s, Y=${velocity.y}cm/s, Z=${velocity.z}cm/s`,
      data: {
        velocity,
        speed: Math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2).toFixed(1),
        movement_status: this.getMovementStatus(velocity),
      },
    };
  }

  /**
   * Execute attitude reading
   */
  private async executeAttitude(): Promise<unknown> {
    this.logger.info('Getting attitude data...');

    const data = await this.client.getAttitude();
    const attitude = data.attitude;

    this.logger.info(`Attitude: Pitch=${attitude.pitch}°, Roll=${attitude.roll}°, Yaw=${attitude.yaw}°`);

    return {
      success: true,
      message: `Attitude: Pitch=${attitude.pitch}°, Roll=${attitude.roll}°, Yaw=${attitude.yaw}°`,
      data: {
        attitude,
        orientation_status: this.getOrientationStatus(attitude),
        stability_warning: this.getAttitudeWarning(attitude),
      },
    };
  }

  /**
   * Execute comprehensive sensor summary
   */
  private async executeSensorSummary(): Promise<unknown> {
    this.logger.info('Getting comprehensive sensor summary...');

    try {
      const [
        status,
        battery,
        temperature,
        flightTime,
        barometer,
        distanceTof,
        acceleration,
        velocity,
        attitude,
      ] = await Promise.all([
        this.client.getStatus(),
        this.client.getBattery(),
        this.client.getTemperature(),
        this.client.getFlightTime(),
        this.client.getBarometer(),
        this.client.getDistanceTof(),
        this.client.getAcceleration(),
        this.client.getVelocity(),
        this.client.getAttitude(),
      ]);

      const summary = {
        connection: {
          connected: status.connected,
          status: status.connected ? 'Connected' : 'Disconnected',
        },
        power: {
          battery: battery.battery,
          status: this.getBatteryStatus(battery.battery),
          estimated_flight_time: this.estimateFlightTime(battery.battery),
        },
        environment: {
          temperature: temperature.temperature,
          temperature_status: this.getTemperatureStatus(temperature.temperature),
          barometer: barometer.barometer,
          pressure_status: this.getPressureStatus(barometer.barometer),
        },
        position: {
          height: status.height,
          flight_status: status.height > 10 ? 'Flying' : 'On Ground',
          tof_distance: distanceTof.distance_tof,
          proximity_status: distanceTof.distance_tof < 300 ? 'Very Close' : distanceTof.distance_tof < 500 ? 'Close' : 'Clear',
        },
        motion: {
          acceleration: acceleration.acceleration,
          velocity: velocity.velocity,
          attitude: attitude.attitude,
          stability: this.getStabilityStatus(acceleration.acceleration),
          speed: Math.sqrt(velocity.velocity.x ** 2 + velocity.velocity.y ** 2 + velocity.velocity.z ** 2).toFixed(1),
        },
        flight_data: {
          cumulative_flight_time: flightTime.flight_time,
          flight_time_formatted: this.formatFlightTime(flightTime.flight_time),
        },
        health_summary: this.generateHealthSummary({
          battery: battery.battery,
          temperature: temperature.temperature,
          connected: status.connected,
          flying: status.height > 10,
        }),
      };

      this.logger.info('Sensor summary compiled successfully');

      return {
        success: true,
        message: 'Comprehensive sensor data retrieved successfully',
        data: summary,
      };
    } catch (error) {
      this.logger.error('Failed to get complete sensor summary', error);
      throw error;
    }
  }

  // Helper methods for status interpretation

  private getBatteryStatus(battery: number): string {
    if (battery >= 75) return 'Excellent';
    if (battery >= 50) return 'Good';
    if (battery >= 30) return 'Fair';
    if (battery >= 15) return 'Low';
    return 'Critical';
  }

  private getBatteryWarning(battery: number): string | null {
    if (battery <= 15) return 'CRITICAL: Land immediately!';
    if (battery <= 30) return 'WARNING: Consider landing soon';
    return null;
  }

  private estimateFlightTime(battery: number): string {
    const maxFlightTime = 13; // Tello EDU max flight time in minutes
    const estimatedMinutes = Math.floor((battery / 100) * maxFlightTime);
    return `~${estimatedMinutes} minutes`;
  }

  private getTemperatureStatus(temp: number): string {
    if (temp < 0) return 'Very Cold';
    if (temp < 10) return 'Cold';
    if (temp < 40) return 'Normal';
    if (temp < 60) return 'Warm';
    if (temp < 80) return 'Hot';
    return 'Very Hot';
  }

  private getTemperatureWarning(temp: number): string | null {
    if (temp > 80) return 'WARNING: Very high temperature - consider landing';
    if (temp < 0) return 'WARNING: Very low temperature - monitor performance';
    return null;
  }

  private formatFlightTime(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  }

  private getPressureStatus(pressure: number): string {
    if (pressure > 1030) return 'High Pressure';
    if (pressure > 1013) return 'Above Average';
    if (pressure > 980) return 'Normal';
    if (pressure > 950) return 'Low Pressure';
    return 'Very Low Pressure';
  }

  private estimateAltitudeFromPressure(pressure: number): string {
    // Rough estimate using standard atmosphere
    const seaLevelPressure = 1013.25;
    const altitude = (1 - Math.pow(pressure / seaLevelPressure, 0.1903)) * 44330;
    return `~${Math.round(altitude)}m above sea level`;
  }

  private getStabilityStatus(acceleration: { x: number; y: number; z: number }): string {
    const magnitude = Math.sqrt(acceleration.x ** 2 + acceleration.y ** 2 + acceleration.z ** 2);
    if (magnitude < 0.5) return 'Very Stable';
    if (magnitude < 1.0) return 'Stable';
    if (magnitude < 2.0) return 'Moderate';
    if (magnitude < 3.0) return 'Unstable';
    return 'Very Unstable';
  }

  private getMovementStatus(velocity: { x: number; y: number; z: number }): string {
    const speed = Math.sqrt(velocity.x ** 2 + velocity.y ** 2 + velocity.z ** 2);
    if (speed < 5) return 'Hovering/Still';
    if (speed < 20) return 'Slow Movement';
    if (speed < 50) return 'Moderate Speed';
    if (speed < 100) return 'Fast Movement';
    return 'Very Fast Movement';
  }

  private getOrientationStatus(attitude: { pitch: number; roll: number; yaw: number }): string {
    const maxTilt = Math.max(Math.abs(attitude.pitch), Math.abs(attitude.roll));
    if (maxTilt < 5) return 'Level';
    if (maxTilt < 15) return 'Slight Tilt';
    if (maxTilt < 30) return 'Moderate Tilt';
    if (maxTilt < 45) return 'Steep Tilt';
    return 'Extreme Tilt';
  }

  private getAttitudeWarning(attitude: { pitch: number; roll: number; yaw: number }): string | null {
    const maxTilt = Math.max(Math.abs(attitude.pitch), Math.abs(attitude.roll));
    if (maxTilt > 45) return 'WARNING: Extreme tilt detected!';
    if (maxTilt > 30) return 'CAUTION: Steep tilt detected';
    return null;
  }

  private generateHealthSummary(params: {
    battery: number;
    temperature: number;
    connected: boolean;
    flying: boolean;
  }): string {
    const issues = [];
    
    if (!params.connected) issues.push('🔴 Not Connected');
    if (params.battery <= 15) issues.push('🔋 Critical Battery');
    else if (params.battery <= 30) issues.push('🟡 Low Battery');
    if (params.temperature > 80) issues.push('🌡️ High Temperature');
    if (params.temperature < 0) issues.push('❄️ Cold Temperature');
    
    if (issues.length === 0) {
      return params.flying ? '✅ All systems normal - Flying' : '✅ All systems normal - Ready for flight';
    } else {
      return `⚠️ Issues: ${issues.join(', ')}`;
    }
  }
}