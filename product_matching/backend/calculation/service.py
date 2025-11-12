import numpy as np
from itertools import product
from calculation.model import Sampling
class LossFunctions:
  """
  x is the already calculated normalised distance array
  attr_array is the pool of the performance values that you consider, i.e across all AW or AW1.1 etc...
  current loss function are applied cross attributes, meaning you can not pick L2 for certain attribute and logistics for other ones
  """
  def l2(X:np.array):
    return np.square(X)
  def logistic(X:np.array):
    return 1/(1+np.exp(-X))
  def gaussian(X:np.array):
    """
    X is the normalised distance array from get_soft_violation
    It is then turned into a pobability distribution
    question here is whether the distribution is only the points within soft requirement or the entire set ?
    """
    return np.exp(-(X/np.std(X))**2/2)
  def get_score_and_penalty(X:np.array, op:str, alpha:float = 2.197, beta:float = 1):
    """
    X is the normalised distance array from get_soft_violation i.e (value- target)/tolerance
    It is then turned into a pobability distribution
    In the example of X = [1,-2, 0.5], each index coorepond a perfomrance channel 
    X[0] corresponds to thickness, X[1] corresponds to price, X[2] corresponds to u-value
    m_pos is the positive part of the distance, i,e [1, 0,0],
    m_neg is the negative part of the distance, i,e [0, 2 0]
    depending on the operaion, m_post or m_neg could be the score or the penalty
    m_pos, m_neg, alpha and beta are alwways positive such that
    the term np.exp(-alpha * m_pos) is always between 0 to 1 as it equals to 1/np.exp(alpha * m_pos)
    alpha is the penalty rate
    beta is always the reward rate

    for "~=", "==", credit and penalty are measured by the closeness to the margin 
    using the same example of X = [1,-2, 0.5], the credit and penalty are calculated with 
    abs(X) = [1, 2, 0.5], the closer the value is to 0, the higher the credit and lower the penalty
    Since peanlty and credits means the same thing, we can just consider score/ penalty and set the other to 0
    here i set a scoring margin of 1, meaning if the value is off witihn 1 tolerance
    it means score else means penalty 
    this has a implication.
    For example, if a datapoint lies just within the margin say 0.999t, it gains score 
    yet, another point that lies just slightly outside thhe margin say 1.0001t, it gets penalised
    since the default penalty is higher than the credit, point2 will be more penalised than point1
    this could also be a good thing, since if "~=", "==" are set, people are generally looking for a narrorower 
    rnage of te value, and whether lying within a margin could be a determining factor
    """
    if "<" in op or ">" in op: # "<", ">", "<=", ">="
      m_pos = np.maximum(X, 0)
      m_neg = np.maximum(-X, 0)
      if "<" in op: # negative is score, positive is penalty
        penalty = 1 - np.exp(-alpha * m_pos)
        credit  = 1 - np.exp(-beta  * m_neg)
      elif ">" in op: # positive is score, negative is penalty
        penalty = 1 - np.exp(-alpha * m_neg)
        credit  = 1 - np.exp(-beta  * m_pos)
    else: # "~=", "=="
      # pure distance
      X_abs = np.abs(X)
      # inside band: |X|<=1 ->, meaning X between 0 and 1  low penalty, high credit	
      mask = X_abs <= 1
      m_within = np.where(X_abs <= 1, X_abs, 0)
      m_outside = np.where(X_abs > 1, X_abs, 0)
      penalty = 1 - np.exp(-alpha * m_outside)
      credit  = np.exp(-0.5 * m_within**2)          # peaks at 1, decays smoothly
    return penalty, credit
  def weighted_loss_aggregate(penalties:np.array,credits:np.array, W:np.array, l:float = 0.2, gamma:float = 0.1):
    """
    Get the maximmum term for penalty from the loss from above functions
    l is a custom rate between 0 to 1
    Currently loss is applied on  the matrix where 
    it further penalsities the worst performing attribute
    gamma is a custom rate between 0 to 1 for rewards here it shows that penalty is more important than credit
    """
    worst = np.max(penalties, axis = 1)
    mean_pen = (penalties @ W).flatten()  # Ensure 1D array
    mean_cred = (credits @ W).flatten()   # Ensure 1D array
    result = ((l * worst + (1 - l) * mean_pen) - gamma * mean_cred)/np.sum(W)
    return result.flatten()  # Return as 1D array
