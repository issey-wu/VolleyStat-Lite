import sys
import os

# Add the current directory to Python's path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the main function
from main import main

if __name__ == "__main__":
    main()