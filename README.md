# Sensor Simulation Project

A Python-based sensor simulation system for generating realistic sensor data patterns.

## Features

- Multi-sensor data simulation
- Configurable noise and drift patterns
- Real-time data generation
- Export capabilities
- Visualization tools

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Project Structure

```
sensor-sim/
├── src/
│   ├── sensors/          # Sensor simulation modules
│   ├── data/            # Data generation and processing
│   ├── visualization/   # Plotting and visualization
│   └── utils/           # Utility functions
├── tests/               # Unit tests
├── config/              # Configuration files
├── examples/            # Example scripts
└── docs/                # Documentation
```

## License

MIT License
