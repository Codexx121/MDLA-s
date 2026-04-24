# MDLA-S: Multi-Directional Lane Adaptation System

A machine learning project that uses reinforcement learning to optimize traffic flow at an intersection. The system dynamically adapts lane configurations in the South incoming direction based on real-time traffic patterns.

## Overview

MDLA-S leverages a PPO (Proximal Policy Optimization) agent integrated with SUMO (Simulation of Urban Mobility) to intelligently manage traffic. The system learns to predict and respond to traffic surges, adapting between three dynamic lane modes while maintaining safety.

## Key Features

- **Dynamic Lane Control**: Three intelligent modes
  - Mode 0: Straight Surge
  - Mode 1: Left Surge (with green-phase safety protection)
  - Mode 2: Right Surge

- **Smart Traffic Patterns**: Three-phase demand cycles
  - Phase 1: Left-turn surge (0-333s)
  - Phase 2: Straight surge (333-667s)
  - Phase 3: Right surge (667-1000s)
  - Phase 4: Random patterns (1000s+)

- **Safety Features**: Green-light restrictions prevent conflicting simultaneous turns

- **Real-time Metrics**: Queue length, exit occupancy, and throughput tracking

## Prerequisites

- Python 3.8+
- SUMO (Simulation of Urban Mobility)
- pip (Python package installer)

## Installation

### 1. Activate Virtual Environment

Navigate to the project root and activate the virtual environment:

```bash
# On Windows
MLProj\Scripts\activate

# On macOS/Linux
source MLProj/Scripts/activate
```

### 2. Install Dependencies

Once the virtual environment is active, install required packages:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install sumo sumo-rl gym stable-baselines3 numpy
```

## Project Structure

```
├── src/                              # Main source code
│   ├── env.py                       # SUMO environment setup
│   ├── train.py                     # PPO training pipeline
│   ├── demo.py                      # Interactive demonstration
│   ├── evaluate.py                  # System evaluation metrics
│   └── demand_generator.py          # Traffic demand patterns
│
├── Sumo Files/                      # SUMO configuration files
│   ├── Intersection.net.xml         # Network topology
│   ├── Intersection.rou.xml         # Route definitions
│   └── Intersection.sumocfg         # SUMO configuration
│
├── mdla_s/                          # Quick training modules
│   ├── config.py                    # Configuration settings
│   ├── mock_env.py                  # Mock environment for testing
│   └── train_fast.py                # Fast training script
│
├── Project files/Results/           # Output storage
│   ├── Models/                      # Trained models
│   ├── Logs/                        # Training logs
│   └── Reports/                     # Evaluation reports
│
└── README.md                        # This file
```

## Quick Start

### Basic Training

```bash
python src/train.py
```

**Parameters:**
- `--episodes`: Number of training episodes (default: 100)
- `--steps-per-episode`: Steps per episode (default: 2000)
- `--output`: Model save path

### Run Demonstration

```bash
python src/demo.py
```

View real-time traffic behavior and MDLA-S decision-making.

### Evaluate Performance

```bash
python src/evaluate.py
```

Compare MDLA-S performance against baseline fixed-lane configuration.

### Fast Training (Quick Test)

```bash
python quick_train.py
```

Lightweight training for rapid prototyping.

## System Components

### Environment (`env.py`)
- SUMO integration for realistic traffic simulation
- South incoming direction control
- Observation space: Queue length, exit occupancy, north queue, current mode
- Action space: 3 discrete modes
- Reward function optimized for South direction throughput

### Demand Generator (`demand_generator.py`)
- Generates realistic three-phase traffic patterns
- Phases test different surge conditions
- Random mode after 1000 seconds
- Adjustable traffic probabilities

### Training (`train.py`)
- PPO agent implementation via Stable-Baselines3
- Multi-episode training loop
- Progress tracking and model checkpointing
- Performance logging

### Demo (`demo.py`)
- Real-time environment visualization
- Displays current traffic state
- Shows MDLA-S decision and reasoning
- Interactive traffic observation

### Evaluation (`evaluate.py`)
- Comprehensive metrics calculation
- Baseline vs. MDLA-S comparison
- Metrics: average queue length, wait time, throughput, safety
- Generates comparison reports

## Configuration

Edit configuration in `mdla_s/config.py`:

```python
EPISODE_LENGTH = 2000
NETWORK_FILE = "path/to/Intersection.net.xml"
ROUTE_FILE = "path/to/Intersection.rou.xml"
GUI_ENABLED = False
```

## Traffic Modes

### Mode 0: Straight Surge
Lane 0 & 2 → Straight, Lane 1 → Straight

### Mode 1: Left Surge (Green-Phase Protected)
Lane 1 → Left (only during green phase), Others → Straight

### Mode 2: Right Surge
Lane 0 & 2 → Right, Lane 1 → Straight

## Safety Mechanisms

- **Green Phase Timing**: 60-second cycle with 50% green time
- **Conflict Prevention**: Simultaneous conflicting turns prevented
- **Fail-Safe**: Non-South directions use fixed lane configuration

## Example Output

```
Episode 1/100: [████████░░] 40%
  Avg South Queue: 12.3 vehicles
  Avg Exit Occupancy: 18.5%
  Episode Reward: 342
  Total Timesteps: 2000
```

## Troubleshooting

### Virtual Environment Issues
```bash
# Recreate virtual environment
python -m venv MLProj
MLProj\Scripts\activate
pip install --upgrade pip
```

### SUMO Connection Errors
- Ensure SUMO is installed and in system PATH
- Check `Intersection.sumocfg` points to correct network/route files
- Verify XML files are valid (no syntax errors)

### Module Import Errors
```bash
pip install --upgrade stable-baselines3 sumo-rl gym
```

## Results

Trained models are saved in `Project files/Results/Models/`

Evaluation reports generated in `Project files/Results/Reports/`

## Citation

If using this system, reference:
- SUMO: [https://sumo.dlr.de/](https://sumo.dlr.de/)
- Stable-Baselines3: [https://stable-baselines3.readthedocs.io/](https://stable-baselines3.readthedocs.io/)

## License

[Your License Here]

## Contact

For questions or issues, refer to the verification report in `VERIFICATION_REPORT.md`

---

**Status**: ✅ All Systems Operational  
**Last Updated**: April 2026
