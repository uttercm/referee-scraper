class RefereeCrew:
    def __init__(self, my_name, ref, ar1, ar2):
        self.ref = ref
        self.ar1 = ar1
        self.ar2 = ar2
        self.my_name = my_name

    def get_my_position(self):
        position = None
        if self.my_name == self.ref:
            position = "Ref"
        elif self.my_name == self.ar1:
            position = "AR1"
        elif self.my_name == self.ar2:
            position = "AR2"
        return position
