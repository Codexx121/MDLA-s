# MDLA-S: Mode-Based Dynamic Lane Allocation using RL

A reinforcement learning framework for adaptive traffic signal and lane management at signalized intersections with four approaches (North, South, East, West). MDLA-S dynamically reconfigures lane permissions and selects optimal signal timing in response to real-time traffic demand.

## Overview

MDLA-S leverages a PPO (Proximal Policy Optimization) agent integrated with SUMO (Simulation of Urban Mobility) to intelligently manage both traffic signals and lane allocations. Unlike traditional fixed-lane systems where each lane is permanently assigned to a single turning movement, MDLA-S dynamically adapts lane permissions to handle varying traffic demand surges. The system makes coordinated decisions on which direction receives green signal AND which dynamic lane mode to activate.

## Key Features

- **Dual Optimization**: Agent selects both signal direction (N/E/S/W) AND lane mode
  - Action space: 12 (4 directions × 3 modes)
  - Decision interval: Every 10 simulation steps (10 seconds)

- **Five Dynamic Lane Modes**:
  - Mode 0: Default (R|S|L)
  - Mode 1: Left Surge (R|S+L|L)
  - Mode 2: Right Surge (R|S+R|L)
  - Mode 3: Straight Surge Right (R+S|S|L)
  - Mode 4: Straight Surge Left (R|S|L+S)

- **Comprehensive State Space**: 26 features
  - Queue lengths (12): 3 lanes × 4 directions
  - Waiting times (4): per direction
  - Exit occupancy (4): spillback detection
  - Current green direction, mode, and time-since-served

- **Structured Demand Scenarios**:
  - Phase 1 (0–250s): Heavy straight
  - Phase 2 (250–500s): Heavy right turns
  - Phase 3 (500–750s): Heavy left turns
  - Phase 4 (750–1000s): Heavy straight (repeat)
  - Phase 5 (1000+s): Random balanced mixture

- **Safety Features**: Exclusive green policy, spillback detection, yellow transition phases

## Prerequisites

- Python 3.8+
- SUMO (Simulation of Urban Mobility)
- pip (Python package installer)

## Installation

### 1. Activate Virtual Environment

Navigate to the project root and activate the virtual environment:

