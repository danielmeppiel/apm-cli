"""Runner for workflow execution."""

import re
from .parser import WorkflowDefinition
from .discovery import discover_workflows


def substitute_parameters(content, params):
    """Simple string-based parameter substitution.
    
    Args:
        content (str): Content to substitute parameters in.
        params (dict): Parameters to substitute.
    
    Returns:
        str: Content with parameters substituted.
    """
    result = content
    for key, value in params.items():
        placeholder = f"${{input:{key}}}"
        result = result.replace(placeholder, str(value))
    return result


def collect_parameters(workflow_def, provided_params=None):
    """Collect parameters from command line or prompt for missing ones.
    
    Args:
        workflow_def (WorkflowDefinition): Workflow definition.
        provided_params (dict, optional): Parameters provided from command line.
    
    Returns:
        dict: Complete set of parameters.
    """
    provided_params = provided_params or {}
    
    # If there are no input parameters defined, return the provided ones
    if not workflow_def.input_parameters:
        return provided_params
    
    # Convert list parameters to dict if they're just names
    if isinstance(workflow_def.input_parameters, list):
        # List of parameter names
        param_names = workflow_def.input_parameters
    else:
        # Already a dict
        param_names = list(workflow_def.input_parameters.keys())
    
    missing_params = [p for p in param_names if p not in provided_params]
    
    if missing_params:
        print(f"Workflow '{workflow_def.name}' requires the following parameters:")
        for param in missing_params:
            value = input(f"  {param}: ")
            provided_params[param] = value
    
    return provided_params


def find_workflow_by_name(name, base_dir=None):
    """Find a workflow by name.
    
    Args:
        name (str): Name of the workflow.
        base_dir (str, optional): Base directory to search in.
    
    Returns:
        WorkflowDefinition: Workflow definition if found, None otherwise.
    """
    workflows = discover_workflows(base_dir)
    for workflow in workflows:
        if workflow.name == name:
            return workflow
    return None


def run_workflow(workflow_name, params=None, base_dir=None):
    """Run a workflow with parameters.
    
    Args:
        workflow_name (str): Name of the workflow to run.
        params (dict, optional): Parameters to use.
        base_dir (str, optional): Base directory to search for workflows.
    
    Returns:
        tuple: (bool, str) Success status and result content.
    """
    params = params or {}
    
    # Find the workflow
    workflow = find_workflow_by_name(workflow_name, base_dir)
    if not workflow:
        return False, f"Workflow '{workflow_name}' not found."
    
    # Validate the workflow
    errors = workflow.validate()
    if errors:
        return False, f"Invalid workflow: {', '.join(errors)}"
    
    # Collect missing parameters
    all_params = collect_parameters(workflow, params)
    
    # Substitute parameters
    result_content = substitute_parameters(workflow.content, all_params)
    
    return True, result_content