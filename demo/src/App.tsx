import React, { useState } from 'react';
import Dashboard from './pages/Dashboard';
import UserOneInterface from './pages/UserOneInterface';
import UserTwoInterface from './pages/UserTwoInterface';
import CompletionPage from './pages/CompletionPage';
import Navigation from './components/Navigation';
export function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedDocument, setSelectedDocument] = useState(null);
  // Steps in the workflow
  const steps = [{
    name: 'Dashboard',
    description: 'View and manage documents'
  }, {
    name: 'User 1',
    description: 'Upload and begin form'
  }, {
    name: 'User 2',
    description: 'Complete and sign'
  }, {
    name: 'Complete',
    description: 'Document finalized'
  }];
  // Render current step content
  const renderStep = () => {
    switch (currentStep) {
      case 0:
        return <Dashboard onStartNew={() => setCurrentStep(1)} onSelectDocument={doc => {
          setSelectedDocument(doc);
          setCurrentStep(doc.status === 'Awaiting User 1' ? 1 : doc.status === 'Awaiting User 2' ? 2 : 3);
        }} />;
      case 1:
        return <UserOneInterface onSubmit={() => setCurrentStep(2)} onCancel={() => setCurrentStep(0)} />;
      case 2:
        return <UserTwoInterface onSubmit={() => setCurrentStep(3)} onCancel={() => setCurrentStep(0)} />;
      case 3:
        return <CompletionPage onDone={() => setCurrentStep(0)} />;
      default:
        return <Dashboard />;
    }
  };
  return <div className="flex flex-col min-h-screen bg-gray-50 w-full">
      <Navigation steps={steps} currentStep={currentStep} onStepClick={step => {
      // Only allow clicking on steps that make sense in the workflow
      if (step === 0 || step < currentStep) {
        setCurrentStep(step);
      }
    }} />
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderStep()}
      </main>
    </div>;
}