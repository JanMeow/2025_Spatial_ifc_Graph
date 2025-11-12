from typing import Dict
import numpy as np
from calculation.service import  PerfomranceCalculation as PC 
from calculation.service import Visualization as V 
from calculation.service import LossFunctions as LF
from calculation.service import Combinations as C
from calculation.model import Sampling
from requirement_profiles.model import factors, Weights    
from cache.model import Cache
from cache.service import get_cache, set_cache
from requirement_profiles.model import RequirementProfileRequest, RequirementProfileResponse
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp
# =========================================================================================
#  Service: Helper Functions
# =========================================================================================
def generate_hash(product:str, sampling:str, preFilter:Dict):
    # Create compact hash from preFilter: e.g., {"Fassade": [0], "Konstruktion": [0,1,2,3]} -> "0_0123"
    if preFilter is None:
        return str(product) + "_" + str(sampling) + "_" + "NoPreFilter"
    parts = []
    for indices in preFilter.values():
        if indices is None or len(indices) == 0:
            parts.append("x")
        else:
            part = str(indices[0]) + ":" + str(indices[-1])
            parts.append(part)
    return str(product) + "_" + str(sampling) + "_" + "_".join(parts)
def apply_comparison(values: np.ndarray, threshold: float, operator: str, tolerance: float = 0, is_soft: bool = False) -> np.ndarray:
    """Apply comparison operator to values with optional tolerance
    is_soft: bool = False, 
    if true, tolerance is taken into account, since "~=" always takes tolerance into account, 
    this line runs after the "~=" comparison
    """
    if operator == "==":
        return values == threshold
    if operator == "~=":
        return np.abs(values - threshold) <= tolerance
    if not is_soft:
        tolerance = 0  # If hard requirement, tolerance is not taken into account
    if operator == "<":
        return values < threshold + tolerance
    if operator == "<=":
        return values <= threshold + tolerance
    if operator == ">":
        return values > threshold - tolerance
    if operator == ">=":
        return values >= threshold - tolerance
    else:
        assert False, f"Invalid operator: {operator}"
def get_fulfilling_indices(request:RequirementProfileRequest, performances:np.array):
    # Vectorized operations - extract columns once
    thicknesses = performances[:, 0]
    prices = performances[:, 1]
    u_values = performances[:, 2]
    
    # Apply hard requirement _h
    # Currently, price and thickness mask is not taken with tolerance, only u-value
    thickness_mask_h = apply_comparison(thicknesses, request.tThresh, request.tThreshOp, request.tTol, is_soft=False)
    price_mask_h = apply_comparison(prices, request.pThresh, request.pThreshOp, request.pTol, is_soft=False)
    u_value_mask_h = apply_comparison(u_values, request.uThresh, request.uThreshOp, request.uTol, is_soft=False)

    # Apply soft requirement, tolernace taken into account _s	
    thickness_mask_s = apply_comparison(thicknesses, request.tThresh, request.tThreshOp, request.tTol, is_soft=True)
    price_mask_s = apply_comparison(prices, request.pThresh, request.pThreshOp, request.pTol, is_soft=True)
    u_value_mask_s = apply_comparison(u_values, request.uThresh, request.uThreshOp, request.uTol, is_soft=True)

    
    # Combined masks with early combination of common parts
    meets_mask = thickness_mask_h & price_mask_h & u_value_mask_h 
    meets_mask_with_tol = thickness_mask_s & price_mask_s & u_value_mask_s & ~meets_mask
    fails_mask = ~(meets_mask | meets_mask_with_tol)  # Slightly faster using OR then NOT
    
    # Use flatnonzero - slightly more semantic and potentially faster
    return np.flatnonzero(meets_mask), np.flatnonzero(meets_mask_with_tol), np.flatnonzero(fails_mask)
