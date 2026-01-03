class Node:
    def __init__(self, id, reliability=1.0, s_ms=0.0, x=0.0, y=0.0):
        self.id = int(id)
        self.reliability = float(reliability)
        self.s_ms = float(s_ms)   # işlem süresi (ms)
        self.x = float(x)
        self.y = float(y)

    def __repr__(self):
        return f"Node(id={self.id}, r={self.reliability}, s_ms={self.s_ms})"
    
    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Node) and self.id == other.id
