#!/usr/bin/env bash
set -e
cd frontend
if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies with npm install..."
  npm install
fi
echo "Starting Vite development server..."
npm run dev