def get_soft_violation(request:RequirementProfileRequest, weights:Weights, matching_indices_with_tol:np.array, performances:np.array):
    if len(matching_indices_with_tol) == 0:
        return []
    p_matched = performances[matching_indices_with_tol]
    weights = np.array([weights.thickness, weights.price, weights.u_value]).reshape(-1, 1)
    #division to normalise the distances, doesnt take in 
    ops = {
        "thickness": request.tThreshOp,
        "price": request.pThreshOp,
        "u_value": request.uThreshOp,
    }
    distances = {
        "thickness": (p_matched[:, 0] - request.tThresh), 
        "price": (p_matched[:, 1] - request.pThresh),
        "u_value": (p_matched[:, 2] - request.uThresh),
    }
    tols = {
        "thickness": request.tTol,
        "price": request.pTol,
        "u_value": request.uTol,
    }
    penalties = np.zeros((p_matched.shape[0], len(ops)), dtype=float)
    credits = np.zeros((p_matched.shape[0], len(ops)), dtype=float)
    #Below operation is to translate the distsnace into loss/ credits
    for i,k in enumerate(ops.keys()):
        op = ops[k]
        # Normalise the distance by the tolerance
        z = distances[k]/tols[k]
        # the param for the logistic function, alpha and beta are tuned to get a good distribution
        alpha = 2.197
        beta = 1
        penalty, credit = LF.get_score_and_penalty(z, op, alpha, beta)
        penalties[:, i] = penalty
        credits[:, i] = credit
    weighted_loss = LF.weighted_loss_aggregate(penalties, credits, weights)
    return weighted_loss
# =========================================================================================
#  Service: Filter  Products
# =========================================================================================
def filter_single_buildup(args):
    """
    Worker function to process a single product in parallel.
    Must be a top-level function for pickling.
    """
    product_name, request_dict, product_data, cache_results = args
    
    # Reconstruct request object
    request = RequirementProfileRequest(**request_dict)
    
    # Generate Cache Key
    cache_key = generate_hash(product_name, request.sampling, request.preFilter)
    
    # Check Cache first
    if cache_key in cache_results and request.preFilter is None:
        performances = cache_results[cache_key]["performances"]
        combinations = cache_results[cache_key]["combinations"]
        print(f"Using cached results for: {cache_key}")
    else:
        print(f"Processing product: {product_name}")
        # Calculate performances for this product
        requirement = request.preFilter.get(product_name) if request.preFilter else None
        combinations = C.get_combinations(
            product_data["variants"], 
            sampling=Sampling(sampling_method=request.sampling), 
            preFilter=requirement
        )
        print(f"number of combinations for {product_name}: {len(combinations)}")
        performances = PC.get_performance_factors(combinations, product_data, factors)
    
    # Vectorized operations
    matching_indices, matching_indices_with_tol, failing_indices = get_fulfilling_indices(request, performances)
    
    # Calculate soft violation
    soft_violation = get_soft_violation(request, Weights(), matching_indices_with_tol, performances)
    
    # Get plot data
    meets_data = V.plot_data(product_data, combinations, matching_indices, performances)
    tol_data = V.plot_data(product_data, combinations, matching_indices_with_tol, performances)
    fails_data = V.plot_data(product_data, combinations, failing_indices, performances)
        
    # Return results
    return {
        'product_name': product_name,
        'cache_key': cache_key,
        'performances': performances,
        'combinations': combinations,
        'meets_data': meets_data,
        'tol_data': tol_data,
        'fails_data': fails_data,
        'soft_violation': soft_violation,
        'should_cache': cache_key not in cache_results
    }
