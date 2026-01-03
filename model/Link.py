class Link:
    def __init__(self, source, target, delay, bandwidth, reliability):
        self.source = source  # Node nesnesi
        self.target = target  # Node nesnesi
        self.delay = float(delay)
        self.bandwidth = float(bandwidth)
        self.reliability = float(reliability)

    def __repr__(self):
        return f"Link({self.source.id} -> {self.target.id}, bw={self.bandwidth})"