/**
 * Workflow Navigation System for FEMS
 * This script handles the workflow navigation based on user roles and application states
 */

// Load workflow definitions from the server
let workflows = [];
let currentWorkflow = null;
let currentStep = null;
let userRole = null;

// Initialize the workflow system
function initWorkflows() {
    // Get the user role from the data attribute in the body tag
    userRole = document.body.dataset.userRole;
    
    // Fetch workflows from the server
    fetch('/api/workflows/')
        .then(response => response.json())
        .then(data => {
            workflows = data.workflows;
            highlightCurrentStep();
            setupWorkflowNavigation();
        })
        .catch(error => {
            console.error('Error loading workflows:', error);
        });
}

// Determine the current workflow and step based on the URL
function highlightCurrentStep() {
    const currentPath = window.location.pathname;
    
    // Find the workflow and step that matches the current URL
    for (const workflow of workflows) {
        for (const step of workflow.steps) {
            // Create a regex pattern from the URL template
            const urlPattern = step.url.replace(/\{[^\}]+\}/g, '[^/]+');
            const regex = new RegExp('^' + urlPattern + '$');
            
            if (regex.test(currentPath) && step.roles.includes(userRole)) {
                currentWorkflow = workflow;
                currentStep = step;
                break;
            }
        }
        if (currentStep) break;
    }
    
    // Highlight the current step in the UI if workflow navigation exists
    if (currentWorkflow && currentStep) {
        const workflowNav = document.getElementById('workflow-navigation');
        if (workflowNav) {
            renderWorkflowNavigation(workflowNav, currentWorkflow, currentStep.step);
        }
    }
}

// Set up workflow navigation elements
function setupWorkflowNavigation() {
    const workflowNav = document.getElementById('workflow-navigation');
    if (!workflowNav) return;
    
    // If we're on an application detail page, get the application ID and status
    const applicationId = document.body.dataset.applicationId;
    const applicationStatus = document.body.dataset.applicationStatus;
    
    if (applicationId && applicationStatus) {
        // Find the appropriate workflow based on the page context
        const workflow = workflows.find(w => w.name === 'Application Processing Flow');
        if (workflow) {
            // Determine current step based on application status
            let currentStepNumber = 1;
            switch (applicationStatus) {
                case 'pending':
                    currentStepNumber = 1;
                    break;
                case 'processing':
                    currentStepNumber = 2;
                    break;
                case 'approved':
                case 'rejected':
                    currentStepNumber = 4;
                    break;
                case 'completed':
                    currentStepNumber = 5;
                    break;
            }
            
            renderWorkflowNavigation(workflowNav, workflow, currentStepNumber);
        }
    } else if (currentWorkflow && currentStep) {
        // Use the workflow and step determined by the URL
        renderWorkflowNavigation(workflowNav, currentWorkflow, currentStep.step);
    }
}

// Render the workflow navigation UI
function renderWorkflowNavigation(container, workflow, currentStepNumber) {
    // Clear the container
    container.innerHTML = '';
    
    // Create the workflow header
    const header = document.createElement('h5');
    header.textContent = workflow.name;
    header.className = 'workflow-title';
    container.appendChild(header);
    
    // Create the progress bar
    const progressContainer = document.createElement('div');
    progressContainer.className = 'workflow-progress';
    container.appendChild(progressContainer);
    
    // Add steps to the progress bar
    workflow.steps.forEach(step => {
        const stepElement = document.createElement('div');
        stepElement.className = 'workflow-step';
        
        // Add appropriate classes based on step status
        if (step.step < currentStepNumber) {
            stepElement.classList.add('completed');
        } else if (step.step === currentStepNumber) {
            stepElement.classList.add('current');
        } else {
            stepElement.classList.add('pending');
        }
        
        // Add step number
        const stepNumber = document.createElement('div');
        stepNumber.className = 'step-number';
        stepNumber.textContent = step.step;
        stepElement.appendChild(stepNumber);
        
        // Add step name
        const stepName = document.createElement('div');
        stepName.className = 'step-name';
        stepName.textContent = step.name;
        stepElement.appendChild(stepName);
        
        // Add tooltip with description
        stepElement.title = step.description;
        
        // Add to container
        progressContainer.appendChild(stepElement);
        
        // Add connector line if not the last step
        if (step.step < workflow.steps.length) {
            const connector = document.createElement('div');
            connector.className = 'step-connector';
            if (step.step < currentStepNumber) {
                connector.classList.add('completed');
            }
            progressContainer.appendChild(connector);
        }
    });
    
    // Add description of current step
    const currentStep = workflow.steps.find(s => s.step === currentStepNumber);
    if (currentStep) {
        const description = document.createElement('p');
        description.className = 'current-step-description';
        description.textContent = currentStep.description;
        container.appendChild(description);
    }
}

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', initWorkflows);