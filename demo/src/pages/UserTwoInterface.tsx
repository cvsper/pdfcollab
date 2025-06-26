import React, { useState } from 'react';
import PDFPreview from '../components/PDFPreview';
import SignatureField from '../components/SignatureField';
import FileUpload from '../components/FileUpload';
interface UserTwoInterfaceProps {
  onSubmit: () => void;
  onCancel: () => void;
}
const UserTwoInterface: React.FC<UserTwoInterfaceProps> = ({
  onSubmit,
  onCancel
}) => {
  const [signatureComplete, setSignatureComplete] = useState(false);
  const [supportingDocs, setSupportingDocs] = useState<File[]>([]);
  const [showUploadPanel, setShowUploadPanel] = useState(false);
  const handleSignatureComplete = (signed: boolean) => {
    setSignatureComplete(signed);
  };
  const handleSupportingDocUpload = (file: File) => {
    setSupportingDocs([...supportingDocs, file]);
    setShowUploadPanel(false);
  };
  return <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          User 2 - Complete & Sign
        </h2>
        <button onClick={onCancel} className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
          Cancel
        </button>
      </div>
      <div className="bg-white shadow sm:rounded-lg overflow-hidden">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex justify-between items-center">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Document from User 1
            </h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              User 2 Editing
            </span>
          </div>
          <div className="mt-4">
            <PDFPreview userType="user2" />
          </div>
          <div className="mt-6">
            <h4 className="text-md font-medium text-gray-900">
              Digital Signature
            </h4>
            <div className="mt-2">
              <SignatureField onSignatureComplete={handleSignatureComplete} />
            </div>
          </div>
          <div className="mt-6">
            <div className="flex justify-between items-center">
              <h4 className="text-md font-medium text-gray-900">
                Supporting Documents
              </h4>
              <button onClick={() => setShowUploadPanel(true)} className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add Document
              </button>
            </div>
            {showUploadPanel && <div className="mt-2 p-4 border border-gray-200 rounded-md">
                <h5 className="text-sm font-medium text-gray-700">
                  Upload Supporting Document
                </h5>
                <div className="mt-2">
                  <FileUpload onFileSelected={handleSupportingDocUpload} />
                </div>
              </div>}
            {supportingDocs.length > 0 && <ul className="mt-3 divide-y divide-gray-200 border border-gray-200 rounded-md">
                {supportingDocs.map((doc, index) => <li key={index} className="px-3 py-3 flex items-center justify-between text-sm">
                    <div className="flex items-center">
                      <svg className="flex-shrink-0 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clipRule="evenodd" />
                      </svg>
                      <span className="ml-2 flex-1 w-0 truncate">
                        {doc.name}
                      </span>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <button className="font-medium text-red-600 hover:text-red-500">
                        Remove
                      </button>
                    </div>
                  </li>)}
              </ul>}
          </div>
          <div className="mt-6 flex justify-end space-x-3">
            <button onClick={onCancel} className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
              Cancel
            </button>
            <button onClick={onSubmit} disabled={!signatureComplete} className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white 
                ${signatureComplete ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-300 cursor-not-allowed'}`}>
              Submit & Finalize
            </button>
          </div>
        </div>
      </div>
    </div>;
};
export default UserTwoInterface;