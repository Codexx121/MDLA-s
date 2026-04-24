import os

def generate_routes(file_path):
    with open(file_path, "w") as f:
        f.write('<routes>\n')
        # Vehicle Type
        f.write('    <vType id="car" accel="2.6" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="15" color="0,1,0" carFollowModel="IDM"/>\n\n')

        # Routes
        routes = [
            ("r_N_S", "end1_junction junction_end3"), # Straight
            ("r_N_L", "end1_junction junction_end2"), # Left
            ("r_N_R", "end1_junction junction_end4"), # Right
            
            ("r_S_N", "end3_junction junction_end1"), # Straight
            ("r_S_L", "end3_junction junction_end4"), # Left
            ("r_S_R", "end3_junction junction_end2"), # Right
            
            ("r_E_W", "end2_junction junction_end4"), # Straight
            ("r_E_L", "end2_junction junction_end3"), # Left
            ("r_E_R", "end2_junction junction_end1"), # Right
            
            ("r_W_E", "end4_junction junction_end2"), # Straight
            ("r_W_L", "end4_junction junction_end1"), # Left
            ("r_W_R", "end4_junction junction_end3"), # Right
        ]
        
        for r_id, edges in routes:
            f.write(f'    <route id="{r_id}" edges="{edges}"/>\n')
            
        # Helper: write background traffic for all directions
        def write_bg(phase_id, begin, end, prob=0.03):
            for r_id, _ in routes:
                f.write(f'    <flow id="{phase_id}_{r_id}" type="car" route="{r_id}" begin="{begin}" end="{end}" probability="{prob}" departLane="random"/>\n')

        # Phase 1: Right Surge (0-200s)
        f.write('\n    <!-- Custom Phase 1: Right Surge (0-200s) -->\n')
        write_bg("bg1", 0, 200)
        f.write('    <flow id="c1_N_R" type="car" route="r_N_R" begin="0" end="200" probability="0.35" departLane="random"/>\n')
        f.write('    <flow id="c1_S_R" type="car" route="r_S_R" begin="0" end="200" probability="0.35" departLane="random"/>\n')

        # Phase 2: Straight Surge (200-400s)
        f.write('\n    <!-- Custom Phase 2: Straight Surge (200-400s) -->\n')
        write_bg("bg2", 200, 400)
        f.write('    <flow id="c2_N_S" type="car" route="r_N_S" begin="200" end="400" probability="0.35" departLane="random"/>\n')
        f.write('    <flow id="c2_E_W" type="car" route="r_E_W" begin="200" end="400" probability="0.35" departLane="random"/>\n')

        # Phase 3: Left Surge (400-600s)
        f.write('\n    <!-- Custom Phase 3: Left Surge (400-600s) -->\n')
        write_bg("bg3", 400, 600)
        f.write('    <flow id="c3_E_L" type="car" route="r_E_L" begin="400" end="600" probability="0.35" departLane="random"/>\n')
        f.write('    <flow id="c3_W_L" type="car" route="r_W_L" begin="400" end="600" probability="0.35" departLane="random"/>\n')

        # Phase 4: Straight Surge (600-800s)
        f.write('\n    <!-- Custom Phase 4: Straight Surge (600-800s) -->\n')
        write_bg("bg4", 600, 800)
        f.write('    <flow id="c4_S_N" type="car" route="r_S_N" begin="600" end="800" probability="0.35" departLane="random"/>\n')
        f.write('    <flow id="c4_W_E" type="car" route="r_W_E" begin="600" end="800" probability="0.35" departLane="random"/>\n')

        # Phase 5: Random Background (800-5000s)
        f.write('\n    <!-- Random Background/Continuation (800-5000s) -->\n')
        write_bg("bg5", 800, 5000, prob=0.08)

        f.write('</routes>\n')

if __name__ == "__main__":
    route_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Sumo Files', 'Intersection.rou.xml'))
    generate_routes(route_file)
    print(f"Successfully generated dynamic demand profiles at {route_file}")
