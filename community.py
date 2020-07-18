"""
Community
"""

class Community:
    """
    Community object with grids
    """
    def __init__(self, width, height, grid_num):
        self.width = width
        self.height = height
        self.grid_num = grid_num
        self.grid = [{'healthy':[], 'infected':[]} for _ in range(grid_num**2)]
        def is_adj(i, j, grid_num):
            divmod_i = divmod(i, grid_num)
            divmod_j = divmod(j, grid_num)
            return abs(divmod_i[0] - divmod_j[0]) <= 1 and abs(divmod_i[1] - divmod_j[1]) <= 1
        self.adjacent_grids = [[j for j in range(grid_num**2) if is_adj(i, j, grid_num)] \
            for i in range(grid_num**2)]
    def clear_grid(self):
        """
        clear grid
        """
        self.grid = [{'healthy':[], 'infected':[]} for _ in range(self.grid_num**2)]
