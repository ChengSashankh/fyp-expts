class Stage:

  def __init__(self, name, ip):
    self.name = name
    self.ip = ip
    self.op = 0.0
  
  def run(self, ip):
    self.op = 0.0
    return self.op