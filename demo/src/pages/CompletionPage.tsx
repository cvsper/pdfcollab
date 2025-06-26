import React from 'react';
interface CompletionPageProps {
  onDone: () => void;
}
const CompletionPage: React.FC<CompletionPageProps> = ({
  onDone
}) => {
  return <div className="max-w-3xl mx-auto">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6 text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
            <svg className="h-6 w-6 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 className="mt-3 text-lg font-medium text-gray-900">
            Document signed and completed!
          </h3>
          <div className="mt-2 text-sm text-gray-500">
            <p>
              The completed PDF has been automatically emailed to both users.
            </p>
          </div>
          <div className="mt-8 p-4 bg-gray-50 rounded-md">
            <h4 className="text-sm font-medium text-gray-900">
              Document Details
            </h4>
            <dl className="mt-2 text-sm text-left">
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Document Name:</dt>
                <dd className="text-gray-900">Employment Contract.pdf</dd>
              </div>
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Completed Date:</dt>
                <dd className="text-gray-900">
                  {new Date().toLocaleDateString()}
                </dd>
              </div>
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Participants:</dt>
                <dd className="text-gray-900">User 1, User 2</dd>
              </div>
              <div className="flex justify-between py-1">
                <dt className="text-gray-500">Supporting Documents:</dt>
                <dd className="text-gray-900">2 files</dd>
              </div>
            </dl>
          </div>
          <div className="mt-5 sm:mt-6 flex justify-center space-x-3">
            <button type="button" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
              <svg className="mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download PDF
            </button>
            <button type="button" onClick={onDone} className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>;
};
export default CompletionPage;