def filter_all_buildups(request: RequirementProfileRequest, raw_data: dict, cache: Cache):
    """Handle filtering for all products comparison with conditional multiprocessing"""
    updated_meets_req = {}
    updated_meets_req_with_tol = {}
    updated_fails_req = {}
    
    if request.product == "All":
        products_to_process = [name for name in raw_data.keys() if "Aussenwand" in name]
    else:
        products_to_process = [request.product] # if only one product process it sequentially
    # ===== Only use multiprocessing for multiple products =====
    MULTIPROCESSING_THRESHOLD = 2  # Only use multiprocessing if 2+ products
    
    if len(products_to_process) < MULTIPROCESSING_THRESHOLD:
        for product_name in products_to_process:
            # Process single product directly (no multiprocessing overhead)
            print(f"Processing {len(products_to_process)} product(s) sequentially")
            # Process inline without multiprocessing
            cache_key = generate_hash(product_name, request.sampling, request.preFilter)
            
            if cache_key in cache.results:
                performances = cache.results[cache_key]["performances"]
                combinations = cache.results[cache_key]["combinations"]
                print(f"Using cached results for: {cache_key}")
            else:
                product_data = raw_data[product_name]
                requirement = request.preFilter.get(product_name) if request.preFilter else None
                combinations = C.get_combinations(
                    product_data["variants"], 
                    sampling=Sampling(sampling_method=request.sampling), 
                    preFilter=requirement
                )
                print(f"number of combinations for {product_name}: {len(combinations)}")
                performances = PC.get_performance_factors(combinations, product_data, factors)
                
                # Cache
                set_cache(cache, cache_key, {"performances": performances, "combinations": combinations})
            
            # Get indices and violations
            matching_indices, matching_indices_with_tol, failing_indices = get_fulfilling_indices(request, performances)
            soft_violation = get_soft_violation(request, Weights(), matching_indices_with_tol, performances)
            gradient_colors = V.map_to_colour_gradient(soft_violation.flatten()) if len(soft_violation) > 0 else []
            
            # Get plot data
            product_data = raw_data[product_name]
            updated_meets_req[product_name] = V.plot_data(product_data, combinations, matching_indices, performances)
            updated_meets_req_with_tol[product_name] = V.plot_data(product_data, combinations, matching_indices_with_tol, performances, soft_violation, gradient_colors)
            updated_fails_req[product_name] = V.plot_data(product_data, combinations, failing_indices, performances)
            
    else:
        # Use multiprocessing for multiple products
        print(f"Processing {len(products_to_process)} products with multiprocessing")
        
        # Convert request to dict for pickling
        request_dict = request.model_dump()
        cache_results = cache.results if hasattr(cache, 'results') else {}
        
        # Prepare arguments for parallel processing
        process_args = [
            (product_name, request_dict, raw_data[product_name], cache_results)
            for product_name in products_to_process
            if product_name in raw_data
        ]
        
        # Use multiprocessing
        num_workers = min(mp.cpu_count(), len(process_args))
        print(f"Using {num_workers} workers")
        
        min_loss, max_loss = 0, 0
        soft_violations = {}
        
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            results = executor.map(filter_single_buildup, process_args)
            
            # Aggregate results
            for result in results:
                product_name = result['product_name']
                updated_meets_req[product_name] = result['meets_data']
                updated_meets_req_with_tol[product_name] = result['tol_data']
                updated_fails_req[product_name] = result['fails_data']
                
                soft_violation = result['soft_violation']
                soft_violations[product_name] = soft_violation
                
                if len(soft_violation) > 0:
                    min_loss = min(min_loss, np.min(soft_violation))
                    max_loss = max(max_loss, np.max(soft_violation))
                
                # Update cache if needed
                if result['should_cache']:
                    set_cache(cache, result['cache_key'], {
                        "performances": result['performances'],
                        "combinations": result['combinations']
                    })

        # Apply gradient colors (for multiple products, min max needs to be pre-calcuated)
        for product_name, soft_violation in soft_violations.items():
            if len(soft_violation) == 0:
                continue
            tol_data = updated_meets_req_with_tol[product_name]
            gradient_colors = V.map_to_colour_gradient(soft_violation, min_loss, max_loss)
            for i, (score, color) in enumerate(zip(soft_violation, gradient_colors)):
                tol_data[i]["color"] = color
                tol_data[i]["soft_violation"] = score
    
    return RequirementProfileResponse(
        meets_req=updated_meets_req, 
        meets_req_with_tol=updated_meets_req_with_tol,
        fails_req=updated_fails_req, 
    )