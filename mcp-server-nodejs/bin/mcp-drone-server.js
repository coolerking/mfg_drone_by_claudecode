#!/usr/bin/env node

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// Get the directory of this script
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the TypeScript source file
const srcPath = join(__dirname, '..', 'src', 'index.ts');

// Path to tsx binary
const tsxPath = join(__dirname, '..', 'node_modules', '.bin', 'tsx');

// Spawn tsx with the TypeScript source file
const child = spawn(tsxPath, [srcPath], {
  stdio: 'inherit',
  env: process.env
});

// Handle process exit
child.on('exit', (code) => {
  process.exit(code || 0);
});

// Handle process errors
child.on('error', (error) => {
  console.error('Failed to start MCP Drone Server:', error);
  process.exit(1);
});