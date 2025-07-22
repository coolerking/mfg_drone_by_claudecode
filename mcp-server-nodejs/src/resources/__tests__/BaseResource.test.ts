/**
 * Tests for BaseResource
 * Test suite for the abstract base class for MCP resources
 */

import { BaseResource, type MCPResourceResponse } from '../BaseResource.js';
import { DroneService } from '@/services/DroneService.js';
import { ErrorHandler } from '@/utils/errors.js';

// Mock dependencies
jest.mock('@/services/DroneService.js');
jest.mock('@/utils/errors.js');

const mockedErrorHandler = jest.mocked(ErrorHandler);

// Concrete implementation for testing
class TestResource extends BaseResource {
  constructor(droneService: DroneService) {
    super(droneService, 'TestResource', 'mcp://test');
  }

  getDescription(): string {
    return 'Test resource for unit testing';
  }

  getUri(): string {
    return `${this.baseUri}/test`;
  }

  getMimeType(): string {
    return 'application/json';
  }

  async getContents(): Promise<MCPResourceResponse> {
    return this.createJsonResponse({ test: 'data' });
  }

  // Expose protected methods for testing
  public testHandleError(error: unknown): MCPResourceResponse {
    return this.handleError(error);
  }

  public testCreateJsonResponse(data: unknown): MCPResourceResponse {
    return this.createJsonResponse(data);
  }

  public testCreateTextResponse(text: string): MCPResourceResponse {
    return this.createTextResponse(text);
  }

  public testCreateHtmlResponse(html: string): MCPResourceResponse {
    return this.createHtmlResponse(html);
  }
}