# =========================================================================================
#  Calculation: Get Combinations
# =========================================================================================
class PerfomranceCalculation:
  def get_U_values(layers, thicknesses, lambdas, rsi = 0.13, rse = 0.04):
    omitted = ["Fassade", "Konstruktion"]
    mask = [not any(keyword in l for keyword in omitted) for l in layers]
    # print(lambdas)
    # print(mask)
    #thickness/1000 because of lambda unit takes on meter
    partial_u = thicknesses.copy()[mask]/lambdas[mask]/ 1000
    return round(1/(rse + np.sum(partial_u) +rsi),2)
  def get_overall_VKF(data):
    rfs = [int(props[1][-1]) for props in data["properties"].values()]
    #0. certain rules apply
    #1. if all layers take the same rf then the overall assembly has the same rf
    #2. if not, take the lowest rfs, programmtically we just always takes the lowest rfs
    #3. the rfs of the construction layer is detemriend by the layers before and after it, take the lowest rfs for the 2
    #4. Second thought the second logic is useless, cause at the end its the lowest one of the layers that matter. ??? Should ask
    for i, layer in enumerate(data["properties"].keys()):
      if "Konstruktion" in layer:
        rf_prev = rfs[i-1]
        rf_next = rfs[i+1]
        # the bigger the value, the worse it is, idea is to take the worse
        if rf_prev > rf_next:
          rfs[i] = rf_prev
        else:
          rfs[i] = rf_next
    return max(rfs)
  def get_performance_factors(combinations, data, factors):
    performances = np.zeros((len(combinations), len(factors)))
    properties = data["properties"]
    variants = data["variants"]
    layers = list(variants.keys())
    for combo_idx, combination in enumerate(combinations):
      thicknesses = np.array([variants[layers[layer_idx]][c][0] for layer_idx, c in enumerate(combination)])
      # overall thickness calculations excludes konstruction layer
      thickness_mask = [False if "Konstruktion" in props else True for props in properties.keys()]
      lambdas = np.array([ p[0] for p in properties.values()])
      U_value = PerfomranceCalculation.get_U_values(layers, thicknesses, lambdas)
      row = performances[combo_idx]
      thickness = np.sum(thicknesses[thickness_mask])
      price = np.sum([variants[layers[layer_idx]][c][1] for layer_idx, c in enumerate(combination)])
      row[0], row[1], row[2] = thickness, price, U_value
    return performances
# =========================================================================================
#  Visualization: Map to Colour Gradient
# =========================================================================================
class Visualization:
  def plot_data(product_data:dict, combinations:np.array, indices:np.array, performances:np.array, soft_violations:np.array = None, gradient_colors:list = None):
    """
    parameters:
      soft_violations: np.array = None, gradient_colors:list = None 
      are optional parameters to add soft violation and gradient colors to the plot data for
      its input for single product since gradient can be calculated in a single product.
      For multiple products, gradient colors are calculated after taking the min max
    """
    if len(indices) == 0:
        return []
    
    variants = product_data["variants"]
    layer_names = list(variants.keys())
    # Pre-extract relevant data
    selected_combinations = combinations[indices]
    selected_performances = performances[indices]
    
    # Build thickness lookup matrix (layers x max_variants)
    max_variants = max(len(v) for v in variants.values())
    thickness_matrix = np.zeros((len(layer_names), max_variants))
    
    for layer_idx, layer_name in enumerate(layer_names):
        layer_variants = variants[layer_name]
        for variant_idx, variant in enumerate(layer_variants):
            thickness_matrix[layer_idx, variant_idx] = variant[0]
    # Vectorized lookup using advanced indexing
    result = []
    layer_indices = np.arange(len(layer_names))
    
    for i, combination in enumerate(selected_combinations):
        # Clip to valid range and extract thicknesses
        valid_combinations = np.clip(combination[:len(layer_names)], 0, max_variants - 1)
        layer_thickness = thickness_matrix[layer_indices, valid_combinations[:len(layer_indices)]].tolist()
        
        item = {
            "thicknesses": layer_thickness,
            "performances": selected_performances[i].tolist()
        }
        
        # Add soft_violation if provided
        if soft_violations is not None:
            # Flatten the soft_violations array and get scalar value
            soft_val = soft_violations.flatten()[i] if soft_violations.ndim > 1 else soft_violations[i]
            item["soft_violation"] = float(soft_val)
        
        if gradient_colors is not None and i < len(gradient_colors):
            item["color"] = gradient_colors[i]
        result.append(item)
    
    return result
  def map_to_colour_gradient(loss: np.array, min_loss: float = 0, max_loss: float = 0, rgb0: np.array = np.array([0, 255, 0]), rgb1: np.array = np.array([255, 0, 0])):
    """
    Map loss values to RGB color gradient.
    Lower loss (better) -> green (rgb0)
    Higher loss (worse) -> red (rgb1)
    Args:
        loss: Array of loss values
        rgb0: RGB color for minimum loss (default: green [0, 255, 0])
        rgb1: RGB color for maximum loss (default: red [255, 0, 0])
    Returns:
        Array of RGB color strings in format 'rgb(r, g, b)'
    """

    if len(loss) == 0:
        return []
    
    # Handle edge case where all losses are the same, or unspecified
    if min_loss == 0 and max_loss == 0:
      min_loss = np.min(loss)
      max_loss = np.max(loss)
    
    if max_loss - min_loss < 1e-10:  # Essentially all the same
        # Return middle color for all
        mid_color = (rgb0 + rgb1) / 2
        return [f'rgb({int(mid_color[0])}, {int(mid_color[1])}, {int(mid_color[2])})'] * len(loss)
    # Normalize loss to 0-1 range (0 = best, 1 = worst)
    normalized_loss = (loss - min_loss) / (max_loss - min_loss)
    # Calculate gradient: interpolate between rgb0 and rgb1
    colors = []
    for norm_val in normalized_loss:
        # Linear interpolation: rgb = rgb0 + norm_val * (rgb1 - rgb0)
        r = int(rgb0[0] + norm_val * (rgb1[0] - rgb0[0]))
        g = int(rgb0[1] + norm_val * (rgb1[1] - rgb0[1]))
        b = int(rgb0[2] + norm_val * (rgb1[2] - rgb0[2]))
        
        # Clamp values to 0-255
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b)) 
        colors.append(f'rgb({r}, {g}, {b})')
    return colors
