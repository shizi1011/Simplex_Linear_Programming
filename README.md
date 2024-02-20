# Linear Programming Solver with Simplex Method

This Python project aims to solve linear programming problems using the simplex method. It handles various cases including:

- Arbitrary variables
- Constraints on arbitrary variables (<=, >=, =)
- Arbitrary constraints (<=, >=, =)
- Minimize / Maximize objective function
- Standard simplex problem cases (like Danzig)
- Two-phase simplex problem cases (with negative b coefficients)
- Bland's rule simplex problem cases (handling loops in Danzig's case)

## Installation

To run this project, please follow the steps below:

1. Clone the repository:

```shell
git clone https://github.com/shizi1011/Simplex_Linear_Programming.git
cd Simplex_Linear_Programming
```

2. Create and activate a virtual environment (optional but recommended):

```shell
python3 -m venv env
source env/bin/activate
```

3. Install the dependencies from the `requirements.txt` file:

```shell
pip install -r requirements.txt
```

## Running the Project

To start the application, run the following command:

```shell
python main.py
```