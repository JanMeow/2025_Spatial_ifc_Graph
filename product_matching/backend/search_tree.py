class ProductSearchTree:
    """
    This class is used to search for the matching subgraphs in the product search tree
    It gets the represntative combinations of the product and then builds a tree of the combinations
    For example, AW1.1 has a tree representation for each of its performance value 
    """
    def __init__(self, representative_combinations):
        self.tree = self.build_tree(representative_combinations)
    
    def find_matching_subgraphs(self, requirements):
        # Find all paths that meet requirements
        matching_paths = self.traverse_tree(self.tree, requirements)
        return matching_paths
    
    def calculate_inbetween_combinations(self, matching_paths):
        # Generate all combinations within the matching subgraphs
        return self.generate_combinations(matching_paths)