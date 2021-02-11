# We need to: 
# 1. ensure we write matrix elements in B at right positions
# 2. can calculate full requirement R based on B
# 3. use R in the linoprog formularion properly (equality or inequality)

# Support materials found in issue #2
# https://github.com/epogrebnyak/aloh/issues/2

# This is a direct rquirements matrix
# We need 0.5 units of second product to make 1 unit of first product
B = [0 0.5; 0 0]
