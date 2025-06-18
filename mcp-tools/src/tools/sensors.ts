import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { EnhancedFastAPIClient } from '../bridge/enhanced-api-client';
import type { ToolDefinition } from './registry';

// Validation schemas for sensor tools
const EmptyArgsSchema = z.object({});

const SensorDetailsArgsSchema = z.object({
  includeHistory: z.boolean().optional().default(false),
  units: z.enum(['metric', 'imperial']).optional().default('metric'),
});

// Create sensor data tools
export function createSensorTools(apiClient: EnhancedFastAPIClient): ToolDefinition[] {
  return [
    {
      tool: {
        name: 'drone_battery',
        description: 'Get current battery level and power status. Critical for flight safety monitoring.',
        inputSchema: {
          type: 'object',
          properties: {
            detailed: {
              type: 'boolean',
              description: 'Include detailed battery information',
              default: false,
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { detailed?: boolean }) => {
        try {
          const result = await apiClient.getBattery();
          
          if (!result.success || result.data === undefined) {
            throw new Error(result.message || 'No battery data available');
          }

          const batteryLevel = result.data.battery || 0;
          const status = this.getBatteryStatus(batteryLevel);
          
          const response = {
            success: true,
            message: `🔋 Battery Level: ${batteryLevel}% - ${status.message}`,
            timestamp: new Date().toISOString(),
            battery: {
              level: batteryLevel,
              percentage: `${batteryLevel}%`,
              status: status.level,
              remainingTime: this.getEstimatedFlightTime(batteryLevel),
            },
            safetyAlert: status.alert,
            recommendations: status.recommendations,
            data: result.data,
          };

          if (args.detailed) {
            return {
              ...response,
              detailedInfo: {
                voltageEstimate: `${(3.7 * batteryLevel / 100).toFixed(1)}V`,
                powerConsumption: this.getPowerConsumption(batteryLevel),
                chargingAdvice: this.getChargingAdvice(batteryLevel),
                batteryHealth: this.getBatteryHealth(batteryLevel),
              },
            };
          }

          return response;
        } catch (error) {
          return {
            success: false,
            message: `❌ Battery check error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            criticalWarning: 'Unable to check battery - LAND IMMEDIATELY if drone is flying',
            troubleshooting: [
              'Check drone connection',
              'Verify sensor functionality',
              'Land drone safely if battery status unknown'
            ]
          };
        }
      },
      validator: z.object({ detailed: z.boolean().optional() }),
      category: 'sensors',
      description: 'Monitors drone battery level and power status',
      examples: [
        'drone_battery() - Get current battery level',
        'drone_battery({"detailed": true}) - Get detailed battery information'
      ],
    },

    {
      tool: {
        name: 'drone_temperature',
        description: 'Get drone internal temperature. Important for monitoring system health and preventing overheating.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['celsius', 'fahrenheit'],
              description: 'Temperature unit',
              default: 'celsius',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { unit?: 'celsius' | 'fahrenheit' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data) {
            throw new Error(result.message || 'No sensor data available');
          }

          const tempCelsius = result.data.temperature || 0;
          const tempFahrenheit = (tempCelsius * 9/5) + 32;
          const displayTemp = args.unit === 'fahrenheit' ? tempFahrenheit : tempCelsius;
          const unit = args.unit === 'fahrenheit' ? '°F' : '°C';

          const status = this.getTemperatureStatus(tempCelsius);

          return {
            success: true,
            message: `🌡️ Drone Temperature: ${displayTemp.toFixed(1)}${unit} - ${status.message}`,
            timestamp: new Date().toISOString(),
            temperature: {
              value: displayTemp.toFixed(1),
              unit: unit,
              celsius: tempCelsius.toFixed(1),
              fahrenheit: tempFahrenheit.toFixed(1),
              status: status.level,
            },
            operatingRange: {
              normal: args.unit === 'fahrenheit' ? '32-104°F' : '0-40°C',
              warning: args.unit === 'fahrenheit' ? '104-122°F' : '40-50°C',
              critical: args.unit === 'fahrenheit' ? '>122°F' : '>50°C',
            },
            recommendations: status.recommendations,
            safetyAlert: status.alert,
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Temperature reading error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            warning: 'Unable to monitor drone temperature - be aware of overheating risk',
            troubleshooting: [
              'Check sensor connectivity',
              'Verify drone system status',
              'Monitor for signs of overheating (reduced performance)'
            ]
          };
        }
      },
      validator: z.object({ unit: z.enum(['celsius', 'fahrenheit']).optional() }),
      category: 'sensors',
      description: 'Monitors drone internal temperature for thermal management',
      examples: [
        'drone_temperature() - Get temperature in Celsius',
        'drone_temperature({"unit": "fahrenheit"}) - Get temperature in Fahrenheit'
      ],
    },

    {
      tool: {
        name: 'drone_flight_time',
        description: 'Get cumulative flight time for current session. Useful for maintenance and battery monitoring.',
        inputSchema: {
          type: 'object',
          properties: {},
          additionalProperties: false,
        },
      },
      handler: async (args: z.infer<typeof EmptyArgsSchema>) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data) {
            throw new Error(result.message || 'No sensor data available');
          }

          const flightTimeSeconds = result.data.flight_time || 0;
          const minutes = Math.floor(flightTimeSeconds / 60);
          const seconds = flightTimeSeconds % 60;

          return {
            success: true,
            message: `⏱️ Flight Time: ${minutes}m ${seconds}s`,
            timestamp: new Date().toISOString(),
            flightTime: {
              total: flightTimeSeconds,
              display: `${minutes}m ${seconds}s`,
              minutes: minutes,
              seconds: seconds,
            },
            sessionInfo: {
              startTime: 'Session start (takeoff)',
              currentSession: true,
              continuousTracking: 'Since last takeoff',
            },
            maintenanceInfo: {
              recommendedMaxFlight: '25-30 minutes per session',
              batteryImpact: 'Longer flights reduce battery life',
              recommendation: flightTimeSeconds > 1500 ? 'Consider landing soon for battery health' : 'Normal flight duration',
            },
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Flight time error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            note: 'Flight time tracking may not be available',
            troubleshooting: [
              'Check drone connection',
              'Verify sensor data availability',
              'Flight time resets on each takeoff'
            ]
          };
        }
      },
      validator: EmptyArgsSchema,
      category: 'sensors',
      description: 'Tracks cumulative flight time for current session',
      examples: [
        'drone_flight_time() - Get current session flight time'
      ],
    },

    {
      tool: {
        name: 'drone_barometer',
        description: 'Get barometric pressure reading. Used for altitude calculation and weather monitoring.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['hPa', 'inHg', 'mmHg'],
              description: 'Pressure unit',
              default: 'hPa',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { unit?: 'hPa' | 'inHg' | 'mmHg' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data) {
            throw new Error(result.message || 'No sensor data available');
          }

          const pressureHPa = result.data.barometer || 1013.25;
          const pressure = this.convertPressure(pressureHPa, args.unit || 'hPa');
          const unit = args.unit || 'hPa';

          const conditions = this.getWeatherConditions(pressureHPa);

          return {
            success: true,
            message: `📊 Barometric Pressure: ${pressure.toFixed(2)} ${unit} - ${conditions.description}`,
            timestamp: new Date().toISOString(),
            barometer: {
              value: pressure.toFixed(2),
              unit: unit,
              hPa: pressureHPa.toFixed(2),
              inHg: this.convertPressure(pressureHPa, 'inHg').toFixed(2),
              mmHg: this.convertPressure(pressureHPa, 'mmHg').toFixed(1),
            },
            weatherInfo: {
              conditions: conditions.description,
              trend: conditions.trend,
              flightSuitability: conditions.flightAdvice,
            },
            referenceValues: {
              seaLevel: '1013.25 hPa (standard)',
              high: '>1020 hPa (clear weather)',
              low: '<1000 hPa (poor weather)',
            },
            altitudeNote: 'Pressure decreases ~1.2 hPa per 10m altitude gain',
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Barometer reading error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            impact: 'Altitude calculations may be less accurate',
            troubleshooting: [
              'Check barometric sensor functionality',
              'Verify sensor calibration',
              'Use GPS altitude as backup'
            ]
          };
        }
      },
      validator: z.object({ unit: z.enum(['hPa', 'inHg', 'mmHg']).optional() }),
      category: 'sensors',
      description: 'Reads barometric pressure for altitude and weather data',
      examples: [
        'drone_barometer() - Get pressure in hPa',
        'drone_barometer({"unit": "inHg"}) - Get pressure in inches of mercury'
      ],
    },

    {
      tool: {
        name: 'drone_distance_tof',
        description: 'Get Time-of-Flight distance sensor reading. Shows distance to nearest object below drone.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['cm', 'm', 'ft'],
              description: 'Distance unit',
              default: 'cm',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { unit?: 'cm' | 'm' | 'ft' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data) {
            throw new Error(result.message || 'No sensor data available');
          }

          const distanceCm = result.data.distance_tof || 0;
          const distance = this.convertDistance(distanceCm, args.unit || 'cm');
          const unit = args.unit || 'cm';

          const proximity = this.getProximityStatus(distanceCm);

          return {
            success: true,
            message: `📏 Ground Distance: ${distance.toFixed(1)} ${unit} - ${proximity.message}`,
            timestamp: new Date().toISOString(),
            distance: {
              value: distance.toFixed(1),
              unit: unit,
              cm: distanceCm,
              m: (distanceCm / 100).toFixed(2),
              ft: (distanceCm / 30.48).toFixed(2),
            },
            proximityStatus: {
              level: proximity.level,
              warning: proximity.warning,
              recommendation: proximity.recommendation,
            },
            sensorInfo: {
              type: 'Time-of-Flight (ToF)',
              range: '10-1200cm typical',
              accuracy: '±3cm',
              purpose: 'Ground proximity detection',
            },
            safetyAlert: proximity.alert,
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Distance sensor error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            criticalWarning: 'Ground proximity unknown - exercise extreme caution',
            troubleshooting: [
              'Check ToF sensor functionality',
              'Verify sensor is not obstructed',
              'Use visual reference for ground distance'
            ]
          };
        }
      },
      validator: z.object({ unit: z.enum(['cm', 'm', 'ft']).optional() }),
      category: 'sensors',
      description: 'Measures distance to ground using Time-of-Flight sensor',
      examples: [
        'drone_distance_tof() - Get ground distance in cm',
        'drone_distance_tof({"unit": "m"}) - Get distance in meters'
      ],
    },

    {
      tool: {
        name: 'drone_acceleration',
        description: 'Get 3-axis acceleration data (X, Y, Z). Shows drone movement and stability.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['g', 'ms2'],
              description: 'Acceleration unit (g-force or m/s²)',
              default: 'g',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { unit?: 'g' | 'ms2' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data || !result.data.acceleration) {
            throw new Error(result.message || 'No acceleration data available');
          }

          const accel = result.data.acceleration;
          const unit = args.unit || 'g';
          const conversionFactor = unit === 'ms2' ? 9.81 : 1;

          const magnitude = Math.sqrt(accel.x * accel.x + accel.y * accel.y + accel.z * accel.z);
          const stability = this.getStabilityStatus(magnitude);

          return {
            success: true,
            message: `📊 Acceleration: X=${(accel.x * conversionFactor).toFixed(2)}, Y=${(accel.y * conversionFactor).toFixed(2)}, Z=${(accel.z * conversionFactor).toFixed(2)} ${unit}`,
            timestamp: new Date().toISOString(),
            acceleration: {
              x: (accel.x * conversionFactor).toFixed(2),
              y: (accel.y * conversionFactor).toFixed(2),
              z: (accel.z * conversionFactor).toFixed(2),
              magnitude: (magnitude * conversionFactor).toFixed(2),
              unit: unit,
            },
            axisInfo: {
              x: 'Left/Right acceleration',
              y: 'Forward/Backward acceleration',
              z: 'Up/Down acceleration (includes gravity)',
            },
            stability: {
              status: stability.level,
              description: stability.description,
              recommendation: stability.recommendation,
            },
            reference: {
              hover: '~1g in Z-axis (gravity)',
              movement: 'Changes indicate acceleration/deceleration',
              stability: '<0.5g variations indicate stable flight',
            },
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Acceleration sensor error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            impact: 'Flight stability monitoring unavailable',
            troubleshooting: [
              'Check accelerometer functionality',
              'Verify sensor calibration',
              'Monitor drone visually for stability'
            ]
          };
        }
      },
      validator: z.object({ unit: z.enum(['g', 'ms2']).optional() }),
      category: 'sensors',
      description: 'Reads 3-axis acceleration data for stability monitoring',
      examples: [
        'drone_acceleration() - Get acceleration in g-force',
        'drone_acceleration({"unit": "ms2"}) - Get acceleration in m/s²'
      ],
    },

    {
      tool: {
        name: 'drone_velocity',
        description: 'Get current velocity in 3D space (X, Y, Z components). Shows drone movement speed and direction.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['cms', 'ms', 'kmh', 'mph'],
              description: 'Velocity unit',
              default: 'cms',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { unit?: 'cms' | 'ms' | 'kmh' | 'mph' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data || !result.data.velocity) {
            throw new Error(result.message || 'No velocity data available');
          }

          const vel = result.data.velocity;
          const velConverted = this.convertVelocity(vel, args.unit || 'cms');
          const unit = args.unit || 'cms';

          const speed = Math.sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);
          const speedConverted = this.convertSpeed(speed, args.unit || 'cms');

          const movement = this.getMovementDescription(vel);

          return {
            success: true,
            message: `🚁 Velocity: ${speedConverted.toFixed(1)} ${unit} - ${movement.description}`,
            timestamp: new Date().toISOString(),
            velocity: {
              x: velConverted.x.toFixed(1),
              y: velConverted.y.toFixed(1),
              z: velConverted.z.toFixed(1),
              speed: speedConverted.toFixed(1),
              unit: unit,
            },
            movementInfo: {
              direction: movement.direction,
              speed: movement.speedLevel,
              components: {
                horizontal: Math.sqrt(vel.x * vel.x + vel.y * vel.y).toFixed(1),
                vertical: Math.abs(vel.z).toFixed(1),
              },
            },
            axisInfo: {
              x: vel.x > 0 ? 'Moving right' : vel.x < 0 ? 'Moving left' : 'No lateral movement',
              y: vel.y > 0 ? 'Moving forward' : vel.y < 0 ? 'Moving backward' : 'No forward/back movement',
              z: vel.z > 0 ? 'Ascending' : vel.z < 0 ? 'Descending' : 'Maintaining altitude',
            },
            speedReference: {
              stationary: '0 cm/s',
              slow: '1-10 cm/s',
              normal: '10-50 cm/s',
              fast: '>50 cm/s',
            },
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Velocity sensor error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            impact: 'Movement speed monitoring unavailable',
            troubleshooting: [
              'Check velocity sensor functionality',
              'Verify GPS or optical flow sensors',
              'Monitor movement visually'
            ]
          };
        }
      },
      validator: z.object({ unit: z.enum(['cms', 'ms', 'kmh', 'mph']).optional() }),
      category: 'sensors',
      description: 'Measures current velocity in 3D space',
      examples: [
        'drone_velocity() - Get velocity in cm/s',
        'drone_velocity({"unit": "ms"}) - Get velocity in m/s'
      ],
    },

    {
      tool: {
        name: 'drone_attitude',
        description: 'Get drone attitude (orientation): pitch, roll, and yaw angles. Shows drone tilt and rotation.',
        inputSchema: {
          type: 'object',
          properties: {
            unit: {
              type: 'string',
              enum: ['degrees', 'radians'],
              description: 'Angle unit',
              default: 'degrees',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { unit?: 'degrees' | 'radians' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data || !result.data.attitude) {
            throw new Error(result.message || 'No attitude data available');
          }

          const attitude = result.data.attitude;
          const unit = args.unit || 'degrees';
          const conversionFactor = unit === 'radians' ? Math.PI / 180 : 1;

          const stability = this.getAttitudeStability(attitude);

          return {
            success: true,
            message: `🧭 Attitude: Pitch=${(attitude.pitch * conversionFactor).toFixed(1)}°, Roll=${(attitude.roll * conversionFactor).toFixed(1)}°, Yaw=${(attitude.yaw * conversionFactor).toFixed(1)}°`,
            timestamp: new Date().toISOString(),
            attitude: {
              pitch: (attitude.pitch * conversionFactor).toFixed(1),
              roll: (attitude.roll * conversionFactor).toFixed(1),
              yaw: (attitude.yaw * conversionFactor).toFixed(1),
              unit: unit,
            },
            orientation: {
              pitch: this.getPitchDescription(attitude.pitch),
              roll: this.getRollDescription(attitude.roll),
              yaw: this.getYawDescription(attitude.yaw),
            },
            stability: {
              status: stability.level,
              description: stability.description,
              recommendation: stability.recommendation,
            },
            angleDefinitions: {
              pitch: 'Nose up/down tilt (positive = nose up)',
              roll: 'Left/right tilt (positive = right side down)',
              yaw: 'Rotation around vertical axis (heading)',
            },
            referenceValues: {
              level: '0° pitch and roll = level flight',
              maxSafe: '±30° for pitch/roll in normal flight',
              yaw: '0-360° compass heading',
            },
            data: result.data,
          };
        } catch (error) {
          return {
            success: false,
            message: `❌ Attitude sensor error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            criticalWarning: 'Drone orientation unknown - monitor visually',
            troubleshooting: [
              'Check IMU/gyroscope functionality',
              'Verify sensor calibration',
              'Monitor drone orientation visually'
            ]
          };
        }
      },
      validator: z.object({ unit: z.enum(['degrees', 'radians']).optional() }),
      category: 'sensors',
      description: 'Reads drone orientation angles (pitch, roll, yaw)',
      examples: [
        'drone_attitude() - Get attitude in degrees',
        'drone_attitude({"unit": "radians"}) - Get attitude in radians'
      ],
    },

    {
      tool: {
        name: 'drone_sensor_summary',
        description: 'Get comprehensive summary of all sensor data in one request. Perfect for overall status monitoring.',
        inputSchema: {
          type: 'object',
          properties: {
            format: {
              type: 'string',
              enum: ['detailed', 'compact'],
              description: 'Summary format',
              default: 'detailed',
            },
          },
          additionalProperties: false,
        },
      },
      handler: async (args: { format?: 'detailed' | 'compact' }) => {
        try {
          const result = await apiClient.getSensorData();
          
          if (!result.success || !result.data) {
            throw new Error(result.message || 'No sensor data available');
          }

          const data = result.data;
          const overallStatus = this.getOverallStatus(data);

          const summary = {
            success: true,
            message: `📊 Sensor Summary - Overall Status: ${overallStatus.level}`,
            timestamp: new Date().toISOString(),
            overallStatus: overallStatus,
            sensors: {
              battery: {
                level: `${data.battery || 0}%`,
                status: this.getBatteryStatus(data.battery || 0).level,
              },
              temperature: {
                value: `${data.temperature || 0}°C`,
                status: this.getTemperatureStatus(data.temperature || 0).level,
              },
              height: {
                value: `${data.height || 0}cm`,
                status: 'normal',
              },
              flightTime: {
                value: `${Math.floor((data.flight_time || 0) / 60)}m ${(data.flight_time || 0) % 60}s`,
                session: 'current',
              },
            },
            quickStatus: {
              flyable: overallStatus.flyable,
              warnings: overallStatus.warnings,
              criticalIssues: overallStatus.critical,
            },
            data: result.data,
          };

          if (args.format === 'detailed') {
            return {
              ...summary,
              detailedSensors: {
                barometer: data.barometer ? `${data.barometer} hPa` : 'N/A',
                distanceToF: data.distance_tof ? `${data.distance_tof}cm` : 'N/A',
                acceleration: data.acceleration ? 
                  `X:${data.acceleration.x}, Y:${data.acceleration.y}, Z:${data.acceleration.z}g` : 'N/A',
                velocity: data.velocity ? 
                  `${Math.sqrt(data.velocity.x ** 2 + data.velocity.y ** 2 + data.velocity.z ** 2).toFixed(1)}cm/s` : 'N/A',
                attitude: data.attitude ? 
                  `P:${data.attitude.pitch}°, R:${data.attitude.roll}°, Y:${data.attitude.yaw}°` : 'N/A',
              },
              systemHealth: {
                sensorCount: this.countActiveSensors(data),
                dataQuality: this.assessDataQuality(data),
                lastUpdate: new Date().toISOString(),
              },
            };
          }

          return summary;
        } catch (error) {
          return {
            success: false,
            message: `❌ Sensor summary error: ${error instanceof Error ? error.message : 'Unknown error'}`,
            timestamp: new Date().toISOString(),
            error: error instanceof Error ? error.message : 'Unknown error',
            criticalWarning: 'Unable to assess drone status - proceed with extreme caution',
            emergencyAction: 'Land drone immediately if flying and unable to get sensor data',
            troubleshooting: [
              'Check overall drone system status',
              'Verify sensor connectivity',
              'Individual sensor tools may still work'
            ]
          };
        }
      },
      validator: z.object({ format: z.enum(['detailed', 'compact']).optional() }),
      category: 'sensors',
      description: 'Provides comprehensive overview of all sensor readings',
      examples: [
        'drone_sensor_summary() - Get detailed sensor overview',
        'drone_sensor_summary({"format": "compact"}) - Get compact sensor summary'
      ],
    },
  ];
}

// Helper functions for sensor analysis (these would be class methods in TypeScript)
function getBatteryStatus(level: number) {
  if (level > 50) return { level: 'good', message: 'Good battery level', alert: null, recommendations: ['Continue normal operation'] };
  if (level > 30) return { level: 'moderate', message: 'Moderate battery level', alert: 'Plan to land soon', recommendations: ['Monitor battery closely', 'Prepare for landing'] };
  if (level > 20) return { level: 'low', message: 'Low battery level', alert: 'Land soon', recommendations: ['Land within 5 minutes', 'Avoid long-distance flights'] };
  return { level: 'critical', message: 'Critical battery level', alert: 'LAND IMMEDIATELY', recommendations: ['Land immediately', 'Do not attempt extended flight'] };
}

function getTemperatureStatus(temp: number) {
  if (temp < 40) return { level: 'normal', message: 'Normal operating temperature', alert: null, recommendations: ['Normal operation'] };
  if (temp < 50) return { level: 'warm', message: 'Elevated temperature', alert: 'Monitor temperature', recommendations: ['Reduce flight intensity', 'Allow cooling breaks'] };
  return { level: 'hot', message: 'High temperature', alert: 'Risk of overheating', recommendations: ['Land and allow cooling', 'Check for obstructions'] };
}

function getEstimatedFlightTime(batteryLevel: number): string {
  const maxFlightTime = 25; // minutes
  const estimatedMinutes = Math.floor((batteryLevel / 100) * maxFlightTime);
  return `~${estimatedMinutes} minutes`;
}

function getPowerConsumption(batteryLevel: number): string {
  if (batteryLevel > 80) return 'Low power consumption';
  if (batteryLevel > 50) return 'Normal power consumption';
  return 'Monitor power usage carefully';
}

function getChargingAdvice(batteryLevel: number): string {
  if (batteryLevel < 20) return 'Charge immediately after flight';
  if (batteryLevel < 50) return 'Charge after this session';
  return 'Charge when convenient';
}

function getBatteryHealth(batteryLevel: number): string {
  return 'Battery health assessment requires multiple flight cycles';
}

function convertPressure(hPa: number, unit: string): number {
  switch (unit) {
    case 'inHg': return hPa * 0.02953;
    case 'mmHg': return hPa * 0.75006;
    default: return hPa;
  }
}

function getWeatherConditions(pressure: number) {
  if (pressure > 1020) return { description: 'High pressure - clear weather', trend: 'stable', flightAdvice: 'Good flying conditions' };
  if (pressure > 1000) return { description: 'Normal pressure', trend: 'stable', flightAdvice: 'Normal flying conditions' };
  return { description: 'Low pressure - possible weather changes', trend: 'variable', flightAdvice: 'Monitor weather conditions' };
}

function getProximityStatus(distance: number) {
  if (distance < 30) return { level: 'critical', message: 'Very close to ground', warning: true, alert: 'CAUTION: Very low altitude', recommendation: 'Ascend immediately' };
  if (distance < 100) return { level: 'low', message: 'Low altitude', warning: true, alert: 'Low altitude warning', recommendation: 'Consider gaining altitude' };
  if (distance < 300) return { level: 'normal', message: 'Normal altitude', warning: false, alert: null, recommendation: 'Safe altitude' };
  return { level: 'high', message: 'High altitude', warning: false, alert: null, recommendation: 'Monitor regulatory limits' };
}

function convertDistance(cm: number, unit: string): number {
  switch (unit) {
    case 'm': return cm / 100;
    case 'ft': return cm / 30.48;
    default: return cm;
  }
}

function getStabilityStatus(magnitude: number) {
  if (magnitude < 0.5) return { level: 'stable', description: 'Very stable flight', recommendation: 'Excellent flight conditions' };
  if (magnitude < 1.0) return { level: 'normal', description: 'Normal flight stability', recommendation: 'Good flight conditions' };
  return { level: 'unstable', description: 'Some instability detected', recommendation: 'Monitor flight carefully' };
}

function convertVelocity(vel: any, unit: string) {
  const factor = unit === 'ms' ? 0.01 : unit === 'kmh' ? 0.036 : unit === 'mph' ? 0.0224 : 1;
  return { x: vel.x * factor, y: vel.y * factor, z: vel.z * factor };
}

function convertSpeed(speed: number, unit: string): number {
  switch (unit) {
    case 'ms': return speed * 0.01;
    case 'kmh': return speed * 0.036;
    case 'mph': return speed * 0.0224;
    default: return speed;
  }
}

function getMovementDescription(vel: any) {
  const speed = Math.sqrt(vel.x * vel.x + vel.y * vel.y + vel.z * vel.z);
  const speedLevel = speed < 5 ? 'stationary' : speed < 20 ? 'slow' : speed < 50 ? 'normal' : 'fast';
  
  let direction = '';
  if (Math.abs(vel.x) > 5) direction += vel.x > 0 ? 'right ' : 'left ';
  if (Math.abs(vel.y) > 5) direction += vel.y > 0 ? 'forward ' : 'backward ';
  if (Math.abs(vel.z) > 5) direction += vel.z > 0 ? 'up' : 'down';
  
  return {
    direction: direction || 'hovering',
    speedLevel,
    description: `${speedLevel} movement ${direction}`.trim()
  };
}

function getAttitudeStability(attitude: any) {
  const maxTilt = Math.max(Math.abs(attitude.pitch), Math.abs(attitude.roll));
  if (maxTilt < 5) return { level: 'stable', description: 'Very stable attitude', recommendation: 'Excellent stability' };
  if (maxTilt < 15) return { level: 'normal', description: 'Normal flight attitude', recommendation: 'Good stability' };
  return { level: 'tilted', description: 'Significant tilt detected', recommendation: 'Monitor stability carefully' };
}

function getPitchDescription(pitch: number): string {
  if (pitch > 10) return `Nose up ${pitch.toFixed(1)}°`;
  if (pitch < -10) return `Nose down ${Math.abs(pitch).toFixed(1)}°`;
  return 'Level pitch';
}

function getRollDescription(roll: number): string {
  if (roll > 10) return `Banking right ${roll.toFixed(1)}°`;
  if (roll < -10) return `Banking left ${Math.abs(roll).toFixed(1)}°`;
  return 'Level roll';
}

function getYawDescription(yaw: number): string {
  const heading = ((yaw + 360) % 360).toFixed(0);
  return `Heading ${heading}°`;
}

function getOverallStatus(data: any) {
  const warnings = [];
  const critical = [];
  
  if ((data.battery || 0) < 30) warnings.push('Low battery');
  if ((data.battery || 0) < 20) critical.push('Critical battery level');
  if ((data.temperature || 0) > 45) warnings.push('High temperature');
  if ((data.distance_tof || 1000) < 50) warnings.push('Low altitude');
  
  const level = critical.length > 0 ? 'critical' : warnings.length > 0 ? 'warning' : 'good';
  const flyable = critical.length === 0;
  
  return { level, flyable, warnings, critical };
}

function countActiveSensors(data: any): number {
  let count = 0;
  if (data.battery !== undefined) count++;
  if (data.temperature !== undefined) count++;
  if (data.height !== undefined) count++;
  if (data.barometer !== undefined) count++;
  if (data.distance_tof !== undefined) count++;
  if (data.acceleration !== undefined) count++;
  if (data.velocity !== undefined) count++;
  if (data.attitude !== undefined) count++;
  return count;
}

function assessDataQuality(data: any): string {
  const sensorCount = countActiveSensors(data);
  if (sensorCount >= 7) return 'Excellent';
  if (sensorCount >= 5) return 'Good';
  if (sensorCount >= 3) return 'Fair';
  return 'Poor';
}