import os

# Get the directory where this script (main.py or dependencies.py) is located
current_dir = os.path.dirname(__file__)

if __name__=="__main__":
    print (current_dir)