import sys
import os
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
    sys.path.insert(0, os.path.join(base_path, 'src'))
else:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def run_main_sim():
    print("\n--- Starting Main Simulation ---")
    try:
        from system_simulation.main import main, G, log_path, dt, record, quick_sim, json_paths
        
        print("Enter the full path to a JSON system file.")
        print("Or just press ENTER to use the default 'predicted_system.json'.")
        user_path = input("Path > ").strip()
        
        user_path = user_path.strip('"').strip("'")
        
        if getattr(sys, 'frozen', False):
            data_dir = os.path.join(sys._MEIPASS, 'system_simulation', 'data')
        else:
            data_dir = os.path.join(os.path.dirname(__file__), "src", "system_simulation", "data")
            
        current_paths = os.path.join(data_dir, "figure_8.json")
        
        if user_path:
            if os.path.exists(user_path):
                print(f"Loading custom system: {user_path}")
                current_paths = [user_path]
            else:
                print(f"File not found: {user_path}")
                print("Using default system instead.")
        if isinstance(current_paths, str):
            current_paths = [current_paths]
            main(G, log_path, dt, record, quick_sim, current_paths)
    except Exception as e:
        print(f"Error: {e}")
        input("Press enter to continue")
                
def run_solar_demo():
    print("starting solar sys demo")
    try:
        from system_simulation.solar_system_demo import run
        run()
    except ImportError as e:
        print(f"Error: {e}")
        input("Press enter to continue")

def run_collision_demo():
    print("starting collision demo")
    try:
        from system_simulation.system_collision_demo import run
        run()
    except ImportError as e:
        print(f"Error: {e}")
        input("PPress enter to continue")

def run_training():
    print("start training")
    try:
        from ThreeBodyProblem.train import train
        train()
    except ImportError as e:
        print(f"Error (Training requires Torch): {e}")
        input("Press enter to continue")

def run_gen():
    print("starting system generation")
    try:
        from ThreeBodyProblem.RL_agent.generate_system_json import main
        main()
    except ImportError as e:
        print(f"Error: {e}")
        input("Press enter to continue")

if __name__ == "__main__":
    while True:
        print("\n=== Polysolaris Launcher ===")
        print("1. Run main simulation")
        print("2. Run Solar System Demo")
        print("3. Run Collision Demo")
        print("4. Train Agent (Requires Torch)")
        print("5. Generate System (Requires Torch)")
        print("q. Quit")

        choice = input("\n select 1-5 or q to quit:  ").strip().lower()
        if choice == '1':
            run_main_sim()
        elif choice == '2':
            run_solar_demo()
        elif choice == '3':
            run_collision_demo()
        elif choice == '4':
            run_training()
        elif choice == '5':
            run_gen()
        elif choice == 'q':
            break