describe('BaseResource', () => {
  let mockDroneService: jest.Mocked<DroneService>;
  let testResource: TestResource;

  beforeEach(() => {
    mockDroneService = new DroneService({} as any) as jest.Mocked<DroneService>;
    testResource = new TestResource(mockDroneService);
    
    mockedErrorHandler.handleError.mockReturnValue(new Error('Handled error'));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Constructor', () => {
    test('should initialize with correct parameters', () => {
      expect(testResource).toBeInstanceOf(BaseResource);
      expect(testResource.getDescription()).toBe('Test resource for unit testing');
      expect(testResource.getUri()).toBe('mcp://test/test');
      expect(testResource.getMimeType()).toBe('application/json');
    });

    test('should store droneService reference', () => {
      // Access protected property through any for testing
      expect((testResource as any).droneService).toBe(mockDroneService);
    });

    test('should store resourceName and baseUri', () => {
      expect((testResource as any).resourceName).toBe('TestResource');
      expect((testResource as any).baseUri).toBe('mcp://test');
    });
  });

  describe('Abstract Methods Implementation', () => {
    test('getDescription should return description', () => {
      expect(testResource.getDescription()).toBe('Test resource for unit testing');
    });

    test('getUri should return formatted URI', () => {
      expect(testResource.getUri()).toBe('mcp://test/test');
    });

    test('getMimeType should return MIME type', () => {
      expect(testResource.getMimeType()).toBe('application/json');
    });

    test('getContents should return response', async () => {
      const result = await testResource.getContents();
      
      expect(result).toEqual({
        contents: [
          {
            uri: 'mcp://test/test',
            mimeType: 'application/json',
            text: JSON.stringify({ test: 'data' }, null, 2),
          }
        ]
      });
    });
  });

  describe('Error Handling', () => {
    test('handleError should create error response', () => {
      const error = new Error('Test error');
      mockedErrorHandler.handleError.mockReturnValue(new Error('Handled error'));

      const result = testResource.testHandleError(error);

      expect(mockedErrorHandler.handleError).toHaveBeenCalledWith(
        error,
        'TestResource.getContents'
      );

      expect(result).toEqual({
        contents: [
          {
            uri: 'mcp://test/test',
            mimeType: 'text/plain',
            text: 'Error retrieving TestResource: Handled error',
          }
        ]
      });
    });

    test('handleError should handle unknown error types', () => {
      const error = 'String error';
      mockedErrorHandler.handleError.mockReturnValue(new Error('Unknown error'));

      const result = testResource.testHandleError(error);

      expect(result.contents[0].text).toContain('Error retrieving TestResource: Unknown error');
    });

    test('handleError should use correct context', () => {
      const error = new Error('Test error');
      
      testResource.testHandleError(error);

      expect(mockedErrorHandler.handleError).toHaveBeenCalledWith(
        error,
        'TestResource.getContents'
      );
    });
  });

  describe('Response Creation Methods', () => {
    describe('createJsonResponse', () => {
      test('should create JSON response with object data', () => {
        const testData = {
          id: 1,
          name: 'Test',
          active: true,
          values: [1, 2, 3]
        };

        const result = testResource.testCreateJsonResponse(testData);

        expect(result).toEqual({
          contents: [
            {
              uri: 'mcp://test/test',
              mimeType: 'application/json',
              text: JSON.stringify(testData, null, 2),
            }
          ]
        });
      });

      test('should create JSON response with array data', () => {
        const testData = [
          { id: 1, name: 'Item 1' },
          { id: 2, name: 'Item 2' }
        ];

        const result = testResource.testCreateJsonResponse(testData);

        expect(result.contents[0].text).toBe(JSON.stringify(testData, null, 2));
        expect(result.contents[0].mimeType).toBe('application/json');
      });

      test('should create JSON response with null data', () => {
        const result = testResource.testCreateJsonResponse(null);

        expect(result.contents[0].text).toBe('null');
        expect(result.contents[0].mimeType).toBe('application/json');
      });

      test('should create JSON response with undefined data', () => {
        const result = testResource.testCreateJsonResponse(undefined);

        expect(result.contents[0].text).toBe('null'); // JSON.stringify(undefined) returns undefined, which becomes null
        expect(result.contents[0].mimeType).toBe('application/json');
      });

      test('should create JSON response with primitive data', () => {
        const primitives = [
          'string',
          123,
          true,
          false
        ];

        primitives.forEach(primitive => {
          const result = testResource.testCreateJsonResponse(primitive);
          expect(result.contents[0].text).toBe(JSON.stringify(primitive, null, 2));
        });
      });
    });

    describe('createTextResponse', () => {
      test('should create text response', () => {
        const testText = 'This is a test message';

        const result = testResource.testCreateTextResponse(testText);

        expect(result).toEqual({
          contents: [
            {
              uri: 'mcp://test/test',
              mimeType: 'text/plain',
              text: testText,
            }
          ]
        });
      });

      test('should create text response with empty string', () => {
        const result = testResource.testCreateTextResponse('');

        expect(result.contents[0].text).toBe('');
        expect(result.contents[0].mimeType).toBe('text/plain');
      });

      test('should create text response with multiline text', () => {
        const multilineText = 'Line 1\nLine 2\nLine 3';

        const result = testResource.testCreateTextResponse(multilineText);

        expect(result.contents[0].text).toBe(multilineText);
      });

      test('should create text response with special characters', () => {
        const specialText = 'Hello 世界! 🚁 Special chars: @#$%^&*()';

        const result = testResource.testCreateTextResponse(specialText);

        expect(result.contents[0].text).toBe(specialText);
      });
    });

    describe('createHtmlResponse', () => {
      test('should create HTML response', () => {
        const testHtml = '<h1>Test HTML</h1><p>Content</p>';

        const result = testResource.testCreateHtmlResponse(testHtml);

        expect(result).toEqual({
          contents: [
            {
              uri: 'mcp://test/test',
              mimeType: 'text/html',
              text: testHtml,
            }
          ]
        });
      });

      test('should create HTML response with complete document', () => {
        const htmlDocument = `
          <!DOCTYPE html>
          <html>
            <head><title>Test</title></head>
            <body>
              <h1>Test Page</h1>
              <p>This is a test.</p>
            </body>
          </html>
        `;

        const result = testResource.testCreateHtmlResponse(htmlDocument);

        expect(result.contents[0].text).toBe(htmlDocument);
        expect(result.contents[0].mimeType).toBe('text/html');
      });

      test('should create HTML response with empty HTML', () => {
        const result = testResource.testCreateHtmlResponse('');

        expect(result.contents[0].text).toBe('');
      });

      test('should create HTML response with HTML entities', () => {
        const htmlWithEntities = '<p>Entities: &lt;tag&gt; &amp; &quot;quotes&quot;</p>';

        const result = testResource.testCreateHtmlResponse(htmlWithEntities);

        expect(result.contents[0].text).toBe(htmlWithEntities);
      });
    });
  });

  describe('Response Structure Validation', () => {
    test('all response methods should return proper MCPResourceResponse structure', () => {
      const jsonResponse = testResource.testCreateJsonResponse({ test: 'data' });
      const textResponse = testResource.testCreateTextResponse('test text');
      const htmlResponse = testResource.testCreateHtmlResponse('<p>test html</p>');
      const errorResponse = testResource.testHandleError(new Error('test'));

      [jsonResponse, textResponse, htmlResponse, errorResponse].forEach(response => {
        expect(response).toHaveProperty('contents');
        expect(Array.isArray(response.contents)).toBe(true);
        expect(response.contents).toHaveLength(1);
        
        const content = response.contents[0];
        expect(content).toHaveProperty('uri');
        expect(content).toHaveProperty('mimeType');
        expect(content).toHaveProperty('text');
        
        expect(typeof content.uri).toBe('string');
        expect(typeof content.mimeType).toBe('string');
        expect(typeof content.text).toBe('string');
        expect(content.uri).toBe('mcp://test/test');
      });
    });

    test('should use correct MIME types for different response types', () => {
      const jsonResponse = testResource.testCreateJsonResponse({ test: 'data' });
      const textResponse = testResource.testCreateTextResponse('test text');
      const htmlResponse = testResource.testCreateHtmlResponse('<p>test html</p>');
      const errorResponse = testResource.testHandleError(new Error('test'));

      expect(jsonResponse.contents[0].mimeType).toBe('application/json');
      expect(textResponse.contents[0].mimeType).toBe('text/plain');
      expect(htmlResponse.contents[0].mimeType).toBe('text/html');
      expect(errorResponse.contents[0].mimeType).toBe('text/plain');
    });
  });

  describe('Integration with DroneService', () => {
    test('should have access to DroneService instance', () => {
      expect((testResource as any).droneService).toBe(mockDroneService);
    });

    test('should be able to use DroneService methods in derived classes', async () => {
      // This test verifies that derived classes can access the droneService
      class DroneServiceUsingResource extends BaseResource {
        constructor(droneService: DroneService) {
          super(droneService, 'TestResource', 'mcp://test');
        }

        getDescription(): string { return 'test'; }
        getUri(): string { return 'test'; }
        getMimeType(): string { return 'application/json'; }

        async getContents(): Promise<MCPResourceResponse> {
          // This should be able to access droneService methods
          expect(this.droneService).toBe(mockDroneService);
          return this.createJsonResponse({ success: true });
        }
      }

      const testResourceWithService = new DroneServiceUsingResource(mockDroneService);
      await testResourceWithService.getContents();
    });
  });

  describe('Edge Cases and Error Scenarios', () => {
    test('should handle circular JSON objects gracefully', () => {
      const circularObj: any = { name: 'test' };
      circularObj.self = circularObj;

      expect(() => {
        testResource.testCreateJsonResponse(circularObj);
      }).toThrow(); // JSON.stringify should throw on circular references
    });

    test('should handle very large data objects', () => {
      const largeArray = Array.from({ length: 10000 }, (_, i) => ({
        id: i,
        data: `Item ${i}`,
        timestamp: new Date().toISOString()
      }));

      const result = testResource.testCreateJsonResponse(largeArray);
      
      expect(result.contents[0].mimeType).toBe('application/json');
      expect(result.contents[0].text).toContain('Item 0');
      expect(result.contents[0].text).toContain('Item 9999');
    });

    test('should handle special JSON values', () => {
      const specialValues = {
        infinity: Infinity,
        negInfinity: -Infinity,
        nan: NaN,
        date: new Date(),
        regex: /test/g
      };

      const result = testResource.testCreateJsonResponse(specialValues);
      
      expect(result.contents[0].mimeType).toBe('application/json');
      // JSON.stringify converts these special values
      expect(result.contents[0].text).toContain('null'); // Infinity becomes null
    });
  });

  describe('Resource Naming and URI Construction', () => {
    test('should construct URI correctly with different base URIs', () => {
      const resources = [
        new TestResource(mockDroneService),
        new (class extends BaseResource {
          constructor() { super(mockDroneService, 'Custom', 'https://example.com'); }
          getDescription() { return 'Custom'; }
          getUri() { return `${this.baseUri}/custom`; }
          getMimeType() { return 'text/plain'; }
          async getContents() { return this.createTextResponse('test'); }
        })(),
      ];

      expect(resources[0].getUri()).toBe('mcp://test/test');
      expect(resources[1].getUri()).toBe('https://example.com/custom');
    });

    test('should handle resource names with special characters', () => {
      class SpecialNameResource extends BaseResource {
        constructor() {
          super(mockDroneService, 'Special-Name_123', 'mcp://special');
        }
        getDescription() { return 'Special name resource'; }
        getUri() { return this.baseUri; }
        getMimeType() { return 'application/json'; }
        async getContents() { return this.createJsonResponse({}); }
        
        public testHandleError(error: unknown) {
          return this.handleError(error);
        }
      }

      const specialResource = new SpecialNameResource();
      const errorResponse = specialResource.testHandleError(new Error('test'));
      
      expect(errorResponse.contents[0].text).toContain('Special-Name_123');
    });
  });
});