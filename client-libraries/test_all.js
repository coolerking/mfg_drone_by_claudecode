#!/usr/bin/env node

/**
 * Test runner for all client libraries
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// ANSI color codes
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Test configurations
const testConfigs = [
  {
    name: 'JavaScript SDK',
    directory: 'javascript',
    command: 'npm',
    args: ['test'],
    setup: ['npm', 'install'],
  },
  {
    name: 'Python SDK',
    directory: 'python',
    command: 'python',
    args: ['-m', 'pytest', 'tests/', '-v', '--tb=short'],
    setup: ['pip', 'install', '-e', '.[test]'],
  },
  {
    name: 'TypeScript Types',
    directory: 'types',
    command: 'npm',
    args: ['test'],
    setup: ['npm', 'install'],
  },
  {
    name: 'CLI Tool',
    directory: 'cli',
    command: 'npm',
    args: ['test'],
    setup: ['npm', 'install'],
  },
];

// Utility functions
function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function runCommand(command, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: true,
      ...options,
    });

    child.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Command failed with exit code ${code}`));
      }
    });

    child.on('error', (error) => {
      reject(error);
    });
  });
}

function directoryExists(dirPath) {
  return fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
}

async function setupProject(config) {
  const projectDir = path.join(__dirname, config.directory);
  
  if (!directoryExists(projectDir)) {
    log(`⚠️  Directory ${config.directory} does not exist, skipping...`, colors.yellow);
    return false;
  }

  log(`📦 Setting up ${config.name}...`, colors.cyan);
  
  try {
    await runCommand(config.setup[0], config.setup.slice(1), {
      cwd: projectDir,
    });
    log(`✅ Setup completed for ${config.name}`, colors.green);
    return true;
  } catch (error) {
    log(`❌ Setup failed for ${config.name}: ${error.message}`, colors.red);
    return false;
  }
}

async function runTests(config) {
  const projectDir = path.join(__dirname, config.directory);
  
  log(`🧪 Running tests for ${config.name}...`, colors.cyan);
  
  try {
    await runCommand(config.command, config.args, {
      cwd: projectDir,
    });
    log(`✅ Tests passed for ${config.name}`, colors.green);
    return true;
  } catch (error) {
    log(`❌ Tests failed for ${config.name}: ${error.message}`, colors.red);
    return false;
  }
}

async function main() {
  log(`${colors.bright}🚀 MCP Drone Client Libraries Test Suite${colors.reset}`);
  log('');

  const results = [];
  
  // Check if we should run specific tests
  const args = process.argv.slice(2);
  const specificTests = args.length > 0 ? args : null;
  
  let filteredConfigs = testConfigs;
  if (specificTests) {
    filteredConfigs = testConfigs.filter(config => 
      specificTests.some(test => 
        config.name.toLowerCase().includes(test.toLowerCase()) ||
        config.directory.includes(test)
      )
    );
    
    if (filteredConfigs.length === 0) {
      log(`❌ No tests found matching: ${specificTests.join(', ')}`, colors.red);
      log('Available tests:', colors.yellow);
      testConfigs.forEach(config => {
        log(`  - ${config.name} (${config.directory})`, colors.yellow);
      });
      process.exit(1);
    }
  }

  // Run setup and tests for each project
  for (const config of filteredConfigs) {
    log(`${colors.bright}==== ${config.name} ====${colors.reset}`);
    
    const setupSuccess = await setupProject(config);
    if (!setupSuccess) {
      results.push({ name: config.name, success: false, stage: 'setup' });
      continue;
    }

    const testSuccess = await runTests(config);
    results.push({ name: config.name, success: testSuccess, stage: 'test' });
    
    log('');
  }

  // Print summary
  log(`${colors.bright}📊 Test Summary${colors.reset}`);
  log('');
  
  let allPassed = true;
  results.forEach(result => {
    const status = result.success ? '✅ PASS' : '❌ FAIL';
    const color = result.success ? colors.green : colors.red;
    const stage = result.stage === 'setup' ? ' (setup)' : '';
    
    log(`${color}${status}${colors.reset} ${result.name}${stage}`);
    
    if (!result.success) {
      allPassed = false;
    }
  });

  log('');
  
  if (allPassed) {
    log(`${colors.green}🎉 All tests passed!${colors.reset}`);
    process.exit(0);
  } else {
    log(`${colors.red}💥 Some tests failed.${colors.reset}`);
    process.exit(1);
  }
}

// Help message
if (process.argv.includes('--help') || process.argv.includes('-h')) {
  log(`${colors.bright}MCP Drone Client Libraries Test Suite${colors.reset}`);
  log('');
  log('Usage:');
  log('  node test_all.js [test-name...]');
  log('');
  log('Examples:');
  log('  node test_all.js                    # Run all tests');
  log('  node test_all.js javascript         # Run JavaScript SDK tests');
  log('  node test_all.js python cli         # Run Python SDK and CLI tests');
  log('  node test_all.js types              # Run TypeScript types tests');
  log('');
  log('Available tests:');
  testConfigs.forEach(config => {
    log(`  - ${config.name} (${config.directory})`);
  });
  process.exit(0);
}

// Run main function
main().catch(error => {
  log(`❌ Unexpected error: ${error.message}`, colors.red);
  process.exit(1);
});