import React, { useState } from 'react';
interface Field {
  id: string;
  label: string;
  value: string;
  assignedTo: 'user1' | 'user2';
}
interface PDFPreviewProps {
  userType: 'user1' | 'user2';
}
const PDFPreview: React.FC<PDFPreviewProps> = ({
  userType
}) => {
  // Initial fields state with assignment information
  const [fields, setFields] = useState<Field[]>([{
    id: 'name',
    label: 'Employee Name',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'empId',
    label: 'Employee ID',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'dept',
    label: 'Department',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'position',
    label: 'Position',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'startDate',
    label: 'Start Date',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'salary',
    label: 'Salary',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'empType',
    label: 'Employment Type',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'address',
    label: 'Address',
    value: '',
    assignedTo: 'user1'
  }, {
    id: 'manager',
    label: 'Manager Name',
    value: '',
    assignedTo: 'user2'
  }, {
    id: 'hrRep',
    label: 'HR Representative',
    value: '',
    assignedTo: 'user2'
  }, {
    id: 'benefits',
    label: 'Benefits Package',
    value: '',
    assignedTo: 'user2'
  }, {
    id: 'notes',
    label: 'Additional Notes',
    value: '',
    assignedTo: 'user2'
  }]);
  // Toggle field assignment between users
  const toggleFieldAssignment = (fieldId: string) => {
    if (userType === 'user1') {
      setFields(fields.map(field => field.id === fieldId ? {
        ...field,
        assignedTo: field.assignedTo === 'user1' ? 'user2' : 'user1'
      } : field));
    }
  };
  // Get field style based on assignment and current user
  const getFieldStyle = (assignedTo: 'user1' | 'user2') => {
    if (userType === 'user1') {
      return assignedTo === 'user1' ? 'border-2 border-blue-300 bg-blue-50' : 'border-2 border-yellow-300 bg-yellow-50';
    }
    return assignedTo === 'user2' ? 'border-2 border-blue-300 bg-blue-50' : 'bg-gray-100';
  };
  // This is a wireframe representation of a PDF document
  // In a real application, this would be replaced with an actual PDF viewer/editor
  return <div className="border border-gray-300 rounded-md overflow-hidden">
      <div className="bg-gray-100 px-4 py-2 border-b border-gray-300 flex justify-between items-center">
        <div className="flex items-center">
          <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
          </svg>
          <span className="ml-2 text-sm font-medium text-gray-700">
            Document.pdf - Page 1 of 3
          </span>
        </div>
        <div className="flex space-x-2">
          <button className="p-1 rounded-md hover:bg-gray-200">
            <svg className="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M15.707 15.707a1 1 0 01-1.414 0l-5-5a1 1 0 010-1.414l5-5a1 1 0 011.414 1.414L11.414 10l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <button className="p-1 rounded-md hover:bg-gray-200">
            <svg className="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 15.707a1 1 0 001.414 0l5-5a1 1 0 000-1.414l-5-5a1 1 0 00-1.414 1.414L8.586 10 4.293 14.293a1 1 0 000 1.414z" clipRule="evenodd" />
            </svg>
          </button>
          <button className="p-1 rounded-md hover:bg-gray-200">
            <svg className="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>
      <div className="bg-white p-6" style={{
      minHeight: '500px'
    }}>
        <div className="space-y-6">
          <div className="border-b border-gray-200 pb-4">
            <h3 className="text-lg font-bold text-center">
              Employment Contract
            </h3>
            <p className="text-sm text-gray-500 text-center mt-1">
              Confidential Document
            </p>
            {userType === 'user1' && <div className="mt-4 flex justify-center space-x-4 text-sm">
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-100 border-2 border-blue-300 rounded-full mr-2"></div>
                  <span>Your fields</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-yellow-100 border-2 border-yellow-300 rounded-full mr-2"></div>
                  <span>Assigned to User 2</span>
                </div>
              </div>}
          </div>
          <div className="space-y-4">
            {/* Employee Information Section */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {fields.slice(0, 2).map(field => <div key={field.id}>
                  <label className="block text-sm font-medium text-gray-700 flex justify-between">
                    {field.label}
                    {userType === 'user1' && <button onClick={() => toggleFieldAssignment(field.id)} className="text-xs text-blue-600 hover:text-blue-500">
                        {field.assignedTo === 'user1' ? 'Assign to User 2' : 'Assign to me'}
                      </button>}
                  </label>
                  <div className={`mt-1 rounded-md px-3 py-2 ${getFieldStyle(field.assignedTo)}`}>
                    {field.assignedTo === userType ? field.value || 'Click to edit' : field.value}
                  </div>
                </div>)}
            </div>
            {/* Department and Position */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {fields.slice(2, 4).map(field => <div key={field.id}>
                  <label className="block text-sm font-medium text-gray-700 flex justify-between">
                    {field.label}
                    {userType === 'user1' && <button onClick={() => toggleFieldAssignment(field.id)} className="text-xs text-blue-600 hover:text-blue-500">
                        {field.assignedTo === 'user1' ? 'Assign to User 2' : 'Assign to me'}
                      </button>}
                  </label>
                  <div className={`mt-1 rounded-md px-3 py-2 ${getFieldStyle(field.assignedTo)}`}>
                    {field.assignedTo === userType ? field.value || 'Click to edit' : field.value}
                  </div>
                </div>)}
            </div>
            {/* Date, Salary, Employment Type */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {fields.slice(4, 7).map(field => <div key={field.id}>
                  <label className="block text-sm font-medium text-gray-700 flex justify-between">
                    {field.label}
                    {userType === 'user1' && <button onClick={() => toggleFieldAssignment(field.id)} className="text-xs text-blue-600 hover:text-blue-500">
                        {field.assignedTo === 'user1' ? 'Assign to User 2' : 'Assign to me'}
                      </button>}
                  </label>
                  <div className={`mt-1 rounded-md px-3 py-2 ${getFieldStyle(field.assignedTo)}`}>
                    {field.assignedTo === userType ? field.value || 'Click to edit' : field.value}
                  </div>
                </div>)}
            </div>
            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 flex justify-between">
                Address
                {userType === 'user1' && <button onClick={() => toggleFieldAssignment('address')} className="text-xs text-blue-600 hover:text-blue-500">
                    {fields.find(f => f.id === 'address')?.assignedTo === 'user1' ? 'Assign to User 2' : 'Assign to me'}
                  </button>}
              </label>
              <div className={`mt-1 rounded-md px-3 py-2 ${getFieldStyle(fields.find(f => f.id === 'address')?.assignedTo || 'user1')}`}>
                {fields.find(f => f.id === 'address')?.value || 'Click to edit'}
              </div>
            </div>
            {/* HR Information Section */}
            <div className="border-t border-gray-200 pt-4">
              <h4 className="text-md font-medium">HR Information</h4>
              <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                {fields.slice(8, 10).map(field => <div key={field.id}>
                    <label className="block text-sm font-medium text-gray-700 flex justify-between">
                      {field.label}
                      {userType === 'user1' && <button onClick={() => toggleFieldAssignment(field.id)} className="text-xs text-blue-600 hover:text-blue-500">
                          {field.assignedTo === 'user1' ? 'Assign to User 2' : 'Assign to me'}
                        </button>}
                    </label>
                    <div className={`mt-1 rounded-md px-3 py-2 ${getFieldStyle(field.assignedTo)}`}>
                      {field.assignedTo === userType ? field.value || 'Click to edit' : field.value}
                    </div>
                  </div>)}
              </div>
              {/* Benefits and Notes */}
              {fields.slice(10).map(field => <div key={field.id} className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 flex justify-between">
                    {field.label}
                    {userType === 'user1' && <button onClick={() => toggleFieldAssignment(field.id)} className="text-xs text-blue-600 hover:text-blue-500">
                        {field.assignedTo === 'user1' ? 'Assign to User 2' : 'Assign to me'}
                      </button>}
                  </label>
                  <div className={`mt-1 rounded-md px-3 py-2 ${getFieldStyle(field.assignedTo)} ${field.id === 'notes' ? 'min-h-[80px]' : ''}`}>
                    {field.assignedTo === userType ? field.value || 'Click to edit' : field.value}
                  </div>
                </div>)}
            </div>
          </div>
        </div>
      </div>
    </div>;
};
export default PDFPreview;