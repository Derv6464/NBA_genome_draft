class TreeNode:   
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        
    def is_leaf(self):
        return self.left is None and self.right is None

    def evaluate(self, variables):
        if self.is_leaf():
            if isinstance(self.value, str) and self.value in variables:
                return variables.get(self.value)
            elif isinstance(self.value, str):
                # Variable not in dict - return 0 as default
                return 0.0
            else:
                return float(self.value)
        else:
            left_value = self.left.evaluate(variables) if self.left else 0.0
            right_value = self.right.evaluate(variables) if self.right else 0.0
            
            # Ensure values are not None
            if left_value is None:
                left_value = 0.0
            if right_value is None:
                right_value = 0.0
            
            if self.value == '+':
                return left_value + right_value
            elif self.value == '-':
                return left_value - right_value
            elif self.value == '*':
                return left_value * right_value
            elif self.value == '/':
                # Safe division with small epsilon and clamping to avoid blowups
                eps = 1e-6
                den = right_value if abs(right_value) > eps else (eps if right_value >= 0 else -eps)
                out = left_value / den
                # Clamp extreme values to keep trees numerically stable
                if out > 1e6:
                    return 1e6
                if out < -1e6:
                    return -1e6
                return out
            elif self.value == 'min':
                return left_value if left_value <= right_value else right_value
            elif self.value == 'max':
                return left_value if left_value >= right_value else right_value
            else:
                # Unknown operator - return 0
                return 0.0