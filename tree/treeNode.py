class TreeNode:   
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        
    def is_leaf(self):
        """Check if node is a terminal (leaf) with no children."""
        return self.left is None and self.right is None

    def evaluate(self, variables):
        """Recursively evaluate tree: substitute variables at leaves, apply operators at internal nodes."""
        if self.is_leaf():
            if isinstance(self.value, str) and self.value in variables:
                return variables.get(self.value)
            else:
                return float(self.value)
        else:
            left_value = self.left.evaluate(variables) if self.left else 0.0
            right_value = self.right.evaluate(variables) if self.right else 0.0
            
            if self.value == '+':
                return left_value + right_value
            elif self.value == '-':
                return left_value - right_value
            elif self.value == '*':
                return left_value * right_value
            elif self.value == '/':
                if right_value == 0:
                   return 0.0
                return left_value / right_value
            elif self.value == 'min':
                return left_value if left_value <= right_value else right_value
            elif self.value == 'max':
                return left_value if left_value >= right_value else right_value