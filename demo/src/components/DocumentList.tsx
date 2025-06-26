import React from 'react';
interface Document {
  id: number;
  name: string;
  status: string;
  lastUpdated: string;
}
interface DocumentListProps {
  documents: Document[];
  onSelectDocument: (doc: Document) => void;
}
const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  onSelectDocument
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Awaiting User 1':
        return 'bg-yellow-100 text-yellow-800';
      case 'Awaiting User 2':
        return 'bg-blue-100 text-blue-800';
      case 'Signed & Sent':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  return <ul className="divide-y divide-gray-200">
      {documents.length === 0 ? <li className="px-4 py-6 text-center text-gray-500">
          No documents found. Start a new workflow to create one.
        </li> : documents.map(doc => <li key={doc.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
            <button className="w-full text-left" onClick={() => onSelectDocument(doc)}>
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-blue-600 truncate">
                  {doc.name}
                </p>
                <div className="ml-2 flex-shrink-0 flex">
                  <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(doc.status)}`}>
                    {doc.status}
                  </p>
                </div>
              </div>
              <div className="mt-2 sm:flex sm:justify-between">
                <div className="sm:flex">
                  <p className="flex items-center text-sm text-gray-500">
                    <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                    </svg>
                    PDF Document
                  </p>
                </div>
                <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                  <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                  </svg>
                  <p>
                    Updated <time>{doc.lastUpdated}</time>
                  </p>
                </div>
              </div>
            </button>
          </li>)}
    </ul>;
};
export default DocumentList;