```bash
# On Windows (PowerShell)
MLProj\Scripts\activate

# On Windows (Command Prompt)
MLProj\Scripts\activate.bat

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
│   ├── env.py                       # SUMO environment (26-dim obs, 12 actions)
│   ├── train.py                     # PPO training pipeline
│   ├── demo.py                      # Real-time demonstration
│   ├── evaluate.py                  # Baseline comparison & metrics
│   └── demand_generator.py          # 5-phase traffic demand patterns
│
├── mdla_s/                          # Fast training utilities
│   ├── config.py                    # System configuration
│   ├── train_fast.py                # Quick prototyping script
│   └── mock_env.py                  # Mock environment for testing
│
├── sumo_files/                      # SUMO network & routing
│   ├── Intersection.net.xml         # 4-way intersection topology
│   ├── Intersection.rou.xml         # Vehicle routes & demand
│   └── Intersection.sumocfg         # SUMO simulation config
│
├── Project files/Results/           # Outputs & results
│   ├── Models/                      # Trained PPO models
│   ├── Logs/                        # Training logs
│   └── Reports/                     # Evaluation reports
│
├── VERIFICATION_REPORT.md           # System test results
├── FIXES_SUMMARY.md                 # Implementation notes
├── README.md                        # This file
└── quick_train.py                   # Quick training script
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
- SUMO integration with TraCI (Traffic Control Interface)
- 26-dimensional observation space (queues, wait times, occupancy, timing info)
- Action space: 12 discrete actions (4 directions × 3 modes)
- Decision interval: Every 10 simulation steps
- Reward function balancing throughput, fairness, and stability

### Demand Generator (`demand_generator.py`)
- Generates five structured traffic phases (0–1000+s)
- Phase 1: Heavy straight; Phase 2: Heavy right turns
- Phase 3: Heavy left turns; Phase 4: Heavy straight (repeat)
- Phase 5 (1000+s): Random balanced mixture
- Per-edge arrival probability configuration

### Training (`train.py`)
- PPO agent with MlpPolicy (128×128 layers)
- Multi-episode training with configurable timesteps
- Episode progress tracking and visualization
- Model checkpointing and save/load

### Demo (`demo.py`)
- Real-time environment visualization
- All-direction queue and occupancy display
- Current green direction and lane mode shown
- Real-time reward feedback

### Evaluation (`evaluate.py`)
- Comprehensive metrics collection
- Fixed-cycle baseline comparison
- Metrics: queue length, wait time, throughput, teleports, reward
- CSV export for analysis

## Reinforcement Learning Configuration

### Agent Hyperparameters

| Parameter | Value |
|-----------|-------|
| Algorithm | PPO (Stable-Baselines3) |
| Policy | MlpPolicy (128×128 hidden layers) |
| Learning rate | 3 × 10⁻⁴ |
| Discount factor (γ) | 0.99 |
| GAE lambda (λ) | 0.95 |
| Clip range | 0.2 |
| Entropy coefficient | 0.01 |
| Batch size | 64 |
| Steps per update | 2048 |
| Training timesteps | 50,000 (demo) / 200,000+ (production) |

### Reward Function

$$R = 2.0 \cdot T + 0.3 \cdot \Delta Q - 0.05 \cdot Q_{total} - 0.02 \cdot S_{max} - P_{spillback} - P_{switch}$$

Where:
- **T** = vehicles reaching destination this step
- **ΔQ** = queue reduction from previous step
- **Q_total** = current total queue
- **S_max** = max unserved time (prevents starvation)
- **P_spillback** = penalty when exit occupancy > 80%
- **P_switch** = penalty for direction (2.0) or mode (1.0) changes

### Project Configuration

Edit in `mdla_s/config.py`:

```python
EPISODE_LENGTH = 2000
NETWORK_FILE = "path/to/Intersection.net.xml"
ROUTE_FILE = "path/to/Intersection.rou.xml"
GUI_ENABLED = False
DECISION_INTERVAL = 10  # steps
```

## Intersection Configuration

Standard 4-way intersection with 3 lanes per direction:

| Lane | Default Assignment |
|------|--------------------|
| Lane 0 (Rightmost) | Right turn only |
| Lane 1 (Middle) | Straight only |
| Lane 2 (Leftmost) | Left turn only |

## Dynamic Lane Modes

| Mode | Name | Lane 0 | Lane 1 | Lane 2 | Use Case |
|------|------|:------:|:------:|:------:|----------|
| **0** | **Default** | R | S | L | Standard operations |
| **1** | **Left Surge** | R | S+L | L | Heavy left-turn demand |
| **2** | **Right Surge** | R | S+R | L | Heavy right-turn demand |
| **3** | **Straight↑ R** | R+S | S | L | Heavy through-traffic via right lane |
| **4** | **Straight↑ L** | R | S | L+S | Heavy through-traffic via left lane |

Where: **S**=Straight, **L**=Left, **R**=Right

## Safety Mechanisms

- **Exclusive Green Policy**: Only one direction receives green at any time
- **Yellow Transition**: 3-step yellow phase when changing green direction
- **Spillback Detection**: Monitors exit occupancy, prevents sending traffic into congested segments
- **Starvation Prevention**: Penalty term discourages indefinitely starving any direction
- **Mode Stability**: Switching penalty reduces oscillation behavior

## Evaluation Metrics

Performance evaluated against fixed-cycle baseline:

1. **Average Queue Length** — mean halting vehicles across all lanes
2. **Maximum Queue Length** — worst-case congestion
3. **Average Waiting Time** — mean per-direction waiting time
4. **Total Throughput** — vehicles completing their route
5. **Teleports** — safety metric (vehicles teleported due to deadlock)
6. **Total Reward** — cumulative RL reward

### Example Output

```
Episode 1/50: [████████░░] 80%
  Timestep: 2000
  Avg Queue: 8.7 vehicles
  Total Throughput: 342 vehicles
  Cumulative Reward: 1,245
  Safety: 0 teleports
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

## Implementation Details

Implemented in Python using:
- **SUMO 1.26.0+** — Microscopic traffic simulation engine
- **TraCI** — Traffic Control Interface for real-time simulation control
- **Gymnasium/Gym** — RL environment interface
- **Stable-Baselines3** — PPO algorithm implementation
- **NumPy/Pandas** — Data processing and metrics calculation

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
