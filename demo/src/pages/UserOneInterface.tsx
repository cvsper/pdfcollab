import React, { useState } from 'react';
import PDFPreview from '../components/PDFPreview';
import FileUpload from '../components/FileUpload';
interface UserOneInterfaceProps {
  onSubmit: () => void;
  onCancel: () => void;
}
const UserOneInterface: React.FC<UserOneInterfaceProps> = ({
  onSubmit,
  onCancel
}) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isEditingPDF, setIsEditingPDF] = useState(false);
  const handleFileUpload = (file: File) => {
    setUploadedFile(file);
    setIsEditingPDF(true);
  };
  return <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">
          User 1 - Upload & Fill
        </h2>
        <button onClick={onCancel} className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
          Cancel
        </button>
      </div>
      {!isEditingPDF ? <div className="bg-white shadow sm:rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Upload PDF Document
            </h3>
            <div className="mt-2 max-w-xl text-sm text-gray-500">
              <p>
                Please upload the PDF form you want to collaborate on. You'll
                fill out your portion before sending it to User 2.
              </p>
            </div>
            <div className="mt-5">
              <FileUpload onFileSelected={handleFileUpload} />
            </div>
          </div>
        </div> : <div className="space-y-6">
          <div className="bg-white shadow sm:rounded-lg overflow-hidden">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  {uploadedFile?.name || 'Document.pdf'}
                </h3>
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                  User 1 Editing
                </span>
              </div>
              <div className="mt-4">
                <PDFPreview userType="user1" />
              </div>
              <div className="mt-6 flex justify-end space-x-3">
                <button onClick={onCancel} className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                  Cancel
                </button>
                <button onClick={onSubmit} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                  Submit to User 2
                </button>
              </div>
            </div>
          </div>
        </div>}
    </div>;
};
export default UserOneInterface;