import os, sys
sys.path.append(os.path.join('C:\\', 'Program Files (x86)', 'Eclipse', 'Sumo', 'tools'))
import traci

sumocfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Intersection.sumocfg'))
traci.start(["sumo", "-c", sumocfg_path])

for lane in ["end1_junction_0", "end1_junction_1", "end1_junction_2"]:
    links = traci.lane.getLinks(lane)
    print(f"Links for {lane}:")
    for link in links:
        print(f"  To: {link[0]}, Internal: {link[4]}, Dir: {link[6]}")

traci.close()