class Combinations:
  def get_max_matrix(data):
    max_rows = max(len(layer) for layer in data.values())
    return np.zeros(shape = (max_rows, len(data.keys())))
  def get_footprint_preFilter(data, preFilter, pre_built_matrix):
    """Getting footprint of a matrix to avoid excessive calculations in each changing of preFilter"""
    if preFilter != None:
      for i, layer in enumerate(preFilter.values()): 
        pre_built_matrix[layer,i] = 1
    else:
      for i, layer in enumerate(data.values()):
        pre_built_matrix[:len(layer),i] = 1
    return pre_built_matrix
  def get_footprint_sampling(data, sampling:Sampling, pre_built_matrix):
    """Getting footprint of a matrix to avoid excessive calculations in each changing of preFilter"""
    sampling_method = sampling.sampling_method
    if sampling_method == None: # explicit return
      return np.ones(shape = pre_built_matrix.shape)
    if sampling_method == "vertical":
      for j in range(pre_built_matrix.shape[1]):
        mask = pre_built_matrix[:,j] == 1
        if len(mask) > 5: #Conditions: If more than 5 variants are selected, sample only half of them
          pre_built_matrix[::2, j] = 1 # since original matrix is all zeros
        else:
          pre_built_matrix[::,j] = 1 #whole columns if the len(col) <=5
      return pre_built_matrix
    if sampling_method == "horizontal":
      filter_idx = [i for i, key in enumerate(data.keys()) if key != "Zellulosefaserdämmung"]
      for j in range(pre_built_matrix.shape[1]):
        if j in filter_idx: # Zellulosefaserdämmung is the u-values main contributor, we keep the column of the zellulose layer while halfing the rest
          pre_built_matrix[::2, j] = 1
        else:
          pre_built_matrix[::,j] = 1 #whole columns if the len(col) <=5
      return pre_built_matrix
  def get_matrix_difference(mask_A:np.array, mask_B:np.array):
    """Comparing two combinations table to get the remaining combinations
    mask_A.shape should be the same as mask_B.shape
    mask_A = the variants for the buildup currently calculated
    mask_B = the variants for the buildup from new
    """
    if mask_A.shape != mask_B.shape:
      raise Exception("shape of matrix A does not equal shape of matrix B")
    # Where mask_A != mask_B
    args = np.argwhere(mask_A != mask_B)

    return 
    
  def get_combinations(data, sampling: Sampling = None, preFilter = None):
    preFilter_matrix = Combinations.get_footprint_preFilter(data, preFilter, Combinations.get_max_matrix(data))
    sampling_matrix = Combinations.get_footprint_sampling(data, sampling, Combinations.get_max_matrix(data))
    combined_mask = preFilter_matrix * sampling_matrix
    thickness_lists = [np.argwhere(combined_mask[:,j] == 1).flatten() for j in range(combined_mask.shape[1])]
    combinations = np.array(np.meshgrid(*thickness_lists, indexing='ij')).T.reshape(-1, len(thickness_lists))
    return combinations
