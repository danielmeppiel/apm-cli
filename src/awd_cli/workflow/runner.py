"""Runner for workflow execution."""

import os
import re
from .parser import WorkflowDefinition
from .discovery import discover_workflows
from ..runtime.factory import RuntimeFactory


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
    """Find a workflow by name or file path.
    
    Args:
        name (str): Name of the workflow or file path.
        base_dir (str, optional): Base directory to search in.
    
    Returns:
        WorkflowDefinition: Workflow definition if found, None otherwise.
    """
    if base_dir is None:
        base_dir = os.getcwd()
    
    # If name looks like a file path, try to parse it directly
    if name.endswith('.prompt.md') or name.endswith('.workflow.md'):
        # Handle relative paths
        if not os.path.isabs(name):
            name = os.path.join(base_dir, name)
        
        if os.path.exists(name):
            try:
                from .parser import parse_workflow_file
                return parse_workflow_file(name)
            except Exception as e:
                print(f"Error parsing workflow file {name}: {e}")
                return None
    
    # Otherwise, search by name
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
    
    # Extract runtime information
    runtime_name = params.pop('_runtime', None)
    
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
    
    # If runtime is specified, execute with runtime adapter
    if runtime_name:
        try:
            # Check if runtime_name is a known runtime type
            if RuntimeFactory.runtime_exists(runtime_name):
                # Use as runtime type
                runtime = RuntimeFactory.create_runtime(runtime_name)
            else:
                # Assume it's a model name for LLM runtime (backward compatibility)
                runtime = RuntimeFactory.create_runtime("llm", runtime_name)
            
            # Execute the prompt with the runtime
            response = runtime.execute_prompt(result_content)
            return True, response
            
        except Exception as e:
            return False, f"Runtime execution failed: {str(e)}"
    
    # Default behavior: return the substituted content
    return True, result_content