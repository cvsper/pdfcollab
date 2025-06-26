import React from 'react';
interface Step {
  name: string;
  description: string;
}
interface NavigationProps {
  steps: Step[];
  currentStep: number;
  onStepClick: (step: number) => void;
}
const Navigation: React.FC<NavigationProps> = ({
  steps,
  currentStep,
  onStepClick
}) => {
  return <header className="bg-white shadow-sm w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-gray-900">
              PDF Collaborator
            </h1>
          </div>
          {/* User profile placeholder */}
          <div className="flex items-center">
            <span className="bg-gray-200 rounded-full h-8 w-8 flex items-center justify-center">
              <span className="text-gray-600">U</span>
            </span>
          </div>
        </div>
        {/* Workflow steps */}
        <nav aria-label="Progress" className="py-4">
          <ol className="flex items-center justify-between w-full">
            {steps.map((step, index) => {
            const isActive = index === currentStep;
            const isCompleted = index < currentStep;
            const isClickable = index === 0 || index < currentStep;
            return <li key={step.name} className={`relative ${index !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''} ${index !== 0 ? 'pl-8 sm:pl-20' : ''}`}>
                  {index !== 0 && <div className="absolute inset-0 flex items-center" aria-hidden="true">
                      <div className={`h-0.5 w-full ${isCompleted ? 'bg-blue-600' : 'bg-gray-200'}`}></div>
                    </div>}
                  <button onClick={() => isClickable && onStepClick(index)} className={`relative flex items-center justify-center ${isClickable ? 'cursor-pointer' : 'cursor-not-allowed'}`} disabled={!isClickable}>
                    <span className="h-9 flex items-center">
                      <span className={`relative z-10 w-8 h-8 flex items-center justify-center rounded-full ${isActive ? 'bg-white border-2 border-blue-600' : isCompleted ? 'bg-blue-600' : 'bg-gray-200'}`}>
                        {isCompleted ? <svg className="w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg> : <span className={`text-sm ${isActive ? 'text-blue-600' : 'text-gray-500'}`}>
                            {index + 1}
                          </span>}
                      </span>
                    </span>
                    <span className="hidden sm:block ml-2 text-sm font-medium text-gray-900">
                      {step.name}
                    </span>
                  </button>
                  <span className="hidden sm:block text-sm text-gray-500">
                    {step.description}
                  </span>
                </li>;
          })}
          </ol>
        </nav>
      </div>
    </header>;
};
export default Navigation;