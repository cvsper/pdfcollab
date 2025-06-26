import React from 'react';
import DocumentList from '../components/DocumentList';
interface DashboardProps {
  onStartNew: () => void;
  onSelectDocument: (doc: any) => void;
}
const Dashboard: React.FC<DashboardProps> = ({
  onStartNew,
  onSelectDocument
}) => {
  // Sample document data
  const documents = [{
    id: 1,
    name: 'Employment Contract',
    status: 'Awaiting User 2',
    lastUpdated: '2 hours ago'
  }, {
    id: 2,
    name: 'Rental Agreement',
    status: 'Signed & Sent',
    lastUpdated: '1 day ago'
  }, {
    id: 3,
    name: 'Insurance Form',
    status: 'Awaiting User 1',
    lastUpdated: '3 days ago'
  }];
  return <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-4 sm:space-y-0">
        <h2 className="text-2xl font-bold text-gray-900">Document Dashboard</h2>
        <button onClick={onStartNew} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Start New PDF Workflow
        </button>
      </div>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 border-b border-gray-200">
          <h3 className="text-lg font-medium leading-6 text-gray-900">
            Your Documents
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            View and manage your document workflows
          </p>
        </div>
        <DocumentList documents={documents} onSelectDocument={onSelectDocument} />
      </div>
    </div>;
};
export default Dashboard;