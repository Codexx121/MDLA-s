# MDLA-S: Mode-Based Dynamic Lane Allocation using Reinforcement Learning

## Methodology

### 1. System Overview

MDLA-S (Mode-Based Dynamic Lane Allocation — SUMO) is a reinforcement learning framework for adaptive traffic signal and lane management at signalized intersections. Unlike traditional fixed-lane systems where each lane is permanently assigned a single turning movement, MDLA-S dynamically reconfigures lane permissions in response to real-time traffic demand. The system is implemented using the SUMO (Simulation of Urban MObility) microscopic traffic simulator and controlled via the TraCI (Traffic Control Interface) API.

### 2. Intersection Configuration

The test intersection is a standard 4-way signalized junction with four approaches: North, South, East, and West. Each approach consists of three incoming lanes:

| Lane | Position | Default Assignment |
|------|----------|--------------------|
| Lane 0 | Rightmost | Right turn only |
| Lane 1 | Middle | Straight only |
| Lane 2 | Leftmost | Left turn only |

This default configuration follows a standard lane layout where dedicated turning lanes occupy the outer positions, and through-traffic occupies the center. The key innovation of MDLA-S is that these assignments are dynamically modified by the RL agent to handle demand surges.

### 3. MDLA Mode Definitions

The system defines five dynamic lane allocation modes. Each mode adds flexibility to one or more lanes while maintaining the default assignments for others:

| Mode | Name | Lane 0 (R) | Lane 1 (S) | Lane 2 (L) | Purpose |
|------|------|:---:|:---:|:---:|:---|
| **0** | **Default** | R | S | L | Standard low-demand operations. |
| **1** | **Left Surge** | R | **S + L** | L | Absorbs heavy left-turn demand into the middle lane. |
| **2** | **Right Surge** | R | **S + R** | L | Absorbs heavy right-turn demand into the middle lane. |
| **3** | **Straight Surge R** | **R + S** | S | L | Absorbs heavy straight demand into the right lane. |
| **4** | **Straight Surge L** | R | S | **L + S** | Absorbs heavy straight demand into the left lane. |

Where: S=Straight, L=Left, R=Right.

These modes are implemented by dynamically modifying the connection permissions via TraCI's `setAllowed()` method. The RL agent identifies which "flexible" connections (defined in a custom `patch.con.xml`) should be enabled based on the current queue lengths and occupancy data.

### 4. Signal Control

The traffic signal operates under an exclusive green policy: only one incoming direction receives a green signal at any time. This eliminates conflicting movements and simplifies the safety analysis. When the RL agent switches the green direction, a 3-step yellow transition phase is inserted to model realistic signal behavior.

### 5. Reinforcement Learning Formulation

#### 5.1 Action Space

The action space is a single discrete space of size 12, representing all combinations of 4 directions × 3 MDLA modes:

$$A = \{(d, m) : d \in \{0,1,2,3\}, m \in \{0,1,2\}\}$$

| Actions 0–2 | Actions 3–5 | Actions 6–8 | Actions 9–11 |
|-------------|-------------|-------------|--------------|
| North + Mode 0/1/2 | East + Mode 0/1/2 | South + Mode 0/1/2 | West + Mode 0/1/2 |

#### 5.2 State Space

The observation vector contains 26 continuous features:

| Features | Count | Description |
|----------|-------|-------------|
| Queue lengths | 12 | Halting vehicles per lane (4 directions × 3 lanes) |
| Waiting times | 4 | Total waiting time per incoming direction |
| Outgoing occupancy | 4 | Exit road occupancy (spillback detection) |
| Current green direction | 1 | Normalized (0–1) |
| Current MDLA mode | 1 | Normalized (0–1) |
| Time since last served | 4 | Per direction, normalized by episode length |

The inclusion of outgoing occupancy enables the agent to detect downstream spillback — a critical feature that prevents the agent from sending traffic into already-congested exit roads.

#### 5.3 Reward Function

The reward function balances throughput maximization with queue management, fairness, and stability:

$$R = 2.0 \cdot T + 0.3 \cdot \Delta Q - 0.05 \cdot Q_{total} - 0.02 \cdot S_{max} - P_{spillback} - P_{switch}$$

Where:
- **T** = vehicles that arrived at their destination this step (throughput)
- **ΔQ** = reduction in total queue from previous step
- **Q_total** = current total queue across all lanes
- **S_max** = maximum time any direction has been unserved (starvation penalty)
- **P_spillback** = penalty when outgoing occupancy exceeds 80%
- **P_switch** = penalty for changing direction (2.0) or mode (1.0) to discourage oscillation

#### 5.4 Decision Interval

The agent makes one decision every 10 simulation steps (10 seconds). This interval balances responsiveness with stability and aligns with typical minimum green times in traffic engineering.

### 6. Training

The agent is trained using Proximal Policy Optimization (PPO) with the following hyperparameters:

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
| Training timesteps | 50,000 (demo) / 200,000+ (final) |

The entropy coefficient of 0.01 encourages exploration across the 12-dimensional action space during early training.

### 7. Traffic Demand Scenarios

To evaluate the agent's adaptability, the simulation uses structured demand phases:

| Phase | Time | Pattern | MDLA Mode Tested |
|-------|------|---------|------------------|
| 1 | 0–250s | Heavy straight from all directions | Mode 1 |
| 2 | 250–500s | Heavy right turns | Mode 0 |
| 3 | 500–750s | Heavy left turns | Mode 2 |
| 4 | 750–1000s | Heavy straight (repeat) | Mode 1 |
| 5 | 1000–3600s | Random balanced mixture | All modes |

### 8. Evaluation Protocol

Performance is evaluated by comparing MDLA-S against a fixed-cycle baseline:

- **Baseline:** Rotates green direction in fixed order (N→E→S→W), always uses Mode 0, no adaptation.
- **MDLA-S:** RL agent selects both direction and mode based on real-time observations.

Metrics collected:
1. **Average Queue Length** — mean halting vehicles across all lanes
2. **Maximum Queue Length** — worst-case congestion
3. **Average Waiting Time** — mean per-direction waiting time
4. **Total Throughput** — vehicles that completed their route
5. **Teleports** — safety metric (vehicles teleported due to deadlock)
6. **Total Reward** — cumulative RL reward

### 9. Implementation

The system is implemented in Python using:
- **SUMO 1.26.0** — microscopic traffic simulation
- **TraCI** — real-time simulation control API
- **Gymnasium** — RL environment interface
- **Stable-Baselines3** — PPO implementation
- **NumPy / Pandas** — data processing and reporting

All source code, SUMO configuration files, and trained models are available in the project repository.
